"""
Email Service for BIONIC HUNT/Chasse
Handles transactional emails (password reset, notifications, etc.)
Uses Resend API for email delivery
"""
import os
import asyncio
import logging
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

# Resend configuration
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")
APP_NAME = "BIONIC HUNT/Chasse"
APP_URL = os.environ.get("APP_URL", "https://bionic-engine-review.preview.emergentagent.com")


class EmailService:
    """Email service using Resend API"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.reset_tokens_collection = db['password_reset_tokens']
        self._resend_configured = bool(RESEND_API_KEY)
        
        if self._resend_configured:
            import resend
            resend.api_key = RESEND_API_KEY
            self.resend = resend
            logger.info("Resend email service configured")
        else:
            self.resend = None
            logger.warning("Resend API key not configured - emails will be logged only")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Send an email via Resend API.
        Returns (success, email_id or error_message)
        """
        if not self._resend_configured:
            logger.info(f"[EMAIL LOG] To: {to_email}, Subject: {subject}")
            logger.info(f"[EMAIL LOG] Content preview: {html_content[:200]}...")
            return True, "logged_only"
        
        try:
            params = {
                "from": f"{APP_NAME} <{SENDER_EMAIL}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }
            
            # Run sync SDK in thread to keep FastAPI non-blocking
            email = await asyncio.to_thread(self.resend.Emails.send, params)
            
            logger.info(f"Email sent to {to_email}: {email.get('id')}")
            return True, email.get("id")
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False, str(e)
    
    # ============================================
    # PASSWORD RESET
    # ============================================
    
    async def generate_reset_token(self, user_id: str, email: str) -> str:
        """Generate a password reset token"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Store token
        await self.reset_tokens_collection.insert_one({
            "token": token,
            "user_id": user_id,
            "email": email,
            "expires_at": expires_at,
            "used": False,
            "created_at": datetime.now(timezone.utc)
        })
        
        return token
    
    async def verify_reset_token(self, token: str) -> Optional[dict]:
        """Verify a password reset token"""
        token_doc = await self.reset_tokens_collection.find_one({
            "token": token,
            "used": False,
            "expires_at": {"$gt": datetime.now(timezone.utc)}
        })
        
        return token_doc
    
    async def mark_token_used(self, token: str) -> bool:
        """Mark a token as used"""
        result = await self.reset_tokens_collection.update_one(
            {"token": token},
            {"$set": {"used": True, "used_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0
    
    async def send_password_reset_email(
        self,
        user_id: str,
        email: str,
        user_name: str
    ) -> Tuple[bool, str]:
        """
        Send a password reset email.
        Returns (success, message)
        """
        # Generate token
        token = await self.generate_reset_token(user_id, email)
        
        # Build reset URL
        reset_url = f"{APP_URL}/reset-password?token={token}"
        
        # Build email HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; background-color: #0f172a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0f172a; padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #1e293b; border-radius: 12px; overflow: hidden;">
                            <!-- Header -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #f5a623 0%, #d4890e 100%); padding: 30px; text-align: center;">
                                    <h1 style="color: #000; margin: 0; font-size: 28px; font-weight: bold;">BIONIC HUNT/Chasse</h1>
                                    <p style="color: #000; margin: 10px 0 0; font-size: 14px;">Chasse Intelligente</p>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px 30px;">
                                    <h2 style="color: #f5a623; margin: 0 0 20px; font-size: 22px;">Réinitialisation de mot de passe</h2>
                                    
                                    <p style="color: #94a3b8; margin: 0 0 20px; font-size: 16px; line-height: 1.6;">
                                        Bonjour {user_name},
                                    </p>
                                    
                                    <p style="color: #94a3b8; margin: 0 0 30px; font-size: 16px; line-height: 1.6;">
                                        Vous avez demandé à réinitialiser votre mot de passe. Cliquez sur le bouton ci-dessous pour créer un nouveau mot de passe.
                                    </p>
                                    
                                    <!-- Button -->
                                    <table width="100%" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td align="center" style="padding: 20px 0;">
                                                <a href="{reset_url}" style="display: inline-block; background-color: #f5a623; color: #000; padding: 16px 40px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">
                                                    Réinitialiser mon mot de passe
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="color: #64748b; margin: 30px 0 0; font-size: 14px; line-height: 1.6;">
                                        Ce lien expire dans <strong>1 heure</strong>. Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email.
                                    </p>
                                    
                                    <!-- Alternative link -->
                                    <p style="color: #475569; margin: 20px 0 0; font-size: 12px; line-height: 1.6;">
                                        Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur:<br>
                                        <span style="color: #f5a623; word-break: break-all;">{reset_url}</span>
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #0f172a; padding: 20px 30px; text-align: center; border-top: 1px solid #334155;">
                                    <p style="color: #475569; margin: 0; font-size: 12px;">
                                        © 2026 BIONIC HUNT/Chasse - Tous droits réservés<br>
                                        Cet email a été envoyé à {email}
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        # Send email
        success, result = await self.send_email(
            to_email=email,
            subject="Réinitialisation de votre mot de passe BIONIC HUNT/Chasse",
            html_content=html_content
        )
        
        if success:
            logger.info(f"Password reset email sent to {email}")
            return True, "Email de réinitialisation envoyé"
        else:
            logger.error(f"Failed to send password reset email to {email}: {result}")
            return False, f"Erreur d'envoi: {result}"
    
    # ============================================
    # NOTIFICATION EMAILS
    # ============================================
    
    async def send_welcome_email(self, email: str, user_name: str) -> Tuple[bool, str]:
        """Send welcome email to new user"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="margin: 0; padding: 0; background-color: #0f172a; font-family: sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0f172a; padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #1e293b; border-radius: 12px;">
                            <tr>
                                <td style="background: linear-gradient(135deg, #f5a623 0%, #d4890e 100%); padding: 30px; text-align: center;">
                                    <h1 style="color: #000; margin: 0;">BIONIC HUNT/Chasse</h1>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 40px 30px;">
                                    <h2 style="color: #f5a623; margin: 0 0 20px;">Bienvenue {user_name}! 🎯</h2>
                                    <p style="color: #94a3b8; line-height: 1.6;">
                                        Votre compte BIONIC HUNT/Chasse a été créé avec succès. Vous êtes maintenant prêt à optimiser vos sorties de chasse avec notre plateforme intelligente.
                                    </p>
                                    <p style="color: #94a3b8; line-height: 1.6;">
                                        <strong>Fonctionnalités disponibles:</strong><br>
                                        • Prévisions de succès basées sur l'IA<br>
                                        • Gestion de waypoints avec score WQS<br>
                                        • Tracking GPS en temps réel<br>
                                        • Analytics de vos sorties
                                    </p>
                                    <table width="100%" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td align="center" style="padding: 20px 0;">
                                                <a href="{APP_URL}/dashboard" style="display: inline-block; background-color: #f5a623; color: #000; padding: 14px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                                                    Accéder à mon tableau de bord
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        success, result = await self.send_email(
            to_email=email,
            subject="Bienvenue sur BIONIC HUNT/Chasse - Votre aventure commence!",
            html_content=html_content
        )
        
        return success, result if not success else "Email de bienvenue envoyé"


    async def send_trip_summary_email(
        self,
        email: str,
        user_name: str,
        trip_title: str,
        target_species: str,
        duration_hours: float,
        observations_count: int,
        success: bool,
        start_time: str,
        end_time: str,
        weather: str = None,
        notes: str = None
    ) -> Tuple[bool, str]:
        """
        Send trip completion summary email to user.
        Called when a hunting trip is ended.
        """
        # Species emoji mapping
        species_emojis = {
            'deer': '🦌',
            'moose': '🫎',
            'bear': '🐻',
            'turkey': '🦃',
            'duck': '🦆',
            'goose': '🪿',
            'grouse': '🐔',
            'rabbit': '🐰',
            'coyote': '🐺',
        }
        
        species_emoji = species_emojis.get(target_species, '🎯')
        success_text = "Réussie ✅" if success else "Sans prise"
        success_color = "#22c55e" if success else "#94a3b8"
        
        # Format duration
        hours = int(duration_hours)
        minutes = int((duration_hours - hours) * 60)
        duration_text = f"{hours}h {minutes:02d}min" if hours > 0 else f"{minutes} min"
        
        # Weather section
        weather_section = ""
        if weather:
            weather_section = f"""
            <tr>
                <td style="padding: 8px 0; border-bottom: 1px solid #334155;">
                    <span style="color: #94a3b8;">🌤️ Météo</span>
                </td>
                <td style="padding: 8px 0; border-bottom: 1px solid #334155; text-align: right;">
                    <span style="color: #fff;">{weather}</span>
                </td>
            </tr>
            """
        
        # Notes section
        notes_section = ""
        if notes:
            notes_section = f"""
            <tr>
                <td colspan="2" style="padding: 16px 0 0 0;">
                    <span style="color: #94a3b8; font-size: 12px;">📝 Notes</span>
                    <p style="color: #fff; margin: 8px 0 0 0; font-style: italic;">"{notes}"</p>
                </td>
            </tr>
            """
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; background-color: #0f172a; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0f172a; padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #1e293b; border-radius: 16px; overflow: hidden; border: 1px solid #334155;">
                            <!-- Header -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #f5a623 0%, #d4890e 100%); padding: 30px; text-align: center;">
                                    <h1 style="margin: 0; color: #000; font-size: 24px;">
                                        {species_emoji} Sortie Terminée
                                    </h1>
                                    <p style="margin: 10px 0 0 0; color: #000; opacity: 0.8;">
                                        {trip_title}
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="padding: 30px;">
                                    <p style="color: #94a3b8; margin: 0 0 20px 0;">
                                        Bonjour <strong style="color: #f5a623;">{user_name}</strong>,
                                    </p>
                                    <p style="color: #e2e8f0; margin: 0 0 30px 0;">
                                        Votre sortie de chasse vient de se terminer. Voici le résumé :
                                    </p>
                                    
                                    <!-- Status Badge -->
                                    <div style="text-align: center; margin-bottom: 30px;">
                                        <span style="display: inline-block; background-color: {success_color}20; color: {success_color}; padding: 12px 24px; border-radius: 30px; font-weight: bold; font-size: 18px;">
                                            {success_text}
                                        </span>
                                    </div>
                                    
                                    <!-- Stats Table -->
                                    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0f172a; border-radius: 12px; padding: 20px;">
                                        <tr>
                                            <td style="padding: 8px 0; border-bottom: 1px solid #334155;">
                                                <span style="color: #94a3b8;">🎯 Espèce ciblée</span>
                                            </td>
                                            <td style="padding: 8px 0; border-bottom: 1px solid #334155; text-align: right;">
                                                <span style="color: #fff; text-transform: capitalize;">{species_emoji} {target_species}</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0; border-bottom: 1px solid #334155;">
                                                <span style="color: #94a3b8;">⏱️ Durée</span>
                                            </td>
                                            <td style="padding: 8px 0; border-bottom: 1px solid #334155; text-align: right;">
                                                <span style="color: #f5a623; font-weight: bold;">{duration_text}</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0; border-bottom: 1px solid #334155;">
                                                <span style="color: #94a3b8;">👁️ Observations</span>
                                            </td>
                                            <td style="padding: 8px 0; border-bottom: 1px solid #334155; text-align: right;">
                                                <span style="color: #8b5cf6; font-weight: bold;">{observations_count}</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0; border-bottom: 1px solid #334155;">
                                                <span style="color: #94a3b8;">🕐 Début</span>
                                            </td>
                                            <td style="padding: 8px 0; border-bottom: 1px solid #334155; text-align: right;">
                                                <span style="color: #fff;">{start_time}</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0; border-bottom: 1px solid #334155;">
                                                <span style="color: #94a3b8;">🏁 Fin</span>
                                            </td>
                                            <td style="padding: 8px 0; border-bottom: 1px solid #334155; text-align: right;">
                                                <span style="color: #fff;">{end_time}</span>
                                            </td>
                                        </tr>
                                        {weather_section}
                                        {notes_section}
                                    </table>
                                    
                                    <!-- CTA -->
                                    <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 30px;">
                                        <tr>
                                            <td align="center">
                                                <a href="{APP_URL}/trips" style="display: inline-block; background-color: #f5a623; color: #000; padding: 14px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                                                    Voir mes statistiques
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="color: #64748b; font-size: 12px; margin-top: 30px; text-align: center;">
                                        Ces données sont synchronisées avec vos analyses et le système WQS pour améliorer vos futures prédictions.
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #0f172a; padding: 20px; text-align: center; border-top: 1px solid #334155;">
                                    <p style="color: #64748b; margin: 0; font-size: 12px;">
                                        BIONIC HUNT/Chasse - Votre compagnon de chasse intelligent
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        success_send, result = await self.send_email(
            to_email=email,
            subject=f"🏁 Sortie terminée - {trip_title} ({success_text})",
            html_content=html_content
        )
        
        return success_send, result if not success_send else "Email de résumé envoyé"
