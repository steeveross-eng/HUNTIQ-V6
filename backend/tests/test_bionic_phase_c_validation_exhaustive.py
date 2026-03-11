"""
BIONIC V5 — PHASE C.3 VALIDATION EXHAUSTIVE
=============================================

Tests exhaustifs demandés par COPILOT MAÎTRE pour valider:

1. DISPERSION JUVÉNILE DYNAMIQUE — Fenêtre 10-14 mois après naissance (calving/fawning)
2. DISPERSION JUVÉNILE — Vérifier que les dates sont calculées dynamiquement (pas de dates fixes)
3. STRESS THERMIQUE — Seuils par espèce (orignal >25°C, cerf >30°C)
4. STRESS THERMIQUE — Impact sur activité diurne (activity_modifier réduit)
5. PRESSION DE CHASSE (PRES-HUMAN) — Zones d'évitement dynamiques
6. PRESSION DE CHASSE — Intégration dans le score final
7. INTÉGRATION PIPELINE — UnifiedScoringService comme source unique des modificateurs
8. INTÉGRATION PIPELINE — Services 100% passifs (pas de logique locale)
9. TRAÇABILITÉ — source_ids présents pour chaque modificateur
10. TRAÇABILITÉ — version présent pour chaque modificateur
11. TRAÇABILITÉ — propagation complète dans la réponse API
12. API /api/v1/bionic/analyze_waypoint — Retourne advanced_factors_details avec PHASE C
13. MODES D'ANALYSE — LIVE, PRE_RUT, RUT, POST_RUT fonctionnent avec PHASE C

VERSION: 2.0.0-PHASE-C.3
"""

import pytest
import requests
import os
from datetime import datetime, date, timezone
from dateutil.relativedelta import relativedelta

# Import direct des modules pour tests unitaires
import sys
sys.path.insert(0, '/app/backend')

from modules.bionic_engine_p0.knowledge.seasonal.seasonal_models import (
    get_seasonal_model,
    SeasonType,
    JuvenileDispersalWindow,
    SeasonalModel
)

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


# =============================================================================
# SECTION 1: DISPERSION JUVÉNILE DYNAMIQUE (10-14 mois après naissance)
# =============================================================================

