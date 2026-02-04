# Copyright-Safe Image Generation System

## 🛡️ Copyright Protection Strategy

Your bot now uses **AI-generated images** to completely avoid copyright issues.

---

## How It Works

### Priority 1: Cloudflare Flux (AI-Generated) ✅
**ALWAYS tries this first**

```python
if cf_client.enabled:
    image_data = cf_client.generate_image(article_title)
```

**Benefits:**
- ✅ 100% copyright-free
- ✅ Unique images for every article
- ✅ Customized for sports context
- ✅ No attribution required
- ✅ No DMCA strikes

### Priority 2: Source Extraction (DISABLED by default) ⚠️
**Only used if explicitly enabled**

```python
ALLOW_SOURCE_IMAGES = False  # Disabled for safety
```

**Why disabled:**
- ❌ Copyright risk
- ❌ Potential DMCA strikes
- ❌ Legal issues
- ❌ Attribution requirements

---

## Image Generation Logic

### Current Flow (Safe Mode)

```
1. Article processed
   ↓
2. Cloudflare Flux generates AI image
   ↓
3. Image optimized to AVIF
   ↓
4. Uploaded to WordPress
   ↓
5. Article published with copyright-free image ✅
```

### If Cloudflare Fails

```
1. Cloudflare unavailable
   ↓
2. Check ALLOW_SOURCE_IMAGES setting
   ↓
3. If False (default): Publish without image ✅
   If True: Extract from source (COPYRIGHT RISK) ⚠️
```

---

## Smart Prompt Generation

The bot creates sport-specific prompts for better images:

### Cricket Articles
```
Input: "India wins IPL final against Australia"
Prompt: "Professional cricket match action photo, stadium atmosphere, 
         dynamic sports photography, high quality, realistic, 
         India wins IPL final"
```

### Football Articles
```
Input: "Barcelona defeats Real Madrid in UCL"
Prompt: "Professional football match action photo, stadium atmosphere, 
         dynamic sports photography, high quality, realistic, 
         Barcelona defeats Real Madrid"
```

### Generic Sports
```
Input: "Nepal sports betting news"
Prompt: "Professional sports news photo, stadium atmosphere, 
         dynamic action, high quality, realistic, 
         Nepal sports betting"
```

---

## Configuration

### config.py Settings

```python
# Image settings
IMAGE_WIDTH = 1200              # HD width
IMAGE_HEIGHT = 675              # 16:9 aspect ratio
IMAGE_QUALITY = 85              # AVIF quality
USE_CLOUDFLARE_IMAGES = True    # Enable AI generation
ALLOW_SOURCE_IMAGES = False     # Disable source extraction (SAFE)
```

### To Enable Source Images (NOT RECOMMENDED)

```python
ALLOW_SOURCE_IMAGES = True  # ⚠️ COPYRIGHT RISK
```

---

## Cloudflare Flux Setup

### 1. Get Cloudflare Account
- Sign up at https://dash.cloudflare.com/
- Go to Workers & Pages → AI

### 2. Get Credentials
- Account ID: Found in dashboard
- API Token: Create with AI permissions

### 3. Add to GitHub Secrets
```
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_TOKEN=your_api_token
```

### 4. Test
```bash
# Run workflow manually
# Check logs for: "Generated copyright-free image"
```

---

## Image Optimization

All images (AI or source) are optimized:

### AVIF Conversion
```python
def optimize_image(image_data):
    # Convert to RGB
    # Resize to max 1200px
    # Save as AVIF (quality 85)
    # Check size limit (2MB)
```

**Benefits:**
- 50-70% smaller than JPEG
- Better quality at same size
- Faster page loads
- Better SEO scores

---

## Cost Analysis

### Cloudflare Flux Pricing

**Free Tier:**
- 10,000 requests/day
- More than enough for this bot

**Usage:**
- 4 runs/day × 5 articles = 20 images/day
- 600 images/month
- Well within free tier ✅

**Paid Tier (if needed):**
- Included in Workers plan ($5/month)
- Unlimited requests

---

## Logging

