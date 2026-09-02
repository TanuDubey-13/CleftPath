from app.core.config import settings


def test_settings_load_defaults():
    assert settings.PROJECT_NAME == "CleftPath"
    assert settings.TAGLINE == "Every journey deserves a path forward."
    assert settings.API_V1_STR == "/api/v1"
    assert "http://localhost:5173" in settings.CORS_ORIGINS
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 15
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7


def test_settings_cors_assembly():
    from app.core.config import Settings
    
    # Test comma-separated string
    s1 = Settings(CORS_ORIGINS="http://test.com, http://example.com")
    assert s1.CORS_ORIGINS == ["http://test.com", "http://example.com"]
    
    # Test JSON list string
    s2 = Settings(CORS_ORIGINS='["http://test.com", "http://example.com"]')
    assert s2.CORS_ORIGINS == ["http://test.com", "http://example.com"]
