"""
BIONIC V5 — CSV/Excel Import Service Tests
============================================
Tests for the import endpoint POST /calibration/observations/import
and template endpoint GET /calibration/import/template.

Features tested:
- CSV import (comma, semicolon, tab delimiters)
- Excel import (.xlsx)
- French column aliases (espèce, comportement, lat, etc.)
- Species and behavior normalization
- Validation of required columns
- Rejection of unsupported formats
- Batch ID and source_ids traceability
- Error reporting for invalid rows

VERSION: 1.0.0
"""

import pytest
import requests
import os
import io
import tempfile

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://bce-4x-visual-fix.preview.emergentagent.com').rstrip('/')
API_PREFIX = f"{BASE_URL}/api/v1/bionic"


class TestImportTemplate:
    """Tests for GET /calibration/import/template endpoint"""

    def test_template_returns_200(self):
        """Template endpoint returns 200"""
        response = requests.get(f"{API_PREFIX}/calibration/import/template")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Template endpoint returns 200")

    def test_template_has_required_columns(self):
        """Template contains required columns list"""
        response = requests.get(f"{API_PREFIX}/calibration/import/template")
        data = response.json()
        
        assert "required_columns" in data, "Missing required_columns"
        required = set(data["required_columns"])
        expected = {"latitude", "longitude", "species", "observed_behavior", "observation_datetime"}
        assert expected == required, f"Expected {expected}, got {required}"
        print(f"✓ Template has required columns: {required}")

    def test_template_has_optional_columns(self):
        """Template contains optional columns list"""
        response = requests.get(f"{API_PREFIX}/calibration/import/template")
        data = response.json()
        
        assert "optional_columns" in data, "Missing optional_columns"
        optional = set(data["optional_columns"])
        assert "region" in optional, "Missing 'region' in optional"
        assert "notes" in optional, "Missing 'notes' in optional"
        assert "confidence" in optional, "Missing 'confidence' in optional"
        print(f"✓ Template has optional columns: {optional}")

    def test_template_has_accepted_formats(self):
        """Template shows accepted file formats"""
        response = requests.get(f"{API_PREFIX}/calibration/import/template")
        data = response.json()
        
        assert "accepted_formats" in data, "Missing accepted_formats"
        formats = data["accepted_formats"]
        assert ".csv" in formats, "Missing .csv format"
        assert ".xlsx" in formats, "Missing .xlsx format"
        print(f"✓ Template has accepted formats: {formats}")

    def test_template_has_csv_example(self):
        """Template provides CSV example"""
        response = requests.get(f"{API_PREFIX}/calibration/import/template")
        data = response.json()
        
        assert "csv_example" in data, "Missing csv_example"
        csv_example = data["csv_example"]
        assert "latitude" in csv_example, "CSV example missing headers"
        assert "orignal" in csv_example or "cerf" in csv_example, "CSV example missing species"
        print(f"✓ Template has CSV example")

    def test_template_has_limits(self):
        """Template shows file limits"""
        response = requests.get(f"{API_PREFIX}/calibration/import/template")
        data = response.json()
        
        assert "limits" in data, "Missing limits"
        limits = data["limits"]
        assert limits.get("max_file_size_mb") == 10, "Expected max_file_size_mb=10"
        assert limits.get("max_rows") == 5000, "Expected max_rows=5000"
        print(f"✓ Template has limits: {limits}")

    def test_template_has_valid_species_list(self):
        """Template provides valid species list"""
        response = requests.get(f"{API_PREFIX}/calibration/import/template")
        data = response.json()
        
        assert "valid_species" in data, "Missing valid_species"
        species = data["valid_species"]
        assert "orignal" in species, "Missing orignal in species"
        assert "cerf_de_virginie" in species, "Missing cerf_de_virginie"
        print(f"✓ Template has valid species: {species}")

    def test_template_has_valid_behaviors_list(self):
        """Template provides valid behaviors list"""
        response = requests.get(f"{API_PREFIX}/calibration/import/template")
        data = response.json()
        
        assert "valid_behaviors" in data, "Missing valid_behaviors"
        behaviors = data["valid_behaviors"]
        assert "alimentation" in behaviors, "Missing alimentation"
        assert "déplacement" in behaviors, "Missing déplacement"
        print(f"✓ Template has valid behaviors: {behaviors}")


