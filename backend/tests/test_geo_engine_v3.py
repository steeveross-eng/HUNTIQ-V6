"""
Test Suite for Geo Engine V3 - Unified Geospatial API
Phase P6.2 (Normalization) + P6.3 (Optimization) + P6.5 (Admin)

Tests:
- CRUD operations for geo entities
- Spatial queries (nearby, within-bbox, clusters)
- Hunting groups management
- Hotspot auto-generation
- Admin analytics and monetization endpoints
- WebSocket sync status
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user and group IDs
TEST_USER_ID = "test_user_geo_v3"
TEST_GROUP_ID = "test_group_geo_v3"
DEFAULT_USER_ID = "default_user"


class TestGeoEngineModuleInfo:
    """Test module info endpoint"""
    
    def test_module_info(self):
        """GET /api/v1/geo/ - Module info"""
        response = requests.get(f"{BASE_URL}/api/v1/geo/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["module"] == "geo_engine"
        assert data["version"] == "1.0.0"
        assert "features" in data
        assert "2dsphere spatial queries" in data["features"]
        print(f"✓ Module info: {data['module']} v{data['version']}")


class TestGeoEntityCRUD:
    """Test CRUD operations for geo entities"""
    
    created_entity_id = None
    
    def test_create_entity_waypoint(self):
        """POST /api/v1/geo/entities - Create waypoint entity"""
        payload = {
            "name": "TEST_Waypoint_V3",
            "entity_type": "waypoint",
            "subtype": "observation",
            "latitude": 46.82,
            "longitude": -71.21,
            "color": "#3b82f6",
            "active": True,
            "visible": True,
            "metadata": {
                "habitat": "forest_mixed",
                "density": 0.65,
                "altitude": 300.0,
                "tags": ["test", "v3"]
            },
            "description": "Test waypoint for V3 API"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/geo/entities?user_id={TEST_USER_ID}",
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "TEST_Waypoint_V3"
        assert data["entity_type"] == "waypoint"
        assert data["latitude"] == 46.82
        assert data["longitude"] == -71.21
        assert data["user_id"] == TEST_USER_ID
        assert "id" in data
        
        TestGeoEntityCRUD.created_entity_id = data["id"]
        print(f"✓ Created waypoint entity: {data['id']}")
    
    def test_create_entity_hotspot(self):
        """POST /api/v1/geo/entities - Create hotspot entity with enriched metadata"""
        payload = {
            "name": "TEST_Hotspot_Premium",
            "entity_type": "hotspot",
            "subtype": "auto_generated",
            "latitude": 46.83,
            "longitude": -71.22,
            "color": "#ef4444",
            "active": True,
            "visible": True,
            "metadata": {
                "habitat": "edge",
                "density": 0.85,
                "altitude": 320.0,
                "activity_score": 78.5,
                "corridors": [],
                "tags": ["test", "premium", "hotspot"]
            },
            "description": "Test premium hotspot"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/geo/entities?user_id={TEST_USER_ID}",
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["entity_type"] == "hotspot"
        # Verify basic metadata fields are preserved
        metadata = data.get("metadata", {})
        assert metadata.get("habitat") == "edge" or metadata.get("density") == 0.85
        print(f"✓ Created hotspot entity: {data['id']}")
    
    def test_create_entity_zone(self):
        """POST /api/v1/geo/entities - Create zone entity with radius"""
        payload = {
            "name": "TEST_Zone_Hunting",
            "entity_type": "zone",
            "latitude": 46.84,
            "longitude": -71.23,
            "radius": 750.0,
            "color": "#22c55e",
            "active": True,
            "metadata": {
                "habitat": "clearing",
                "density": 0.55,
                "tags": ["zone", "test"]
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/geo/entities?user_id={TEST_USER_ID}",
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["entity_type"] == "zone"
        assert data["radius"] == 750.0
        print(f"✓ Created zone entity: {data['id']}")
    
    def test_list_entities(self):
        """GET /api/v1/geo/entities - List entities with filters"""
        response = requests.get(
            f"{BASE_URL}/api/v1/geo/entities?user_id={TEST_USER_ID}&limit=50"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verify structure
        for entity in data:
            assert "id" in entity
            assert "name" in entity
            assert "entity_type" in entity
            assert "user_id" in entity
        
        print(f"✓ Listed {len(data)} entities for user {TEST_USER_ID}")
    
    def test_list_entities_by_type(self):
        """GET /api/v1/geo/entities - Filter by entity_type"""
        response = requests.get(
            f"{BASE_URL}/api/v1/geo/entities?user_id={TEST_USER_ID}&entity_type=waypoint"
        )
        assert response.status_code == 200
        
        data = response.json()
        for entity in data:
            assert entity["entity_type"] == "waypoint"
        
        print(f"✓ Filtered {len(data)} waypoint entities")
    
    def test_get_entity_by_id(self):
        """GET /api/v1/geo/entities/{id} - Get specific entity"""
        if not TestGeoEntityCRUD.created_entity_id:
            pytest.skip("No entity created to get")
        
        response = requests.get(
            f"{BASE_URL}/api/v1/geo/entities/{TestGeoEntityCRUD.created_entity_id}?user_id={TEST_USER_ID}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == TestGeoEntityCRUD.created_entity_id
        assert data["name"] == "TEST_Waypoint_V3"
        print(f"✓ Retrieved entity by ID: {data['id']}")
    
    def test_update_entity(self):
        """PUT /api/v1/geo/entities/{id} - Update entity"""
        if not TestGeoEntityCRUD.created_entity_id:
            pytest.skip("No entity created to update")
        
        update_payload = {
            "name": "TEST_Waypoint_V3_Updated",
            "description": "Updated description",
            "metadata": {
                "density": 0.75,
                "tags": ["test", "v3", "updated"]
            }
        }
        
        response = requests.put(
            f"{BASE_URL}/api/v1/geo/entities/{TestGeoEntityCRUD.created_entity_id}?user_id={TEST_USER_ID}",
            json=update_payload
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "TEST_Waypoint_V3_Updated"
        assert data["description"] == "Updated description"
        print(f"✓ Updated entity: {data['id']}")
        
        # Verify persistence with GET
        get_response = requests.get(
            f"{BASE_URL}/api/v1/geo/entities/{TestGeoEntityCRUD.created_entity_id}?user_id={TEST_USER_ID}"
        )
        assert get_response.status_code == 200
        fetched = get_response.json()
        assert fetched["name"] == "TEST_Waypoint_V3_Updated"
        print("✓ Update persisted correctly")


class TestSpatialQueries:
    """Test spatial query endpoints using 2dsphere index"""
    
    def test_nearby_search(self):
        """GET /api/v1/geo/nearby - Find entities near a location"""
        response = requests.get(
            f"{BASE_URL}/api/v1/geo/nearby",
            params={
                "latitude": 46.82,
                "longitude": -71.21,
                "max_distance": 10000,  # 10km
                "user_id": DEFAULT_USER_ID,
                "limit": 50
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Found {len(data)} entities within 10km")
    
    def test_nearby_search_with_type_filter(self):
        """GET /api/v1/geo/nearby - Filter by entity type"""
        response = requests.get(
            f"{BASE_URL}/api/v1/geo/nearby",
            params={
                "latitude": 46.82,
                "longitude": -71.21,
                "max_distance": 20000,
                "user_id": DEFAULT_USER_ID,
                "entity_type": "hotspot",
                "limit": 50
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        for entity in data:
            assert entity["entity_type"] == "hotspot"
        print(f"✓ Found {len(data)} hotspots nearby")
    
    def test_within_bbox(self):
        """GET /api/v1/geo/within-bbox - Find entities in bounding box"""
        response = requests.get(
            f"{BASE_URL}/api/v1/geo/within-bbox",
            params={
                "sw_lat": 46.70,
                "sw_lng": -71.40,
                "ne_lat": 46.90,
                "ne_lng": -71.00,
                "user_id": DEFAULT_USER_ID,
                "limit": 100
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # Verify all entities are within bbox
        for entity in data:
            if entity.get("latitude") and entity.get("longitude"):
                assert 46.70 <= entity["latitude"] <= 46.90
                assert -71.40 <= entity["longitude"] <= -71.00
        
        print(f"✓ Found {len(data)} entities within bounding box")
    
    def test_clusters(self):
        """GET /api/v1/geo/clusters - Get clustered entities for map"""
        response = requests.get(
            f"{BASE_URL}/api/v1/geo/clusters",
            params={
                "user_id": DEFAULT_USER_ID,
                "zoom_level": 10
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "zoom_level" in data
        assert "clusters" in data
        assert data["zoom_level"] == 10
        
        print(f"✓ Got {len(data['clusters'])} clusters at zoom level 10")


class TestHuntingGroups:
    """Test hunting groups management"""
    
    created_group_id = None
    
    def test_create_group(self):
        """POST /api/v1/geo/groups - Create hunting group"""
        payload = {
            "name": "TEST_Hunting_Group_V3",
            "description": "Test group for geo sync",
            "settings": {"sync_enabled": True}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/geo/groups?user_id={TEST_USER_ID}",
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "TEST_Hunting_Group_V3"
        assert data["owner_id"] == TEST_USER_ID
        assert len(data["members"]) >= 1  # Owner is auto-added
        
        TestHuntingGroups.created_group_id = data["id"]
        print(f"✓ Created hunting group: {data['id']}")
    
    def test_list_groups(self):
        """GET /api/v1/geo/groups - List user's groups"""
        response = requests.get(
            f"{BASE_URL}/api/v1/geo/groups?user_id={TEST_USER_ID}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Listed {len(data)} groups for user")
    
    def test_add_group_member(self):
        """POST /api/v1/geo/groups/{id}/members - Add member to group"""
        if not TestHuntingGroups.created_group_id:
            pytest.skip("No group created")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/geo/groups/{TestHuntingGroups.created_group_id}/members",
            params={
                "member_id": "new_member_test",
                "role": "member",
                "user_id": TEST_USER_ID
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "added"
        print(f"✓ Added member to group")
    
    def test_remove_group_member(self):
        """DELETE /api/v1/geo/groups/{id}/members/{member_id} - Remove member"""
        if not TestHuntingGroups.created_group_id:
            pytest.skip("No group created")
        
        response = requests.delete(
            f"{BASE_URL}/api/v1/geo/groups/{TestHuntingGroups.created_group_id}/members/new_member_test?user_id={TEST_USER_ID}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "removed"
        print(f"✓ Removed member from group")


class TestHotspotGeneration:
    """Test hotspot auto-generation"""
    
    def test_generate_hotspots(self):
        """POST /api/v1/geo/hotspots/generate - Auto-generate hotspots"""
        response = requests.post(
            f"{BASE_URL}/api/v1/geo/hotspots/generate",
            params={
                "user_id": TEST_USER_ID,
                "center_lat": 46.82,
                "center_lng": -71.21,
                "radius_km": 3,
                "count": 5
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "generated"
        assert "count" in data
        assert "hotspots" in data
        
        # Verify hotspot structure
        for hotspot in data["hotspots"]:
            assert hotspot["entity_type"] == "hotspot"
            assert hotspot["metadata"]["is_auto_generated"] == True
            assert "confidence" in hotspot["metadata"]
        
        print(f"✓ Generated {data['count']} hotspots")


class TestGeoStats:
    """Test statistics endpoint"""
    
    def test_get_stats(self):
        """GET /api/v1/geo/stats - Get user statistics"""
        response = requests.get(
            f"{BASE_URL}/api/v1/geo/stats?user_id={DEFAULT_USER_ID}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "total_entities" in data
        assert "by_type" in data
        assert "by_habitat" in data
        assert "hotspots_count" in data
        assert "active_count" in data
        
        print(f"✓ Stats: {data['total_entities']} total entities, {data['hotspots_count']} hotspots")


class TestAdminGeoEndpoints:
    """Test admin geo endpoints"""
    
    def test_admin_analytics_overview(self):
        """GET /api/admin/geo/analytics/overview - Global analytics"""
        response = requests.get(f"{BASE_URL}/api/admin/geo/analytics/overview")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_entities" in data
        assert "by_type" in data
        assert "by_habitat" in data
        assert "top_users" in data
        assert "auto_generated_count" in data
        assert "premium_hotspots" in data
        
        print(f"✓ Admin analytics: {data['total_entities']} entities, {data['premium_hotspots']} premium hotspots")
    
    def test_admin_all_entities(self):
        """GET /api/admin/geo/all - Get all entities (admin view)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/geo/all",
            params={"limit": 50}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Admin view: {len(data)} entities")
    
    def test_admin_all_entities_filtered(self):
        """GET /api/admin/geo/all - Filter by entity_type and habitat"""
        response = requests.get(
            f"{BASE_URL}/api/admin/geo/all",
            params={
                "entity_type": "hotspot",
                "is_auto_generated": True,
                "limit": 50
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        for entity in data:
            assert entity["entity_type"] == "hotspot"
        print(f"✓ Filtered admin view: {len(data)} auto-generated hotspots")
    
    def test_admin_hotspots(self):
        """GET /api/admin/geo/hotspots - Get all hotspots with scoring"""
        response = requests.get(
            f"{BASE_URL}/api/admin/geo/hotspots",
            params={"limit": 50}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "hotspots" in data
        assert "summary" in data
        
        print(f"✓ Admin hotspots: {data['summary']['total']} total, {data['summary']['premium_unclaimed']} premium unclaimed")
    
    def test_admin_monetization_available_hotspots(self):
        """GET /api/admin/geo/monetization/available-hotspots - Premium unclaimed hotspots"""
        response = requests.get(
            f"{BASE_URL}/api/admin/geo/monetization/available-hotspots",
            params={"min_confidence": 0.3}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "available_hotspots" in data
        # Summary may be at root level or nested
        total_available = data.get("total_available", data.get("summary", {}).get("total_available", 0))
        
        # Verify hotspot structure
        for hotspot in data["available_hotspots"]:
            assert "id" in hotspot
            assert "name" in hotspot
            assert "confidence" in hotspot
            assert "estimated_value" in hotspot
        
        print(f"✓ Monetization: {total_available} available hotspots")


class TestWebSocketSyncStatus:
    """Test WebSocket sync status endpoints"""
    
    def test_sync_status(self):
        """GET /api/v1/geo-sync/status - Get sync status for group"""
        response = requests.get(
            f"{BASE_URL}/api/v1/geo-sync/status",
            params={"group_id": "default_group"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "group_id" in data
        assert "connected_members" in data
        assert "member_count" in data
        assert "sync_enabled" in data
        
        print(f"✓ Sync status: {data['member_count']} connected members")
    
    def test_list_active_groups(self):
        """GET /api/v1/geo-sync/groups - List active WebSocket groups"""
        response = requests.get(f"{BASE_URL}/api/v1/geo-sync/groups")
        assert response.status_code == 200
        
        data = response.json()
        assert "active_groups" in data
        print(f"✓ Active groups: {len(data['active_groups'])}")


class TestMigration:
    """Test migration endpoint"""
    
    def test_migration_from_territory_waypoints(self):
        """POST /api/v1/geo/migrate/from-territory-waypoints - Migration utility"""
        response = requests.post(
            f"{BASE_URL}/api/v1/geo/migrate/from-territory-waypoints?user_id={TEST_USER_ID}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "completed"
        assert "migrated" in data
        assert "skipped" in data
        assert "total_in_new_collection" in data
        
        print(f"✓ Migration: {data['migrated']} migrated, {data['skipped']} skipped, {data['total_in_new_collection']} total")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_entities(self):
        """Delete test entities created during testing"""
        # Get all test entities
        response = requests.get(
            f"{BASE_URL}/api/v1/geo/entities?user_id={TEST_USER_ID}&limit=100"
        )
        
        if response.status_code == 200:
            entities = response.json()
            deleted_count = 0
            
            for entity in entities:
                if entity["name"].startswith("TEST_"):
                    del_response = requests.delete(
                        f"{BASE_URL}/api/v1/geo/entities/{entity['id']}?user_id={TEST_USER_ID}"
                    )
                    if del_response.status_code == 200:
                        deleted_count += 1
            
            print(f"✓ Cleaned up {deleted_count} test entities")
        else:
            print("⚠ Could not fetch entities for cleanup")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
