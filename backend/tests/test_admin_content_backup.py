"""
Test Admin Content & Backup APIs - Phase 2 Migration
=====================================================

Tests for:
- Content Admin: Categories, Content Depot, SEO Analytics
- Backup Admin: Stats, Code Files, Database Backups

Phase 2 Migration - V5-ULTIME Administration Premium
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestContentCategories:
    """Tests for Content Categories API"""
    
    def test_get_categories(self):
        """GET /api/v1/admin/content/categories - List all categories"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/content/categories")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "categories" in data
        assert "total" in data
        print(f"✓ GET categories: {data['total']} categories found")
    
    def test_init_default_categories(self):
        """POST /api/v1/admin/content/categories/init-defaults - Initialize defaults"""
        response = requests.post(f"{BASE_URL}/api/v1/admin/content/categories/init-defaults")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "inserted" in data
        assert "total_defaults" in data
        print(f"✓ Init defaults: {data['inserted']} inserted, {data['total_defaults']} total defaults")
    
    def test_create_category(self):
        """POST /api/v1/admin/content/categories - Create new category"""
        test_id = f"TEST_cat_{uuid.uuid4().hex[:8]}"
        payload = {
            "id": test_id,
            "name": "Test Category",
            "icon": "🧪",
            "order": 99
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/content/categories",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "category" in data
        assert data["category"]["id"] == test_id
        assert data["category"]["name"] == "Test Category"
        print(f"✓ Create category: {test_id} created")
        
        # Cleanup - delete the test category
        requests.delete(f"{BASE_URL}/api/v1/admin/content/categories/{test_id}")
    
    def test_update_category(self):
        """PUT /api/v1/admin/content/categories/{id} - Update category"""
        # First create a test category
        test_id = f"TEST_upd_{uuid.uuid4().hex[:8]}"
        create_payload = {"id": test_id, "name": "Original Name", "icon": "📦", "order": 50}
        requests.post(f"{BASE_URL}/api/v1/admin/content/categories", json=create_payload)
        
        # Update it
        update_payload = {"name": "Updated Name", "icon": "✏️", "order": 51}
        response = requests.put(
            f"{BASE_URL}/api/v1/admin/content/categories/{test_id}",
            json=update_payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("updated") == True
        print(f"✓ Update category: {test_id} updated")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/v1/admin/content/categories/{test_id}")
    
    def test_delete_category(self):
        """DELETE /api/v1/admin/content/categories/{id} - Delete category"""
        # First create a test category
        test_id = f"TEST_del_{uuid.uuid4().hex[:8]}"
        create_payload = {"id": test_id, "name": "To Delete", "icon": "🗑️", "order": 100}
        requests.post(f"{BASE_URL}/api/v1/admin/content/categories", json=create_payload)
        
        # Delete it
        response = requests.delete(f"{BASE_URL}/api/v1/admin/content/categories/{test_id}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("deleted") == True
        print(f"✓ Delete category: {test_id} deleted")
    
    def test_delete_nonexistent_category(self):
        """DELETE /api/v1/admin/content/categories/{id} - Delete non-existent returns error"""
        response = requests.delete(f"{BASE_URL}/api/v1/admin/content/categories/nonexistent_id_12345")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == False
        assert "error" in data
        print(f"✓ Delete non-existent: Correctly returns error")


class TestContentDepot:
    """Tests for Content Depot API"""
    
    def test_get_content_depot(self):
        """GET /api/v1/admin/content/depot - List content items"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/content/depot")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "items" in data
        assert "total" in data
        assert "status_counts" in data
        print(f"✓ GET depot: {data['total']} items, status_counts: {data['status_counts']}")
    
    def test_get_content_depot_with_filter(self):
        """GET /api/v1/admin/content/depot?status=pending - Filter by status"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/content/depot?status=pending")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✓ GET depot filtered: {data['total']} pending items")
    
    def test_create_content_item(self):
        """POST /api/v1/admin/content/depot - Create content item"""
        payload = {
            "title": f"TEST_Content_{uuid.uuid4().hex[:8]}",
            "content_type": "article",
            "platform": "website",
            "original_content": "This is test content for validation.",
            "keywords": ["test", "validation"]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/content/depot",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "item" in data
        assert data["item"]["title"] == payload["title"]
        assert data["item"]["status"] == "pending"
        item_id = data["item"]["id"]
        print(f"✓ Create content: {item_id} created with status 'pending'")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/v1/admin/content/depot/{item_id}")
    
    def test_update_content_status(self):
        """PUT /api/v1/admin/content/depot/{id}/status - Update status"""
        # Create test item
        payload = {"title": f"TEST_Status_{uuid.uuid4().hex[:8]}", "content_type": "blog"}
        create_resp = requests.post(f"{BASE_URL}/api/v1/admin/content/depot", json=payload)
        item_id = create_resp.json()["item"]["id"]
        
        # Update status to optimized
        response = requests.put(f"{BASE_URL}/api/v1/admin/content/depot/{item_id}/status?status=optimized")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("new_status") == "optimized"
        print(f"✓ Update status: {item_id} -> optimized")
        
        # Update to accepted
        response = requests.put(f"{BASE_URL}/api/v1/admin/content/depot/{item_id}/status?status=accepted")
        assert response.status_code == 200
        data = response.json()
        assert data.get("new_status") == "accepted"
        print(f"✓ Update status: {item_id} -> accepted")
        
        # Update to published
        response = requests.put(f"{BASE_URL}/api/v1/admin/content/depot/{item_id}/status?status=published")
        assert response.status_code == 200
        data = response.json()
        assert data.get("new_status") == "published"
        print(f"✓ Update status: {item_id} -> published")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/v1/admin/content/depot/{item_id}")
    
    def test_update_content_invalid_status(self):
        """PUT /api/v1/admin/content/depot/{id}/status - Invalid status returns error"""
        # Create test item
        payload = {"title": f"TEST_Invalid_{uuid.uuid4().hex[:8]}"}
        create_resp = requests.post(f"{BASE_URL}/api/v1/admin/content/depot", json=payload)
        item_id = create_resp.json()["item"]["id"]
        
        # Try invalid status
        response = requests.put(f"{BASE_URL}/api/v1/admin/content/depot/{item_id}/status?status=invalid_status")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == False
        assert "error" in data
        print(f"✓ Invalid status: Correctly returns error")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/v1/admin/content/depot/{item_id}")


class TestSEOAnalytics:
    """Tests for SEO Analytics API"""
    
    def test_get_seo_analytics(self):
        """GET /api/v1/admin/content/seo-analytics - Get SEO stats"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/content/seo-analytics")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "analytics" in data
        analytics = data["analytics"]
        assert "total_content" in analytics
        assert "published_content" in analytics
        assert "pending_content" in analytics
        assert "avg_seo_score" in analytics
        assert "categories_count" in analytics
        assert "publish_rate" in analytics
        print(f"✓ SEO Analytics: total={analytics['total_content']}, published={analytics['published_content']}, avg_score={analytics['avg_seo_score']}")


class TestBackupStats:
    """Tests for Backup Stats API"""
    
    def test_get_backup_stats(self):
        """GET /api/v1/admin/backup/stats - Get backup statistics"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/backup/stats")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "stats" in data
        stats = data["stats"]
        assert "code_files_tracked" in stats
        assert "prompt_versions" in stats
        assert "db_backups_count" in stats
        assert "total_backup_size" in stats
        print(f"✓ Backup stats: code_files={stats['code_files_tracked']}, prompts={stats['prompt_versions']}, db_backups={stats['db_backups_count']}")


class TestCodeBackups:
    """Tests for Code Backup API"""
    
    def test_get_code_files(self):
        """GET /api/v1/admin/backup/code/files - List code files"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/backup/code/files")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "files" in data
        assert "total" in data
        print(f"✓ Code files: {data['total']} files tracked")
    
    def test_get_code_files_with_search(self):
        """GET /api/v1/admin/backup/code/files?search=test - Search files"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/backup/code/files?search=test")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✓ Code files search: {data['total']} files matching 'test'")


class TestDatabaseBackups:
    """Tests for Database Backup API"""
    
    def test_get_database_backups(self):
        """GET /api/v1/admin/backup/database - List DB backups"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/backup/database")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "backups" in data
        assert "total" in data
        print(f"✓ DB backups: {data['total']} backups found")
    
    def test_create_database_backup(self):
        """POST /api/v1/admin/backup/database - Create DB backup"""
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/backup/database?backup_type=manual&description=TEST_backup"
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "backup" in data
        backup = data["backup"]
        assert backup.get("status") == "completed"
        assert "collections" in backup
        assert len(backup["collections"]) > 0
        backup_id = backup["id"]
        print(f"✓ Create backup: {backup_id} with {len(backup['collections'])} collections")
        
        # Verify backup appears in list
        list_resp = requests.get(f"{BASE_URL}/api/v1/admin/backup/database")
        backups = list_resp.json().get("backups", [])
        backup_ids = [b["id"] for b in backups]
        assert backup_id in backup_ids
        print(f"✓ Verify backup: {backup_id} found in list")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/v1/admin/backup/database/{backup_id}")
    
    def test_delete_database_backup(self):
        """DELETE /api/v1/admin/backup/database/{id} - Delete backup"""
        # Create a backup first
        create_resp = requests.post(
            f"{BASE_URL}/api/v1/admin/backup/database?backup_type=manual&description=TEST_to_delete"
        )
        backup_id = create_resp.json()["backup"]["id"]
        
        # Delete it
        response = requests.delete(f"{BASE_URL}/api/v1/admin/backup/database/{backup_id}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("deleted") == True
        print(f"✓ Delete backup: {backup_id} deleted")
        
        # Verify it's gone
        list_resp = requests.get(f"{BASE_URL}/api/v1/admin/backup/database")
        backups = list_resp.json().get("backups", [])
        backup_ids = [b["id"] for b in backups]
        assert backup_id not in backup_ids
        print(f"✓ Verify deletion: {backup_id} not in list")
    
    def test_delete_nonexistent_backup(self):
        """DELETE /api/v1/admin/backup/database/{id} - Delete non-existent returns error"""
        response = requests.delete(f"{BASE_URL}/api/v1/admin/backup/database/nonexistent_backup_12345")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == False
        assert "error" in data
        print(f"✓ Delete non-existent: Correctly returns error")


class TestPromptBackups:
    """Tests for Prompt Backup API"""
    
    def test_get_prompt_versions(self):
        """GET /api/v1/admin/backup/prompts - List prompt versions"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/backup/prompts")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "versions" in data
        assert "prompt_types" in data
        print(f"✓ Prompt versions: {data['total']} versions, types: {data['prompt_types']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