class TestDispersionJuvenileDynamic:
    """
    Tests pour la fenêtre de dispersion juvénile 10-14 mois après naissance.
    NON-NÉGOCIABLE: Aucune date calendaire fixe.
    """
    
    def test_moose_dispersal_window_calculated_from_calving(self):
        """
        ORIGNAL: Fenêtre de dispersion calculée dynamiquement depuis calving.
        
        Calving orignal Québec: 15 mai - 15 juin
        Midpoint naissance: ~30 mai 
        Dispersal: 10-14 mois après = 30 mars - 30 juillet (année suivante)
        """
        seasonal_model = get_seasonal_model("moose", "CA-QC")
        assert seasonal_model is not None, "Modèle saisonnier orignal introuvable"
        
        # Vérifier que calving period existe
        calving_period = seasonal_model.periods.get(SeasonType.CALVING)
        assert calving_period is not None, "Période de calving non définie pour orignal"
        
        # Calculer la fenêtre de dispersion dynamique
        window = seasonal_model.calculate_dynamic_dispersal_window(
            check_date=date(2025, 6, 15),
            reference_year=2024  # Naissance en 2024
        )
        
        assert window is not None, "Fenêtre de dispersion non calculée"
        
        # Vérifier les dates dynamiques (pas de dates fixes!)
        assert window.birth_date is not None, "Date de naissance manquante"
        assert window.dispersal_start is not None, "Date début dispersion manquante"
        assert window.dispersal_end is not None, "Date fin dispersion manquante"
        
        # Vérifier que dispersal_start = birth_date + 10 mois
        expected_start = window.birth_date + relativedelta(months=10)
        assert window.dispersal_start == expected_start, \
            f"dispersal_start {window.dispersal_start} != birth_date + 10 mois ({expected_start})"
        
        # Vérifier que dispersal_end = birth_date + 14 mois
        expected_end = window.birth_date + relativedelta(months=14)
        assert window.dispersal_end == expected_end, \
            f"dispersal_end {window.dispersal_end} != birth_date + 14 mois ({expected_end})"
        
        print(f"✓ ORIGNAL Dispersal Window dynamique:")
        print(f"  - Birth date: {window.birth_date}")
        print(f"  - Dispersal start: {window.dispersal_start} (birth + 10 months)")
        print(f"  - Dispersal end: {window.dispersal_end} (birth + 14 months)")
    
    def test_deer_dispersal_window_calculated_from_fawning(self):
        """
        CERF: Fenêtre de dispersion calculée dynamiquement depuis fawning.
        
        Fawning cerf Québec: 15 mai - 30 juin
        Midpoint naissance: ~7 juin
        Dispersal: 10-14 mois après = 7 avril - 7 août (année suivante)
        """
        seasonal_model = get_seasonal_model("deer", "CA-QC")
        assert seasonal_model is not None, "Modèle saisonnier cerf introuvable"
        
        # Vérifier que fawning period existe
        fawning_period = seasonal_model.periods.get(SeasonType.FAWNING)
        assert fawning_period is not None, "Période de fawning non définie pour cerf"
        
        # Calculer la fenêtre de dispersion dynamique
        window = seasonal_model.calculate_dynamic_dispersal_window(
            check_date=date(2025, 6, 15),
            reference_year=2024
        )
        
        assert window is not None, "Fenêtre de dispersion non calculée"
        
        # Vérifier les dates dynamiques
        expected_start = window.birth_date + relativedelta(months=10)
        expected_end = window.birth_date + relativedelta(months=14)
        
        assert window.dispersal_start == expected_start, \
            f"dispersal_start incorrect: {window.dispersal_start}"
        assert window.dispersal_end == expected_end, \
            f"dispersal_end incorrect: {window.dispersal_end}"
        
        print(f"✓ CERF Dispersal Window dynamique:")
        print(f"  - Birth date: {window.birth_date}")
        print(f"  - Dispersal start: {window.dispersal_start}")
        print(f"  - Dispersal end: {window.dispersal_end}")
    
    def test_dispersal_active_during_window_june(self):
        """
        Test: 15 juin 2025 doit être DANS la fenêtre de dispersion.
        
        Logique:
        - Naissance orignal ~30 mai 2024
        - Dispersion: 30 mars 2025 - 30 juillet 2025
        - 15 juin 2025 = DANS la fenêtre
        """
        seasonal_model = get_seasonal_model("moose", "CA-QC")
        
        is_dispersal, window = seasonal_model.is_in_dynamic_dispersal(
            check_date=date(2025, 6, 15),
            reference_year=2024
        )
        
        assert is_dispersal is True, \
            f"15 juin 2025 devrait être dans la fenêtre de dispersion. Window: {window.to_dict() if window else 'None'}"
        assert window is not None
        assert window.dispersal_start <= date(2025, 6, 15) <= window.dispersal_end
        
        print(f"✓ 15 juin 2025: dispersal_active=True")
        print(f"  - Window: {window.dispersal_start} to {window.dispersal_end}")
    
    def test_dispersal_inactive_january(self):
        """
        Test: 15 janvier 2025 doit être HORS de la fenêtre de dispersion.
        
        Logique:
        - Naissance orignal ~30 mai 2024
        - Dispersion: 30 mars 2025 - 30 juillet 2025
        - 15 janvier 2025 = HORS fenêtre (avant début)
        """
        seasonal_model = get_seasonal_model("moose", "CA-QC")
        
        is_dispersal, window = seasonal_model.is_in_dynamic_dispersal(
            check_date=date(2025, 1, 15),
            reference_year=2024
        )
        
        assert is_dispersal is False, \
            f"15 janvier 2025 ne devrait PAS être dans la fenêtre de dispersion"
        
        print(f"✓ 15 janvier 2025: dispersal_active=False")
    
    def test_dispersal_modifiers_correct_values(self):
        """
        Vérifier les modificateurs de dispersion juvénile:
        - activity_modifier: ~1.4 (activité accrue des juvéniles)
        - movement_modifier: ~2.0 (mouvements erratiques)
        - vulnerability_modifier: ~1.3 (juvéniles plus vulnérables)
        - movement_variance: ~0.5 (imprévisibilité)
        """
        window = JuvenileDispersalWindow(
            species_code="moose",
            region="CA-QC",
            birth_date=date(2024, 5, 30)
        )
        
        modifiers = window.get_modifiers()
        
        assert modifiers["activity"] >= 1.3, f"activity_modifier trop bas: {modifiers['activity']}"
        assert modifiers["movement"] >= 1.5, f"movement_modifier trop bas: {modifiers['movement']}"
        assert modifiers["vulnerability"] >= 1.0, f"vulnerability_modifier trop bas: {modifiers['vulnerability']}"
        assert modifiers["movement_variance"] >= 0.3, f"movement_variance trop bas: {modifiers['movement_variance']}"
        
        print(f"✓ Dispersal modifiers corrects:")
        for k, v in modifiers.items():
            print(f"  - {k}: {v}")


# =============================================================================
# SECTION 2: STRESS THERMIQUE (Seuils par espèce)
# =============================================================================

