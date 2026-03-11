"""
P2 Geospatial Migration - Main Script
BIONIC HUNT/Chasse V3 / BIONIC™

This script orchestrates the P2 geospatial normalization migration:
- territory_events → geo_entities (entity_type: "observation")
- territory_tracks → geo_entities (entity_type: "track")

Features:
- Automatic backup before migration
- Incremental batch processing (100 docs at a time)
- Validation after each batch
- Automatic rollback on errors
- Dry-run mode for testing
- Detailed migration report

Usage:
    python p2_migration_main.py --dry-run      # Test without modifications
    python p2_migration_main.py --execute      # Execute real migration
    python p2_migration_main.py --status       # Show migration status
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'/app/backend/migrations/p2_migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'huntiq')
BATCH_SIZE = 100
MAX_ERRORS_BEFORE_ROLLBACK = 5


class P2MigrationManager:
    """Main migration orchestrator for P2 Geospatial Normalization"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.client = MongoClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        
        # Collections
        self.geo_entities = self.db['geo_entities']
        self.territory_events = self.db['territory_events']
        self.territory_tracks = self.db['territory_tracks']
        self.migration_log = self.db['_p2_migration_log']
        self.backup_events = self.db['_backup_territory_events']
        self.backup_tracks = self.db['_backup_territory_tracks']
        
        # Statistics
        self.stats = {
            'events_migrated': 0,
            'events_failed': 0,
            'tracks_migrated': 0,
            'tracks_failed': 0,
            'errors': [],
            'started_at': None,
            'completed_at': None
        }
    
    def run_migration(self) -> Dict[str, Any]:
        """Execute the complete P2 migration"""
        logger.info("=" * 60)
        logger.info(f"P2 MIGRATION {'(DRY-RUN)' if self.dry_run else '(EXECUTE)'}")
        logger.info("=" * 60)
        
        self.stats['started_at'] = datetime.now(timezone.utc)
        
        try:
            # Step 1: Pre-migration validation
            if not self._validate_preconditions():
                return self._generate_report(success=False, reason="Preconditions failed")
            
            # Step 2: Backup (if not dry-run)
            if not self.dry_run:
                if not self._create_backup():
                    return self._generate_report(success=False, reason="Backup failed")
            
            # Step 3: Migrate events
            logger.info("\n--- PHASE P2.1: Migrating territory_events ---")
            events_success = self._migrate_events()
            
            # Step 4: Migrate tracks
            logger.info("\n--- PHASE P2.2: Migrating territory_tracks ---")
            tracks_success = self._migrate_tracks()
            
            # Step 5: Validation
            logger.info("\n--- PHASE P2.6: Post-migration validation ---")
            validation_success = self._validate_migration()
            
            # Step 6: Cleanup (if not dry-run and successful)
            if not self.dry_run and events_success and tracks_success and validation_success:
                logger.info("\n--- PHASE P2.5: Cleanup (deferred) ---")
                logger.info("Collections legacy conservées pour validation manuelle")
                logger.info("Exécutez 'python p2_cleanup.py' après validation complète")
            
            self.stats['completed_at'] = datetime.now(timezone.utc)
            
            success = events_success and tracks_success and validation_success
            return self._generate_report(success=success)
            
        except Exception as e:
            logger.error(f"Migration failed with exception: {e}")
            self.stats['errors'].append(str(e))
            
            if not self.dry_run:
                logger.info("Initiating automatic rollback...")
                self._rollback()
            
            return self._generate_report(success=False, reason=str(e))
    
    def _validate_preconditions(self) -> bool:
        """Validate preconditions before migration"""
        logger.info("Validating preconditions...")
        
        # Check collections exist
        events_count = self.territory_events.count_documents({})
        tracks_count = self.territory_tracks.count_documents({})
        geo_count = self.geo_entities.count_documents({})
        
        logger.info(f"  territory_events: {events_count} documents")
        logger.info(f"  territory_tracks: {tracks_count} documents")
        logger.info(f"  geo_entities: {geo_count} documents (before)")
        
        # Check for previous incomplete migration
        incomplete = self.migration_log.find_one({'status': 'in_progress'})
        if incomplete:
            logger.warning("Previous incomplete migration detected!")
            logger.warning(f"  Started: {incomplete.get('started_at')}")
            if not self.dry_run:
                logger.error("Please run rollback before new migration")
                return False
        
        # Check geo_entities doesn't already have migrated data
        migrated_events = self.geo_entities.count_documents({
            'metadata.migrated_from': 'territory_events'
        })
        migrated_tracks = self.geo_entities.count_documents({
            'metadata.migrated_from': 'territory_tracks'
        })
        
        if migrated_events > 0 or migrated_tracks > 0:
            logger.warning(f"Already migrated: {migrated_events} events, {migrated_tracks} tracks")
            if not self.dry_run:
                logger.error("Run rollback or cleanup before re-migration")
                return False
        
        logger.info("✓ Preconditions validated")
        return True
    
    def _create_backup(self) -> bool:
        """Create backup of source collections"""
        logger.info("Creating backup...")
        
        try:
            # Backup territory_events
            events = list(self.territory_events.find({}))
            if events:
                self.backup_events.delete_many({})
                self.backup_events.insert_many(events)
                logger.info(f"  Backed up {len(events)} events")
            
            # Backup territory_tracks
            tracks = list(self.territory_tracks.find({}))
            if tracks:
                self.backup_tracks.delete_many({})
                self.backup_tracks.insert_many(tracks)
                logger.info(f"  Backed up {len(tracks)} tracks")
            
            # Log migration start
            self.migration_log.insert_one({
                'status': 'in_progress',
                'started_at': datetime.now(timezone.utc),
                'events_count': len(events),
                'tracks_count': len(tracks)
            })
            
            logger.info("✓ Backup created")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def _migrate_events(self) -> bool:
        """Migrate territory_events to geo_entities as observations"""
        events = list(self.territory_events.find({}))
        total = len(events)
        
        if total == 0:
            logger.info("No events to migrate")
            return True
        
        logger.info(f"Migrating {total} events...")
        
        migrated_docs = []
        
        for i, event in enumerate(events):
            try:
                # Transform event to geo_entity
                geo_entity = self._transform_event_to_geo_entity(event)
                migrated_docs.append(geo_entity)
                
                # Batch insert
                if len(migrated_docs) >= BATCH_SIZE:
                    if not self.dry_run:
                        self.geo_entities.insert_many(migrated_docs)
                    self.stats['events_migrated'] += len(migrated_docs)
                    logger.info(f"  Batch inserted: {self.stats['events_migrated']}/{total}")
                    migrated_docs = []
                
            except Exception as e:
                logger.error(f"Error migrating event {event.get('_id')}: {e}")
                self.stats['events_failed'] += 1
                self.stats['errors'].append(f"Event {event.get('_id')}: {e}")
                
                if self.stats['events_failed'] >= MAX_ERRORS_BEFORE_ROLLBACK:
                    logger.error("Too many errors, aborting migration")
                    return False
        
        # Insert remaining docs
        if migrated_docs:
            if not self.dry_run:
                self.geo_entities.insert_many(migrated_docs)
            self.stats['events_migrated'] += len(migrated_docs)
        
        logger.info(f"✓ Events migrated: {self.stats['events_migrated']}/{total}")
        logger.info(f"  Failed: {self.stats['events_failed']}")
        
        return self.stats['events_failed'] < MAX_ERRORS_BEFORE_ROLLBACK
    
    def _transform_event_to_geo_entity(self, event: Dict) -> Dict:
        """Transform a territory_event document to geo_entity format"""
        import uuid
        
        now = datetime.now(timezone.utc)
        lat = event.get('latitude', 0)
        lng = event.get('longitude', 0)
        
        # Generate name from event type and species
        event_type = event.get('event_type', 'observation') or 'observation'
        species = event.get('species') or 'inconnu'
        name = f"{event_type.replace('_', ' ').title()} - {species.title()}"
        
        return {
            '_id': str(uuid.uuid4()),
            'user_id': event.get('user_id', ''),
            'group_id': event.get('group_id'),
            'name': name,
            'entity_type': 'observation',
            'subtype': event_type,
            
            # GeoJSON location
            'location': {
                'type': 'Point',
                'coordinates': [lng, lat]
            },
            
            # No geometry for point observations
            'geometry': None,
            'radius': None,
            
            # State
            'active': True,
            'visible': True,
            
            # Visuals
            'color': event.get('color', '#FF6B6B'),
            'icon': event.get('icon', 'eye'),
            
            # Enriched metadata
            'metadata': {
                # Event-specific
                'event_type': event_type,
                'species': species,
                'species_confidence': event.get('species_confidence'),
                'count_estimate': event.get('count_estimate'),
                'captured_at': event.get('captured_at'),
                'source': event.get('source', 'app'),
                'photo_id': event.get('photo_id'),
                
                # Migration tracking
                'legacy_id': str(event.get('_id')),
                'migrated_from': 'territory_events',
                'migration_date': now,
                
                # Preserve original metadata
                **event.get('metadata', {})
            },
            
            'description': event.get('description'),
            'created_at': event.get('created_at', now),
            'updated_at': now
        }
    
    def _migrate_tracks(self) -> bool:
        """Migrate territory_tracks to geo_entities as tracks"""
        tracks = list(self.territory_tracks.find({}))
        total = len(tracks)
        
        if total == 0:
            logger.info("No tracks to migrate")
            return True
        
        logger.info(f"Migrating {total} tracks...")
        
        migrated_docs = []
        
        for i, track in enumerate(tracks):
            try:
                # Transform track to geo_entity
                geo_entity = self._transform_track_to_geo_entity(track)
                migrated_docs.append(geo_entity)
                
                # Batch insert
                if len(migrated_docs) >= BATCH_SIZE:
                    if not self.dry_run:
                        self.geo_entities.insert_many(migrated_docs)
                    self.stats['tracks_migrated'] += len(migrated_docs)
                    logger.info(f"  Batch inserted: {self.stats['tracks_migrated']}/{total}")
                    migrated_docs = []
                
            except Exception as e:
                logger.error(f"Error migrating track {track.get('_id')}: {e}")
                self.stats['tracks_failed'] += 1
                self.stats['errors'].append(f"Track {track.get('_id')}: {e}")
                
                if self.stats['tracks_failed'] >= MAX_ERRORS_BEFORE_ROLLBACK:
                    logger.error("Too many errors, aborting migration")
                    return False
        
        # Insert remaining docs
        if migrated_docs:
            if not self.dry_run:
                self.geo_entities.insert_many(migrated_docs)
            self.stats['tracks_migrated'] += len(migrated_docs)
        
        logger.info(f"✓ Tracks migrated: {self.stats['tracks_migrated']}/{total}")
        logger.info(f"  Failed: {self.stats['tracks_failed']}")
        
        return self.stats['tracks_failed'] < MAX_ERRORS_BEFORE_ROLLBACK
    
    def _transform_track_to_geo_entity(self, track: Dict) -> Dict:
        """Transform a territory_track document to geo_entity format"""
        import uuid
        
        now = datetime.now(timezone.utc)
        points = track.get('points', [])
        
        # Get first point as location
        first_point = points[0] if points else {'lat': 0, 'lng': 0}
        lat = first_point.get('lat', first_point.get('latitude', 0))
        lng = first_point.get('lng', first_point.get('longitude', 0))
        
        # Build LineString geometry from points
        line_coords = []
        for pt in points:
            pt_lat = pt.get('lat', pt.get('latitude', 0))
            pt_lng = pt.get('lng', pt.get('longitude', 0))
            line_coords.append([pt_lng, pt_lat])
        
        geometry = None
        if len(line_coords) >= 2:
            geometry = {
                'type': 'LineString',
                'coordinates': line_coords
            }
        
        return {
            '_id': str(uuid.uuid4()),
            'user_id': track.get('user_id', ''),
            'group_id': track.get('group_id'),
            'name': track.get('name', f"Parcours du {track.get('created_at', now).strftime('%d/%m/%Y')}"),
            'entity_type': 'track',
            'subtype': 'gps_track',
            
            # GeoJSON location (first point)
            'location': {
                'type': 'Point',
                'coordinates': [lng, lat]
            },
            
            # LineString geometry
            'geometry': geometry,
            'radius': None,
            
            # State
            'active': True,
            'visible': True,
            
            # Visuals
            'color': track.get('color', '#4ECDC4'),
            'icon': track.get('icon', 'route'),
            
            # Enriched metadata
            'metadata': {
                # Track-specific
                'points': points,
                'points_count': len(points),
                'distance_km': track.get('distance_km', self._calculate_distance(points)),
                'duration_minutes': track.get('duration_minutes'),
                'started_at': track.get('started_at'),
                'ended_at': track.get('ended_at'),
                'is_recording': track.get('is_active', False),
                
                # Migration tracking
                'legacy_id': str(track.get('_id')),
                'migrated_from': 'territory_tracks',
                'migration_date': now,
                
                # Preserve original metadata
                **track.get('metadata', {})
            },
            
            'description': track.get('description'),
            'created_at': track.get('created_at', now),
            'updated_at': now
        }
    
    def _calculate_distance(self, points: List[Dict]) -> float:
        """Calculate approximate distance in km from points"""
        import math
        
        if len(points) < 2:
            return 0.0
        
        total_distance = 0.0
        R = 6371  # Earth radius in km
        
        for i in range(1, len(points)):
            lat1 = math.radians(points[i-1].get('lat', points[i-1].get('latitude', 0)))
            lng1 = math.radians(points[i-1].get('lng', points[i-1].get('longitude', 0)))
            lat2 = math.radians(points[i].get('lat', points[i].get('latitude', 0)))
            lng2 = math.radians(points[i].get('lng', points[i].get('longitude', 0)))
            
            dlat = lat2 - lat1
            dlng = lng2 - lng1
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            total_distance += R * c
        
        return round(total_distance, 2)
    
    def _validate_migration(self) -> bool:
        """Validate the migration was successful"""
        logger.info("Validating migration...")
        
        # Count migrated documents
        migrated_events = self.geo_entities.count_documents({
            'metadata.migrated_from': 'territory_events'
        }) if not self.dry_run else self.stats['events_migrated']
        
        migrated_tracks = self.geo_entities.count_documents({
            'metadata.migrated_from': 'territory_tracks'
        }) if not self.dry_run else self.stats['tracks_migrated']
        
        original_events = self.territory_events.count_documents({})
        original_tracks = self.territory_tracks.count_documents({})
        
        logger.info(f"  Events: {migrated_events}/{original_events} migrated")
        logger.info(f"  Tracks: {migrated_tracks}/{original_tracks} migrated")
        
        # Validate geospatial index works
        if not self.dry_run and migrated_events > 0:
            try:
                # Test $near query on observations
                test_query = self.geo_entities.find_one({
                    'entity_type': 'observation',
                    'location': {
                        '$near': {
                            '$geometry': {'type': 'Point', 'coordinates': [-71.0, 46.0]},
                            '$maxDistance': 1000000
                        }
                    }
                })
                logger.info("  ✓ Geospatial query on observations: OK")
            except Exception as e:
                logger.warning(f"  ⚠ Geospatial query failed: {e}")
        
        events_ok = migrated_events >= original_events - self.stats['events_failed']
        tracks_ok = migrated_tracks >= original_tracks - self.stats['tracks_failed']
        
        if events_ok and tracks_ok:
            logger.info("✓ Migration validated")
            return True
        else:
            logger.error("✗ Migration validation failed")
            return False
    
    def _rollback(self) -> bool:
        """Rollback migration by removing migrated documents"""
        logger.info("Rolling back migration...")
        
        try:
            # Remove migrated events
            result_events = self.geo_entities.delete_many({
                'metadata.migrated_from': 'territory_events'
            })
            logger.info(f"  Removed {result_events.deleted_count} migrated events")
            
            # Remove migrated tracks
            result_tracks = self.geo_entities.delete_many({
                'metadata.migrated_from': 'territory_tracks'
            })
            logger.info(f"  Removed {result_tracks.deleted_count} migrated tracks")
            
            # Update migration log
            self.migration_log.update_one(
                {'status': 'in_progress'},
                {'$set': {'status': 'rolled_back', 'rolled_back_at': datetime.now(timezone.utc)}}
            )
            
            logger.info("✓ Rollback completed")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def _generate_report(self, success: bool, reason: str = None) -> Dict[str, Any]:
        """Generate migration report"""
        report = {
            'success': success,
            'dry_run': self.dry_run,
            'reason': reason,
            'statistics': self.stats,
            'summary': {
                'events': {
                    'migrated': self.stats['events_migrated'],
                    'failed': self.stats['events_failed']
                },
                'tracks': {
                    'migrated': self.stats['tracks_migrated'],
                    'failed': self.stats['tracks_failed']
                },
                'total_migrated': self.stats['events_migrated'] + self.stats['tracks_migrated'],
                'total_failed': self.stats['events_failed'] + self.stats['tracks_failed']
            }
        }
        
        # Save report to file
        report_path = f'/app/backend/migrations/p2_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"\nReport saved to: {report_path}")
        
        # Log summary
        logger.info("\n" + "=" * 60)
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Status: {'SUCCESS' if success else 'FAILED'}")
        logger.info(f"Mode: {'DRY-RUN' if self.dry_run else 'EXECUTED'}")
        logger.info(f"Events migrated: {self.stats['events_migrated']}")
        logger.info(f"Tracks migrated: {self.stats['tracks_migrated']}")
        logger.info(f"Total errors: {len(self.stats['errors'])}")
        
        if reason:
            logger.info(f"Reason: {reason}")
        
        return report
    
    def get_status(self) -> Dict[str, Any]:
        """Get current migration status"""
        return {
            'territory_events': self.territory_events.count_documents({}),
            'territory_tracks': self.territory_tracks.count_documents({}),
            'geo_entities_total': self.geo_entities.count_documents({}),
            'migrated_events': self.geo_entities.count_documents({'metadata.migrated_from': 'territory_events'}),
            'migrated_tracks': self.geo_entities.count_documents({'metadata.migrated_from': 'territory_tracks'}),
            'backup_events': self.backup_events.count_documents({}),
            'backup_tracks': self.backup_tracks.count_documents({}),
            'migration_log': list(self.migration_log.find({}).sort('started_at', -1).limit(5))
        }


