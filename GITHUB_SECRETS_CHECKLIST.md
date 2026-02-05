# GitHub Secrets Checklist

**Date**: February 5, 2026  
**Purpose**: Update GitHub repository secrets for the Nepal Sports News Bot

---

## Current Secrets in GitHub Actions

Based on `.github/workflows/news-automation.yml`, you currently have these secrets configured:

### ✅ Already Configured (From Previous Setup)
1. `SERPER_KEY_MAIN` - Main Serper API key for Google Search
2. `SERPER_KEY_BACKUP` - Backup Serper API key (optional)
3. `OPENROUTER_API_KEY` - OpenRouter API key for Claude 3.5 Sonnet
4. `OPENROUTER_MODEL` - Model name (deepseek/deepseek-chat or anthropic/claude-3.5-sonnet)
5. `CLOUDFLARE_ACCOUNT_ID` - Cloudflare account ID for image generation
6. `CLOUDFLARE_TOKEN` - Cloudflare API token
7. `WP_URL` - WordPress site URL (https://1xbatnepal.com)
8. `WP_USERNAME` - WordPress username
9. `WP_APP_PASSWORD` - WordPress application password
10. `GA_MEASUREMENT_ID` - Google Analytics measurement ID (optional)

---

## 🚨 NEW SECRET REQUIRED

### ❌ Missing (Needs to be Added)
**`APIFREE_API_KEY`** - APIFree.ai API key for image generation

**Why it's needed**:
- APIFree.ai is now the PRIMARY image generator (fast, cheap, high quality)
- Cloudflare is the FALLBACK (free but slower)
- Cost: $0.004 per image (vs Cloudflare free but limited)

**How to get it**:
1. Go to https://apifree.ai/api-keys
2. Sign up / Log in
3. Create a new API key
4. Copy the key

---

## How to Add GitHub Secrets

### Step 1: Go to Repository Settings
1. Open your GitHub repository
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions** (left sidebar)

### Step 2: Add New Secret
1. Click **New repository secret**
2. Name: `APIFREE_API_KEY`
3. Value: Paste your APIFree.ai API key
4. Click **Add secret**

---

## Updated GitHub Actions Workflow

The workflow file needs to be updated to include the new secret. Here's what needs to be added:

### Current (Missing APIFREE_API_KEY)
```yaml
- name: Run news bot
  env:
    SERPER_KEY_MAIN: ${{ secrets.SERPER_KEY_MAIN }}
    SERPER_KEY_BACKUP: ${{ secrets.SERPER_KEY_BACKUP }}
    OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
    OPENROUTER_MODEL: ${{ secrets.OPENROUTER_MODEL }}
    CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
    CLOUDFLARE_TOKEN: ${{ secrets.CLOUDFLARE_TOKEN }}
    WP_URL: ${{ secrets.WP_URL }}
    WP_USERNAME: ${{ secrets.WP_USERNAME }}
    WP_APP_PASSWORD: ${{ secrets.WP_APP_PASSWORD }}
    GA_MEASUREMENT_ID: ${{ secrets.GA_MEASUREMENT_ID }}
```

### Updated (With APIFREE_API_KEY)
```yaml
- name: Run news bot
  env:
    SERPER_KEY_MAIN: ${{ secrets.SERPER_KEY_MAIN }}
    SERPER_KEY_BACKUP: ${{ secrets.SERPER_KEY_BACKUP }}
    OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
    OPENROUTER_MODEL: ${{ secrets.OPENROUTER_MODEL }}
    APIFREE_API_KEY: ${{ secrets.APIFREE_API_KEY }}  # ← ADD THIS LINE
    CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
    CLOUDFLARE_TOKEN: ${{ secrets.CLOUDFLARE_TOKEN }}
    WP_URL: ${{ secrets.WP_URL }}
    WP_USERNAME: ${{ secrets.WP_USERNAME }}
    WP_APP_PASSWORD: ${{ secrets.WP_APP_PASSWORD }}
    GA_MEASUREMENT_ID: ${{ secrets.GA_MEASUREMENT_ID }}
```

---

## Complete Secrets List (After Update)

### Required Secrets (Must Have)
1. ✅ `SERPER_KEY_MAIN` - Google Search API
2. ✅ `OPENROUTER_API_KEY` - Claude 3.5 Sonnet API
3. ✅ `WP_URL` - WordPress site URL
4. ✅ `WP_USERNAME` - WordPress username
5. ✅ `WP_APP_PASSWORD` - WordPress app password
6. ❌ `APIFREE_API_KEY` - **NEEDS TO BE ADDED**

### Optional Secrets (Recommended)
7. ✅ `SERPER_KEY_BACKUP` - Backup search API key
8. ✅ `CLOUDFLARE_ACCOUNT_ID` - Fallback image generation
9. ✅ `CLOUDFLARE_TOKEN` - Fallback image generation
10. ✅ `GA_MEASUREMENT_ID` - Google Analytics tracking
11. ✅ `OPENROUTER_MODEL` - Model selection (anthropic/claude-3.5-sonnet)

---

## Verification Steps

After adding the secret and updating the workflow:

1. **Test locally first**:
   ```bash
   # Add to your .env file
   APIFREE_API_KEY=your_key_here
   
   # Run test
   python3 test_single_article.py
   ```

2. **Push changes to GitHub**:
   ```bash
   git add .github/workflows/news-automation.yml
   git commit -m "Add APIFREE_API_KEY to workflow"
   git push
   ```

3. **Test GitHub Action**:
   - Go to **Actions** tab
   - Click **Nepal Sports News Automation**
   - Click **Run workflow** (manual trigger)
   - Check if it runs successfully

---

## Cost Breakdown (With APIFree.ai)

### Per Article
- APIFree.ai image: $0.004
- Claude 3.5 Sonnet: ~$0.015
- **Total**: ~$0.019/article

### Daily (80 articles)
- **Cost**: ~$1.52/day
- **Monthly**: ~$45.60/month

### Fallback Strategy
If APIFree.ai fails or quota exceeded:
1. Try Cloudflare Flux (free)
2. Skip image if both fail (article still publishes)

---

## Summary

### Action Items
1. ❌ **Get APIFree.ai API key** from https://apifree.ai/api-keys
2. ❌ **Add to GitHub Secrets** as `APIFREE_API_KEY`
3. ❌ **Update workflow file** to include the new secret
4. ❌ **Test locally** with `test_single_article.py`
5. ❌ **Push to GitHub** and test the action

### Why This Matters
- APIFree.ai is now the primary image generator (better quality, faster)
- Without this secret, the bot will fall back to Cloudflare only
- Cloudflare has rate limits and may be slower
- APIFree.ai provides more consistent, higher-quality images

---

## Need Help?

If you need help adding the secret:
1. I can update the workflow file for you
2. You just need to add the secret in GitHub Settings
3. Then push the updated workflow file

Let me know when you've added the `APIFREE_API_KEY` secret and I'll update the workflow file!