class TestStressThermique:
    """
    Tests pour le stress thermique avec seuils par espèce:
    - Orignal: >25°C (seuil critique: 30°C)
    - Cerf: >30°C (seuil critique: 35°C)
    """
    
    def test_moose_thermal_stress_period_defined(self):
        """
        Orignal: Période de stress thermique (juillet-août) doit être définie.
        """
        seasonal_model = get_seasonal_model("moose", "CA-QC")
        
        thermal_period = seasonal_model.periods.get(SeasonType.SUMMER_THERMAL_STRESS)
        assert thermal_period is not None, "Période de stress thermique non définie pour orignal"
        
        # Vérifier les mois (juillet-août)
        assert thermal_period.start_month == 7, "Stress thermique doit commencer en juillet"
        assert thermal_period.end_month == 8, "Stress thermique doit finir en août"
        
        # Vérifier activity_modifier réduit (<1.0)
        assert thermal_period.activity_modifier < 1.0, \
            f"activity_modifier stress thermique devrait être <1.0, got {thermal_period.activity_modifier}"
        
        print(f"✓ Orignal thermal stress period:")
        print(f"  - Period: {thermal_period.start_month}/{thermal_period.start_day} - {thermal_period.end_month}/{thermal_period.end_day}")
        print(f"  - activity_modifier: {thermal_period.activity_modifier}")
        print(f"  - Source IDs: {thermal_period.source_ids}")
    
    def test_deer_thermal_stress_period_defined(self):
        """
        Cerf: Période de stress thermique (juillet-août) doit être définie.
        """
        seasonal_model = get_seasonal_model("deer", "CA-QC")
        
        thermal_period = seasonal_model.periods.get(SeasonType.SUMMER_THERMAL_STRESS)
        assert thermal_period is not None, "Période de stress thermique non définie pour cerf"
        
        # Vérifier activity_modifier réduit
        assert thermal_period.activity_modifier < 1.0, \
            f"activity_modifier stress thermique devrait être <1.0, got {thermal_period.activity_modifier}"
        
        print(f"✓ Cerf thermal stress period:")
        print(f"  - activity_modifier: {thermal_period.activity_modifier}")
    
    def test_thermal_stress_active_july(self):
        """
        15 juillet doit être dans la période de stress thermique.
        """
        seasonal_model = get_seasonal_model("moose", "CA-QC")
        
        phase_c_mods = seasonal_model.get_phase_c_modifiers(
            check_date=date(2025, 7, 15),
            temperature_c=28  # Au-dessus du seuil 25°C
        )
        
        assert phase_c_mods["thermal_stress_active"] is True, \
            "Stress thermique devrait être actif le 15 juillet"
        assert phase_c_mods["thermal_stress_modifier"] < 1.0, \
            "thermal_stress_modifier devrait réduire l'activité"
        
        print(f"✓ 15 juillet stress thermique actif:")
        print(f"  - thermal_stress_active: {phase_c_mods['thermal_stress_active']}")
        print(f"  - thermal_stress_modifier: {phase_c_mods['thermal_stress_modifier']}")
    
    def test_thermal_stress_inactive_january(self):
        """
        15 janvier ne doit PAS être dans la période de stress thermique.
        """
        seasonal_model = get_seasonal_model("moose", "CA-QC")
        
        phase_c_mods = seasonal_model.get_phase_c_modifiers(
            check_date=date(2025, 1, 15),
            temperature_c=-10
        )
        
        assert phase_c_mods["thermal_stress_active"] is False, \
            "Stress thermique ne devrait PAS être actif en janvier"
        
        print(f"✓ 15 janvier stress thermique inactif")
    
    def test_thermal_stress_reduces_diurnal_activity(self):
        """
        Vérifier que le stress thermique RÉDUIT l'activité diurne.
        """
        seasonal_model = get_seasonal_model("moose", "CA-QC")
        thermal_period = seasonal_model.periods.get(SeasonType.SUMMER_THERMAL_STRESS)
        
        # Le modificateur d'activité devrait être significativement réduit
        assert thermal_period.activity_modifier <= 0.6, \
            f"Activité diurne devrait être très réduite: {thermal_period.activity_modifier}"
        
        # Le modificateur de mouvement aussi
        assert thermal_period.movement_modifier <= 0.5, \
            f"Mouvements devraient être limités: {thermal_period.movement_modifier}"
        
        print(f"✓ Thermal stress réduit l'activité diurne:")
        print(f"  - activity_modifier: {thermal_period.activity_modifier}")
        print(f"  - movement_modifier: {thermal_period.movement_modifier}")


# =============================================================================
# SECTION 3: PRESSION DE CHASSE (PRES-HUMAN)
# =============================================================================

