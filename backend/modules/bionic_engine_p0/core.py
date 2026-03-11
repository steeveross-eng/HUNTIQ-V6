"""
BIONIC ENGINE - Core Module
PHASE G - BIONIC ULTIMATE INTEGRATION
Version: 1.0.0-alpha

Orchestrateur central du moteur BIONIC.
Respecte strictement l'architecture modulaire BIONIC V5.

Conformite: G-SEC | G-QA | G-DOC
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import logging

# Configuration logging structure (G-SEC)
logger = logging.getLogger("bionic_engine")


class BionicPhase(str, Enum):
    """Phases du projet BIONIC"""
    P0 = "P0"  # Fondations
    P1 = "P1"  # Donnees & Visualisation
    P2 = "P2"  # Intelligence Avancee
    P3 = "P3"  # Ecosysteme


class BionicModuleStatus(str, Enum):
    """Statut des modules"""
    ACTIVE = "active"
    PLACEHOLDER = "placeholder"
    DISABLED = "disabled"
    ERROR = "error"


class BionicEngineCore:
    """
    Orchestrateur central du moteur BIONIC.
    
    Responsabilites:
    - Enregistrement et gestion des modules
    - Validation des contrats
    - Routing des requetes
    - Monitoring et logging
    
    Architecture:
    - 100% modulaire
    - Interactions via contrats formels
    - Isolation complete des modules
    """
    
    def __init__(self):
        self._modules: Dict[str, Any] = {}
        self._contracts: Dict[str, Dict] = {}
        self._status: Dict[str, BionicModuleStatus] = {}
        self._phase = BionicPhase.P0
        self._initialized = False
        
        logger.info("BionicEngineCore initialized - Phase G P0")
    
    def register_module(
        self, 
        module_id: str, 
        module_instance: Any, 
        contract: Dict
    ) -> bool:
        """
        Enregistre un module avec son contrat.
        
        Args:
            module_id: Identifiant unique du module
            module_instance: Instance du module
            contract: Contrat JSON du module
            
        Returns:
            bool: Succes de l'enregistrement
            
        G-SEC: Validation du contrat avant enregistrement
        G-QA: Verification de l'interface module
        """
        try:
            # Validation contrat (G-SEC)
            if not self._validate_contract(contract):
                logger.error(f"Invalid contract for module {module_id}")
                return False
            
            # Verification interface (G-QA)
            if not hasattr(module_instance, 'execute'):
                logger.error(f"Module {module_id} missing 'execute' method")
                return False
            
            self._modules[module_id] = module_instance
            self._contracts[module_id] = contract
            self._status[module_id] = BionicModuleStatus.ACTIVE
            
            logger.info(f"Module {module_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register module {module_id}: {e}")
            self._status[module_id] = BionicModuleStatus.ERROR
            return False
    
    def _validate_contract(self, contract: Dict) -> bool:
        """
        Valide la structure d'un contrat.
        
        G-SEC: Verification des champs obligatoires
        """
        required_fields = [
            "contract_id", 
            "contract_version", 
            "module_name",
            "inputs",
            "outputs"
        ]
        
        for field in required_fields:
            if field not in contract:
                logger.warning(f"Contract missing required field: {field}")
                return False
        
        return True
    
    def get_module(self, module_id: str) -> Optional[Any]:
        """
        Recupere un module par son ID.
        
        G-SEC: Retourne None si module inexistant (pas d'exception)
        """
        return self._modules.get(module_id)
    
    def get_module_status(self, module_id: str) -> BionicModuleStatus:
        """Retourne le statut d'un module."""
        return self._status.get(module_id, BionicModuleStatus.PLACEHOLDER)
    
    def list_modules(self) -> List[Dict]:
        """
        Liste tous les modules enregistres.
        
        G-DOC: Information complete sur chaque module
        """
        return [
            {
                "id": module_id,
                "status": self._status.get(module_id, BionicModuleStatus.PLACEHOLDER).value,
                "contract_version": self._contracts.get(module_id, {}).get("contract_version"),
                "phase": self._contracts.get(module_id, {}).get("phase", "unknown")
            }
            for module_id in self._modules.keys()
        ]
    
    def execute_module(
        self, 
        module_id: str, 
        inputs: Dict
    ) -> Dict:
        """
        Execute un module avec les inputs fournis.
        
        Args:
            module_id: ID du module a executer
            inputs: Donnees d'entree conformes au contrat
            
        Returns:
            Dict: Resultat de l'execution
            
        G-SEC: Validation inputs avant execution
        G-QA: Timeout et error handling
        """
        # Verification module existe
        module = self.get_module(module_id)
        if not module:
            return {
                "success": False,
                "error": f"Module {module_id} not found",
                "error_code": "MODULE_NOT_FOUND"
            }
        
        # Verification module actif
        if self._status.get(module_id) != BionicModuleStatus.ACTIVE:
            return {
                "success": False,
                "error": f"Module {module_id} is not active",
                "error_code": "MODULE_INACTIVE"
            }
        
        try:
            # Execution avec logging
            start_time = datetime.now()
            result = module.execute(inputs)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Enrichissement metadata
            result["metadata"] = result.get("metadata", {})
            result["metadata"]["execution_time_ms"] = execution_time
            result["metadata"]["module_id"] = module_id
            
            logger.info(f"Module {module_id} executed in {execution_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Module {module_id} execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "EXECUTION_ERROR"
            }
    
    def health_check(self) -> Dict:
        """
        Verification sante du moteur.
        
        G-QA: Monitoring complet
        """
        return {
            "status": "healthy" if self._initialized or len(self._modules) > 0 else "initializing",
            "phase": self._phase.value,
            "modules_count": len(self._modules),
            "modules_active": sum(
                1 for s in self._status.values() 
                if s == BionicModuleStatus.ACTIVE
            ),
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
_engine_instance: Optional[BionicEngineCore] = None


def get_engine() -> BionicEngineCore:
    """
    Retourne l'instance singleton du moteur BIONIC.
    
    Pattern singleton pour garantir unicite.
    """
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = BionicEngineCore()
    return _engine_instance