class TestCSVImportValidRows:
    """Tests for POST /calibration/observations/import with valid CSV"""

    def test_import_comma_separated_csv(self):
        """Import valid CSV with comma delimiter"""
        csv_content = """latitude,longitude,species,observed_behavior,observation_datetime,region,notes,confidence
46.8139,-71.2080,orignal,alimentation,2026-02-24T08:30:00Z,CA-QC,Test comma import,0.9
47.1000,-70.5000,cerf_de_virginie,repos,2026-02-24T14:00:00Z,CA-QC,Test line 2,0.85"""
        
        files = {'file': ('test_comma.csv', io.BytesIO(csv_content.encode('utf-8')), 'text/csv')}
        response = requests.post(f"{API_PREFIX}/calibration/observations/import", files=files)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("status") == "success", f"Expected success, got {data.get('status')}"
        assert data.get("imported") >= 1, f"Expected at least 1 imported, got {data.get('imported')}"
        assert "batch_id" in data, "Missing batch_id"
        assert "source_ids" in data, "Missing source_ids"
        print(f"✓ Comma-separated CSV imported: {data.get('imported')} rows, batch_id={data.get('batch_id')}")

    def test_import_semicolon_separated_csv(self):
        """Import valid CSV with semicolon delimiter (French format)"""
        csv_content = """latitude;longitude;species;observed_behavior;observation_datetime;region;notes
46.5;-71.0;ours_noir;déplacement;2026-06-15T06:00:00Z;CA-QC;Test semicolon import
47.2;-70.8;caribou;fuite;2026-02-24T15:00:00Z;CA-QC;Test line 2"""
        
        files = {'file': ('test_semicolon.csv', io.BytesIO(csv_content.encode('utf-8')), 'text/csv')}
        response = requests.post(f"{API_PREFIX}/calibration/observations/import", files=files)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("status") == "success", f"Expected success, got {data.get('status')}"
        assert data.get("imported") >= 1, f"Expected at least 1 imported"
        print(f"✓ Semicolon-separated CSV imported: {data.get('imported')} rows")

    def test_import_french_column_names(self):
        """Import CSV with French column aliases (lat, espèce, comportement, date)"""
        csv_content = """lat;longitude;espèce;comportement;date;région;notes
46.9;-71.3;orignal;repos;2026-02-24T10:30:00Z;CA-QC;Test French columns
47.2;-70.8;cerf de virginie;fuite;2026-02-24T15:00:00Z;CA-QC;Test normalization"""
        
        files = {'file': ('test_french_cols.csv', io.BytesIO(csv_content.encode('utf-8')), 'text/csv')}
        response = requests.post(f"{API_PREFIX}/calibration/observations/import", files=files)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("status") == "success", f"Expected success, got {data.get('status')}"
        assert data.get("imported") >= 1, "Expected at least 1 imported"
        print(f"✓ French column names parsed correctly: {data.get('imported')} rows")

    def test_import_normalizes_species_names(self):
        """Import normalizes species names (cerf de virginie → cerf_de_virginie)"""
        csv_content = """latitude,longitude,species,observed_behavior,observation_datetime
46.8,-71.2,cerf de virginie,alimentation,2026-02-24T08:30:00Z
47.0,-70.5,ours noir,repos,2026-02-24T14:00:00Z"""
        
        files = {'file': ('test_species_norm.csv', io.BytesIO(csv_content.encode('utf-8')), 'text/csv')}
        response = requests.post(f"{API_PREFIX}/calibration/observations/import", files=files)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data.get("status") == "success", "Expected success"
        assert data.get("imported") == 2, f"Expected 2 imported, got {data.get('imported')}"
        print(f"✓ Species names normalized: cerf de virginie → cerf_de_virginie")

    def test_import_normalizes_behavior_names(self):
        """Import normalizes behavior names (feeding → alimentation)"""
        csv_content = """latitude,longitude,species,observed_behavior,observation_datetime
46.8,-71.2,orignal,feeding,2026-02-24T08:30:00Z
47.0,-70.5,cerf_de_virginie,movement,2026-02-24T14:00:00Z
47.5,-70.0,ours_noir,resting,2026-02-24T18:00:00Z"""
        
        files = {'file': ('test_behavior_norm.csv', io.BytesIO(csv_content.encode('utf-8')), 'text/csv')}
        response = requests.post(f"{API_PREFIX}/calibration/observations/import", files=files)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data.get("status") == "success", "Expected success"
        assert data.get("imported") == 3, f"Expected 3 imported, got {data.get('imported')}"
        print(f"✓ Behavior names normalized: feeding→alimentation, movement→déplacement, resting→repos")

    def test_import_returns_batch_id_and_source_ids(self):
        """Import returns batch_id and source_ids for traceability"""
        csv_content = """latitude,longitude,species,observed_behavior,observation_datetime
46.8,-71.2,orignal,alimentation,2026-02-24T08:30:00Z"""
        
        files = {'file': ('test_traceability.csv', io.BytesIO(csv_content.encode('utf-8')), 'text/csv')}
        response = requests.post(f"{API_PREFIX}/calibration/observations/import", files=files)
        
        data = response.json()
        
        assert "batch_id" in data, "Missing batch_id"
        assert data["batch_id"].startswith("BATCH-"), f"batch_id should start with BATCH-, got {data['batch_id']}"
        
        assert "source_ids" in data, "Missing source_ids"
        source_ids = data["source_ids"]
        assert len(source_ids) >= 1, "Expected at least 1 source_id"
        assert any("SRC-IMPORT" in sid for sid in source_ids), f"Expected SRC-IMPORT in source_ids: {source_ids}"
        print(f"✓ Traceability: batch_id={data['batch_id']}, source_ids={source_ids}")