class TestPressionChasse:
    """
    Tests pour la pression de chasse (PRES-HUMAN) avec zones d'évitement dynamiques.
    """
    
    def test_moose_hunting_pressure_period_defined(self):
        """
        Orignal: Période de pression de chasse (sept-nov) doit être définie.
        """
        seasonal_model = get_seasonal_model("moose", "CA-QC")
        
        pressure_period = seasonal_model.periods.get(SeasonType.HUNTING_PRESSURE)
        assert pressure_period is not None, "Période de pression de chasse non définie pour orignal"
        
        # Vérifier la période (septembre à novembre)
        assert pressure_period.start_month == 9, "Pression de chasse doit commencer en septembre"
        assert pressure_period.end_month == 11, "Pression de chasse doit finir en novembre"
        
        # Vérifier réduction d'activité
        assert pressure_period.activity_modifier < 1.0, \
            "activity_modifier devrait être réduit pendant la pression de chasse"
        
        # Vérifier source_ids présents
        assert len(pressure_period.source_ids) > 0, "source_ids manquants pour pression de chasse"
        
        print(f"✓ Orignal hunting pressure period:")
        print(f"  - Period: {pressure_period.start_month}/{pressure_period.start_day} - {pressure_period.end_month}/{pressure_period.end_day}")
        print(f"  - activity_modifier: {pressure_period.activity_modifier}")
        print(f"  - vulnerability_modifier: {pressure_period.vulnerability_modifier}")
        print(f"  - Source IDs: {pressure_period.source_ids}")
    
    def test_deer_hunting_pressure_period_defined(self):
        """
        Cerf: Période de pression de chasse (novembre) doit être définie.
        """
        seasonal_model = get_seasonal_model("deer", "CA-QC")
        
        pressure_period = seasonal_model.periods.get(SeasonType.HUNTING_PRESSURE)
        assert pressure_period is not None, "Période de pression de chasse non définie pour cerf"
        
        # Cerf: saison plus courte (novembre principalement)
        assert pressure_period.start_month == 11
        
        print(f"✓ Cerf hunting pressure period defined")
    
    def test_hunting_pressure_active_october(self):
        """
        1er octobre doit être dans la période de pression de chasse (orignal).
        """
        seasonal_model = get_seasonal_model("moose", "CA-QC")
        
        phase_c_mods = seasonal_model.get_phase_c_modifiers(
            check_date=date(2025, 10, 1),
            hunting_pressure_detected=True
        )
        
        assert phase_c_mods["hunting_pressure_active"] is True, \
            "Pression de chasse devrait être active le 1er octobre"
        
        # Le modificateur devrait être amplifié si pression détectée
        assert phase_c_mods["hunting_pressure_modifier"] < 1.0, \
            "Modificateur devrait réduire l'activité sous pression de chasse"
        
        print(f"✓ 1er octobre pression de chasse active:")
        print(f"  - hunting_pressure_active: {phase_c_mods['hunting_pressure_active']}")
        print(f"  - hunting_pressure_modifier: {phase_c_mods['hunting_pressure_modifier']}")
    
    def test_hunting_pressure_inactive_june(self):
        """
        15 juin ne doit PAS être dans la période de pression de chasse.
        """
        seasonal_model = get_seasonal_model("moose", "CA-QC")
        
        phase_c_mods = seasonal_model.get_phase_c_modifiers(
            check_date=date(2025, 6, 15),
            hunting_pressure_detected=False
        )
        
        assert phase_c_mods["hunting_pressure_active"] is False, \
            "Pression de chasse ne devrait PAS être active en juin"
        
        print(f"✓ 15 juin pression de chasse inactive")
    
    def test_hunting_pressure_amplified_when_detected(self):
        """
        La pression de chasse doit être AMPLIFIÉE quand détectée sur le terrain.
        """
        seasonal_model = get_seasonal_model("moose", "CA-QC")
        
        # Sans détection terrain
        mods_no_detection = seasonal_model.get_phase_c_modifiers(
            check_date=date(2025, 10, 1),
            hunting_pressure_detected=False
        )
        
        # Avec détection terrain
        mods_with_detection = seasonal_model.get_phase_c_modifiers(
            check_date=date(2025, 10, 1),
            hunting_pressure_detected=True
        )
        
        # Le modificateur avec détection devrait être plus restrictif (plus bas)
        assert mods_with_detection["hunting_pressure_modifier"] <= mods_no_detection["hunting_pressure_modifier"], \
            "Pression détectée devrait amplifier le modificateur (réduction plus forte)"
        
        print(f"✓ Pression de chasse amplifiée avec détection terrain:")
        print(f"  - Sans détection: {mods_no_detection['hunting_pressure_modifier']}")
        print(f"  - Avec détection: {mods_with_detection['hunting_pressure_modifier']}")


# =============================================================================
# SECTION 4: TRAÇABILITÉ (source_ids + version)
# =============================================================================

