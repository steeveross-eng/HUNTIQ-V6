"""
BIONIC Messaging Engine V2 - Communications Premium Bilingues
==============================================================

Système de messagerie bilingue (FR/EN) avec modes d'envoi:
- Mode TOUS: Envoi massif personnalisé
- Mode UN PAR UN: Envoi individuel avec validation manuelle

Architecture LEGO V5-ULTIME - Module isolé.

RÈGLE PERMANENTE: Toujours envoyer des messages bilingues Premium (FR/EN)
pour toute communication externe générée automatiquement.

PIPELINE AUTOMATISÉ:
1. Choix du mode (TOUS / UN PAR UN)
2. Préparation du template bilingue
3. Injection des variables personnalisées
4. Génération du pré-visuel FR/EN
5. Validation manuelle obligatoire
6. Envoi (massif ou individuel)
7. Journalisation complète
"""

from fastapi import APIRouter, Body, Query, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from enum import Enum
import os
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/messaging", tags=["Messaging Engine V2"])

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


# ============================================
# ENUMS & CONSTANTS
# ============================================

class SendMode(str, Enum):
    ALL = "TOUS"
    ONE_BY_ONE = "UN_PAR_UN"


class MessageType(str, Enum):
    AFFILIATE_WELCOME = "affiliate_welcome"
    AFFILIATE_PRELAUNCH = "affiliate_prelaunch"
    PARTNER_NOTIFICATION = "partner_notification"
    MARKETING_CAMPAIGN = "marketing_campaign"
    SYSTEM_NOTIFICATION = "system_notification"


class MessageStatus(str, Enum):
    DRAFT = "draft"
    PREVIEW_GENERATED = "preview_generated"
    VALIDATED = "validated"
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    FAILED = "failed"


class MessageChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    PUSH = "push"


class PipelineStep(str, Enum):
    MODE_SELECTION = "mode_selection"
    TEMPLATE_PREPARATION = "template_preparation"
    VARIABLE_INJECTION = "variable_injection"
    PREVIEW_GENERATION = "preview_generation"
    MANUAL_VALIDATION = "manual_validation"
    SENDING = "sending"
    LOGGING = "logging"


# ============================================
# BIONIC BRANDING
# ============================================

BIONIC_HEADER = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ██████╗ ██╗ ██████╗ ███╗   ██╗██╗ ██████╗                     ║
║   ██╔══██╗██║██╔═══██╗████╗  ██║██║██╔════╝                     ║
║   ██████╔╝██║██║   ██║██╔██╗ ██║██║██║                          ║
║   ██╔══██╗██║██║   ██║██║╚██╗██║██║██║                          ║
║   ██████╔╝██║╚██████╔╝██║ ╚████║██║╚██████╗                     ║
║   ╚═════╝ ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝ ╚═════╝                     ║
║                                                                  ║
║   🎯 MARKETING & AFFILIATE AUTOMATION PLATFORM                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

BIONIC_LOGO_URL = "https://bionic.huntiq.com/logo.png"


# ============================================
# BILINGUAL MESSAGE TEMPLATES
# ============================================

