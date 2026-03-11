"""
SHIM de retrocompatibilite — Phase 1.6-B
Le contenu original de email_service.py a ete fusionne dans email_notifications.py.
Ce fichier re-exporte les symboles necessaires pour ne casser aucun import.
"""
from email_notifications import (
    send_cancellation_email,
    send_analysis_report_email,
    is_email_configured,
)

__all__ = ["send_cancellation_email", "send_analysis_report_email", "is_email_configured"]
