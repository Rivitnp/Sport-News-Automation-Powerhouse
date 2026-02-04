# Next Steps - Fix Article Publishing Issue

## What I Just Fixed

### 1. Enhanced Error Logging
- Added detailed WordPress API error messages in `api_clients.py`
- Now shows exact HTTP status codes (401, 403, etc.)
- Logs full error responses for debugging

### 2. Improved Article Filtering Logs
- Added detailed logging in `news_bot.py` to show:
  - How many articles fetched vs filtered
  - Why articles are being skipped
  - Content length when insufficient
  - Priority scores for each article

### 3. Fixed 1xbet Branding
- Updated `config.py` to use `1xbet.com` instead of generic placeholder
- All articles will now mention 1xbet.com in betting sections

### 4. Created Diagnostic Tools
- **`diagnose.py`** - Comprehensive testing script
- **`TROUBLESHOOTING.md`** - Complete troubleshooting guide

## What You Need To Do NOW

### Step 1: Run Local Diagnostic (CRITICAL)

```bash
# Make sure .env file has your real credentials
python3 diagnose.py
```

This will tell you EXACTLY what's wrong:
- ✅ If WordPress authentication works
- ✅ If user has publish_posts permission  
- ✅ If RSS feeds return cricket/football articles
- ✅ If APIs are working

### Step 2: Fix Issues Found

**If WordPress test FAILS:**
1. Go to WordPress Admin → Users → Your Profile
2. Scroll to "Application Passwords"
3. Delete old password, create NEW one
4. Copy the new password immediately
5. Update `.env` file: `WP_APP_PASSWORD=new_password_here`
6. Run `python3 diagnose.py` again to verify

**If RSS feeds return 0 priority articles:**
- This means ESPN/Cricbuzz aren't showing cricket/football right now
- Wait a few hours and try again
- Or adjust priority scoring in `config.py`

**If articles have insufficient content:**
- RSS summaries are too short
- Scraping is being blocked
- Solution: Reduce minimum length (see TROUBLESHOOTING.md)

### Step 3: Test Locally

```bash
# Once diagnose.py passes all tests, run the actual bot
python3 news_bot.py
```

Watch the output:
- Should say "Found X new articles"
- Should say "Processing (Priority X): [title]"
- Should say "Created post ID: X at https://..."
- Should say "Completed: X/10 articles published"

### Step 4: Update GitHub Secrets

Once local testing works, update GitHub Secrets:

1. Go to: https://github.com/Rivitnp/Sport-News-Automation-Powerhouse/settings/secrets/actions

2. Update these secrets (if you changed them):
   - `WP_APP_PASSWORD` - NEW app password from WordPress
   - `WP_URL` - Make sure no trailing slash
   - `WP_USERNAME` - Exact username from WordPress

3. Verify all 9 secrets are set:
   ```
   ✅ SERPER_KEY_MAIN
   ✅ SERPER_KEY_BACKUP
   ✅ OPENROUTER_API_KEY
   ✅ WP_URL
   ✅ WP_USERNAME
   ✅ WP_APP_PASSWORD
   ✅ CLOUDFLARE_ACCOUNT_ID
   ✅ CLOUDFLARE_TOKEN
   ✅ GA_MEASUREMENT_ID
   ```

### Step 5: Push Changes to GitHub

```bash
git add .
git commit -m "Enhanced logging and fixed 1xbet branding"
git push origin main
```

### Step 6: Run GitHub Actions Workflow

1. Go to: https://github.com/Rivitnp/Sport-News-Automation-Powerhouse/actions
2. Click "Nepal Sports News Automation"
3. Click "Run workflow" → "Run workflow"
4. Wait for it to complete
5. Check the logs in "Run news bot" step

### Step 7: Check Logs for Issues

Look for these messages in GitHub Actions logs:

**✅ SUCCESS indicators:**
```
Environment validation passed
Found 10 new articles
RSS Summary: 50 total, 20 filtered, 30 priority articles
Processing (Priority 10): [article title]
Created post ID: 123 at https://yoursite.com/...
Completed: 10/10 articles published
```

**❌ FAILURE indicators:**
```
WordPress API Error: 401
→ Fix: Regenerate app password

WordPress API Error: 403  
→ Fix: User needs publish_posts permission

Insufficient content (45 chars), skipping
→ Fix: Reduce minimum content length

Found 0 new articles
→ Fix: Wait for new RSS content or adjust filtering
```

## Most Likely Issues (Based on Symptoms)

Since the workflow ran but published 0 articles, here are the most likely causes:

### Issue #1: WordPress Authentication Failed (80% likely)
**Symptoms:** HTTP 401 or 403 errors in logs

**Fix:**
1. Regenerate WordPress app password
2. Update GitHub Secret: `WP_APP_PASSWORD`
3. Verify user is Administrator or Editor

### Issue #2: All Articles Filtered (15% likely)
**Symptoms:** "Found 0 new articles" or "RSS Summary: X total, X filtered, 0 priority"

**Fix:**
1. Check RSS feeds manually - do they have cricket/football?
2. Adjust priority scoring in `config.py`
3. Wait for new content to be published

### Issue #3: Insufficient Content (5% likely)
**Symptoms:** "Insufficient content, skipping" messages

**Fix:**
1. Reduce minimum content length in `news_bot.py`
2. Improve scraping headers
3. Use longer RSS summaries

## Quick Test Commands

```bash
# Test WordPress connection
curl -u "your_username:your_app_password" https://yoursite.com/wp-json/wp/v2/users/me

# Should return your user info, not 401 error

# Test REST API
curl https://yoursite.com/wp-json/wp/v2/posts

# Should return list of posts, not error
```

## Expected Results

After fixing issues, you should see:
- ✅ 10 articles published every 3 hours
- ✅ 80 articles per day (8 runs × 10 articles)
- ✅ Each article has betting tips section
- ✅ 1xbet.com mentioned in every article
- ✅ 18+ disclaimer present
- ✅ Copyright-free AI images from Cloudflare

## Need Help?

1. Run `python3 diagnose.py` and share the output
2. Check GitHub Actions logs for error messages
3. Read `TROUBLESHOOTING.md` for detailed solutions
4. Test WordPress credentials with curl commands above

## Summary

**DO THIS NOW:**
1. ✅ Run `python3 diagnose.py`
2. ✅ Fix any ❌ errors it shows
3. ✅ Test locally with `python3 news_bot.py`
4. ✅ Update GitHub Secrets if needed
5. ✅ Push changes to GitHub
6. ✅ Run workflow manually
7. ✅ Check logs for success/failure

The diagnostic script will tell you EXACTLY what's wrong!