### Success
```
INFO: Generating copyright-free image with Cloudflare Flux
INFO: Generated copyright-free image (87.3KB)
INFO: Uploaded copyright-free featured image
```

### Cloudflare Unavailable (Safe Mode)
```
WARNING: Cloudflare unavailable
WARNING: Publishing article without image (no copyright risk)
```

### Source Extraction (If Enabled)
```
WARNING: Cloudflare unavailable, extracting image from source (COPYRIGHT RISK)
```

---

## Troubleshooting

### No Images Generated

**Check Cloudflare credentials:**
```bash
# In GitHub Secrets
CLOUDFLARE_ACCOUNT_ID=xxx
CLOUDFLARE_TOKEN=xxx
```

**Check logs:**
```
Actions → Latest run → View logs
Search for: "Cloudflare"
```

**Common issues:**
- Invalid API token
- Wrong account ID
- API quota exceeded (unlikely)
- Network timeout

### Images Look Generic

**Improve prompts in api_clients.py:**
```python
# Add more specific keywords
if 'ipl' in enhanced_prompt:
    image_prompt = "IPL cricket match, Indian stadium, crowd cheering..."
```

### Want Source Images (Not Recommended)

**Enable in config.py:**
```python
ALLOW_SOURCE_IMAGES = True  # ⚠️ Use at your own risk
```

---

## Legal Compliance

### AI-Generated Images (Cloudflare)
- ✅ No copyright restrictions
- ✅ Commercial use allowed
- ✅ No attribution required
- ✅ Unique to your site

### Source Images (If Enabled)
- ⚠️ Copyright belongs to original source
- ⚠️ May require attribution
- ⚠️ Risk of DMCA takedown
- ⚠️ Potential legal issues

---

## Best Practices

### 1. Always Use Cloudflare
```python
ALLOW_SOURCE_IMAGES = False  # Keep disabled
```

### 2. Monitor Generation
Check logs to ensure images are being generated

### 3. Customize Prompts
Edit `api_clients.py` for better sport-specific images

### 4. Test Regularly
Run manual workflow to verify image generation

### 5. Backup Plan
If Cloudflare fails, articles publish without images (safe)

---

## Example Output

### Article: "India Wins IPL Final"

**Image Generation:**
```
1. Detect sport: Cricket/IPL
2. Generate prompt: "Professional cricket match action photo, 
   stadium atmosphere, dynamic sports photography, 
   India wins IPL final"
3. Call Cloudflare Flux API
4. Receive AI-generated image (unique, copyright-free)
5. Optimize to AVIF (reduce size 60%)
6. Upload to WordPress
7. Set as featured image
```

**Result:**
- Unique cricket stadium image
- No copyright issues
- Optimized for web
- SEO-friendly

---

## Migration from Source Images

If you were using source images before:

### 1. Enable Cloudflare
Add secrets to GitHub

### 2. Set Safe Mode
```python
ALLOW_SOURCE_IMAGES = False
```

### 3. Run Test
Manual workflow trigger

### 4. Verify
Check WordPress for AI-generated images

### 5. Monitor
Watch for any Cloudflare errors

---

## Summary

✅ **Default behavior:** AI-generated images only (copyright-safe)
✅ **Fallback:** Publish without image (still safe)
✅ **Cost:** Free tier (10,000/day)
✅ **Quality:** HD images (1200×675)
✅ **Format:** AVIF (optimized)
✅ **Legal:** 100% copyright-free

⚠️ **Source images:** Disabled by default (copyright risk)

---

## Quick Reference

### Enable AI Images
```bash
# GitHub Secrets
CLOUDFLARE_ACCOUNT_ID=xxx
CLOUDFLARE_TOKEN=xxx
```

### Disable Source Images (Default)
```python
# config.py
ALLOW_SOURCE_IMAGES = False
```

### Check Image Generation
```bash
# GitHub Actions logs
Search for: "Generated copyright-free image"
```

### Customize Prompts
```python
# api_clients.py → CloudflareClient.generate_image()
# Edit sport-specific prompts
```

---

**Your bot is now 100% copyright-safe with AI-generated images!** 🎉