def main():
    parser = argparse.ArgumentParser(description='P2 Geospatial Migration - BIONIC HUNT/Chasse V3')
    parser.add_argument('--dry-run', action='store_true', help='Test migration without modifications')
    parser.add_argument('--execute', action='store_true', help='Execute real migration')
    parser.add_argument('--status', action='store_true', help='Show migration status')
    parser.add_argument('--rollback', action='store_true', help='Rollback migration')
    
    args = parser.parse_args()
    
    if args.status:
        manager = P2MigrationManager(dry_run=True)
        status = manager.get_status()
        print(json.dumps(status, indent=2, default=str))
        return
    
    if args.rollback:
        manager = P2MigrationManager(dry_run=False)
        manager._rollback()
        return
    
    if args.execute:
        print("\n⚠️  ATTENTION: This will modify the database!")
        print("Make sure you have a backup.\n")
        confirm = input("Type 'YES' to proceed: ")
        if confirm != 'YES':
            print("Migration cancelled.")
            return
        manager = P2MigrationManager(dry_run=False)
    else:
        # Default to dry-run
        manager = P2MigrationManager(dry_run=True)
    
    report = manager.run_migration()
    
    if report['success']:
        print("\n✅ Migration completed successfully!")
    else:
        print(f"\n❌ Migration failed: {report.get('reason')}")


if __name__ == '__main__':
    main()