class TestCSVImportValidation:
    """Tests for import validation and error handling"""

    def test_import_rejects_unsupported_format_txt(self):
        """Import rejects .txt files with 400"""
        content = "latitude,longitude,species,observed_behavior,observation_datetime\n46.8,-71.2,orignal,alimentation,2026-02-24T08:30:00Z"
        files = {'file': ('test.txt', io.BytesIO(content.encode('utf-8')), 'text/plain')}
        response = requests.post(f"{API_PREFIX}/calibration/observations/import", files=files)
        
        assert response.status_code == 400, f"Expected 400 for .txt, got {response.status_code}"
        print(f"✓ .txt file rejected with 400")

    def test_import_rejects_unsupported_format_json(self):
        """Import rejects .json files with 400"""
        content = '{"test": "data"}'
        files = {'file': ('test.json', io.BytesIO(content.encode('utf-8')), 'application/json')}
        response = requests.post(f"{API_PREFIX}/calibration/observations/import", files=files)
        
        assert response.status_code == 400, f"Expected 400 for .json, got {response.status_code}"
        print(f"✓ .json file rejected with 400")

    def test_import_rejects_unsupported_format_pdf(self):
        """Import rejects .pdf files with 400"""
        content = b"%PDF-1.4 fake pdf content"
        files = {'file': ('test.pdf', io.BytesIO(content), 'application/pdf')}
        response = requests.post(f"{API_PREFIX}/calibration/observations/import", files=files)
        
        assert response.status_code == 400, f"Expected 400 for .pdf, got {response.status_code}"
        print(f"✓ .pdf file rejected with 400")

    def test_import_reports_missing_required_columns(self):
        """Import reports error when required columns are missing"""
        # Missing observation_datetime
        csv_content = """latitude,longitude,species,observed_behavior
46.8,-71.2,orignal,alimentation"""
        
        files = {'file': ('test_missing_cols.csv', io.BytesIO(csv_content.encode('utf-8')), 'text/csv')}
        response = requests.post(f"{API_PREFIX}/calibration/observations/import", files=files)
        
        assert response.status_code == 200, f"Expected 200 with error status, got {response.status_code}"
        data = response.json()
        
        assert data.get("status") == "error" or data.get("imported") == 0, f"Expected error or 0 imported: {data}"
        assert len(data.get("errors", [])) > 0, "Expected errors list"
        print(f"✓ Missing columns error reported: {data.get('errors', [])[:2]}")

    def test_import_reports_invalid_latitude(self):
        """Import reports error for invalid latitude values"""
        csv_content = """latitude,longitude,species,observed_behavior,observation_datetime
999,-71.2,orignal,alimentation,2026-02-24T08:30:00Z
46.8,-71.2,orignal,repos,2026-02-24T10:00:00Z"""
        
        files = {'file': ('test_invalid_lat.csv', io.BytesIO(csv_content.encode('utf-8')), 'text/csv')}
        response = requests.post(f"{API_PREFIX}/calibration/observations/import", files=files)
        
        data = response.json()
        
        # Should import valid row, report error for invalid
        assert data.get("imported") == 1, f"Expected 1 valid import, got {data.get('imported')}"
        assert data.get("errors_count", 0) >= 1, "Expected at least 1 error"
        print(f"✓ Invalid latitude error reported, valid rows imported: {data.get('imported')}")

    def test_import_reports_invalid_longitude(self):
        """Import reports error for invalid longitude values"""
        csv_content = """latitude,longitude,species,observed_behavior,observation_datetime
46.8,-999,orignal,alimentation,2026-02-24T08:30:00Z
46.8,-71.2,orignal,repos,2026-02-24T10:00:00Z"""
        
        files = {'file': ('test_invalid_lng.csv', io.BytesIO(csv_content.encode('utf-8')), 'text/csv')}
        response = requests.post(f"{API_PREFIX}/calibration/observations/import", files=files)
        
        data = response.json()
        
        assert data.get("imported") == 1, f"Expected 1 valid import, got {data.get('imported')}"
        assert data.get("errors_count", 0) >= 1, "Expected at least 1 error"
        print(f"✓ Invalid longitude error reported, valid rows imported: {data.get('imported')}")

    def test_import_reports_invalid_datetime(self):
        """Import reports error for invalid datetime values"""
        csv_content = """latitude,longitude,species,observed_behavior,observation_datetime
46.8,-71.2,orignal,alimentation,not-a-date
46.8,-71.2,orignal,repos,2026-02-24T10:00:00Z"""
        
        files = {'file': ('test_invalid_dt.csv', io.BytesIO(csv_content.encode('utf-8')), 'text/csv')}
        response = requests.post(f"{API_PREFIX}/calibration/observations/import", files=files)
        
        data = response.json()
        
        assert data.get("imported") == 1, f"Expected 1 valid import, got {data.get('imported')}"
        assert data.get("errors_count", 0) >= 1, "Expected at least 1 error"
        print(f"✓ Invalid datetime error reported, valid rows imported: {data.get('imported')}")

    def test_import_imports_valid_rows_and_reports_errors(self):
        """Import imports valid rows while reporting errors for invalid ones"""
        csv_content = """latitude,longitude,species,observed_behavior,observation_datetime
46.8,-71.2,orignal,alimentation,2026-02-24T08:30:00Z
INVALID,-71.2,orignal,repos,2026-02-24T10:00:00Z
47.0,-70.5,cerf_de_virginie,déplacement,2026-02-24T14:00:00Z
46.5,INVALID,ours_noir,fuite,2026-02-24T16:00:00Z"""
        
        files = {'file': ('test_mixed.csv', io.BytesIO(csv_content.encode('utf-8')), 'text/csv')}
        response = requests.post(f"{API_PREFIX}/calibration/observations/import", files=files)
        
        data = response.json()
        
        assert data.get("status") == "success", f"Expected success, got {data.get('status')}"
        assert data.get("imported") == 2, f"Expected 2 valid imports, got {data.get('imported')}"
        assert data.get("errors_count", 0) == 2, f"Expected 2 errors, got {data.get('errors_count')}"
        print(f"✓ Mixed import: {data.get('imported')} valid, {data.get('errors_count')} errors")


