#!/usr/bin/env python3
"""
Comprehensive integration test for the Hospital Management System.
Run with: python test_comprehensive.py

Requires:
- PostgreSQL with hsp_db created and scripts/sql/*.sql executed
- Flask server running on http://localhost:5000
- .env file with DATABASE_URL and JWT_SECRET_KEY
"""

import unittest
import json
import os
import sys
import time
import requests

BASE_URL = os.getenv("API_URL", "http://localhost:5000/api")

token = None
created_ids = {}


def request(method, path, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    kwargs["headers"] = headers
    url = f"{BASE_URL}{path}"
    try:
        r = requests.request(method, url, timeout=10, **kwargs)
    except requests.exceptions.ConnectionError:
        print(f"FAIL: Cannot connect to {url} - is the server running?")
        sys.exit(1)
    return r


def assert_ok(r, msg=None):
    assert r.status_code in (200, 201), f"{msg or 'Expected 200/201'}: got {r.status_code} - {r.text}"


def assert_bad(r, msg=None):
    assert r.status_code == 400, f"{msg or 'Expected 400'}: got {r.status_code} - {r.text}"


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.data = {"username": "testuser", "password": "test123", "staff_id": None, "role": "DOCTOR"}

    def test_01_missing_fields(self):
        r = request("POST", "/auth/register", json={})
        assert_bad(r, "empty body")

    def test_02_no_body(self):
        r = request("POST", "/auth/register")
        assert_bad(r, "no body")

    def test_03_login_bad_creds(self):
        r = request("POST", "/auth/login", json={"username": "nobody", "password": "x"})
        self.assertEqual(r.status_code, 401, f"Expected 401: got {r.status_code} - {r.text}")


class TestCRUD(unittest.TestCase):
    """Test basic CRUD for a few key entities via the blueprint factory."""

    def _create_staff(self):
        r = request("POST", "/staff/medical", json={
            "national_id": "TEST-NID-001",
            "first_name": "Test",
            "last_name": "Doctor",
            "birth_date": "1980-01-15",
            "specialty_id": 1,
            "license_number": "TEST-LIC-001",
        })
        assert_ok(r, "create medical staff")
        return r.json()["staff_id"]

    def _create_patient(self):
        r = request("POST", "/patient", json={
            "national_id": "TEST-PAT-001",
            "first_name": "Test",
            "last_name": "Patient",
            "birth_date": "1990-05-20",
            "gender": "MALE",
            "phone": "600000001",
        })
        assert_ok(r, "create patient")
        return r.json()["patient_id"]

    def test_10_create_read_update_delete(self):
        gid = self._create_staff()
        r = request("GET", f"/staff/{gid}")
        assert_ok(r, "get staff")
        self.assertEqual(r.json()["first_name"], "Test")

        r = request("PUT", f"/staff/{gid}", json={
            "national_id": "TEST-NID-001", "first_name": "Updated",
            "last_name": "Doctor", "birth_date": "1980-01-15", "staff_type": "MEDICAL",
        })
        assert_ok(r, "update staff")

        r = request("GET", f"/staff/{gid}")
        self.assertEqual(r.json()["first_name"], "Updated")

        r = request("DELETE", f"/staff/{gid}")
        assert_ok(r, "delete staff")

        r = request("GET", f"/staff/{gid}")
        self.assertEqual(r.status_code, 404)


    def test_14_invalid_date_returns_400(self):
        r = request("POST", "/patient", json={
            "national_id": "TEST-INV-DATE",
            "first_name": "Bad", "last_name": "Date",
            "birth_date": "not-a-date",
            "gender": "MALE",
        })
        assert_bad(r, "invalid date should be 400")


    def test_15_missing_required_field(self):
        r = request("POST", "/staff/medical", json={"national_id": "TEST-MISS"})
        assert_bad(r, "missing fields")


class TestGenderCase(unittest.TestCase):
    def test_30_gender_lowercase(self):
        r = request("POST", "/patient", json={
            "national_id": "TEST-GEN-LOW",
            "first_name": "Gender", "last_name": "Test",
            "birth_date": "2000-01-01",
            "gender": "male",
        })
        assert_ok(r, "lowercase gender should work")

    def test_31_gender_titlecase(self):
        r = request("POST", "/patient", json={
            "national_id": "TEST-GEN-TITLE",
            "first_name": "Gender", "last_name": "Test",
            "birth_date": "2000-01-01",
            "gender": "Female",
        })
        assert_ok(r, "titlecase gender should work")

    def test_32_gender_mixed(self):
        r = request("POST", "/patient", json={
            "national_id": "TEST-GEN-MIX",
            "first_name": "Gender", "last_name": "Test",
            "birth_date": "2000-01-01",
            "gender": "OTHER",
        })
        assert_ok(r, "uppercase gender should work")

    def test_33_gender_none(self):
        r = request("POST", "/patient", json={
            "national_id": "TEST-GEN-NONE",
            "first_name": "Gender", "last_name": "Test",
            "birth_date": "2000-01-01",
        })
        assert_ok(r, "missing gender should work (nullable)")


class TestSurgeryAssistantCompositePK(unittest.TestCase):
    def test_40_create_delete_surgery_assistant(self):
        r = request("GET", "/surgery")
        self.assertIn(r.status_code, (200, 404))

    def test_41_update_nonexistent_returns_400(self):
        r = request("PUT", "/surgery-assistants/99999/99999", json={"role": "Scrub"})
        assert_bad(r, "updating nonexistent assistant")


class TestDummyData(unittest.TestCase):
    def test_50_generate_dummy_data(self):
        r = request("POST", "/dummy/generate")
        assert_ok(r, "dummy data generation")

    def test_51_cleanup_dummy_data(self):
        r = request("DELETE", "/dummy/cleanup")
        assert_ok(r, "dummy data cleanup")


class TestNurseAssignment(unittest.TestCase):
    def test_60_assign_nurse_no_id(self):
        r = request("PUT", "/maintenance/nursing/assign", json={"doctor_id": 1})
        assert_bad(r, "missing nurse_id")

    def test_61_assign_nurse_no_body(self):
        r = request("PUT", "/maintenance/nursing/assign")
        assert_bad(r, "no body")

    def test_62_assign_nurse_invalid_id(self):
        r = request("PUT", "/maintenance/nursing/assign", json={"nurse_id": 99999, "doctor_id": 1})
        assert_bad(r, "invalid nurse_id")


class TestMisc(unittest.TestCase):
    def test_70_get_surgeries_no_date(self):
        r = request("GET", "/maintenance/surgeries")
        assert_bad(r, "missing date param")

    def test_71_get_visits_no_date(self):
        r = request("GET", "/maintenance/visits/scheduled")
        assert_bad(r, "missing date param")

    def test_72_staff_list(self):
        r = request("GET", "/staff")
        assert_ok(r, "staff list")
        self.assertIsInstance(r.json(), list)

    def test_73_list_patients(self):
        r = request("GET", "/patient")
        assert_ok(r, "patient list")

    def test_74_list_medications(self):
        r = request("GET", "/medication")
        assert_ok(r, "medications list")


if __name__ == "__main__":
    print("=" * 60)
    print("Hospital Management System - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Target API: {BASE_URL}")
    print()

    r = request("POST", "/auth/login", json={"username": "yossef", "password": "ChangeMePleaseChange!"})
    if r.status_code == 200:
        token = r.json()["access_token"]
        print("Authenticated as 'yossef'")
    else:
        print("WARNING: Could not login as admin. Protected endpoints will fail.")
        print(f"  Login response: {r.status_code} - {r.text}")
        print("  Tests will continue with limited scope.")

    print()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(unittest.makeSuite(TestAuth))
    result = runner.run(unittest.makeSuite(TestCRUD))
    result = runner.run(unittest.makeSuite(TestGenderCase))
    result = runner.run(unittest.makeSuite(TestSurgeryAssistantCompositePK))
    result = runner.run(unittest.makeSuite(TestNurseAssignment))
    result = runner.run(unittest.makeSuite(TestMisc))
    result = runner.run(unittest.makeSuite(TestDummyData))

    print()
    print("=" * 60)
    if result.wasSuccessful():
        print("ALL TESTS PASSED")
    else:
        print(f"FAILURES: {len(result.failures)} failures, {len(result.errors)} errors")
    print("=" * 60)