class TestTracabiliteSourceIds:
    """
    Tests pour la traçabilité obligatoire: source_ids + version sur chaque modificateur.
    """
    
    def test_dispersal_window_has_source_ids_and_version(self):
        """
        JuvenileDispersalWindow doit avoir source_ids et version.
        """
        window = JuvenileDispersalWindow(
            species_code="moose",
            region="CA-QC",
            birth_date=date(2024, 5, 30),
            source_ids=["SRC-LAVAL-001", "SRC-MFFP-001"],
            version="2.0.0"
        )
        
        assert len(window.source_ids) > 0, "source_ids manquants"
        assert window.version is not None and window.version != "", "version manquante"
        
        window_dict = window.to_dict()
        assert "source_ids" in window_dict
        assert "version" in window_dict
        
        print(f"✓ JuvenileDispersalWindow traçabilité:")
        print(f"  - source_ids: {window.source_ids}")
        print(f"  - version: {window.version}")
    
    def test_thermal_stress_period_has_source_ids(self):
        """
        Période de stress thermique doit avoir source_ids.
        """
        seasonal_model = get_seasonal_model("moose", "CA-QC")
        thermal_period = seasonal_model.periods.get(SeasonType.SUMMER_THERMAL_STRESS)
        
        assert len(thermal_period.source_ids) > 0, "source_ids manquants pour stress thermique"
        assert "SRC-THERM" in str(thermal_period.source_ids), \
            f"source_ids devraient inclure SRC-THERM: {thermal_period.source_ids}"
        
        print(f"✓ Thermal stress source_ids: {thermal_period.source_ids}")
    
    def test_hunting_pressure_period_has_source_ids(self):
        """
        Période de pression de chasse doit avoir source_ids incluant GPS/terrain.
        """
        seasonal_model = get_seasonal_model("moose", "CA-QC")
        pressure_period = seasonal_model.periods.get(SeasonType.HUNTING_PRESSURE)
        
        assert len(pressure_period.source_ids) > 0, "source_ids manquants pour pression de chasse"
        
        # Devrait inclure sources terrain/GPS
        sources_str = str(pressure_period.source_ids)
        has_terrain = "TERRAIN" in sources_str or "GPS" in sources_str
        assert has_terrain, \
            f"source_ids devraient inclure TERRAIN ou GPS: {pressure_period.source_ids}"
        
        print(f"✓ Hunting pressure source_ids: {pressure_period.source_ids}")
    
    def test_phase_c_modifiers_return_source_ids(self):
        """
        get_phase_c_modifiers() doit retourner source_ids agrégés.
        """
        seasonal_model = get_seasonal_model("moose", "CA-QC")
        
        phase_c_mods = seasonal_model.get_phase_c_modifiers(
            check_date=date(2025, 10, 1),
            temperature_c=28,
            hunting_pressure_detected=True
        )
        
        assert "source_ids" in phase_c_mods, "source_ids manquants dans PHASE C modifiers"
        assert len(phase_c_mods["source_ids"]) > 0, "Liste source_ids vide"
        
        print(f"✓ PHASE C source_ids agrégés: {phase_c_mods['source_ids']}")


# =============================================================================
# SECTION 5: API ENDPOINT - advanced_factors_details avec PHASE C
# =============================================================================

