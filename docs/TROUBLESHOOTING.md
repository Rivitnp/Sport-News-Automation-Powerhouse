# Troubleshooting Guide - Why Articles Aren't Publishing

## Quick Diagnosis

Run the diagnostic script locally:
```bash
python3 diagnose.py
```

This will test:
1. ✅ RSS feeds are accessible
2. ✅ WordPress authentication works
3. ✅ User has publish_posts permission
4. ✅ Serper API returns results
5. ✅ OpenRouter API works

## Common Issues

### Issue 1: WordPress Authentication Failed (401)
**Symptoms:** Logs show "Authentication failed" or HTTP 401 errors

**Solutions:**
1. Regenerate WordPress App Password:
   - Go to WordPress Admin → Users → Profile
   - Scroll to "Application Passwords"
   - Create new password (copy it immediately!)
   - Update GitHub Secret: `WP_APP_PASSWORD`

2. Verify credentials:
   ```bash
   # Test locally first
   curl -u "username:app_password" https://yoursite.com/wp-json/wp/v2/users/me
   ```

### Issue 2: Permission Denied (403)
**Symptoms:** Logs show "Permission denied" or HTTP 403 errors

**Solutions:**
1. Check user role in WordPress:
   - User must be Administrator or Editor
   - Must have `publish_posts` capability

2. Verify with diagnostic script:
   ```bash
   python3 diagnose.py
   # Look for "User has 'publish_posts' permission"
   ```

### Issue 3: No Articles Found (0 published)
**Symptoms:** Workflow runs but publishes 0/10 articles

**Possible Causes:**

**A) RSS feeds returning low-priority content**
- ESPN RSS might have American football instead of cricket
- Solution: Check RSS feeds manually or adjust priority scoring

**B) Articles filtered due to insufficient content**
- RSS summaries too short (<100 chars)
- Scraping fails with 403 Forbidden
- Solution: Improve scraping or use longer summaries

**C) All articles already processed (duplicates)**
- Database cache marks them as seen
- Solution: Clear cache or wait for new articles

### Issue 4: Scraping Fails (403 Forbidden)
**Symptoms:** Logs show "Could not scrape" or "Using RSS summary as fallback"

**Solutions:**
1. ESPN Cricinfo blocks bots - this is expected
2. Bot falls back to RSS summary automatically
3. If summaries too short, articles get skipped

**Workaround:** Adjust minimum content length in `news_bot.py`:
```python
if len(full_content) < 50:  # Reduced from 100
```

### Issue 5: Serper Returns 0 Results
**Symptoms:** Logs show "Serper returned 0 priority articles"

**Solutions:**
1. Check Serper API key is valid
2. Query might be too specific
3. Try broader queries in `config.py`

## Checking GitHub Actions Logs

1. Go to: https://github.com/Rivitnp/Sport-News-Automation-Powerhouse/actions
2. Click latest workflow run
3. Click "Run news bot" step
4. Look for these key log messages:

```
✅ Good signs:
- "Environment validation passed"
- "Found X new articles"
- "Created post ID: 123 at https://..."
- "Completed: 10/10 articles published"

❌ Problem signs:
- "WordPress API Error: 401" → Wrong credentials
- "WordPress API Error: 403" → No permission
- "Insufficient content, skipping" → RSS content too short
- "Found 0 new articles" → No priority articles or all duplicates
- "Serper returned 0 priority articles" → API issue or filtering too aggressive
```

## Testing Locally Before GitHub

**ALWAYS test locally first:**

1. Copy `.env.example` to `.env`
2. Fill in your actual API keys
3. Run diagnostic:
   ```bash
   python3 diagnose.py
   ```
4. If all tests pass, run the bot:
   ```bash
   python3 news_bot.py
   ```
5. Check if articles publish to WordPress
6. Only then update GitHub Secrets

## GitHub Secrets Checklist

Verify all secrets are set correctly:

```
Required:
✅ SERPER_KEY_MAIN
✅ SERPER_KEY_BACKUP
✅ OPENROUTER_API_KEY
✅ WP_URL (no trailing slash!)
✅ WP_USERNAME
✅ WP_APP_PASSWORD (not regular password!)
✅ CLOUDFLARE_ACCOUNT_ID
✅ CLOUDFLARE_TOKEN
✅ GA_MEASUREMENT_ID

Optional:
- OPENROUTER_MODEL (defaults to deepseek/deepseek-v3:free)
```

## Quick Fixes

### Fix 1: Clear Database Cache
If all articles show as duplicates:
```bash
# In GitHub Actions, cache is auto-managed
# To force refresh, go to Actions → Caches → Delete "news-db-*"
```

### Fix 2: Reduce Content Requirements
Edit `news_bot.py` line ~270:
```python
# Before:
if len(full_content) < 100:

# After (more lenient):
if len(full_content) < 50:
```

### Fix 3: Adjust Priority Scoring
Edit `config.py` to be less strict:
```python
PRIORITY_SPORTS = {
    'cricket': 10,
    'football': 9,
    'soccer': 9,
    'ipl': 10,
    'ucl': 9,
    'premier league': 9,
    'american football': 1,  # Keep low
    'nfl': 1  # Keep low
}
```

### Fix 4: Test WordPress Connection
```bash
# Test REST API
curl https://yoursite.com/wp-json/wp/v2/posts

# Test authentication
curl -u "username:app_password" https://yoursite.com/wp-json/wp/v2/users/me

# Should return your user info, not 401 error
```

## Getting Help

If issues persist:

1. Run `python3 diagnose.py` and share output
2. Check GitHub Actions logs for exact error messages
3. Verify WordPress REST API is enabled
4. Test credentials manually with curl commands above
5. Check WordPress error logs in hosting panel

## Most Likely Issue

Based on the symptoms (workflow runs but 0 articles published), the most likely causes are:

1. **WordPress authentication failing** (401/403 errors)
   - Fix: Regenerate app password
   
2. **Articles skipped due to insufficient content**
   - Fix: Reduce minimum content length or improve scraping
   
3. **All articles filtered as low priority**
   - Fix: Check RSS feeds have cricket/football content

Run `python3 diagnose.py` to identify which one!
