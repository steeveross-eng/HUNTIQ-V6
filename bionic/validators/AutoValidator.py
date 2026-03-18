"""
AutoValidator — Exécution automatique BCE-4X + STEEVE-MAX
============================================================
Exécuté après chaque commit et avant chaque progression M2/M3/M4.
Usage: python -m bionic.validators.AutoValidator
"""
import json
import sys
import time
import logging
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger("AutoValidator")

_ROOT = Path(__file__).resolve().parent.parent.parent


def run_validation(output_file: str = None) -> dict:
    """Exécute l'ensemble des validations BCE-4X + STEEVE-MAX."""
    sys.path.insert(0, str(_ROOT / "backend"))

    start = time.time()

    # BCE-4X
    from bionic.bce4x.BCE4XGuard import BCE4XGuard
    bce = BCE4XGuard()
    bce_report = bce.run_all()

    # STEEVE-MAX
    from bionic.steevemax.SteeveMaxRules import SteeveMaxRules
    sm = SteeveMaxRules()
    sm_report = sm.run_all()

    elapsed = time.time() - start

    report = {
        "validator": "AutoValidator",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_s": round(elapsed, 2),
        "overall_compliant": bce_report["compliant"] and sm_report["compliant"],
        "bce4x": bce_report,
        "steeve_max": sm_report,
        "summary": {
            "total_tests": bce_report["total_tests"] + sm_report["total_tests"],
            "passed": bce_report["passed"] + sm_report["passed"],
            "failed": bce_report["failed"] + sm_report["failed"],
        },
    }

    if output_file:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"Rapport sauvé: {output_file}")

    return report


if __name__ == "__main__":
    output = str(_ROOT / "test_reports" / "autovalidator_latest.json")
    report = run_validation(output)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if report["overall_compliant"] else 1)
