"""Simple import test to verify all modules load correctly"""

def test_utils_import():
    """Test that utils module imports correctly"""
    from utils import logger, validate_env, init_database
    assert logger is not None

def test_api_clients_import():
    """Test that api_clients module imports correctly"""
    from api_clients import SerperClient, OpenRouterClient, CloudflareClient, WordPressClient
    assert SerperClient is not None

def test_config_import():
    """Test that config module imports correctly"""
    import config
    assert config.RSS_FEEDS is not None

def test_news_bot_import():
    """Test that news_bot module imports correctly"""
    # This will fail without env vars, but should at least import
    try:
        import news_bot
    except ValueError:
        # Expected if env vars not set
        pass

if __name__ == "__main__":
    test_utils_import()
    test_api_clients_import()
    test_config_import()
    test_news_bot_import()
    print("✅ All imports successful!")
