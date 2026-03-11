"""Notification Engine Service - MÉTIER

Business logic for notifications.

Version: 1.0.0
"""

import os
from typing import List, Dict, Any
from datetime import datetime, timezone
from pymongo import MongoClient

from .models import (
    Notification, NotificationTemplate, NotificationPreferences, NotificationType, NotificationChannel,
    NotificationPriority
)


class NotificationService:
    """Service for notification management"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    async def send_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        channels: List[NotificationChannel] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        data: Dict[str, Any] = None,
        action_url: str = None
    ) -> Notification:
        """Send a notification to a user"""
        
        if channels is None:
            channels = [NotificationChannel.IN_APP]
        
        # Check user preferences
        prefs = await self.get_preferences(user_id)
        
        # Filter channels based on preferences
        allowed_channels = []
        for channel in channels:
            if channel == NotificationChannel.IN_APP and prefs.in_app_enabled:
                allowed_channels.append(channel)
            elif channel == NotificationChannel.EMAIL and prefs.email_enabled:
                allowed_channels.append(channel)
            elif channel == NotificationChannel.PUSH and prefs.push_enabled:
                allowed_channels.append(channel)
            elif channel == NotificationChannel.SMS and prefs.sms_enabled:
                allowed_channels.append(channel)
        
        # Check notification type preferences
        type_enabled = True
        if notification_type == NotificationType.PROMOTION:
            type_enabled = prefs.promotion_notifications
        elif notification_type == NotificationType.SYSTEM:
            type_enabled = prefs.system_notifications
        elif notification_type == NotificationType.ORDER:
            type_enabled = prefs.order_notifications
        elif notification_type == NotificationType.MESSAGE:
            type_enabled = prefs.message_notifications
        
        if not type_enabled or not allowed_channels:
            # Still create notification but don't send
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                channel=NotificationChannel.IN_APP,
                priority=priority,
                title=title,
                message=message,
                data=data or {},
                action_url=action_url,
                is_sent=False
            )
        else:
            # Create and send
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                channel=allowed_channels[0],
                priority=priority,
                title=title,
                message=message,
                data=data or {},
                action_url=action_url,
                is_sent=True,
                sent_at=datetime.now(timezone.utc)
            )
            
            # Send via each channel
            for channel in allowed_channels:
                if channel == NotificationChannel.EMAIL:
                    await self._send_email(user_id, title, message, data)
                elif channel == NotificationChannel.PUSH:
                    await self._send_push(user_id, title, message, data)
                elif channel == NotificationChannel.SMS:
                    await self._send_sms(user_id, message)
        
        # Store notification
        notif_dict = notification.model_dump()
        notif_dict.pop("_id", None)
        self.db.notifications.insert_one(notif_dict)
        
        return notification
    
    async def _send_email(self, user_id: str, title: str, message: str, data: Dict = None):
        """Send email notification (placeholder)"""
        # In production, integrate with email service
        pass
    
    async def _send_push(self, user_id: str, title: str, message: str, data: Dict = None):
        """Send push notification (placeholder)"""
        # In production, integrate with push service
        pass
    
    async def _send_sms(self, user_id: str, message: str):
        """Send SMS notification (placeholder)"""
        # In production, integrate with SMS service
        pass
    
    async def get_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        notification_type: NotificationType = None,
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for a user"""
        query = {"user_id": user_id}
        if unread_only:
            query["is_read"] = False
        if notification_type:
            query["type"] = notification_type.value
        
        cursor = self.db.notifications.find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
        return [Notification(**doc) for doc in cursor]
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read"""
        result = self.db.notifications.update_one(
            {"id": notification_id, "user_id": user_id},
            {"$set": {"is_read": True, "read_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read"""
        result = self.db.notifications.update_many(
            {"user_id": user_id, "is_read": False},
            {"$set": {"is_read": True, "read_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count
    
    async def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        result = self.db.notifications.delete_one({"id": notification_id, "user_id": user_id})
        return result.deleted_count > 0
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get unread notification count"""
        return self.db.notifications.count_documents({"user_id": user_id, "is_read": False})
    
    async def get_preferences(self, user_id: str) -> NotificationPreferences:
        """Get user notification preferences"""
        prefs = self.db.notification_preferences.find_one({"user_id": user_id}, {"_id": 0})
        if prefs:
            return NotificationPreferences(**prefs)
        return NotificationPreferences(user_id=user_id)
    
    async def update_preferences(self, user_id: str, prefs_data: Dict[str, Any]) -> NotificationPreferences:
        """Update notification preferences"""
        prefs_data["user_id"] = user_id
        prefs_data["updated_at"] = datetime.now(timezone.utc)
        
        self.db.notification_preferences.update_one(
            {"user_id": user_id},
            {"$set": prefs_data},
            upsert=True
        )
        
        return await self.get_preferences(user_id)
    
    async def broadcast(
        self,
        user_ids: List[str],
        notification_type: NotificationType,
        title: str,
        message: str,
        channels: List[NotificationChannel] = None
    ) -> int:
        """Broadcast notification to multiple users"""
        sent_count = 0
        
        for user_id in user_ids:
            try:
                await self.send_notification(
                    user_id=user_id,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    channels=channels
                )
                sent_count += 1
            except Exception:
                continue
        
        return sent_count
    
    async def get_templates(self, notification_type: NotificationType = None) -> List[NotificationTemplate]:
        """Get notification templates"""
        query = {}
        if notification_type:
            query["type"] = notification_type.value
        
        cursor = self.db.notification_templates.find(query, {"_id": 0})
        return [NotificationTemplate(**doc) for doc in cursor]
    
    async def create_template(self, template: NotificationTemplate) -> NotificationTemplate:
        """Create a notification template"""
        template_dict = template.model_dump()
        template_dict.pop("_id", None)
        self.db.notification_templates.insert_one(template_dict)
        return template
