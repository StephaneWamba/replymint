"""Tests for health endpoints"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test basic health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "replymint-backend"


def test_ready_check():
    """Test readiness check endpoint"""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ready", "degraded"]
    assert "timestamp" in data
    assert data["service"] == "replymint-backend"
    assert "environment" in data
    assert "checks" in data


def test_info_endpoint():
    """Test info endpoint"""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "ReplyMint Backend"
    assert data["version"] == "0.1.0"
    assert "environment" in data
    assert "region" in data
    assert "tables" in data