class TestExcelImport:
    """Tests for Excel (.xlsx) file import"""

    def test_import_xlsx_file(self):
        """Import valid Excel file"""
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not installed")
        
        # Create a simple Excel file in memory
        wb = openpyxl.Workbook()
        ws = wb.active
        
        # Headers
        ws.append(["latitude", "longitude", "species", "observed_behavior", "observation_datetime", "region", "notes"])
        # Data
        ws.append([46.8139, -71.2080, "orignal", "alimentation", "2026-02-24T08:30:00Z", "CA-QC", "Excel test row 1"])
        ws.append([47.1000, -70.5000, "cerf_de_virginie", "repos", "2026-02-24T14:00:00Z", "CA-QC", "Excel test row 2"])
        
        # Save to bytes
        excel_buffer = io.BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)
        
        files = {'file': ('test_import.xlsx', excel_buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        response = requests.post(f"{API_PREFIX}/calibration/observations/import", files=files)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("status") == "success", f"Expected success, got {data.get('status')}"
        assert data.get("imported") >= 1, f"Expected at least 1 imported from Excel"
        assert data.get("format") == "xlsx", f"Expected format=xlsx, got {data.get('format')}"
        print(f"✓ Excel (.xlsx) imported: {data.get('imported')} rows")

    def test_import_xlsx_with_french_columns(self):
        """Import Excel file with French column names"""
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not installed")
        
        wb = openpyxl.Workbook()
        ws = wb.active
        
        # French headers
        ws.append(["lat", "longitude", "espèce", "comportement", "date", "région", "notes"])
        ws.append([46.8, -71.2, "orignal", "alimentation", "2026-02-24T08:30:00Z", "CA-QC", "Excel FR test"])
        
        excel_buffer = io.BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)
        
        files = {'file': ('test_fr.xlsx', excel_buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        response = requests.post(f"{API_PREFIX}/calibration/observations/import", files=files)
        
        data = response.json()
        
        assert data.get("status") == "success", f"Expected success, got {data.get('status')}: {data}"
        assert data.get("imported") >= 1, "Expected at least 1 imported"
        print(f"✓ Excel with French columns imported: {data.get('imported')} rows")


class TestNonRegressionObservations:
    """Non-regression tests for existing observations endpoints"""

    def test_create_observation_still_works(self):
        """POST /calibration/observations still works"""
        payload = {
            "latitude": 46.8139,
            "longitude": -71.2080,
            "species": "orignal",
            "observed_behavior": "alimentation",
            "observation_datetime": "2026-02-24T08:30:00Z",
            "region": "CA-QC",
            "notes": "Non-regression test observation",
            "confidence": 0.9
        }
        
        response = requests.post(
            f"{API_PREFIX}/calibration/observations",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("status") == "created", f"Expected status=created, got {data.get('status')}"
        assert "observation" in data, "Missing observation in response"
        
        obs = data["observation"]
        assert obs.get("species") == "orignal", f"Expected species=orignal, got {obs.get('species')}"
        
        # Clean up
        if obs.get("observation_id"):
            requests.delete(f"{API_PREFIX}/calibration/observations/{obs['observation_id']}")
        
        print(f"✓ POST /calibration/observations works (non-regression)")

    def test_list_observations_still_works(self):
        """GET /calibration/observations still works"""
        response = requests.get(f"{API_PREFIX}/calibration/observations?limit=10")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "observations" in data, "Missing observations in response"
        assert "total" in data, "Missing total in response"
        assert isinstance(data["observations"], list), "observations should be a list"
        print(f"✓ GET /calibration/observations works: {data.get('total')} total observations")

    def test_get_observation_by_id_still_works(self):
        """GET /calibration/observations/{id} still works"""
        # First get a list to find an existing ID
        list_response = requests.get(f"{API_PREFIX}/calibration/observations?limit=1")
        list_data = list_response.json()
        
        if list_data.get("total", 0) == 0:
            pytest.skip("No observations to test")
        
        obs_id = list_data["observations"][0]["observation_id"]
        
        response = requests.get(f"{API_PREFIX}/calibration/observations/{obs_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data.get("observation_id") == obs_id, f"Expected observation_id={obs_id}"
        print(f"✓ GET /calibration/observations/{{id}} works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
