"""
SHIM de retrocompatibilite — Phase 1.6-B
Le contenu original de global_master_switch/router.py a ete fusionne dans master_switch/router.py.
Ce fichier re-exporte le routeur necessaire pour ne casser aucun import.
"""
from modules.master_switch.router import global_switch_router as router

__all__ = ["router"]
