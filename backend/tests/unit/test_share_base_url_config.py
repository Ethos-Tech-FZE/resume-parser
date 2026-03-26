"""
Unit tests for SHARE_BASE_URL configuration property.

These tests validate the share_base_url property implementation
including the fallback logic to allowed_origins_list[0].

Test Strategy: TDD Red-Green-Refactor
- Red: Write failing tests first
- Green: Implement minimum code to pass
- Refactor: Improve implementation while tests pass
"""
import pytest
from app.core.config import Settings, clear_settings_cache


class TestShareBaseURLProperty:
    """Test share_base_url property with fallback logic."""

    def test_explicit_share_base_url_is_used(self, monkeypatch):
        """Test that explicit SHARE_BASE_URL is returned when set."""
        # Arrange: Set explicit SHARE_BASE_URL
        monkeypatch.setenv("SHARE_BASE_URL", "https://explicit-frontend.vercel.app")
        monkeypatch.setenv("ALLOWED_ORIGINS", "https://first.vercel.app,https://second.vercel.app")
        clear_settings_cache()
        
        # Act
        settings = Settings()
        
        # Assert: Should use explicit SHARE_BASE_URL, not ALLOWED_ORIGINS[0]
        assert settings.share_base_url == "https://explicit-frontend.vercel.app"
        assert settings.share_base_url != "https://first.vercel.app"

    def test_fallback_to_first_allowed_origin_when_empty(self, monkeypatch):
        """Test fallback to allowed_origins_list[0] when SHARE_BASE_URL is empty string."""
        # Arrange: Set SHARE_BASE_URL to empty string
        monkeypatch.setenv("SHARE_BASE_URL", "")
        monkeypatch.setenv("ALLOWED_ORIGINS", "https://first-origin.vercel.app,https://second-origin.vercel.app")
        clear_settings_cache()
        
        # Act
        settings = Settings()
        
        # Assert: Should fall back to first allowed origin
        assert settings.share_base_url == "https://first-origin.vercel.app"

    def test_fallback_to_first_allowed_origin_when_not_set(self, monkeypatch):
        """Test fallback to allowed_origins_list[0] when SHARE_BASE_URL is not set."""
        # Arrange: Don't set SHARE_BASE_URL at all
        monkeypatch.delenv("SHARE_BASE_URL", raising=False)
        monkeypatch.setenv("ALLOWED_ORIGINS", "https://fallback-origin.vercel.app,https://another.vercel.app")
        clear_settings_cache()
        
        # Act
        settings = Settings()
        
        # Assert: Should fall back to first allowed origin
        assert settings.share_base_url == "https://fallback-origin.vercel.app"

    def test_fallback_to_localhost_when_no_origins(self, monkeypatch):
        """Test fallback to localhost when both SHARE_BASE_URL and ALLOWED_ORIGINS are empty."""
        # Arrange: Empty everything
        monkeypatch.setenv("SHARE_BASE_URL", "")
        monkeypatch.setenv("ALLOWED_ORIGINS", "")
        clear_settings_cache()
        
        # Act
        settings = Settings()
        
        # Assert: Should fall back to localhost
        assert settings.share_base_url == "http://localhost:3000"

    def test_whitespace_handling_in_allowed_origins(self, monkeypatch):
        """Test that whitespace is properly handled in ALLOWED_ORIGINS."""
        # Arrange: ALLOWED_ORIGINS with extra whitespace
        monkeypatch.setenv("SHARE_BASE_URL", "")
        monkeypatch.setenv("ALLOWED_ORIGINS", "  https://spacy-origin.vercel.app  ,  https://another.vercel.app  ")
        clear_settings_cache()
        
        # Act
        settings = Settings()
        
        # Assert: Should strip whitespace and use first origin
        assert settings.share_base_url == "https://spacy-origin.vercel.app"

    def test_multiple_origins_uses_first_one(self, monkeypatch):
        """Test that when multiple origins exist, first one is used for fallback."""
        # Arrange: Multiple origins in specific order
        monkeypatch.setenv("SHARE_BASE_URL", "")
        monkeypatch.setenv(
            "ALLOWED_ORIGINS",
            "https://production.vercel.app,https://staging.vercel.app,https://dev.vercel.app"
        )
        clear_settings_cache()
        
        # Act
        settings = Settings()
        
        # Assert: Should use first origin (production)
        assert settings.share_base_url == "https://production.vercel.app"

    def test_real_world_scenario_correct_domain_first(self, monkeypatch):
        """Test real-world scenario: correct domain first in ALLOWED_ORIGINS."""
        # Arrange: Real-world configuration with correct domain first
        monkeypatch.setenv("SHARE_BASE_URL", "")
        monkeypatch.setenv(
            "ALLOWED_ORIGINS",
            "https://resumate-frontend-three.vercel.app,https://resumate-backend.onrender.com"
        )
        clear_settings_cache()
        
        # Act
        settings = Settings()
        
        # Assert: Should use correct production domain
        assert settings.share_base_url == "https://resumate-frontend-three.vercel.app"

    def test_real_world_scenario_old_domain_first(self, monkeypatch):
        """Test real-world scenario: old domain first (current problem)."""
        # Arrange: Current problematic configuration
        monkeypatch.setenv("SHARE_BASE_URL", "")
        monkeypatch.setenv(
            "ALLOWED_ORIGINS",
            "https://resumate-frontend.vercel.app,https://resumate-backend.onrender.com,https://resumate-frontend-three.vercel.app"
        )
        clear_settings_cache()
        
        # Act
        settings = Settings()
        
        # Assert: Demonstrates the problem - uses old domain
        # This test documents why we need explicit SHARE_BASE_URL
        assert settings.share_base_url == "https://resumate-frontend.vercel.app"

    def test_explicit_overrides_old_domain_problem(self, monkeypatch):
        """Test that explicit SHARE_BASE_URL solves the old domain problem."""
        # Arrange: Old configuration but with explicit SHARE_BASE_URL
        monkeypatch.setenv("SHARE_BASE_URL", "https://resumate-frontend-three.vercel.app")
        monkeypatch.setenv(
            "ALLOWED_ORIGINS",
            "https://resumate-frontend.vercel.app,https://resumate-backend.onrender.com"
        )
        clear_settings_cache()
        
        # Act
        settings = Settings()
        
        # Assert: Should use explicit value, not old domain
        assert settings.share_base_url == "https://resumate-frontend-three.vercel.app"
        assert settings.share_base_url != "https://resumate-frontend.vercel.app"
