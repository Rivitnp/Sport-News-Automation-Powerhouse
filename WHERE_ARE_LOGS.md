# Where to Find Logs - GitHub Actions

## Quick Access

**Direct link to your workflow runs:**
https://github.com/Rivitnp/Sport-News-Automation-Powerhouse/actions

## Step-by-Step Guide

### 1. Go to Actions Tab
```
https://github.com/Rivitnp/Sport-News-Automation-Powerhouse
→ Click "Actions" tab at top
```

### 2. Find Latest Run
```
You'll see a list of workflow runs:
- ✅ Green checkmark = Success
- ❌ Red X = Failed
- 🟡 Yellow dot = Running
- ⚪ Gray circle = Queued
```

### 3. Click on a Run
```
Click on any run to see details:
- Run name: "Nepal Sports News Automation"
- Triggered by: schedule or workflow_dispatch
- Duration: ~2-5 minutes
```

### 4. View Job Logs
```
Inside the run, you'll see:
- "publish-news" job
- Click on it to expand
```

### 5. Check Each Step
```
Steps shown:
1. Set up job
2. Checkout code
3. Set up Python
4. Install dependencies
5. Cache database
6. Run news bot ← THIS IS WHERE THE LOGS ARE!
7. Post Run actions/cache
8. Complete job
```

### 6. Read "Run news bot" Logs
```
Click "Run news bot" to expand

You'll see output like:
---
INFO - Starting Nepal Sports News Bot
INFO - Found 10 new articles
INFO - Processing (Priority 10): India vs Pakistan...
INFO - Created post ID: 123 at https://...
INFO - Completed: 10/10 articles published
---
```

## What to Look For

### ✅ SUCCESS Logs
```
INFO - Environment validation passed
INFO - Found 10 new articles
INFO - RSS Summary: 50 total, 20 filtered, 30 priority articles
INFO - Processing (Priority 10): [title]
INFO - Generated copyright-free image (245.3KB)
INFO - Uploaded copyright-free featured image
INFO - Created post ID: 123 at https://yoursite.com/...
INFO - Published with betting content: https://...
INFO - Completed: 10/10 articles published
```

### ❌ FAILURE Logs

**WordPress Authentication Failed:**
```
ERROR - WordPress API Error: 401 Unauthorized
ERROR - Authentication failed - check WP_USERNAME and WP_APP_PASSWORD
```
**Fix:** Regenerate app password

**Permission Denied:**
```
ERROR - WordPress API Error: 403 Forbidden
ERROR - Permission denied - user needs 'publish_posts' capability
```
**Fix:** Make user Administrator or Editor

**No Articles Found:**
```
INFO - Found 0 new articles
INFO - No new articles to process
```
**Fix:** Wait for new RSS content or adjust filtering

**Insufficient Content:**
```
WARNING - Insufficient content (45 chars), skipping: [title]
WARNING - Insufficient content (67 chars), skipping: [title]
INFO - Completed: 0/10 articles published
```
**Fix:** Reduce minimum content length

**Scraping Failed:**
```
WARNING - Could not scrape https://...: 403 Forbidden
INFO - Using RSS summary as fallback
```
**Fix:** This is normal, bot uses RSS summary

## Download Logs

### Option 1: View in Browser
- Just click through the steps as shown above
- Logs are displayed in real-time

### Option 2: Download Raw Logs
```
1. Go to workflow run
2. Click "..." (three dots) in top right
3. Click "Download log archive"
4. Extract ZIP file
5. Open "2_Run news bot.txt"
```

## Check Specific Information

### How many articles were published?
```
Search for: "Completed:"
Example: "Completed: 10/10 articles published"
```

### Why were articles skipped?
```
Search for: "skipping" or "WARNING"
Example: "Insufficient content (45 chars), skipping"
```

### WordPress errors?
```
Search for: "WordPress API Error"
Example: "WordPress API Error: 401 Unauthorized"
```

### What articles were processed?
```
Search for: "Processing (Priority"
Example: "Processing (Priority 10): India wins against..."
```

### Were images generated?
```
Search for: "Generated copyright-free image"
Example: "Generated copyright-free image (245.3KB)"
```

## Real-Time Monitoring

### Watch Live Logs
```
1. Go to Actions tab
2. Click on running workflow (yellow dot)
3. Click "publish-news" job
4. Click "Run news bot" step
5. Logs update in real-time!
```

### Manual Trigger
```
1. Go to Actions tab
2. Click "Nepal Sports News Automation"
3. Click "Run workflow" button (right side)
4. Select branch: main
5. Click green "Run workflow" button
6. Wait ~30 seconds, refresh page
7. Click on new run to watch logs
```

## Common Log Patterns

### Pattern 1: Everything Works
```
✅ Environment validation passed
✅ Found 10 new articles
✅ RSS Summary: 50 total, 20 filtered, 30 priority articles
✅ Processing (Priority 10): [title]
✅ Generated copyright-free image
✅ Created post ID: 123
✅ Completed: 10/10 articles published
```

### Pattern 2: WordPress Auth Failed
```
✅ Environment validation passed
✅ Found 10 new articles
✅ Processing (Priority 10): [title]
✅ Generated copyright-free image
❌ WordPress API Error: 401 Unauthorized
❌ Failed to process article
❌ Completed: 0/10 articles published
```

### Pattern 3: No Priority Articles
```
✅ Environment validation passed
✅ RSS Summary: 50 total, 50 filtered, 0 priority articles
❌ Found 0 new articles
❌ No new articles to process
```

### Pattern 4: Insufficient Content
```
✅ Environment validation passed
✅ Found 10 new articles
✅ Processing (Priority 10): [title]
⚠️  Using RSS summary as fallback
❌ Insufficient content (45 chars), skipping
❌ Completed: 0/10 articles published
```

## Quick Debugging

### If you see 0/10 published:
1. Search logs for "WordPress API Error"
   - If found → Fix authentication
2. Search logs for "Insufficient content"
   - If found → Reduce minimum length
3. Search logs for "Found 0 new articles"
   - If found → Wait for new RSS content

### If you see authentication errors:
1. Regenerate WordPress app password
2. Update GitHub Secret: WP_APP_PASSWORD
3. Re-run workflow

### If you see permission errors:
1. Check WordPress user role
2. Must be Administrator or Editor
3. Must have publish_posts capability

## Testing Locally First

**ALWAYS test locally before checking GitHub logs:**

```bash
# Run diagnostic
python3 diagnose.py

# If passes, run bot
python3 news_bot.py

# Watch output in terminal
# Same logs as GitHub Actions!
```

## Summary

**To find logs:**
1. Go to https://github.com/Rivitnp/Sport-News-Automation-Powerhouse/actions
2. Click latest run
3. Click "Run news bot" step
4. Read the output

**To debug:**
1. Search for "ERROR" or "WARNING"
2. Check "Completed: X/10" at the end
3. Follow TROUBLESHOOTING.md for fixes

**To test:**
1. Run `python3 diagnose.py` locally first
2. Fix issues before pushing to GitHub
3. Saves time and API quota!