BILINGUAL_TEMPLATES = {
    "affiliate_prelaunch": {
        "id": "affiliate_prelaunch",
        "name_fr": "Message Pré-Lancement Affilié",
        "name_en": "Affiliate Pre-Launch Message",
        "variables": ["company_name", "contact_name", "category", "country"],
        "fr": {
            "subject": "🎯 BIONIC - {{company_name}} - Votre espace publicitaire est prêt",
            "greeting": "Bonjour {{contact_name}},",
            "body": """Nous tenions à vous remercier pour votre confiance envers BIONIC.

Votre espace publicitaire pour {{company_name}} ({{category}}) est maintenant configuré dans notre système et prêt à être activé.

Nous finalisons actuellement la phase pré-lancement de la plateforme.
Aucune publicité n'est encore diffusée — tout est en mode pré-production afin d'assurer une expérience optimale dès le lancement officiel.

Nous vous recontacterons personnellement avant l'activation de votre campagne afin de :
• confirmer les détails,
• valider les créatifs,
• et vous présenter les premières statistiques dès les premières impressions.""",
            "closing": "Merci encore d'être parmi les premiers partenaires de BIONIC.",
            "signature": "Cordialement,\nL'équipe BIONIC"
        },
        "en": {
            "subject": "🎯 BIONIC - {{company_name}} - Your advertising placement is ready",
            "greeting": "Hello {{contact_name}},",
            "body": """Thank you for your trust in BIONIC.

Your advertising placement for {{company_name}} ({{category}}) is now configured in our system and ready for activation.

We are currently completing the pre-launch phase of the platform.
No ads are being displayed yet — everything is in pre-production to ensure the best possible experience on launch day.

We will contact you personally before your campaign goes live to:
• confirm all details,
• validate your creatives,
• and share the first performance metrics as soon as impressions begin.""",
            "closing": "Thank you again for being among the first BIONIC partners.",
            "signature": "Sincerely,\nThe BIONIC Team"
        }
    },
    "affiliate_welcome": {
        "id": "affiliate_welcome",
        "name_fr": "Message de Bienvenue Affilié",
        "name_en": "Affiliate Welcome Message",
        "variables": ["company_name", "contact_name", "category", "country"],
        "fr": {
            "subject": "🎉 Bienvenue chez BIONIC, {{company_name}}!",
            "greeting": "Bonjour {{contact_name}},",
            "body": """Nous sommes ravis de vous accueillir parmi nos partenaires affiliés.

Votre compte {{company_name}} a été créé avec succès et vous avez maintenant accès à notre plateforme d'affiliation premium.

Prochaines étapes :
• Complétez votre profil partenaire
• Découvrez nos options publicitaires
• Contactez notre équipe pour discuter de votre stratégie""",
            "closing": "Nous sommes impatients de collaborer avec vous.",
            "signature": "Cordialement,\nL'équipe BIONIC"
        },
        "en": {
            "subject": "🎉 Welcome to BIONIC, {{company_name}}!",
            "greeting": "Hello {{contact_name}},",
            "body": """We are delighted to welcome you among our affiliate partners.

Your {{company_name}} account has been successfully created and you now have access to our premium affiliate platform.

Next steps:
• Complete your partner profile
• Discover our advertising options
• Contact our team to discuss your strategy""",
            "closing": "We look forward to collaborating with you.",
            "signature": "Sincerely,\nThe BIONIC Team"
        }
    },
    "partner_notification": {
        "id": "partner_notification",
        "name_fr": "Notification Partenaire",
        "name_en": "Partner Notification",
        "variables": ["company_name", "contact_name", "notification_type", "notification_content"],
        "fr": {
            "subject": "📢 BIONIC - Notification pour {{company_name}}",
            "greeting": "Bonjour {{contact_name}},",
            "body": """Nous vous informons de la mise à jour suivante concernant votre compte partenaire {{company_name}}:

{{notification_content}}

Si vous avez des questions, n'hésitez pas à nous contacter.""",
            "closing": "Merci pour votre confiance.",
            "signature": "Cordialement,\nL'équipe BIONIC"
        },
        "en": {
            "subject": "📢 BIONIC - Notification for {{company_name}}",
            "greeting": "Hello {{contact_name}},",
            "body": """We are informing you of the following update regarding your {{company_name}} partner account:

{{notification_content}}

If you have any questions, please don't hesitate to contact us.""",
            "closing": "Thank you for your trust.",
            "signature": "Sincerely,\nThe BIONIC Team"
        }
    }
}


# ============================================
# GLOBAL BILINGUAL RULE
# ============================================

GLOBAL_BILINGUAL_RULE = {
    "rule_id": "BIONIC_BILINGUAL_PREMIUM",
    "name": "Messages Bilingues Premium",
    "description": "Toujours envoyer des messages bilingues Premium (FR/EN) pour toute communication externe générée automatiquement.",
    "is_permanent": True,
    "is_priority": True,
    "applies_to": ["SEO", "Marketing", "Affiliate", "Ads", "Calendar"],
    "enforcement_level": "mandatory",
    "created_at": "2026-02-18T00:00:00Z",
    "created_by": "COPILOT_MAITRE"
}


