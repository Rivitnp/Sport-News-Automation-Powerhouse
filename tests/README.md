# Tests

This folder contains all testing and diagnostic scripts.

## Test Files

### Unit Tests
- **`test_bot.py`** - Unit tests for the news bot
  - Tests RSS feed parsing
  - Tests priority scoring
  - Tests API client initialization
  - Tests content generation
  - Run with: `pytest tests/test_bot.py -v`

### Diagnostic Scripts
- **`diagnose.py`** - Comprehensive diagnostic tool
  - Tests all environment variables
  - Tests WordPress authentication
  - Tests API connections (Serper, OpenRouter, Cloudflare)
  - Tests post creation
  - Run with: `python tests/diagnose.py`

- **`test_local.py`** - Local testing script
  - Similar to diagnose.py but more detailed
  - Creates actual test posts in WordPress (as drafts)
  - Run with: `python tests/test_local.py`

- **`test_imports.py`** - Import verification
  - Tests that all modules can be imported
  - Useful for debugging dependency issues
  - Run with: `python tests/test_imports.py`

## Running Tests

### Before Pushing to GitHub

**ALWAYS run diagnostics locally first:**

```bash
# 1. Set up environment
cp .env.example .env
# Edit .env with your actual API keys

# 2. Run comprehensive diagnostic
python tests/diagnose.py

# 3. If all tests pass, run the actual bot
PYTHONPATH=src python src/news_bot.py

# 4. Run unit tests
pytest tests/test_bot.py -v
```

### In GitHub Actions

Tests run automatically on push/PR via `.github/workflows/test.yml`

## What Each Test Checks

### diagnose.py
✅ Environment variables are set  
✅ Modules can be imported  
✅ WordPress REST API is accessible  
✅ WordPress authentication works  
✅ User has publish_posts permission  
✅ Serper API returns results  
✅ OpenRouter API generates content  
✅ Cloudflare API is configured  
✅ Can create WordPress posts  

### test_bot.py
✅ RSS feeds can be parsed  
✅ Priority scoring works correctly  
✅ API clients initialize properly  
✅ Content generation functions work  
✅ Image optimization works  

### test_local.py
✅ All environment variables present  
✅ WordPress connection successful  
✅ Authentication successful  
✅ Can create draft posts  
✅ All APIs responding  

## Troubleshooting

If tests fail, check:

1. **Environment Variables**
   - All required vars set in `.env`
   - No typos in variable names
   - Values are correct (no trailing spaces)

2. **WordPress Issues**
   - REST API enabled
   - App password generated correctly
   - User has Administrator or Editor role
   - Site is accessible

3. **API Issues**
   - API keys are valid
   - Not rate limited
   - Services are online

4. **Import Errors**
   - All dependencies installed: `pip install -r requirements.txt`
   - Python version 3.11+
   - PYTHONPATH includes src folder

## Common Test Failures

### ImportError: cannot import name 'logger'
```bash
# Fix: Install dependencies
pip install -r requirements.txt

# Or check utils.py has logger defined
```

### WordPress 401 Unauthorized
```bash
# Fix: Regenerate app password
# WordPress Admin → Users → Profile → Application Passwords
```

### WordPress 403 Forbidden
```bash
# Fix: Check user permissions
# User must have 'publish_posts' capability
```

### Serper API Error
```bash
# Fix: Check API key
# Verify at https://serper.dev/dashboard
```

## Test Coverage

Current test coverage focuses on:
- ✅ Core functionality (RSS, filtering, publishing)
- ✅ API integrations
- ✅ Authentication and permissions
- ✅ Error handling

Future improvements:
- ⏳ More edge case testing
- ⏳ Mock API responses
- ⏳ Integration tests
- ⏳ Performance tests

## Running Specific Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_bot.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run diagnostic only
python tests/diagnose.py

# Run local test only
python tests/test_local.py
```

## CI/CD Integration

Tests run automatically in GitHub Actions:
- On every push to main/develop
- On every pull request
- Before deployment

See `.github/workflows/test.yml` for configuration.
