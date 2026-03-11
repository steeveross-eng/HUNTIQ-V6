"""
P2 Rollback Script
BIONIC HUNT/Chasse V3 / BIONIC™

This script provides complete rollback functionality for the P2 migration.
It can restore the database to its pre-migration state.

Features:
- Remove all migrated documents from geo_entities
- Restore from backup collections if needed
- Clear migration logs
- Validate rollback success

Usage:
    python p2_rollback.py --confirm      # Execute rollback
    python p2_rollback.py --status       # Show rollback status
    python p2_rollback.py --restore      # Restore from backup (if data lost)
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timezone
from typing import Dict, Any
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'huntiq')


class P2RollbackManager:
    """Rollback manager for P2 Geospatial Migration"""
    
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        
        # Collections
        self.geo_entities = self.db['geo_entities']
        self.territory_events = self.db['territory_events']
        self.territory_tracks = self.db['territory_tracks']
        self.migration_log = self.db['_p2_migration_log']
        self.backup_events = self.db['_backup_territory_events']
        self.backup_tracks = self.db['_backup_territory_tracks']
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status before rollback"""
        return {
            'migrated_events': self.geo_entities.count_documents({
                'metadata.migrated_from': 'territory_events'
            }),
            'migrated_tracks': self.geo_entities.count_documents({
                'metadata.migrated_from': 'territory_tracks'
            }),
            'backup_events_available': self.backup_events.count_documents({}),
            'backup_tracks_available': self.backup_tracks.count_documents({}),
            'original_events': self.territory_events.count_documents({}),
            'original_tracks': self.territory_tracks.count_documents({}),
            'last_migration': self.migration_log.find_one(
                sort=[('started_at', -1)]
            )
        }
    
    def execute_rollback(self) -> Dict[str, Any]:
        """Execute complete rollback"""
        logger.info("=" * 60)
        logger.info("P2 ROLLBACK")
        logger.info("=" * 60)
        
        stats = {
            'events_removed': 0,
            'tracks_removed': 0,
            'errors': []
        }
        
        try:
            # Step 1: Remove migrated events
            logger.info("Removing migrated events from geo_entities...")
            result_events = self.geo_entities.delete_many({
                'metadata.migrated_from': 'territory_events'
            })
            stats['events_removed'] = result_events.deleted_count
            logger.info(f"  Removed {stats['events_removed']} events")
            
            # Step 2: Remove migrated tracks
            logger.info("Removing migrated tracks from geo_entities...")
            result_tracks = self.geo_entities.delete_many({
                'metadata.migrated_from': 'territory_tracks'
            })
            stats['tracks_removed'] = result_tracks.deleted_count
            logger.info(f"  Removed {stats['tracks_removed']} tracks")
            
            # Step 3: Update migration log
            logger.info("Updating migration log...")
            self.migration_log.update_many(
                {'status': 'in_progress'},
                {
                    '$set': {
                        'status': 'rolled_back',
                        'rolled_back_at': datetime.now(timezone.utc)
                    }
                }
            )
            
            # Step 4: Log rollback
            self.migration_log.insert_one({
                'status': 'rollback_completed',
                'rolled_back_at': datetime.now(timezone.utc),
                'events_removed': stats['events_removed'],
                'tracks_removed': stats['tracks_removed']
            })
            
            logger.info("✓ Rollback completed successfully")
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            stats['errors'].append(str(e))
            return {
                'success': False,
                'stats': stats,
                'error': str(e)
            }
    
    def restore_from_backup(self) -> Dict[str, Any]:
        """Restore original data from backup collections"""
        logger.info("=" * 60)
        logger.info("P2 RESTORE FROM BACKUP")
        logger.info("=" * 60)
        
        stats = {
            'events_restored': 0,
            'tracks_restored': 0,
            'errors': []
        }
        
        try:
            # Check backups exist
            backup_events_count = self.backup_events.count_documents({})
            backup_tracks_count = self.backup_tracks.count_documents({})
            
            if backup_events_count == 0 and backup_tracks_count == 0:
                logger.warning("No backup data found!")
                return {
                    'success': False,
                    'error': 'No backup data available'
                }
            
            # Restore events
            if backup_events_count > 0:
                logger.info(f"Restoring {backup_events_count} events from backup...")
                
                # Clear current events
                self.territory_events.delete_many({})
                
                # Restore from backup
                backup_events = list(self.backup_events.find({}))
                if backup_events:
                    self.territory_events.insert_many(backup_events)
                    stats['events_restored'] = len(backup_events)
                    logger.info(f"  Restored {stats['events_restored']} events")
            
            # Restore tracks
            if backup_tracks_count > 0:
                logger.info(f"Restoring {backup_tracks_count} tracks from backup...")
                
                # Clear current tracks
                self.territory_tracks.delete_many({})
                
                # Restore from backup
                backup_tracks = list(self.backup_tracks.find({}))
                if backup_tracks:
                    self.territory_tracks.insert_many(backup_tracks)
                    stats['tracks_restored'] = len(backup_tracks)
                    logger.info(f"  Restored {stats['tracks_restored']} tracks")
            
            # Log restoration
            self.migration_log.insert_one({
                'status': 'restored_from_backup',
                'restored_at': datetime.now(timezone.utc),
                'events_restored': stats['events_restored'],
                'tracks_restored': stats['tracks_restored']
            })
            
            logger.info("✓ Restoration completed successfully")
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Restoration failed: {e}")
            stats['errors'].append(str(e))
            return {
                'success': False,
                'stats': stats,
                'error': str(e)
            }
    
    def cleanup_backups(self) -> Dict[str, Any]:
        """Remove backup collections after successful migration"""
        logger.info("Cleaning up backup collections...")
        
        try:
            events_deleted = self.backup_events.count_documents({})
            tracks_deleted = self.backup_tracks.count_documents({})
            
            self.backup_events.drop()
            self.backup_tracks.drop()
            
            logger.info(f"  Removed backup_events: {events_deleted} docs")
            logger.info(f"  Removed backup_tracks: {tracks_deleted} docs")
            
            return {
                'success': True,
                'events_deleted': events_deleted,
                'tracks_deleted': tracks_deleted
            }
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }


def main():
    parser = argparse.ArgumentParser(description='P2 Rollback - BIONIC HUNT/Chasse V3')
    parser.add_argument('--confirm', action='store_true', help='Execute rollback')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--restore', action='store_true', help='Restore from backup')
    parser.add_argument('--cleanup', action='store_true', help='Remove backup collections')
    
    args = parser.parse_args()
    
    manager = P2RollbackManager()
    
    if args.status:
        status = manager.get_status()
        print(json.dumps(status, indent=2, default=str))
        return
    
    if args.restore:
        print("\n⚠️  ATTENTION: This will restore data from backup!")
        print("Current data in territory_events and territory_tracks will be replaced.\n")
        confirm = input("Type 'YES' to proceed: ")
        if confirm != 'YES':
            print("Restoration cancelled.")
            return
        result = manager.restore_from_backup()
        print(json.dumps(result, indent=2, default=str))
        return
    
    if args.cleanup:
        print("\n⚠️  ATTENTION: This will permanently delete backup collections!")
        print("Only do this after confirming migration success.\n")
        confirm = input("Type 'YES' to proceed: ")
        if confirm != 'YES':
            print("Cleanup cancelled.")
            return
        result = manager.cleanup_backups()
        print(json.dumps(result, indent=2, default=str))
        return
    
    if args.confirm:
        print("\n⚠️  ATTENTION: This will rollback the P2 migration!")
        print("Migrated documents will be removed from geo_entities.\n")
        confirm = input("Type 'YES' to proceed: ")
        if confirm != 'YES':
            print("Rollback cancelled.")
            return
        result = manager.execute_rollback()
        print(json.dumps(result, indent=2, default=str))
        return
    
    # Default: show help
    parser.print_help()


if __name__ == '__main__':
    main()