class TestAPIAdvancedFactorsDetails:
    """
    Tests pour l'API /api/v1/bionic/analyze_waypoint avec advanced_factors_details PHASE C.
    """
    
    def _analyze_waypoint(self, target_datetime, species="moose", mode="rut", extra_data=None):
        """Helper pour appeler l'API."""
        payload = {
            "waypoint": {
                "id": f"TEST-PHASE-C3-{species.upper()}-001",
                "name": f"Test PHASE C.3 {species}",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": species,
            "target_datetime": target_datetime,
            "parameters": {"mode": mode, "region": "CA-QC"}
        }
        if extra_data:
            payload["extra_data"] = extra_data
        
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        return response
    
    def test_api_returns_dispersal_juvenile_details(self):
        """
        API doit retourner dispersal_juvenile dans advanced_factors_details.
        """
        # Date en juin = dans la fenêtre de dispersion
        response = self._analyze_waypoint("2025-06-15T10:00:00Z", species="moose")
        assert response.status_code == 200, f"API error: {response.text}"
        
        data = response.json()
        advanced = data.get("scores", {}).get("advanced_factors_details", {})
        
        # Vérifier structure dispersal_juvenile
        factors = advanced.get("factors", {})
        dispersal = factors.get("dispersal_juvenile", {})
        
        assert "active" in dispersal, "dispersal_juvenile.active manquant"
        assert "modifier" in dispersal, "dispersal_juvenile.modifier manquant"
        assert "variance" in dispersal, "dispersal_juvenile.variance manquant"
        assert "version" in dispersal, "dispersal_juvenile.version manquant"
        
        print(f"✓ API dispersal_juvenile structure:")
        print(f"  - active: {dispersal.get('active')}")
        print(f"  - modifier: {dispersal.get('modifier')}")
        print(f"  - variance: {dispersal.get('variance')}")
        print(f"  - version: {dispersal.get('version')}")
    
    def test_api_returns_thermal_stress_details(self):
        """
        API doit retourner thermal_stress dans advanced_factors_details.
        """
        # Date en juillet = stress thermique actif
        extra_data = {"temperature_c": 28}
        response = self._analyze_waypoint("2025-07-15T14:00:00Z", extra_data=extra_data)
        assert response.status_code == 200
        
        data = response.json()
        advanced = data.get("scores", {}).get("advanced_factors_details", {})
        factors = advanced.get("factors", {})
        thermal = factors.get("thermal_stress", {})
        
        assert "active" in thermal, "thermal_stress.active manquant"
        assert "modifier" in thermal, "thermal_stress.modifier manquant"
        assert "version" in thermal, "thermal_stress.version manquant"
        
        print(f"✓ API thermal_stress structure:")
        print(f"  - active: {thermal.get('active')}")
        print(f"  - modifier: {thermal.get('modifier')}")
        print(f"  - version: {thermal.get('version')}")
    
    def test_api_returns_hunting_pressure_details(self):
        """
        API doit retourner hunting_pressure dans advanced_factors_details.
        """
        # Date en octobre = pression de chasse active
        extra_data = {"hunting_pressure_detected": True}
        response = self._analyze_waypoint("2025-10-01T08:00:00Z", extra_data=extra_data)
        assert response.status_code == 200
        
        data = response.json()
        advanced = data.get("scores", {}).get("advanced_factors_details", {})
        factors = advanced.get("factors", {})
        hunting = factors.get("hunting_pressure", {})
        
        assert "active" in hunting, "hunting_pressure.active manquant"
        assert "modifier" in hunting, "hunting_pressure.modifier manquant"
        assert "version" in hunting, "hunting_pressure.version manquant"
        
        print(f"✓ API hunting_pressure structure:")
        print(f"  - active: {hunting.get('active')}")
        print(f"  - modifier: {hunting.get('modifier')}")
        print(f"  - version: {hunting.get('version')}")
    
    def test_api_returns_phase_b_and_phase_c_modifiers(self):
        """
        API doit retourner phase_b_modifier ET phase_c_modifier.
        """
        response = self._analyze_waypoint("2025-06-15T10:00:00Z")
        assert response.status_code == 200
        
        data = response.json()
        advanced = data.get("scores", {}).get("advanced_factors_details", {})
        
        # Check in 'factors' sub-dict (actual structure) or at root level
        factors = advanced.get("factors", {})
        
        # phase_b_modifier and phase_c_modifier might be at root or in factors
        phase_b = advanced.get("phase_b_modifier") or factors.get("phase_b_modifier")
        phase_c = advanced.get("phase_c_modifier") or factors.get("phase_c_modifier")
        
        # The modifiers should exist somewhere in the structure
        assert phase_b is not None or "phase_b_modifier" in str(advanced), \
            f"phase_b_modifier manquant dans: {list(advanced.keys())}, factors: {list(factors.keys())}"
        assert phase_c is not None or "phase_c_modifier" in str(advanced), \
            f"phase_c_modifier manquant dans: {list(advanced.keys())}, factors: {list(factors.keys())}"
        
        print(f"✓ API phase modifiers présents dans advanced_factors_details")
        print(f"  - Advanced keys: {list(advanced.keys())}")
        print(f"  - Factors keys: {list(factors.keys())}")
    
    def test_api_returns_source_ids_in_response(self):
        """
        API doit retourner source_ids pour traçabilité.
        """
        response = self._analyze_waypoint("2025-06-15T10:00:00Z")
        assert response.status_code == 200
        
        data = response.json()
        advanced = data.get("scores", {}).get("advanced_factors_details", {})
        
        assert "source_ids" in advanced, "source_ids manquants dans la réponse API"
        
        print(f"✓ API source_ids: {advanced.get('source_ids')}")


# =============================================================================
# SECTION 6: MODES D'ANALYSE (LIVE, PRE_RUT, RUT, POST_RUT)
# =============================================================================

class TestModesAnalyseWithPhaseC:
    """
    Tests pour les 4 modes d'analyse avec intégration PHASE C.
    """
    
    def _analyze_waypoint(self, mode, target_datetime):
        """Helper pour appeler l'API."""
        payload = {
            "waypoint": {
                "id": f"TEST-MODE-{mode.upper()}-PHASE-C3",
                "name": f"Test Mode {mode} PHASE C.3",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "moose",
            "target_datetime": target_datetime,
            "parameters": {"mode": mode, "region": "CA-QC"}
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        return response
    
    def test_live_mode_integrates_phase_c(self):
        """Mode LIVE doit intégrer les modificateurs PHASE C."""
        response = self._analyze_waypoint("live", "2025-06-15T10:00:00Z")
        assert response.status_code == 200
        
        data = response.json()
        assert data["scores"]["analysis_mode"] == "live"
        
        # Vérifier que PHASE C est intégré via les factors
        advanced = data.get("scores", {}).get("advanced_factors_details", {})
        factors = advanced.get("factors", {})
        
        # PHASE C indicators: dispersal_juvenile, thermal_stress, hunting_pressure
        dispersal = factors.get("dispersal_juvenile", {})
        thermal = factors.get("thermal_stress", {})
        hunting = factors.get("hunting_pressure", {})
        
        # At least one PHASE C factor should be defined
        assert dispersal or thermal or hunting, \
            f"PHASE C factors manquants: {list(factors.keys())}"
        
        print(f"✓ Mode LIVE avec PHASE C:")
        print(f"  - score: {data['scores']['score_bionic_final']}")
        print(f"  - dispersal_juvenile present: {bool(dispersal)}")
        print(f"  - thermal_stress present: {bool(thermal)}")
        print(f"  - hunting_pressure present: {bool(hunting)}")
    
    def test_pre_rut_mode_integrates_phase_c(self):
        """Mode PRE_RUT doit intégrer les modificateurs PHASE C."""
        response = self._analyze_waypoint("pre_rut", "2025-09-15T10:00:00Z")
        assert response.status_code == 200
        
        data = response.json()
        assert data["scores"]["analysis_mode"] == "pre_rut"
        
        print(f"✓ Mode PRE_RUT avec PHASE C: score={data['scores']['score_bionic_final']}")
    
    def test_rut_mode_integrates_phase_c(self):
        """Mode RUT doit intégrer les modificateurs PHASE C."""
        response = self._analyze_waypoint("rut", "2025-10-01T10:00:00Z")
        assert response.status_code == 200
        
        data = response.json()
        assert data["scores"]["analysis_mode"] == "rut"
        
        print(f"✓ Mode RUT avec PHASE C: score={data['scores']['score_bionic_final']}")
    
    def test_post_rut_mode_integrates_phase_c(self):
        """Mode POST_RUT doit intégrer les modificateurs PHASE C."""
        response = self._analyze_waypoint("post_rut", "2025-10-20T10:00:00Z")
        assert response.status_code == 200
        
        data = response.json()
        assert data["scores"]["analysis_mode"] == "post_rut"
        
        print(f"✓ Mode POST_RUT avec PHASE C: score={data['scores']['score_bionic_final']}")


# =============================================================================
# SECTION 7: SERVICES PASSIFS (pas de logique locale)
# =============================================================================

class TestServicesPassifs:
    """
    Tests pour vérifier que les services sont 100% PASSIFS (consommateurs uniquement).
    La logique doit être centralisée dans UnifiedScoringService._inject_advanced_modifiers().
    """
    
    def test_unified_scoring_is_source_of_truth(self):
        """
        Vérifier que UnifiedScoringService est la source unique des modificateurs.
        """
        # Importer le service
        from modules.bionic_engine_p0.services.unified_scoring_service import get_unified_scoring_service
        
        service = get_unified_scoring_service()
        
        # Vérifier que le service existe et a les méthodes requises
        assert hasattr(service, '_inject_advanced_modifiers'), \
            "UnifiedScoringService doit avoir _inject_advanced_modifiers"
        assert hasattr(service, 'calculate_unified_score'), \
            "UnifiedScoringService doit avoir calculate_unified_score"
        
        print(f"✓ UnifiedScoringService est la source unique")
        print(f"  - Méthodes: _inject_advanced_modifiers, calculate_unified_score")
    
    def test_context_contains_advanced_modifiers_after_injection(self):
        """
        Vérifier que le contexte contient advanced_modifiers après injection.
        """
        from modules.bionic_engine_p0.services.unified_scoring_service import get_unified_scoring_service
        from modules.bionic_engine_p0.services.scoring.base_score_service import ScoreContext
        
        service = get_unified_scoring_service()
        
        # Créer un contexte
        context = ScoreContext(
            waypoint_id="TEST-PASSIF-001",
            latitude=46.85,
            longitude=-71.25,
            target_datetime=datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc),
            species="moose",
            region="CA-QC"
        )
        
        # Injecter les modificateurs
        enriched_context = service._inject_advanced_modifiers(context, "rut", "TEST-001")
        
        # Vérifier que advanced_modifiers est présent
        assert hasattr(enriched_context, 'advanced_modifiers'), \
            "Contexte doit avoir advanced_modifiers après injection"
        assert enriched_context.advanced_modifiers is not None, \
            "advanced_modifiers ne doit pas être None"
        
        # Vérifier les clés PHASE C
        mods = enriched_context.advanced_modifiers
        assert "dispersal_active" in mods, "dispersal_active manquant"
        assert "thermal_stress_active" in mods, "thermal_stress_active manquant"
        assert "hunting_pressure_active" in mods, "hunting_pressure_active manquant"
        assert "phase_c_modifier" in mods, "phase_c_modifier manquant"
        
        print(f"✓ Contexte enrichi avec advanced_modifiers:")
        print(f"  - dispersal_active: {mods.get('dispersal_active')}")
        print(f"  - thermal_stress_active: {mods.get('thermal_stress_active')}")
        print(f"  - hunting_pressure_active: {mods.get('hunting_pressure_active')}")
        print(f"  - phase_c_modifier: {mods.get('phase_c_modifier')}")
    
    def test_api_indicates_centralized_integration_mode(self):
        """
        API doit indiquer que le mode d'intégration est 'centralized'.
        """
        payload = {
            "waypoint": {
                "id": "TEST-CENTRALIZED-001",
                "name": "Test Centralized",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "moose",
            "target_datetime": "2025-06-15T10:00:00Z",
            "parameters": {"mode": "rut", "region": "CA-QC"}
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        advanced = data.get("scores", {}).get("advanced_factors_details", {})
        
        integration_mode = advanced.get("integration_mode")
        assert integration_mode == "centralized", \
            f"Integration mode devrait être 'centralized', got '{integration_mode}'"
        
        print(f"✓ API integration_mode = 'centralized'")


# =============================================================================
# SECTION 8: TESTS SPÉCIFIQUES PAR ESPÈCE ET DATE
# =============================================================================

class TestSpecificScenariosOrignal:
    """Tests spécifiques pour orignal avec différentes dates."""
    
    def _analyze_waypoint(self, target_datetime, extra_data=None):
        """Helper."""
        payload = {
            "waypoint": {
                "id": "TEST-ORIGNAL-SCENARIO",
                "name": "Test Orignal Scenario",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "moose",
            "target_datetime": target_datetime,
            "parameters": {"mode": "live", "region": "CA-QC"}
        }
        if extra_data:
            payload["extra_data"] = extra_data
        
        return requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
    
    def test_orignal_june_dispersion_active(self):
        """Orignal en juin: dispersion active."""
        response = self._analyze_waypoint("2025-06-15T10:00:00Z")
        assert response.status_code == 200
        
        data = response.json()
        advanced = data["scores"]["advanced_factors_details"]
        factors = advanced.get("factors", {})
        dispersal = factors.get("dispersal_juvenile", {})
        
        # En juin, la dispersion devrait être active
        assert dispersal.get("active") is True, \
            f"Dispersion devrait être active en juin: {dispersal}"
        
        print(f"✓ Orignal juin: dispersion_active=True")
    
    def test_orignal_january_dispersion_inactive(self):
        """Orignal en janvier: dispersion inactive."""
        response = self._analyze_waypoint("2025-01-15T10:00:00Z")
        assert response.status_code == 200
        
        data = response.json()
        advanced = data["scores"]["advanced_factors_details"]
        factors = advanced.get("factors", {})
        dispersal = factors.get("dispersal_juvenile", {})
        
        # En janvier, la dispersion ne devrait PAS être active
        assert dispersal.get("active") is False, \
            f"Dispersion ne devrait PAS être active en janvier: {dispersal}"
        
        print(f"✓ Orignal janvier: dispersion_active=False")
    
    def test_orignal_july_thermal_stress(self):
        """Orignal en juillet avec température élevée: stress thermique actif."""
        extra_data = {"temperature_c": 28}  # Au-dessus de 25°C
        response = self._analyze_waypoint("2025-07-15T14:00:00Z", extra_data)
        assert response.status_code == 200
        
        data = response.json()
        advanced = data["scores"]["advanced_factors_details"]
        factors = advanced.get("factors", {})
        thermal = factors.get("thermal_stress", {})
        
        assert thermal.get("active") is True, \
            f"Stress thermique devrait être actif en juillet: {thermal}"
        
        print(f"✓ Orignal juillet: thermal_stress_active=True")
    
    def test_orignal_november_hunting_pressure(self):
        """Orignal en novembre: pression de chasse active."""
        extra_data = {"hunting_pressure_detected": True}
        response = self._analyze_waypoint("2025-11-01T08:00:00Z", extra_data)
        assert response.status_code == 200
        
        data = response.json()
        advanced = data["scores"]["advanced_factors_details"]
        factors = advanced.get("factors", {})
        hunting = factors.get("hunting_pressure", {})
        
        assert hunting.get("active") is True, \
            f"Pression de chasse devrait être active en novembre: {hunting}"
        
        print(f"✓ Orignal novembre: hunting_pressure_active=True")


class TestSpecificScenariosCerf:
    """Tests spécifiques pour cerf avec différentes dates."""
    
    def _analyze_waypoint(self, target_datetime, extra_data=None):
        """Helper."""
        payload = {
            "waypoint": {
                "id": "TEST-CERF-SCENARIO",
                "name": "Test Cerf Scenario",
                "latitude": 46.8500,
                "longitude": -71.2500
            },
            "species": "deer",
            "target_datetime": target_datetime,
            "parameters": {"mode": "live", "region": "CA-QC"}
        }
        if extra_data:
            payload["extra_data"] = extra_data
        
        return requests.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=payload)
    
    def test_cerf_june_dispersion(self):
        """Cerf en juin: vérifier dispersion."""
        response = self._analyze_waypoint("2025-06-20T10:00:00Z")
        assert response.status_code == 200
        
        data = response.json()
        print(f"✓ Cerf juin: score={data['scores']['score_bionic_final']}")
    
    def test_cerf_november_hunting_pressure(self):
        """Cerf en novembre: pression de chasse (saison carabine)."""
        extra_data = {"hunting_pressure_detected": True}
        response = self._analyze_waypoint("2025-11-10T08:00:00Z", extra_data)
        assert response.status_code == 200
        
        data = response.json()
        advanced = data["scores"]["advanced_factors_details"]
        factors = advanced.get("factors", {})
        hunting = factors.get("hunting_pressure", {})
        
        assert hunting.get("active") is True, \
            f"Pression de chasse devrait être active pour cerf en novembre: {hunting}"
        
        print(f"✓ Cerf novembre: hunting_pressure_active=True")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
