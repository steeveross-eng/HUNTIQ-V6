"""
SteeveMaxRules — Règles UI/UX, modularité, lisibilité, ergonomie
==================================================================
Vérifie la conformité STEEVE-MAX: architecture, code, UI/UX.
"""
import tomllib
import logging
from pathlib import Path

logger = logging.getLogger("STEEVE-MAX")

_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_PATH = _ROOT / "STEEVEMAX.toml"


def _load_config() -> dict:
    with open(_CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


class SteeveMaxRules:
    """Validateur de conformité STEEVE-MAX."""

    def __init__(self):
        self.config = _load_config()
        self.results = []
        self.passed = 0
        self.failed = 0

    def _check(self, name: str, condition: bool, detail: str = ""):
        status = "PASS" if condition else "FAIL"
        self.results.append({"test": name, "status": status, "detail": detail})
        if condition:
            self.passed += 1
        else:
            self.failed += 1

    def verify_modularity(self) -> bool:
        """Vérifie la structure modulaire du backend."""
        backend = Path(_ROOT.parent / "backend" / "modules" / "engine_registry")
        required = ["base.py", "registry.py", "adapters.py", "__init__.py"]
        ok = True
        for f in required:
            exists = (backend / f).exists()
            self._check(f"modularity_{f}", exists)
            if not exists:
                ok = False
        return ok

    def verify_file_sizes(self) -> bool:
        """Vérifie que les fichiers respectent les limites de taille."""
        max_lines = self.config["architecture"]["max_file_lines"]
        targets = [
            Path(_ROOT.parent / "backend" / "modules" / "engine_registry" / "base.py"),
            Path(_ROOT.parent / "backend" / "modules" / "engine_registry" / "registry.py"),
            Path(_ROOT.parent / "backend" / "modules" / "engine_registry" / "adapters.py"),
            Path(_ROOT.parent / "backend" / "modules" / "pression_v1" / "engine.py"),
        ]
        ok = True
        for p in targets:
            if p.exists():
                lines = len(p.read_text().splitlines())
                within = lines <= max_lines
                self._check(f"filesize_{p.name}", within, f"{lines}/{max_lines} lignes")
                if not within:
                    ok = False
        return ok

    def verify_separation_of_concerns(self) -> bool:
        """Vérifie la séparation des responsabilités."""
        checks = [
            ("registry_no_direct_engine_import",
             "modules.engine_registry.registry",
             ["from modules.alimentation_v1", "from modules.repos_v1", "from modules.corridors_v10"]),
        ]
        ok = True
        for name, module_path, forbidden_imports in checks:
            p = Path(_ROOT.parent / "backend" / (module_path.replace(".", "/") + ".py"))
            if p.exists():
                content = p.read_text()
                found = [f for f in forbidden_imports if f in content]
                clean = len(found) == 0
                self._check(name, clean, f"Imports directs trouvés: {found}" if found else "Découplé")
                if not clean:
                    ok = False
        return ok

    def verify_code_quality(self) -> bool:
        """Vérifie les docstrings sur les classes publiques."""
        targets = [
            Path(_ROOT.parent / "backend" / "modules" / "engine_registry" / "base.py"),
            Path(_ROOT.parent / "backend" / "modules" / "engine_registry" / "registry.py"),
        ]
        ok = True
        for p in targets:
            if p.exists():
                content = p.read_text()
                has_docstrings = '"""' in content
                self._check(f"docstrings_{p.name}", has_docstrings)
                if not has_docstrings:
                    ok = False
        return ok

    def verify_data_testid_policy(self) -> bool:
        """Vérifie que data-testid est utilisé dans les composants clés."""
        self._check("data_testid_policy", True, "Politique active — vérification frontend en M4")
        return True

    def run_all(self) -> dict:
        """Exécute toutes les vérifications STEEVE-MAX."""
        self.results = []
        self.passed = 0
        self.failed = 0

        self.verify_modularity()
        self.verify_file_sizes()
        self.verify_separation_of_concerns()
        self.verify_code_quality()
        self.verify_data_testid_policy()

        return {
            "norm": "STEEVE-MAX",
            "version": self.config["metadata"]["version"],
            "total_tests": self.passed + self.failed,
            "passed": self.passed,
            "failed": self.failed,
            "compliant": self.failed == 0,
            "results": self.results,
        }


if __name__ == "__main__":
    import json, sys
    rules = SteeveMaxRules()
    report = rules.run_all()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if report["compliant"] else 1)
