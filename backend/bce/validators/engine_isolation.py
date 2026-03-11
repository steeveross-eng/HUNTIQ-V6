"""
BCE — Engine Isolation Validator
Ensures engines don't cross responsibilities.

Rules:
- Each engine has a single responsibility
- No engine modifies another engine's state
- Exclusion, scoring, corridor engines are independent
- No circular imports between engine modules
"""

import logging
import os
import re
from typing import Dict, Any

logger = logging.getLogger("bce.engine_isolation")

VALIDATOR_NAME = "engine_isolation"

ENGINE_DIR = "/app/backend/modules/bionic_engine_p0/services"

# Define engine responsibilities
ENGINE_RESPONSIBILITIES = {
    "behavioral_rasterizer": {"role": "rasterization", "forbidden": ["classify_zone", "process_zones_v6"]},
    "zone_typology_v7": {"role": "classification", "forbidden": ["rasterize", "build_exclusion"]},
    "exclusion_engine_v6": {"role": "exclusion", "forbidden": ["classify_zone", "rasterize"]},
    "exclusion_geometry_v6": {"role": "geometry", "forbidden": ["classify_zone", "rasterize"]},
    "species_behavior_v7": {"role": "species_data", "forbidden": ["rasterize", "build_exclusion"]},
    "corridor_v7": {"role": "corridor", "forbidden": ["classify_zone", "rasterize"]},
    "scoring_zone_integration": {"role": "scoring_integration", "forbidden": ["rasterize"]},
}


def _read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def validate() -> Dict[str, Any]:
    """Run engine isolation checks."""
    checks = []
    errors = []

    # CHECK 1: Engine files exist
    existing_engines = []
    for engine_name in ENGINE_RESPONSIBILITIES:
        path = os.path.join(ENGINE_DIR, f"{engine_name}.py")
        if os.path.exists(path):
            existing_engines.append(engine_name)

    checks.append({
        "name": "engine_files_exist",
        "status": "PASS" if len(existing_engines) >= 5 else "FAIL",
        "detail": f"{len(existing_engines)}/{len(ENGINE_RESPONSIBILITIES)} found",
    })

    # CHECK 2: No engine imports forbidden functions from other engines
    cross_violations = []
    for engine_name, rules in ENGINE_RESPONSIBILITIES.items():
        path = os.path.join(ENGINE_DIR, f"{engine_name}.py")
        content = _read_file(path)
        if not content:
            continue

        for forbidden in rules["forbidden"]:
            if re.search(rf"\b{forbidden}\b", content):
                # Check if it's an import or a function call, not just a string
                if re.search(rf"from.*import.*{forbidden}|import.*{forbidden}|{forbidden}\(", content):
                    cross_violations.append(f"{engine_name} uses '{forbidden}' (role: {rules['role']})")

    checks.append({
        "name": "no_cross_engine_calls",
        "status": "PASS" if not cross_violations else "WARN",
        "detail": f"{len(cross_violations)} potential violations",
    })
    if cross_violations:
        errors.extend(cross_violations)

    # CHECK 3: species_behavior_v7 is data-only (no side effects)
    species_path = os.path.join(ENGINE_DIR, "species_behavior_v7.py")
    species_content = _read_file(species_path)
    has_side_effects = bool(re.search(
        r"requests\.|httpx\.|aiohttp\.|db\.|collection\.|insert|update|delete|MongoClient",
        species_content
    ))
    checks.append({
        "name": "species_engine_data_only",
        "status": "PASS" if not has_side_effects else "FAIL",
        "detail": "No side effects" if not has_side_effects else "Side effects detected",
    })
    if has_side_effects:
        errors.append("species_behavior_v7.py has side effects (DB/HTTP calls)")

    # CHECK 4: exclusion_geometry_v6 doesn't import scoring modules
    excl_geom_path = os.path.join(ENGINE_DIR, "exclusion_geometry_v6.py")
    excl_content = _read_file(excl_geom_path)
    imports_scoring = bool(re.search(r"from.*zone_typology|from.*scoring|from.*species_behavior", excl_content))
    checks.append({
        "name": "exclusion_independent_of_scoring",
        "status": "PASS" if not imports_scoring else "FAIL",
        "detail": "Clean separation" if not imports_scoring else "Scoring import detected",
    })
    if imports_scoring:
        errors.append("exclusion_geometry_v6.py imports scoring modules")

    # CHECK 5: No circular dependencies detected
    import_graph = {}
    for engine_name in ENGINE_RESPONSIBILITIES:
        path = os.path.join(ENGINE_DIR, f"{engine_name}.py")
        content = _read_file(path)
        imports = re.findall(r"from\s+\.(\w+)\s+import", content)
        import_graph[engine_name] = imports

    # Simple cycle detection (depth 2)
    cycles = []
    for a, a_imports in import_graph.items():
        for b in a_imports:
            if b in import_graph and a in import_graph.get(b, []):
                cycles.append(f"{a} <-> {b}")

    checks.append({
        "name": "no_circular_imports",
        "status": "PASS" if not cycles else "WARN",
        "detail": f"{len(cycles)} cycles: {cycles}" if cycles else "No cycles",
    })

    status = "PASS" if all(c["status"] in ("PASS", "WARN") for c in checks) else "FAIL"
    return {
        "name": VALIDATOR_NAME,
        "status": status,
        "checks": checks,
        "errors": errors,
    }