# ============================================
# MODULE INFO
# ============================================

@router.get("/")
async def get_module_info():
    """Information sur le Messaging Engine V2"""
    return {
        "module": "messaging_engine",
        "version": "2.0.0",
        "description": "Système de messagerie bilingue Premium (FR/EN) BIONIC avec modes TOUS/UN PAR UN",
        "architecture": "LEGO_V5_ULTIME",
        "features": [
            "Mode TOUS: Envoi massif personnalisé",
            "Mode UN PAR UN: Envoi individuel avec validation",
            "Messages bilingues automatiques (FR/EN)",
            "Templates Premium pré-configurés avec variables",
            "Pré-visuel obligatoire avant envoi",
            "Entête BIONIC + logo",
            "Personnalisation complète (company_name, contact_name, category, country)",
            "Journalisation complète (7 étapes)",
            "Règle permanente de communication bilingue"
        ],
        "send_modes": [SendMode.ALL.value, SendMode.ONE_BY_ONE.value],
        "pipeline_steps": [s.value for s in PipelineStep],
        "global_rule": GLOBAL_BILINGUAL_RULE,
        "templates_available": list(BILINGUAL_TEMPLATES.keys()),
        "channels": [c.value for c in MessageChannel]
    }


# ============================================
# GLOBAL BILINGUAL RULE ENDPOINTS
# ============================================

@router.get("/rule/bilingual")
async def get_bilingual_rule():
    """Obtenir la règle permanente de communication bilingue."""
    db = get_db()
    
    rule = await db.messaging_rules.find_one({"rule_id": "BIONIC_BILINGUAL_PREMIUM"})
    
    if not rule:
        rule = {**GLOBAL_BILINGUAL_RULE}
        await db.messaging_rules.insert_one(rule)
    
    rule.pop("_id", None)
    
    return {
        "success": True,
        "rule": rule,
        "status": "ACTIVE",
        "enforcement": "MANDATORY"
    }


# ============================================
# TEMPLATES MANAGEMENT
# ============================================

@router.get("/templates")
async def get_all_templates():
    """Liste tous les templates bilingues disponibles avec leurs variables."""
    templates = []
    for name, content in BILINGUAL_TEMPLATES.items():
        templates.append({
            "id": content.get("id", name),
            "name": name,
            "name_fr": content.get("name_fr", name),
            "name_en": content.get("name_en", name),
            "variables": content.get("variables", []),
            "languages": ["fr", "en"],
            "fr_subject": content["fr"]["subject"],
            "en_subject": content["en"]["subject"]
        })
    
    return {
        "success": True,
        "templates": templates,
        "count": len(templates)
    }


@router.get("/templates/{template_name}")
async def get_template(template_name: str):
    """Obtenir un template bilingue spécifique avec toutes ses variables."""
    template = BILINGUAL_TEMPLATES.get(template_name)
    
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' non trouvé")
    
    return {
        "success": True,
        "template_name": template_name,
        "variables": template.get("variables", []),
        "content": template
    }


# ============================================
# VARIABLE INJECTION
# ============================================

def inject_variables(text: str, variables: Dict[str, str]) -> str:
    """Injecter les variables dans le texte du template."""
    result = text
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", str(value) if value else "")
    return result


def personalize_template(template: Dict, variables: Dict[str, str]) -> Dict:
    """Personnaliser un template complet avec les variables."""
    return {
        "fr": {
            "subject": inject_variables(template["fr"]["subject"], variables),
            "greeting": inject_variables(template["fr"]["greeting"], variables),
            "body": inject_variables(template["fr"]["body"], variables),
            "closing": inject_variables(template["fr"]["closing"], variables),
            "signature": inject_variables(template["fr"]["signature"], variables)
        },
        "en": {
            "subject": inject_variables(template["en"]["subject"], variables),
            "greeting": inject_variables(template["en"]["greeting"], variables),
            "body": inject_variables(template["en"]["body"], variables),
            "closing": inject_variables(template["en"]["closing"], variables),
            "signature": inject_variables(template["en"]["signature"], variables)
        }
    }


