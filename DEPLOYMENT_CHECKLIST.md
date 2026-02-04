# 🚀 GitHub Deployment Checklist

## Pre-Deployment Verification

### ✅ Files Ready
- [x] news_bot.py (main script)
- [x] api_clients.py (API integrations)
- [x] utils.py (utilities)
- [x] config.py (configuration)
- [x] requirements.txt (dependencies)
- [x] .github/workflows/news-automation.yml (automation)
- [x] .gitignore (security)

### ✅ Security
- [x] No hardcoded secrets
- [x] All credentials use os.getenv()
- [x] .env files ignored
- [x] Safe for public repo

### ✅ Features
- [x] Cricket/Football priority (not American sports)
- [x] Automatic betting tips section
- [x] 1xbet.com mentions with 18+ disclaimer
- [x] Google Analytics integration
- [x] Cloudflare AI image generation
- [x] Copyright-safe images
- [x] Nepal/India geo-targeting
- [x] SEO optimization

---

## GitHub Setup Steps

### Step 1: Create/Connect Repository

```bash
# If new repo
git init
git add .
git commit -m "Initial commit: Sports news automation bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main

# If existing repo
git add .
git commit -m "Update: Optimized for 10k visitors/month"
git push
```

### Step 2: Add GitHub Secrets

Go to: **Settings → Secrets and variables → Actions → New repository secret**

#### Required Secrets (6)
```
1. SERPER_KEY_MAIN = your_serper_api_key
2. OPENROUTER_API_KEY = your_openrouter_api_key
3. WP_URL = https://yoursite.com
4. WP_USERNAME = your_wordpress_username
5. WP_APP_PASSWORD = your_wordpress_app_password
6. CLOUDFLARE_ACCOUNT_ID = your_cloudflare_account_id
```

#### Optional Secrets (3)
```
7. SERPER_KEY_BACKUP = backup_serper_key
8. CLOUDFLARE_TOKEN = your_cloudflare_token
9. GA_MEASUREMENT_ID = G-XXXXXXXXXX
```

### Step 3: Enable GitHub Actions

1. Go to **Actions** tab
2. Click **"I understand my workflows, go ahead and enable them"**
3. Workflow will appear: "Nepal Sports News Automation"

### Step 4: Test Run

1. Go to **Actions** tab
2. Click **"Nepal Sports News Automation"**
3. Click **"Run workflow"** dropdown
4. Click **"Run workflow"** button
5. Wait 5-10 minutes
6. Check logs for success

---

## Verification Checklist

### After First Run

- [ ] Check Actions logs (no errors)
- [ ] Visit WordPress site (articles published)
- [ ] Check featured images (AI-generated)
- [ ] Verify betting section (1xbet.com + 18+ notice)
- [ ] Check Google Analytics (tracking works)
- [ ] Verify article quality (SEO optimized)
- [ ] Check sport priority (cricket/football only)

### Monitor for 24 Hours

- [ ] 8 runs completed (every 3 hours)
- [ ] 80 articles published (10 per run)
- [ ] No duplicate articles
- [ ] Images generated successfully
- [ ] No API errors
- [ ] Database cache working

---

## Expected Behavior

### Workflow Schedule
```
Runs: Every 3 hours (8 times/day)
Articles per run: 10
Daily output: 80 articles
Monthly output: 2,400 articles
```

### Article Structure
```
✅ Title: SEO-optimized with Nepal/India context
✅ Content: 800-1200 words, HTML formatted
✅ Image: AI-generated, copyright-free, AVIF format
✅ Betting section: Tips + 1xbet.com + 18+ disclaimer
✅ Analytics: Google Analytics + Schema.org markup
```

### Sport Priority
```
✅ Cricket: 70% of articles
✅ Football: 25% of articles
✅ Other: 5% of articles
❌ American Football: Filtered out
```

---

## Troubleshooting

### No Articles Published

**Check:**
1. GitHub Secrets are set correctly
2. WordPress credentials are valid
3. RSS feeds are accessible
4. Check Actions logs for errors

**Fix:**
```bash
# Test WordPress connection
curl -u username:app_password https://yoursite.com/wp-json/wp/v2/posts
```

### Images Not Generated

**Check:**
1. CLOUDFLARE_ACCOUNT_ID is set
2. CLOUDFLARE_TOKEN is set
3. Cloudflare AI is enabled

**Fix:**
- Articles will publish without images (safe)
- Add Cloudflare secrets to enable images

### API Rate Limits

**Check:**
1. Serper API quota (2,500/month free)
2. OpenRouter credits
3. Cloudflare quota (10,000/day free)

**Fix:**
- Add SERPER_KEY_BACKUP for rotation
- Reduce MAX_ARTICLES_PER_RUN in config.py

### Duplicate Articles

**Check:**
1. Database cache is working
2. news_cache.db is persisted

**Fix:**
- Cache is automatic via GitHub Actions cache
- Clear cache in Actions if needed

---

## Performance Monitoring

### Daily Checks
```
✅ Articles published: ~80/day
✅ No errors in logs
✅ Images generated
✅ Betting sections present
```

### Weekly Checks
```
✅ Total articles: ~560/week
✅ Traffic growth in Google Analytics
✅ No duplicate content
✅ API quotas not exceeded
```

### Monthly Review
```
✅ Total articles: ~2,400/month
✅ Visitors: 40,000-60,000
✅ Goal achieved: 10,000+ ✅
✅ Costs: $0 (using free models)
```

---

## Quick Commands

### Check Workflow Status
```bash
# View in browser
https://github.com/YOUR_USERNAME/YOUR_REPO/actions
```

### Manual Trigger
```bash
# Actions → Nepal Sports News Automation → Run workflow
```

### View Logs
```bash
# Actions → Latest run → publish-news → View logs
```

### Check Secrets
```bash
# Settings → Secrets and variables → Actions
```

---

## Success Criteria

### Week 1
- [ ] 560 articles published
- [ ] No major errors
- [ ] Images generating
- [ ] 500-1,000 visitors

### Week 2
- [ ] 1,120 total articles
- [ ] Consistent publishing
- [ ] 2,000-3,000 visitors

### Week 3
- [ ] 1,680 total articles
- [ ] Traffic growing
- [ ] 5,000-7,000 visitors

### Week 4
- [ ] 2,240 total articles
- [ ] Goal achieved
- [ ] 10,000+ visitors ✅

---

## Emergency Contacts

### If Something Breaks

1. **Check Actions logs** first
2. **Disable workflow** if needed (Actions → Disable)
3. **Fix issue** in code
4. **Re-enable workflow**

### Common Fixes

**WordPress errors:**
```bash
# Regenerate app password
WordPress Admin → Users → Profile → Application Passwords
```

**API errors:**
```bash
# Check quotas
Serper: https://serper.dev/dashboard
OpenRouter: https://openrouter.ai/credits
Cloudflare: https://dash.cloudflare.com/
```

**Database errors:**
```bash
# Clear cache
Actions → Caches → Delete news-db cache
```

---

## Final Checklist Before Going Live

- [ ] All secrets added to GitHub
- [ ] Workflow enabled
- [ ] Test run successful
- [ ] Articles appearing on WordPress
- [ ] Images generating
- [ ] Betting sections present
- [ ] Google Analytics tracking
- [ ] No errors in logs

---

## 🎉 You're Ready!

Once all checks pass:
1. Let it run automatically
2. Monitor daily for first week
3. Check traffic in Google Analytics
4. Adjust keywords if needed
5. Watch your traffic grow to 10,000+!

**Good luck with your 10,000 visitor goal!** 🚀
