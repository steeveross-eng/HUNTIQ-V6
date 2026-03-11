"""
BIONIC Data Quality Monitor
============================
Système de monitoring automatique de la qualité des données.
Scan les collections sensibles pour détecter les types incorrects
et génère des rapports de qualité.

Version: 1.0.0
Date: 2026-02-19

Fonctionnalités:
- Scan quotidien des collections sensibles
- Détection de types incorrects
- Rapport automatique dans /app/logs/data_quality_report.log
- Support pour exécution manuelle ou planifiée (cron)
"""

import os
import logging
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Any
from motor.motor_asyncio import AsyncIOMotorClient
from dataclasses import dataclass, field, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CollectionScanResult:
    """Result of scanning a single collection."""
    collection_name: str
    total_documents: int = 0
    corrupted_documents: int = 0
    corruption_details: List[Dict[str, Any]] = field(default_factory=list)
    scan_duration_ms: float = 0
    status: str = "OK"


@dataclass
class DataQualityReport:
    """Complete data quality report."""
    report_id: str
    timestamp: str
    collections_scanned: int = 0
    total_documents: int = 0
    total_corrupted: int = 0
    corruption_rate: float = 0.0
    collection_results: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "OK"
    recommendations: List[str] = field(default_factory=list)


class DataQualityMonitor:
    """
    Monitors data quality in MongoDB collections.
    Detects type corruptions that could cause TypeError.
    """
    
    # Collections to monitor with their critical fields
    MONITORED_COLLECTIONS = {
        "user_contexts": {
            "critical_array_fields": [
                "pages_visited",
                "tools_used",
                "gibiers_secondaires",
                "pourvoiries_consulted",
                "setups_consulted",
                "permis_consulted"
            ],
            "critical_object_fields": [
                "season_dates",
                "quotas"
            ]
        },
        "permis_checklists": {
            "critical_array_fields": [
                "items"
            ],
            "critical_object_fields": []
        }
    }
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL')
        self.db_name = os.environ.get('DB_NAME', 'huntiq')
        self.log_file = "/app/logs/data_quality_report.log"
        self._client = None
    
    async def _get_client(self) -> AsyncIOMotorClient:
        """Get or create MongoDB client."""
        if self._client is None:
            self._client = AsyncIOMotorClient(self.mongo_url)
        return self._client
    
    async def _get_db(self):
        """Get database instance."""
        client = await self._get_client()
        return client[self.db_name]
    
    async def scan_collection(self, collection_name: str) -> CollectionScanResult:
        """
        Scan a single collection for type corruptions.
        
        Args:
            collection_name: Name of the collection to scan
        
        Returns:
            CollectionScanResult with scan details
        """
        start_time = datetime.now(timezone.utc)
        result = CollectionScanResult(collection_name=collection_name)
        
        db = await self._get_db()
        collection = db[collection_name]
        
        # Get collection config
        config = self.MONITORED_COLLECTIONS.get(collection_name, {})
        array_fields = config.get("critical_array_fields", [])
        object_fields = config.get("critical_object_fields", [])
        
        # Count total documents
        result.total_documents = await collection.count_documents({})
        
        # Build query to find corrupted documents
        or_conditions = []
        
        for field in array_fields:
            or_conditions.append({field: {"$exists": True, "$not": {"$type": "array"}}})
        
        for field in object_fields:
            or_conditions.append({field: {"$exists": True, "$not": {"$type": "object"}}})
        
        if or_conditions:
            query = {"$or": or_conditions}
            
            # Find corrupted documents
            async for doc in collection.find(query, {"_id": 0}):
                corruption_info = {
                    "document_id": doc.get("user_id", doc.get("_id", "unknown")),
                    "corrupted_fields": []
                }
                
                for field in array_fields:
                    value = doc.get(field)
                    if value is not None and not isinstance(value, list):
                        corruption_info["corrupted_fields"].append({
                            "field": field,
                            "expected_type": "array",
                            "actual_type": type(value).__name__,
                            "actual_value": str(value)[:50]
                        })
                
                for field in object_fields:
                    value = doc.get(field)
                    if value is not None and not isinstance(value, dict):
                        corruption_info["corrupted_fields"].append({
                            "field": field,
                            "expected_type": "object",
                            "actual_type": type(value).__name__,
                            "actual_value": str(value)[:50]
                        })
                
                if corruption_info["corrupted_fields"]:
                    result.corruption_details.append(corruption_info)
                    result.corrupted_documents += 1
        
        # Calculate duration
        end_time = datetime.now(timezone.utc)
        result.scan_duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Set status
        if result.corrupted_documents > 0:
            result.status = "CORRUPTED"
        
        return result
    
    async def run_full_scan(self) -> DataQualityReport:
        """
        Run a full scan of all monitored collections.
        
        Returns:
            DataQualityReport with complete scan results
        """
        logger.info("Starting data quality scan...")
        
        report = DataQualityReport(
            report_id=f"DQ-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        for collection_name in self.MONITORED_COLLECTIONS:
            logger.info(f"Scanning collection: {collection_name}")
            
            try:
                result = await self.scan_collection(collection_name)
                report.collection_results.append(asdict(result))
                report.collections_scanned += 1
                report.total_documents += result.total_documents
                report.total_corrupted += result.corrupted_documents
                
                if result.corrupted_documents > 0:
                    logger.warning(
                        f"Found {result.corrupted_documents} corrupted documents "
                        f"in {collection_name}"
                    )
            except Exception as e:
                logger.error(f"Error scanning {collection_name}: {e}")
                report.collection_results.append({
                    "collection_name": collection_name,
                    "status": "ERROR",
                    "error": str(e)
                })
        
        # Calculate corruption rate
        if report.total_documents > 0:
            report.corruption_rate = (report.total_corrupted / report.total_documents) * 100
        
        # Set overall status
        if report.total_corrupted > 0:
            report.status = "CORRUPTED"
            report.recommendations.append(
                "Run cleanup script to fix corrupted documents"
            )
            report.recommendations.append(
                "Investigate source of corruption"
            )
        else:
            report.recommendations.append(
                "No issues detected - continue monitoring"
            )
        
        logger.info(
            f"Scan complete: {report.total_documents} documents, "
            f"{report.total_corrupted} corrupted ({report.corruption_rate:.2f}%)"
        )
        
        return report
    
    async def save_report(self, report: DataQualityReport):
        """Save report to log file."""
        # Ensure logs directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Append to log file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(asdict(report)) + "\n")
        
        logger.info(f"Report saved to {self.log_file}")
    
    async def run_and_report(self) -> DataQualityReport:
        """Run full scan and save report."""
        report = await self.run_full_scan()
        await self.save_report(report)
        return report
    
    async def close(self):
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None


# Convenience function for command-line or cron usage
async def run_data_quality_check():
    """Run data quality check and print results."""
    monitor = DataQualityMonitor()
    try:
        report = await monitor.run_and_report()
        
        print("═══════════════════════════════════════════════════════════════")
        print("BIONIC DATA QUALITY REPORT")
        print("═══════════════════════════════════════════════════════════════")
        print(f"Report ID: {report.report_id}")
        print(f"Timestamp: {report.timestamp}")
        print(f"Status: {report.status}")
        print(f"Collections Scanned: {report.collections_scanned}")
        print(f"Total Documents: {report.total_documents}")
        print(f"Corrupted Documents: {report.total_corrupted}")
        print(f"Corruption Rate: {report.corruption_rate:.2f}%")
        print("")
        print("Recommendations:")
        for rec in report.recommendations:
            print(f"  - {rec}")
        print("═══════════════════════════════════════════════════════════════")
        
        return report
    finally:
        await monitor.close()


# Create singleton instance
data_quality_monitor = DataQualityMonitor()


# Main entry point
if __name__ == "__main__":
    asyncio.run(run_data_quality_check())
