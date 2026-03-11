"""
Brand Identity Module - PDF Generation and Logo Management
Handles document headers, logo uploads, and brand asset management
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import os
import io
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# PDF Generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_RIGHT

load_dotenv()

logger = logging.getLogger(__name__)

brand_router = APIRouter(prefix="/brand", tags=["Brand Identity"])

# Database connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "bionic_territory")

client = None
db = None

async def get_db():
    global client, db
    if client is None:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
    return db

# Logo storage paths
LOGO_DIR = "/app/frontend/public/logos"
CUSTOM_LOGO_DIR = f"{LOGO_DIR}/custom"

# Ensure directories exist
os.makedirs(CUSTOM_LOGO_DIR, exist_ok=True)

# Brand configuration - Uses unified logo
BRAND_CONFIG = {
    "fr": {
        "name": "Chasse Bionic™",
        "tagline": "Votre parcours guidé vers une chasse parfaite",
        "slogan": "La science valide ce que le terrain confirme.™",
        "logo": f"{LOGO_DIR}/bionic-logo-main.png",
        "website": "www.chassebionic.ca",
        "email": "info@chassebionic.ca"
    },
    "en": {
        "name": "Bionic Hunt™",
        "tagline": "Your guided path to a perfect hunt",
        "slogan": "Science validates what the field confirms.™",
        "logo": f"{LOGO_DIR}/bionic-logo-main.png",
        "website": "www.bionichunt.ca",
        "email": "info@bionichunt.ca"
    }
}

# Document templates
DOCUMENT_TEMPLATES = {
    "letter": {"name_fr": "Lettre officielle", "name_en": "Official Letter"},
    "email": {"name_fr": "En-tête Email", "name_en": "Email Header"},
    "contract": {"name_fr": "Contrat", "name_en": "Contract"},
    "invoice": {"name_fr": "Facture", "name_en": "Invoice"},
    "partner": {"name_fr": "Document Partenaire", "name_en": "Partner Document"},
    "zec": {"name_fr": "Document ZEC/Sépaq", "name_en": "ZEC/Sépaq Document"},
    "press": {"name_fr": "Communiqué de Presse", "name_en": "Press Release"}
}


# ============================================
# PYDANTIC MODELS
# ============================================

class LogoUploadResponse(BaseModel):
    success: bool
    filename: str
    url: str
    message: str

class PDFGenerationRequest(BaseModel):
    template_type: str
    language: str = "fr"
    title: Optional[str] = None
    content: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_address: Optional[str] = None


# ============================================
# PDF GENERATION
# ============================================

def create_document_header(canvas, doc, brand_config, template_type):
    """Add branded header to PDF document"""
    canvas.saveState()
    
    width, height = A4
    
    # Header background line
    canvas.setStrokeColor(colors.HexColor("#f5a623"))
    canvas.setLineWidth(3)
    canvas.line(1*cm, height - 3*cm, width - 1*cm, height - 3*cm)
    
    # Logo (if exists)
    logo_path = brand_config["logo"]
    if os.path.exists(logo_path):
        try:
            canvas.drawImage(logo_path, 1.5*cm, height - 2.8*cm, width=4*cm, height=2*cm, preserveAspectRatio=True)
        except:
            pass
    
    # Brand name and contact info on right
    canvas.setFont("Helvetica-Bold", 14)
    canvas.setFillColor(colors.HexColor("#f5a623"))
    canvas.drawRightString(width - 1.5*cm, height - 1.5*cm, brand_config["name"])
    
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawRightString(width - 1.5*cm, height - 2*cm, brand_config["website"])
    canvas.drawRightString(width - 1.5*cm, height - 2.4*cm, brand_config["email"])
    
    # Footer
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#999999"))
    footer_text = f"© {datetime.now().year} {brand_config['name']} - {brand_config['slogan']}"
    canvas.drawCentredString(width / 2, 1.5*cm, footer_text)
    
    # Page number
    canvas.drawRightString(width - 1.5*cm, 1.5*cm, f"Page {doc.page}")
    
    canvas.restoreState()


def generate_pdf_document(template_type: str, language: str, title: str = None, 
                          content: str = None, recipient_name: str = None, 
                          recipient_address: str = None) -> io.BytesIO:
    """Generate a branded PDF document"""
    
    brand = BRAND_CONFIG.get(language, BRAND_CONFIG["fr"])
    template = DOCUMENT_TEMPLATES.get(template_type, DOCUMENT_TEMPLATES["letter"])
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        topMargin=4*cm,
        bottomMargin=3*cm,
        leftMargin=2*cm,
        rightMargin=2*cm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='BrandTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor("#f5a623"),
        spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        name='BrandBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor("#333333"),
        spaceAfter=12,
        leading=16
    ))
    styles.add(ParagraphStyle(
        name='BrandDate',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor("#666666"),
        alignment=TA_RIGHT
    ))
    
    story = []
    
    # Date
    date_str = datetime.now().strftime("%d %B %Y") if language == "fr" else datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph(date_str, styles['BrandDate']))
    story.append(Spacer(1, 20))
    
    # Recipient (if provided)
    if recipient_name:
        story.append(Paragraph(recipient_name, styles['BrandBody']))
        if recipient_address:
            story.append(Paragraph(recipient_address.replace('\n', '<br/>'), styles['BrandBody']))
        story.append(Spacer(1, 20))
    
    # Title
    doc_title = title or (template["name_fr"] if language == "fr" else template["name_en"])
    story.append(Paragraph(doc_title, styles['BrandTitle']))
    
    # Content
    if content:
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.replace('\n', '<br/>'), styles['BrandBody']))
    else:
        # Default placeholder content
        placeholder = "[Contenu du document]" if language == "fr" else "[Document content]"
        story.append(Spacer(1, 50))
        story.append(Paragraph(placeholder, styles['BrandBody']))
        story.append(Spacer(1, 50))
    
    # Signature area
    story.append(Spacer(1, 40))
    signature = "Cordialement," if language == "fr" else "Sincerely,"
    story.append(Paragraph(signature, styles['BrandBody']))
    story.append(Spacer(1, 30))
    story.append(Paragraph(f"<b>{brand['name']}</b>", styles['BrandBody']))
    
    # Build PDF with header/footer
    def add_header_footer(canvas, doc):
        create_document_header(canvas, doc, brand, template_type)
    
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    
    buffer.seek(0)
    return buffer


# ============================================
# API ENDPOINTS
# ============================================

@brand_router.get("/config")
async def get_brand_config():
    """Get brand configuration for both languages"""
    return {
        "fr": {
            "name": BRAND_CONFIG["fr"]["name"],
            "tagline": BRAND_CONFIG["fr"]["tagline"],
            "slogan": BRAND_CONFIG["fr"]["slogan"],
            "website": BRAND_CONFIG["fr"]["website"],
            "email": BRAND_CONFIG["fr"]["email"],
            "logo_url": "/logos/logo-chasse-bionic-fr.png"
        },
        "en": {
            "name": BRAND_CONFIG["en"]["name"],
            "tagline": BRAND_CONFIG["en"]["tagline"],
            "slogan": BRAND_CONFIG["en"]["slogan"],
            "website": BRAND_CONFIG["en"]["website"],
            "email": BRAND_CONFIG["en"]["email"],
            "logo_url": "/logos/logo-bionic-hunt-en.png"
        }
    }


@brand_router.get("/templates")
async def get_document_templates():
    """Get available document templates"""
    return {
        "templates": [
            {"id": tid, **template}
            for tid, template in DOCUMENT_TEMPLATES.items()
        ]
    }


@brand_router.post("/generate-pdf")
async def generate_pdf(request: PDFGenerationRequest):
    """Generate a branded PDF document"""
    
    if request.template_type not in DOCUMENT_TEMPLATES:
        raise HTTPException(status_code=400, detail=f"Invalid template type: {request.template_type}")
    
    if request.language not in ["fr", "en"]:
        raise HTTPException(status_code=400, detail="Language must be 'fr' or 'en'")
    
    try:
        pdf_buffer = generate_pdf_document(
            template_type=request.template_type,
            language=request.language,
            title=request.title,
            content=request.content,
            recipient_name=request.recipient_name,
            recipient_address=request.recipient_address
        )
        
        # Generate filename
        template = DOCUMENT_TEMPLATES[request.template_type]
        template_name = template["name_fr"] if request.language == "fr" else template["name_en"]
        filename = f"{template_name.replace(' ', '_')}_{request.language}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@brand_router.get("/generate-pdf/{template_type}/{language}")
async def generate_pdf_get(
    template_type: str,
    language: str,
    title: Optional[str] = None
):
    """Generate a branded PDF document (GET method for easy download)"""
    request = PDFGenerationRequest(
        template_type=template_type,
        language=language,
        title=title
    )
    return await generate_pdf(request)


@brand_router.post("/upload-logo")
async def upload_logo(
    file: UploadFile = File(...),
    language: str = Query("fr", description="Language: fr or en"),
    logo_type: str = Query("primary", description="Logo type: primary, secondary, icon")
):
    """Upload a custom logo"""
    
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/webp", "image/svg+xml"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File must be PNG, JPEG, WebP or SVG")
    
    # Validate file size (max 5MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")
    
    try:
        database = await get_db()
        
        # Generate filename
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'png'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logo-{language}-{logo_type}-{timestamp}.{ext}"
        filepath = os.path.join(CUSTOM_LOGO_DIR, filename)
        
        # Save file
        with open(filepath, 'wb') as f:
            f.write(content)
        
        # Log to database
        await database.brand_logo_history.insert_one({
            "filename": filename,
            "language": language,
            "logo_type": logo_type,
            "original_filename": file.filename,
            "file_size": len(content),
            "content_type": file.content_type,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "url": f"/logos/custom/{filename}"
        })
        
        logger.info(f"Logo uploaded: {filename}")
        
        return LogoUploadResponse(
            success=True,
            filename=filename,
            url=f"/logos/custom/{filename}",
            message=f"Logo {language.upper()} uploadé avec succès"
        )
        
    except Exception as e:
        logger.error(f"Error uploading logo: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading logo: {str(e)}")


@brand_router.get("/logos")
async def get_logos():
    """Get all available logos"""
    
    logos = {
        "official": {
            "fr": {
                "primary": "/logos/logo-chasse-bionic-fr.png",
                "exists": os.path.exists(f"{LOGO_DIR}/logo-chasse-bionic-fr.png")
            },
            "en": {
                "primary": "/logos/logo-bionic-hunt-en.png",
                "exists": os.path.exists(f"{LOGO_DIR}/logo-bionic-hunt-en.png")
            }
        },
        "custom": []
    }
    
    # Get custom logos
    if os.path.exists(CUSTOM_LOGO_DIR):
        for filename in os.listdir(CUSTOM_LOGO_DIR):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.webp', '.svg')):
                logos["custom"].append({
                    "filename": filename,
                    "url": f"/logos/custom/{filename}"
                })
    
    return logos


@brand_router.get("/logo-history")
async def get_logo_history(limit: int = 20):
    """Get logo upload history"""
    database = await get_db()
    
    history = await database.brand_logo_history.find(
        {},
        {"_id": 0}
    ).sort("uploaded_at", -1).limit(limit).to_list(limit)
    
    return {"history": history}


@brand_router.delete("/logo/{filename}")
async def delete_custom_logo(filename: str):
    """Delete a custom logo"""
    filepath = os.path.join(CUSTOM_LOGO_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Logo not found")
    
    try:
        os.remove(filepath)
        
        # Update database
        database = await get_db()
        await database.brand_logo_history.update_one(
            {"filename": filename},
            {"$set": {"deleted_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return {"success": True, "message": "Logo supprimé"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting logo: {str(e)}")


logger.info("Brand Identity module initialized")
