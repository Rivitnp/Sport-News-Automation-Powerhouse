# Project Structure

## Overview

The project is now organized into three main folders for better clarity and maintainability:

```
Sport-News-Automation-Powerhouse/
│
├── 📁 src/                     # Source Code (Production)
├── 📁 tests/                   # Testing & Diagnostics
├── 📁 docs/                    # Documentation
├── 📁 .github/workflows/       # GitHub Actions
│
├── 📄 README.md                # Main project documentation
├── 📄 requirements.txt         # Python dependencies
├── 📄 .env.example            # Environment template
├── 📄 .gitignore              # Git ignore rules
└── 📄 PROJECT_STRUCTURE.md    # This file
```

## 📁 src/ - Source Code

**Purpose:** Production code that runs the bot

```
src/
├── news_bot.py         # Main bot script (entry point)
├── api_clients.py      # API integrations (Serper, OpenRouter, Cloudflare, WordPress)
├── config.py           # Configuration settings
├── utils.py            # Helper functions (logging, database, validation)
└── README.md           # Source code documentation
```

**Key Files:**
- **`news_bot.py`** - Orchestrates entire workflow (fetch → filter → generate → publish)
- **`api_clients.py`** - All external API integrations
- **`config.py`** - RSS feeds, priority sports, betting settings
- **`utils.py`** - Logging, environment validation, duplicate detection

**Run Command:**
```bash
PYTHONPATH=src python src/news_bot.py
```

## 📁 tests/ - Testing & Diagnostics

**Purpose:** All testing, diagnostic, and verification scripts

```
tests/
├── test_bot.py         # Unit tests (pytest)
├── diagnose.py         # Comprehensive diagnostic tool
├── test_local.py       # Local testing script
├── test_imports.py     # Import verification
└── README.md           # Testing documentation
```

**Key Files:**
- **`diagnose.py`** - **RUN THIS FIRST!** Tests all APIs and WordPress connection
- **`test_local.py`** - Detailed local testing with WordPress post creation
- **`test_bot.py`** - Unit tests for core functionality
- **`test_imports.py`** - Verifies all modules can be imported

**Run Commands:**
```bash
# Diagnostic (run first!)
python tests/diagnose.py

# Unit tests
pytest tests/test_bot.py -v

# Local test
python tests/test_local.py

# All tests
pytest tests/ -v
```

## 📁 docs/ - Documentation

**Purpose:** All project documentation and guides

```
docs/
├── Setup & Configuration
│   ├── SETUP_GUIDE.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   └── FINAL_SETUP_SUMMARY.md
│
├── Troubleshooting
│   ├── TROUBLESHOOTING.md
│   ├── WHERE_ARE_LOGS.md
│   └── NEXT_STEPS.md
│
├── Features
│   ├── BETTING_FEATURES.md
│   ├── BETTING_IMPROVEMENTS.md
│   ├── IMPROVEMENTS_SUMMARY.md
│   └── TRAFFIC_STRATEGY.md
│
├── Security
│   ├── SECURITY.md
│   ├── SECURITY_SCAN_RESULTS.md
│   └── IMAGE_COPYRIGHT_SAFETY.md
│
└── README.md
```

**Quick Reference:**
- **Having issues?** → `TROUBLESHOOTING.md`
- **Setting up?** → `SETUP_GUIDE.md`
- **What's next?** → `NEXT_STEPS.md`
- **Where are logs?** → `WHERE_ARE_LOGS.md`

## 📁 .github/workflows/ - Automation

**Purpose:** GitHub Actions workflows for automation

```
.github/workflows/
├── news-automation.yml    # Main bot (runs every 3 hours)
└── test.yml              # Tests (runs on push/PR)
```

**Workflows:**
- **`news-automation.yml`** - Publishes 10 articles every 3 hours (80/day)
- **`test.yml`** - Runs unit tests on every push

## 📄 Root Files

