import pytest
from pydantic import ValidationError
from src.config import Settings

def test_settings_missing_api_key(monkeypatch):
    # Ensure ANTHROPIC_API_KEY is not set
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    # Pydantic v2 Settings will raise ValidationError on missing required fields
    with pytest.raises(ValidationError):
        Settings(_env_file=None)

def test_settings_valid_load(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-12345")
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    s = Settings(_env_file=None)
    assert s.anthropic_api_key == "test-key-12345"
    assert s.environment == "testing"
    assert s.log_level == "DEBUG"