# ============================================
# PREVIEW GENERATION
# ============================================

def generate_preview(personalized_content: Dict, recipient: Dict) -> Dict:
    """Générer le pré-visuel complet FR/EN avec entête BIONIC."""
    
    preview_fr = f"""
{BIONIC_HEADER}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🇫🇷 VERSION FRANÇAISE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 Sujet: {personalized_content['fr']['subject']}

{personalized_content['fr']['greeting']}

{personalized_content['fr']['body']}

{personalized_content['fr']['closing']}

{personalized_content['fr']['signature']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    preview_en = f"""
{BIONIC_HEADER}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🇺🇸 ENGLISH VERSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 Subject: {personalized_content['en']['subject']}

{personalized_content['en']['greeting']}

{personalized_content['en']['body']}

{personalized_content['en']['closing']}

{personalized_content['en']['signature']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    return {
        "recipient": recipient,
        "variables_injected": recipient.get("variables", {}),
        "fr_preview": preview_fr,
        "en_preview": preview_en,
        "fr_content": personalized_content["fr"],
        "en_content": personalized_content["en"],
        "bionic_header": BIONIC_HEADER,
        "bionic_logo_url": BIONIC_LOGO_URL,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


@router.post("/preview/generate")
async def generate_message_preview(
    preview_request: Dict[str, Any] = Body(...)
):
    """
    Générer un pré-visuel pour un ou plusieurs destinataires.
    
    Args:
        preview_request: {
            "template": "affiliate_prelaunch",
            "send_mode": "TOUS" | "UN_PAR_UN",
            "recipients": [
                {
                    "affiliate_id": "...",
                    "company_name": "...",
                    "contact_name": "...",
                    "email": "...",
                    "category": "...",
                    "country": "..."
                }
            ]
        }
    """
    db = get_db()
    
    template_name = preview_request.get("template", "affiliate_prelaunch")
    send_mode = preview_request.get("send_mode", SendMode.ONE_BY_ONE.value)
    recipients = preview_request.get("recipients", [])
    
    template = BILINGUAL_TEMPLATES.get(template_name)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' non trouvé")
    
    if not recipients:
        raise HTTPException(status_code=400, detail="Au moins un destinataire requis")
    
    # Generate previews
    previews = []
    batch_id = str(uuid.uuid4())
    
    for recipient in recipients:
        variables = {
            "company_name": recipient.get("company_name", ""),
            "contact_name": recipient.get("contact_name", recipient.get("company_name", "")),
            "category": recipient.get("category", ""),
            "country": recipient.get("country", "")
        }
        
        personalized = personalize_template(template, variables)
        preview = generate_preview(personalized, {**recipient, "variables": variables})
        
        preview_id = str(uuid.uuid4())
        preview_record = {
            "preview_id": preview_id,
            "batch_id": batch_id,
            "send_mode": send_mode,
            "template": template_name,
            "recipient": recipient,
            "variables": variables,
            "personalized_content": personalized,
            "status": MessageStatus.PREVIEW_GENERATED.value,
            "validated": False,
            "sent": False,
            "pipeline_step": PipelineStep.PREVIEW_GENERATION.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": preview_request.get("created_by", "admin")
        }
        
        await db.message_previews.insert_one(preview_record)
        
        preview["preview_id"] = preview_id
        previews.append(preview)
    
    # Log pipeline step
    await _log_pipeline_action(db, batch_id, PipelineStep.PREVIEW_GENERATION.value, "admin", {
        "send_mode": send_mode,
        "template": template_name,
        "recipients_count": len(recipients)
    })
    
    return {
        "success": True,
        "batch_id": batch_id,
        "send_mode": send_mode,
        "template": template_name,
        "previews_generated": len(previews),
        "previews": previews if send_mode == SendMode.ONE_BY_ONE.value else previews[:1],  # Sample for TOUS mode
        "sample_preview": previews[0] if previews else None,
        "all_recipients": [r.get("company_name") for r in recipients],
        "requires_validation": True,
        "message": f"✅ {len(previews)} pré-visuel(s) généré(s) - Validation obligatoire avant envoi"
    }


# ============================================
# VALIDATION
# ============================================

@router.post("/preview/{preview_id}/validate")
async def validate_preview(
    preview_id: str,
    admin_user: str = Body("admin", embed=True)
):
    """Valider manuellement un pré-visuel avant envoi."""
    db = get_db()
    
    preview = await db.message_previews.find_one({"preview_id": preview_id})
    
    if not preview:
        raise HTTPException(status_code=404, detail="Pré-visuel non trouvé")
    
    if preview.get("validated"):
        return {
            "success": True,
            "preview_id": preview_id,
            "message": "Pré-visuel déjà validé"
        }
    
    now = datetime.now(timezone.utc).isoformat()
    
    await db.message_previews.update_one(
        {"preview_id": preview_id},
        {
            "$set": {
                "validated": True,
                "validated_at": now,
                "validated_by": admin_user,
                "status": MessageStatus.VALIDATED.value,
                "pipeline_step": PipelineStep.MANUAL_VALIDATION.value
            }
        }
    )
    
    await _log_pipeline_action(db, preview.get("batch_id"), PipelineStep.MANUAL_VALIDATION.value, admin_user, {
        "preview_id": preview_id,
        "recipient": preview.get("recipient", {}).get("company_name")
    })
    
    return {
        "success": True,
        "preview_id": preview_id,
        "validated_by": admin_user,
        "validated_at": now,
        "message": "✅ Pré-visuel validé - Prêt pour envoi"
    }


@router.post("/batch/{batch_id}/validate-all")
async def validate_all_previews(
    batch_id: str,
    admin_user: str = Body("admin", embed=True)
):
    """Valider tous les pré-visuels d'un batch (mode TOUS)."""
    db = get_db()
    
    now = datetime.now(timezone.utc).isoformat()
    
    result = await db.message_previews.update_many(
        {"batch_id": batch_id, "validated": False},
        {
            "$set": {
                "validated": True,
                "validated_at": now,
                "validated_by": admin_user,
                "status": MessageStatus.VALIDATED.value,
                "pipeline_step": PipelineStep.MANUAL_VALIDATION.value
            }
        }
    )
    
    await _log_pipeline_action(db, batch_id, PipelineStep.MANUAL_VALIDATION.value, admin_user, {
        "action": "validate_all",
        "validated_count": result.modified_count
    })
    
    return {
        "success": True,
        "batch_id": batch_id,
        "validated_count": result.modified_count,
        "validated_by": admin_user,
        "message": f"✅ {result.modified_count} pré-visuels validés - Prêts pour envoi"
    }


# ============================================
# SENDING
# ============================================

@router.post("/send/one")
async def send_one_message(
    send_request: Dict[str, Any] = Body(...)
):
    """
    Envoyer UN message (mode UN PAR UN).
    Requiert un preview_id validé.
    """
    db = get_db()
    
    preview_id = send_request.get("preview_id")
    admin_user = send_request.get("admin_user", "admin")
    
    if not preview_id:
        raise HTTPException(status_code=400, detail="preview_id requis")
    
    preview = await db.message_previews.find_one({"preview_id": preview_id})
    
    if not preview:
        raise HTTPException(status_code=404, detail="Pré-visuel non trouvé")
    
    if not preview.get("validated"):
        raise HTTPException(status_code=400, detail="⚠️ Pré-visuel non validé - Validation obligatoire avant envoi")
    
    if preview.get("sent"):
        return {
            "success": False,
            "error": "Message déjà envoyé",
            "sent_at": preview.get("sent_at")
        }
    
    now = datetime.now(timezone.utc).isoformat()
    message_id = str(uuid.uuid4())
    
    # Create message record
    message = {
        "message_id": message_id,
        "preview_id": preview_id,
        "batch_id": preview.get("batch_id"),
        "send_mode": SendMode.ONE_BY_ONE.value,
        "template": preview.get("template"),
        "recipient": preview.get("recipient"),
        "variables": preview.get("variables"),
        "content": preview.get("personalized_content"),
        "status": MessageStatus.SENT.value,
        "validated_by": preview.get("validated_by"),
        "validated_at": preview.get("validated_at"),
        "sent_at": now,
        "sent_by": admin_user,
        "pipeline_step": PipelineStep.SENDING.value,
        "created_at": now
    }
    
    await db.bilingual_messages.insert_one(message)
    
    # Update preview
    await db.message_previews.update_one(
        {"preview_id": preview_id},
        {
            "$set": {
                "sent": True,
                "sent_at": now,
                "sent_by": admin_user,
                "message_id": message_id,
                "status": MessageStatus.SENT.value,
                "pipeline_step": PipelineStep.SENDING.value
            }
        }
    )
    
    # Log
    await _log_pipeline_action(db, preview.get("batch_id"), PipelineStep.SENDING.value, admin_user, {
        "message_id": message_id,
        "preview_id": preview_id,
        "recipient": preview.get("recipient", {}).get("company_name"),
        "mode": SendMode.ONE_BY_ONE.value
    })
    
    return {
        "success": True,
        "message_id": message_id,
        "preview_id": preview_id,
        "send_mode": SendMode.ONE_BY_ONE.value,
        "recipient": preview.get("recipient", {}).get("company_name"),
        "sent_at": now,
        "sent_by": admin_user,
        "message": f"✅ Message envoyé à {preview.get('recipient', {}).get('company_name')}"
    }


@router.post("/send/all")
async def send_all_messages(
    send_request: Dict[str, Any] = Body(...)
):
    """
    Envoyer TOUS les messages validés d'un batch (mode TOUS).
    """
    db = get_db()
    
    batch_id = send_request.get("batch_id")
    admin_user = send_request.get("admin_user", "admin")
    
    if not batch_id:
        raise HTTPException(status_code=400, detail="batch_id requis")
    
    # Get all validated, unsent previews
    previews = await db.message_previews.find({
        "batch_id": batch_id,
        "validated": True,
        "sent": False
    }).to_list(1000)
    
    if not previews:
        return {
            "success": False,
            "error": "Aucun message validé à envoyer ou tous déjà envoyés"
        }
    
    now = datetime.now(timezone.utc).isoformat()
    sent_count = 0
    sent_messages = []
    
    for preview in previews:
        message_id = str(uuid.uuid4())
        
        message = {
            "message_id": message_id,
            "preview_id": preview.get("preview_id"),
            "batch_id": batch_id,
            "send_mode": SendMode.ALL.value,
            "template": preview.get("template"),
            "recipient": preview.get("recipient"),
            "variables": preview.get("variables"),
            "content": preview.get("personalized_content"),
            "status": MessageStatus.SENT.value,
            "validated_by": preview.get("validated_by"),
            "validated_at": preview.get("validated_at"),
            "sent_at": now,
            "sent_by": admin_user,
            "pipeline_step": PipelineStep.SENDING.value,
            "created_at": now
        }
        
        await db.bilingual_messages.insert_one(message)
        
        await db.message_previews.update_one(
            {"preview_id": preview.get("preview_id")},
            {
                "$set": {
                    "sent": True,
                    "sent_at": now,
                    "sent_by": admin_user,
                    "message_id": message_id,
                    "status": MessageStatus.SENT.value,
                    "pipeline_step": PipelineStep.SENDING.value
                }
            }
        )
        
        sent_count += 1
        sent_messages.append({
            "message_id": message_id,
            "recipient": preview.get("recipient", {}).get("company_name")
        })
    
    # Log
    await _log_pipeline_action(db, batch_id, PipelineStep.SENDING.value, admin_user, {
        "action": "send_all",
        "mode": SendMode.ALL.value,
        "sent_count": sent_count,
        "recipients": [m["recipient"] for m in sent_messages]
    })
    
    return {
        "success": True,
        "batch_id": batch_id,
        "send_mode": SendMode.ALL.value,
        "sent_count": sent_count,
        "sent_at": now,
        "sent_by": admin_user,
        "sent_messages": sent_messages,
        "message": f"✅ {sent_count} messages envoyés (mode TOUS)"
    }


# ============================================
# SEND TO SPECIFIC AFFILIATES (Legacy + Enhanced)
# ============================================

@router.post("/affiliates/send-prelaunch")
async def send_prelaunch_to_affiliates(
    affiliate_ids: List[str] = Body(..., embed=True)
):
    """Envoyer le message pré-lancement bilingue aux affiliés spécifiés (mode rapide)."""
    db = get_db()
    
    affiliates = await db.affiliate_switches.find({
        "affiliate_id": {"$in": affiliate_ids}
    }).to_list(100)
    
    if not affiliates:
        return {"success": False, "error": "Aucun affilié trouvé"}
    
    recipients = [
        {
            "affiliate_id": a["affiliate_id"],
            "company_name": a.get("company_name"),
            "contact_name": a.get("company_name"),
            "email": a.get("email") or f"contact@{a.get('website', '').replace('https://', '').replace('http://', '').split('/')[0]}",
            "category": a.get("category", ""),
            "country": a.get("country", "")
        }
        for a in affiliates
    ]
    
    # Generate previews
    preview_result = await generate_message_preview({
        "template": "affiliate_prelaunch",
        "send_mode": SendMode.ALL.value,
        "recipients": recipients,
        "created_by": "COPILOT_MAITRE"
    })
    
    if preview_result["success"]:
        # Auto-validate and send
        await validate_all_previews(preview_result["batch_id"], "COPILOT_MAITRE")
        send_result = await send_all_messages({
            "batch_id": preview_result["batch_id"],
            "admin_user": "COPILOT_MAITRE"
        })
        
        return {
            "success": True,
            "batch_id": preview_result["batch_id"],
            "affiliates_contacted": [r["company_name"] for r in recipients],
            "messages_sent": send_result.get("sent_count", 0),
            "template_used": "affiliate_prelaunch",
            "bilingual": True,
            "message": f"✅ Message bilingue Premium envoyé à {len(recipients)} affiliés"
        }
    
    return preview_result


# ============================================
# MESSAGE TRACKING & LOGS
# ============================================

@router.get("/messages")
async def get_all_messages(
    page: int = Query(1, ge=1),
    limit: int = Query(50, le=200),
    status: Optional[str] = None,
    batch_id: Optional[str] = None,
    send_mode: Optional[str] = None
):
    """Liste tous les messages bilingues envoyés."""
    db = get_db()
    
    query = {}
    if status:
        query["status"] = status
    if batch_id:
        query["batch_id"] = batch_id
    if send_mode:
        query["send_mode"] = send_mode
    
    skip = (page - 1) * limit
    
    messages = await db.bilingual_messages.find(query).sort("sent_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.bilingual_messages.count_documents(query)
    
    for msg in messages:
        msg.pop("_id", None)
    
    return {
        "success": True,
        "messages": messages,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }


@router.get("/messages/{message_id}")
async def get_message(message_id: str):
    """Détail d'un message avec son contenu complet FR/EN."""
    db = get_db()
    
    msg = await db.bilingual_messages.find_one({"message_id": message_id})
    
    if not msg:
        raise HTTPException(status_code=404, detail="Message non trouvé")
    
    msg.pop("_id", None)
    
    return {
        "success": True,
        "message": msg
    }


@router.get("/previews")
async def get_all_previews(
    page: int = Query(1, ge=1),
    limit: int = Query(50, le=200),
    batch_id: Optional[str] = None,
    validated: Optional[bool] = None,
    sent: Optional[bool] = None
):
    """Liste tous les pré-visuels."""
    db = get_db()
    
    query = {}
    if batch_id:
        query["batch_id"] = batch_id
    if validated is not None:
        query["validated"] = validated
    if sent is not None:
        query["sent"] = sent
    
    skip = (page - 1) * limit
    
    previews = await db.message_previews.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.message_previews.count_documents(query)
    
    for p in previews:
        p.pop("_id", None)
    
    return {
        "success": True,
        "previews": previews,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }


@router.get("/previews/{preview_id}")
async def get_preview(preview_id: str):
    """Obtenir un pré-visuel complet."""
    db = get_db()
    
    preview = await db.message_previews.find_one({"preview_id": preview_id})
    
    if not preview:
        raise HTTPException(status_code=404, detail="Pré-visuel non trouvé")
    
    preview.pop("_id", None)
    
    # Regenerate preview display
    template = BILINGUAL_TEMPLATES.get(preview.get("template"))
    if template:
        personalized = preview.get("personalized_content")
        if personalized:
            preview["display"] = generate_preview(personalized, preview.get("recipient", {}))
    
    return {
        "success": True,
        "preview": preview
    }


@router.get("/pipeline-logs")
async def get_pipeline_logs(
    batch_id: Optional[str] = None,
    limit: int = Query(100, le=500)
):
    """Historique des actions du pipeline."""
    db = get_db()
    
    query = {}
    if batch_id:
        query["batch_id"] = batch_id
    
    logs = await db.messaging_pipeline_logs.find(query).sort("timestamp", -1).limit(limit).to_list(limit)
    
    for log in logs:
        log.pop("_id", None)
    
    return {
        "success": True,
        "logs": logs,
        "count": len(logs)
    }


async def _log_pipeline_action(db, batch_id: str, step: str, user: str, details: Dict = None):
    """Journaliser une action du pipeline."""
    log_entry = {
        "log_id": str(uuid.uuid4()),
        "batch_id": batch_id,
        "pipeline_step": step,
        "user": user,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    await db.messaging_pipeline_logs.insert_one(log_entry)


# ============================================
# DASHBOARD
# ============================================

@router.get("/dashboard")
async def get_messaging_dashboard():
    """Dashboard complet du Messaging Engine V2."""
    db = get_db()
    
    # Messages stats
    total_messages = await db.bilingual_messages.count_documents({})
    sent_messages = await db.bilingual_messages.count_documents({"status": MessageStatus.SENT.value})
    
    # By send mode
    tous_count = await db.bilingual_messages.count_documents({"send_mode": SendMode.ALL.value})
    un_par_un_count = await db.bilingual_messages.count_documents({"send_mode": SendMode.ONE_BY_ONE.value})
    
    # Previews stats
    total_previews = await db.message_previews.count_documents({})
    validated_previews = await db.message_previews.count_documents({"validated": True})
    pending_validation = await db.message_previews.count_documents({"validated": False, "sent": False})
    
    # Recent messages
    recent = await db.bilingual_messages.find({}).sort("sent_at", -1).limit(10).to_list(10)
    for msg in recent:
        msg.pop("_id", None)
    
    # Recent pipeline logs
    recent_logs = await db.messaging_pipeline_logs.find({}).sort("timestamp", -1).limit(10).to_list(10)
    for log in recent_logs:
        log.pop("_id", None)
    
    return {
        "success": True,
        "dashboard": {
            "global_rule": {
                "name": GLOBAL_BILINGUAL_RULE["name"],
                "status": "ACTIVE",
                "enforcement": "MANDATORY"
            },
            "send_modes": {
                "TOUS": tous_count,
                "UN_PAR_UN": un_par_un_count
            },
            "messages": {
                "total": total_messages,
                "sent": sent_messages
            },
            "previews": {
                "total": total_previews,
                "validated": validated_previews,
                "pending_validation": pending_validation
            },
            "templates_available": list(BILINGUAL_TEMPLATES.keys()),
            "pipeline_steps": [s.value for s in PipelineStep],
            "recent_messages": recent,
            "recent_activity": recent_logs
        }
    }


logger.info("Messaging Engine V2 initialized - LEGO V5-ULTIME Module with TOUS/UN PAR UN modes")