```
├── README.md              # Main project documentation
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── .gitignore            # Git ignore rules
└── PROJECT_STRUCTURE.md  # This file
```

## File Organization Rules

### ✅ Source Code (src/)
- Production code only
- No test files
- No documentation
- Must be importable

### ✅ Tests (tests/)
- All test files
- Diagnostic scripts
- Verification tools
- No production code

### ✅ Documentation (docs/)
- All markdown documentation
- Setup guides
- Troubleshooting
- Feature descriptions

### ✅ Root Directory
- Main README
- Configuration files
- Environment templates
- Project metadata

## Import Paths

### From Root Directory
```python
# Set PYTHONPATH
PYTHONPATH=src python src/news_bot.py
```

### In GitHub Actions
```yaml
env:
  PYTHONPATH: ${{ github.workspace }}/src
run: python src/news_bot.py
```

### In Tests
```python
# Tests can import from src/
from api_clients import SerperClient
from config import RSS_FEEDS
from utils import logger
```

## Quick Navigation

### I want to...

**Run the bot locally:**
```bash
PYTHONPATH=src python src/news_bot.py
```

**Test if everything works:**
```bash
python tests/diagnose.py
```

**Fix an issue:**
1. Check `docs/TROUBLESHOOTING.md`
2. Run `python tests/diagnose.py`
3. Check GitHub Actions logs (see `docs/WHERE_ARE_LOGS.md`)

**Understand a feature:**
- Betting: `docs/BETTING_FEATURES.md`
- Security: `docs/SECURITY.md`
- Traffic: `docs/TRAFFIC_STRATEGY.md`

**Set up from scratch:**
1. Read `docs/SETUP_GUIDE.md`
2. Follow `docs/DEPLOYMENT_CHECKLIST.md`
3. Check `docs/NEXT_STEPS.md`

**Modify configuration:**
- Edit `src/config.py`
- RSS feeds, priority sports, betting settings

**Add new features:**
1. Edit files in `src/`
2. Add tests in `tests/`
3. Update docs in `docs/`
4. Update `README.md`

## Benefits of This Structure

### ✅ Clear Separation
- Production code separate from tests
- Documentation separate from code
- Easy to find what you need

### ✅ Better Imports
- Clean import paths
- No circular dependencies
- PYTHONPATH clearly defined

### ✅ Easier Maintenance
- Know where to add new files
- Consistent organization
- Scalable structure

### ✅ Professional
- Industry-standard layout
- Easy for others to understand
- Good for portfolio/resume

## Migration Notes

### Old Structure → New Structure

```
Old                    →  New
─────────────────────────────────────────
news_bot.py           →  src/news_bot.py
api_clients.py        →  src/api_clients.py
config.py             →  src/config.py
utils.py              →  src/utils.py

test_bot.py           →  tests/test_bot.py
diagnose.py           →  tests/diagnose.py
test_local.py         →  tests/test_local.py
test_imports.py       →  tests/test_imports.py

*.md (all docs)       →  docs/*.md
README.md             →  README.md (updated)
```

### What Changed

1. **File Locations** - All files moved to appropriate folders
2. **Import Paths** - Added PYTHONPATH to workflows
3. **Documentation** - Created README in each folder
4. **Main README** - Completely rewritten with new structure

### What Stayed the Same

1. **Functionality** - Bot works exactly the same
2. **Configuration** - Same settings in config.py
3. **Environment** - Same .env variables
4. **Workflows** - Same schedule (every 3 hours)

## Summary

**Before:** All files mixed together in root directory
**After:** Organized into src/, tests/, docs/ folders

**Benefits:**
- ✅ Easier to navigate
- ✅ Clearer purpose of each file
- ✅ Professional structure
- ✅ Better for future maintenance

**Next Steps:**
1. Run `python tests/diagnose.py` to verify everything works
2. Check `docs/NEXT_STEPS.md` for what to do next
3. Read `README.md` for project overview
