"""
Marketing Engine V1 - API Router
=================================
Dedicated API endpoints for marketing automation.
Architecture LEGO V5 - Module isolé.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import os
import logging

from .models import (
    CampaignCreate, PostCreate, SegmentCreate, AutomationCreate,
    ContentGenerationRequest
)
from .service import MarketingEngineService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/marketing",
    tags=["Marketing Engine V1"],
    responses={404: {"description": "Not found"}}
)

# Database dependency
_db = None


def get_db():
    global _db
    if _db is None:
        from motor.motor_asyncio import AsyncIOMotorClient
        MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        DB_NAME = os.environ.get('DB_NAME', 'hunttrack')
        client = AsyncIOMotorClient(MONGO_URL)
        _db = client[DB_NAME]
    return _db


def get_service() -> MarketingEngineService:
    return MarketingEngineService(get_db())


# ============================================
# MODULE INFO
# ============================================

@router.get("/", summary="Module Info")
async def get_module_info():
    """Get marketing engine module information"""
    return {
        "module": "marketing_engine",
        "version": "1.0.0",
        "description": "Marketing Automation Engine avec intégration Tracking Engine",
        "features": [
            "Campaign management",
            "Multi-platform posts (Facebook, Instagram, Twitter, LinkedIn)",
            "AI content generation",
            "Audience segmentation",
            "Marketing automations",
            "Behavioral triggers (Tracking Engine integration)",
            "Analytics & reporting"
        ],
        "integrations": [
            "tracking_engine (behavioral triggers)",
            "notification_engine (automation actions)"
        ]
    }


# ============================================
# DASHBOARD
# ============================================

@router.get("/dashboard", summary="Marketing Dashboard")
async def get_dashboard(service: MarketingEngineService = Depends(get_service)):
    """Get marketing dashboard with stats and KPIs"""
    try:
        stats = await service.get_dashboard_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# CAMPAIGNS
# ============================================

@router.post("/campaigns", summary="Create Campaign")
async def create_campaign(
    data: CampaignCreate,
    service: MarketingEngineService = Depends(get_service)
):
    """Create a new marketing campaign"""
    try:
        campaign = await service.create_campaign(data)
        return {"success": True, "campaign": campaign}
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns", summary="List Campaigns")
async def list_campaigns(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    service: MarketingEngineService = Depends(get_service)
):
    """List marketing campaigns"""
    try:
        campaigns = await service.get_campaigns(status, limit)
        return {"success": True, "total": len(campaigns), "campaigns": campaigns}
    except Exception as e:
        logger.error(f"Error listing campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}", summary="Get Campaign")
async def get_campaign(
    campaign_id: str,
    service: MarketingEngineService = Depends(get_service)
):
    """Get campaign details with analytics"""
    try:
        analytics = await service.get_campaign_analytics(campaign_id)
        if "error" in analytics:
            raise HTTPException(status_code=404, detail=analytics["error"])
        return {"success": True, **analytics}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/campaigns/{campaign_id}/status", summary="Update Campaign Status")
async def update_campaign_status(
    campaign_id: str,
    status: str = Query(..., description="New status"),
    service: MarketingEngineService = Depends(get_service)
):
    """Update campaign status"""
    valid_statuses = ["draft", "active", "paused", "completed", "archived"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Valid: {valid_statuses}")
    
    try:
        success = await service.update_campaign_status(campaign_id, status)
        if not success:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return {"success": True, "campaign_id": campaign_id, "status": status}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating campaign status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/campaigns/{campaign_id}", summary="Delete Campaign")
async def delete_campaign(
    campaign_id: str,
    service: MarketingEngineService = Depends(get_service)
):
    """Delete a campaign and its posts"""
    try:
        success = await service.delete_campaign(campaign_id)
        if not success:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return {"success": True, "deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# POSTS
# ============================================

@router.post("/posts", summary="Create Post")
async def create_post(
    data: PostCreate,
    service: MarketingEngineService = Depends(get_service)
):
    """Create a new marketing post"""
    try:
        post = await service.create_post(data)
        return {"success": True, "post": post}
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posts", summary="List Posts")
async def list_posts(
    status: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    service: MarketingEngineService = Depends(get_service)
):
    """List marketing posts"""
    try:
        posts = await service.get_posts(status, platform, limit)
        return {"success": True, "total": len(posts), "posts": posts}
    except Exception as e:
        logger.error(f"Error listing posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/posts/{post_id}/schedule", summary="Schedule Post")
async def schedule_post(
    post_id: str,
    scheduled_at: str = Query(..., description="ISO datetime for scheduling"),
    service: MarketingEngineService = Depends(get_service)
):
    """Schedule a post for future publication"""
    try:
        success = await service.schedule_post(post_id, scheduled_at)
        if not success:
            raise HTTPException(status_code=404, detail="Post not found")
        return {"success": True, "post_id": post_id, "scheduled_at": scheduled_at}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/posts/{post_id}/publish", summary="Publish Post")
async def publish_post(
    post_id: str,
    service: MarketingEngineService = Depends(get_service)
):
    """Publish a post immediately"""
    try:
        result = await service.publish_post(post_id)
        return result
    except Exception as e:
        logger.error(f"Error publishing post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/posts/{post_id}", summary="Delete Post")
async def delete_post(
    post_id: str,
    service: MarketingEngineService = Depends(get_service)
):
    """Delete a post"""
    try:
        success = await service.delete_post(post_id)
        if not success:
            raise HTTPException(status_code=404, detail="Post not found")
        return {"success": True, "deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# CONTENT GENERATION
# ============================================

@router.post("/generate", summary="Generate Content")
async def generate_content(
    request: ContentGenerationRequest,
    service: MarketingEngineService = Depends(get_service)
):
    """Generate marketing content with AI"""
    try:
        result = await service.generate_content(request)
        return {
            "success": True,
            "content": result.content,
            "hashtags": result.hashtags,
            "platform": result.platform,
            "content_type": result.content_type,
            "generated_at": result.generated_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SEGMENTS
# ============================================

@router.get("/segments", summary="List Segments")
async def list_segments(service: MarketingEngineService = Depends(get_service)):
    """List audience segments"""
    try:
        segments = await service.get_segments()
        return {"success": True, "total": len(segments), "segments": segments}
    except Exception as e:
        logger.error(f"Error listing segments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/segments", summary="Create Segment")
async def create_segment(
    data: SegmentCreate,
    service: MarketingEngineService = Depends(get_service)
):
    """Create a new audience segment"""
    try:
        segment = await service.create_segment(data)
        return {"success": True, "segment": segment}
    except Exception as e:
        logger.error(f"Error creating segment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# AUTOMATIONS
# ============================================

@router.get("/automations", summary="List Automations")
async def list_automations(
    is_active: Optional[bool] = Query(None),
    service: MarketingEngineService = Depends(get_service)
):
    """List marketing automations"""
    try:
        automations = await service.get_automations(is_active)
        return {"success": True, "total": len(automations), "automations": automations}
    except Exception as e:
        logger.error(f"Error listing automations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/automations", summary="Create Automation")
async def create_automation(
    data: AutomationCreate,
    service: MarketingEngineService = Depends(get_service)
):
    """Create a new marketing automation"""
    try:
        automation = await service.create_automation(data)
        return {"success": True, "automation": automation}
    except Exception as e:
        logger.error(f"Error creating automation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/automations/{automation_id}/toggle", summary="Toggle Automation")
async def toggle_automation(
    automation_id: str,
    is_active: bool = Query(...),
    service: MarketingEngineService = Depends(get_service)
):
    """Enable or disable an automation"""
    try:
        success = await service.toggle_automation(automation_id, is_active)
        if not success:
            raise HTTPException(status_code=404, detail="Automation not found")
        return {"success": True, "automation_id": automation_id, "is_active": is_active}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling automation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# BEHAVIORAL TRIGGERS (Tracking Engine Integration)
# ============================================

@router.post("/triggers", summary="Create Behavioral Trigger")
async def create_behavioral_trigger(
    automation_id: str = Query(...),
    event_type: str = Query(..., description="Event type from Tracking Engine"),
    event_name: Optional[str] = Query(None),
    page_url_pattern: Optional[str] = Query(None),
    min_occurrences: int = Query(1, ge=1),
    time_window_hours: int = Query(24, ge=1, le=720),
    service: MarketingEngineService = Depends(get_service)
):
    """Create a behavioral trigger linked to Tracking Engine events"""
    try:
        trigger = await service.create_behavioral_trigger(
            automation_id=automation_id,
            event_type=event_type,
            event_name=event_name,
            page_url_pattern=page_url_pattern,
            min_occurrences=min_occurrences,
            time_window_hours=time_window_hours
        )
        return {"success": True, "trigger": trigger}
    except Exception as e:
        logger.error(f"Error creating trigger: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/triggers", summary="List Behavioral Triggers")
async def list_triggers(
    automation_id: Optional[str] = Query(None),
    service: MarketingEngineService = Depends(get_service)
):
    """List behavioral triggers"""
    try:
        triggers = await service.get_behavioral_triggers(automation_id)
        return {"success": True, "total": len(triggers), "triggers": triggers}
    except Exception as e:
        logger.error(f"Error listing triggers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/triggers/check", summary="Check and Execute Triggers")
async def check_triggers(
    user_id: str = Query(...),
    session_id: str = Query(...),
    service: MarketingEngineService = Depends(get_service)
):
    """Check tracking events and execute matching triggers for a user"""
    try:
        executed = await service.check_and_execute_triggers(user_id, session_id)
        return {
            "success": True,
            "executed_count": len(executed),
            "executions": executed
        }
    except Exception as e:
        logger.error(f"Error checking triggers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/triggers/executions", summary="List Trigger Executions")
async def list_executions(
    automation_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    service: MarketingEngineService = Depends(get_service)
):
    """List trigger execution history"""
    try:
        executions = await service.get_trigger_executions(automation_id, user_id, days)
        return {"success": True, "total": len(executions), "executions": executions}
    except Exception as e:
        logger.error(f"Error listing executions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
