"""
BIONIC Data Validation Integration Tests
=========================================
Tests d'intégration pour valider que le JSON Schema MongoDB rejette
les documents corrompus et accepte les documents valides.

Version: 1.0.0
Date: 2026-02-19

Tests:
- test_insert_corrupted_pages_visited_rejected
- test_insert_corrupted_tools_used_rejected
- test_insert_valid_user_context_accepted
- test_update_corrupted_rejected
- test_insert_corrupted_checklist_items_rejected
- test_insert_valid_checklist_accepted
"""

import pytest
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from pymongo.errors import WriteError


# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'huntiq')


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db():
    """Get MongoDB database connection."""
    client = AsyncIOMotorClient(MONGO_URL)
    database = client[DB_NAME]
    yield database
    client.close()


class TestUserContextSchemaValidation:
    """Tests for user_contexts collection schema validation."""
    
    @pytest.mark.asyncio
    async def test_insert_corrupted_pages_visited_rejected(self, db):
        """
        Test that inserting a document with pages_visited as int is REJECTED.
        This is the exact bug we fixed - should now be blocked by schema.
        """
        corrupted_doc = {
            "user_id": "test-schema-001",
            "pages_visited": 42,  # CORRUPTED - should be array
            "tools_used": []
        }
        
        with pytest.raises(WriteError) as exc_info:
            await db.user_contexts.insert_one(corrupted_doc)
        
        assert "Document failed validation" in str(exc_info.value) or "validation" in str(exc_info.value).lower()
        print("✓ Corrupted pages_visited (int) correctly rejected by schema")
    
    @pytest.mark.asyncio
    async def test_insert_corrupted_tools_used_rejected(self, db):
        """
        Test that inserting a document with tools_used as int is REJECTED.
        """
        corrupted_doc = {
            "user_id": "test-schema-002",
            "pages_visited": [],
            "tools_used": 10  # CORRUPTED - should be array
        }
        
        with pytest.raises(WriteError) as exc_info:
            await db.user_contexts.insert_one(corrupted_doc)
        
        assert "Document failed validation" in str(exc_info.value) or "validation" in str(exc_info.value).lower()
        print("✓ Corrupted tools_used (int) correctly rejected by schema")
    
    @pytest.mark.asyncio
    async def test_insert_valid_user_context_accepted(self, db):
        """
        Test that inserting a valid document is ACCEPTED.
        """
        valid_doc = {
            "user_id": "test-schema-003",
            "gibier_principal": "orignal",
            "region": "Laurentides",
            "pages_visited": ["page1", "page2"],
            "tools_used": ["tool1"],
            "pourvoiries_consulted": [],
            "setups_consulted": [],
            "permis_consulted": [],
            "needs_gibier_popup": False,
            "has_complete_profile": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            result = await db.user_contexts.insert_one(valid_doc)
            assert result.inserted_id is not None
            print(f"✓ Valid document accepted, id={result.inserted_id}")
            
            # Cleanup
            await db.user_contexts.delete_one({"user_id": "test-schema-003"})
        except WriteError as e:
            pytest.fail(f"Valid document should be accepted: {e}")
    
    @pytest.mark.asyncio
    async def test_update_corrupted_rejected(self, db):
        """
        Test that updating a document to corrupted state is REJECTED.
        """
        # First insert a valid document
        valid_doc = {
            "user_id": "test-schema-004",
            "pages_visited": ["page1"],
            "tools_used": []
        }
        await db.user_contexts.insert_one(valid_doc)
        
        # Try to update with corrupted data
        try:
            with pytest.raises(WriteError):
                await db.user_contexts.update_one(
                    {"user_id": "test-schema-004"},
                    {"$set": {"pages_visited": 999}}  # CORRUPTED
                )
            print("✓ Corrupted update correctly rejected by schema")
        finally:
            # Cleanup
            await db.user_contexts.delete_one({"user_id": "test-schema-004"})


class TestPermisChecklistSchemaValidation:
    """Tests for permis_checklists collection schema validation."""
    
    @pytest.mark.asyncio
    async def test_insert_corrupted_items_rejected(self, db):
        """
        Test that inserting a document with items as int is REJECTED.
        """
        corrupted_doc = {
            "user_id": "test-schema-005",
            "permis_type": "orignal",
            "items": 12  # CORRUPTED - should be array
        }
        
        with pytest.raises(WriteError) as exc_info:
            await db.permis_checklists.insert_one(corrupted_doc)
        
        assert "Document failed validation" in str(exc_info.value) or "validation" in str(exc_info.value).lower()
        print("✓ Corrupted items (int) correctly rejected by schema")
    
    @pytest.mark.asyncio
    async def test_insert_valid_checklist_accepted(self, db):
        """
        Test that inserting a valid checklist is ACCEPTED.
        """
        valid_doc = {
            "user_id": "test-schema-006",
            "permis_type": "orignal",
            "province": "QC",
            "items": [
                {
                    "id": "item-001",
                    "label": "Certificat du chasseur",
                    "label_en": "Hunter's certificate",
                    "is_completed": False,
                    "required": True
                }
            ],
            "completion_percentage": 0
        }
        
        try:
            result = await db.permis_checklists.insert_one(valid_doc)
            assert result.inserted_id is not None
            print(f"✓ Valid checklist accepted, id={result.inserted_id}")
            
            # Cleanup
            await db.permis_checklists.delete_one({"user_id": "test-schema-006"})
        except WriteError as e:
            pytest.fail(f"Valid checklist should be accepted: {e}")


class TestReadOperations:
    """Tests for read operations - should work regardless of schema."""
    
    @pytest.mark.asyncio
    async def test_read_empty_collection(self, db):
        """
        Test that reading from empty collection works.
        """
        cursor = db.user_contexts.find({})
        docs = await cursor.to_list(10)
        
        # Should return list (possibly empty)
        assert isinstance(docs, list)
        print(f"✓ Read operation works, found {len(docs)} documents")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-x"])
