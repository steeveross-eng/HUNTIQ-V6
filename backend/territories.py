"""
# ══════════════════════════════════════════════════════════════
# LEGACY FIGÉ — NE PAS MODIFIER, NE PAS RÉACTIVER, NE PAS MIGRER
# Raison: Remplacé par bionic_engine_p0/ (pipeline V7 canonique)
# Date gel: 2026-03-10
# BCE: Ce fichier est exclu du pipeline de conformité
# ══════════════════════════════════════════════════════════════
SHIM de retrocompatibilite — Phase 1.6-B
Le contenu original de territories.py a ete fusionne dans territory.py.
Ce fichier re-exporte les symboles necessaires pour ne casser aucun import.
"""
from territory import territories_router as router, sync_partnership_to_territory

__all__ = ["router", "sync_partnership_to_territory"]
