#!/usr/bin/env python3
import os, sys, time, feedparser, requests, re
from bs4 import BeautifulSoup
from utils import logger, validate_env, init_database, is_duplicate, mark_processed, sanitize_html
from api_clients import SerperClient, OpenRouterClient, CloudflareClient, WordPressClient, optimize_image
from config import (RSS_FEEDS, MAX_ARTICLES_PER_RUN, ARTICLE_DELAY_SECONDS, NEPAL_KEYWORDS,
                    PRIORITY_SPORTS, BETTING_TRIGGERS, BETTING_BRAND, BETTING_DISCLAIMER,
                    ALLOW_SOURCE_IMAGES)

def validate_startup():
    """Validate required environment variables"""
    required = ['WP_URL', 'WP_USERNAME', 'WP_APP_PASSWORD', 'OPENROUTER_API_KEY', 'SERPER_KEY_MAIN']
    for var in required:
        validate_env(var)
    logger.info("Environment validation passed")

def calculate_article_priority(title, summary):
    """Calculate priority score based on sport type and betting relevance"""
    text = f"{title} {summary}".lower()
    score = 0
    
    # Check sport priority
    for sport, priority in PRIORITY_SPORTS.items():
        if sport in text:
            score += priority
            break
    
    # Boost for betting-relevant content
    for trigger in BETTING_TRIGGERS:
        if trigger in text:
            score += 2
    
    # Boost for Nepal/India mentions
    if 'nepal' in text or 'india' in text:
        score += 5
    
    return score

def fetch_rss_articles(max_articles=MAX_ARTICLES_PER_RUN):
    """Fetch articles from RSS feeds with priority filtering"""
    articles = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                if not is_duplicate(entry.link):
                    title = entry.title
                    summary = entry.get('summary', '')
                    priority = calculate_article_priority(title, summary)
                    
                    # Skip low-priority sports (American football, etc.)
                    if priority < 3:
                        continue
                    
                    articles.append({
                        'title': title,
                        'link': entry.link,
                        'summary': summary,
                        'source': feed.feed.get('title', 'Unknown'),
                        'priority': priority
                    })
            logger.info(f"Fetched {len(feed.entries)} articles from {feed_url}")
        except Exception as e:
            logger.error(f"Failed to fetch RSS {feed_url}: {e}")
    
    # Sort by priority (highest first)
    articles.sort(key=lambda x: x['priority'], reverse=True)
    logger.info(f"Prioritized {len(articles)} articles (top priority: {articles[0]['priority'] if articles else 0})")
    
    return articles[:max_articles]

def scrape_article_content(url):
    """Scrape full article content from URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)'}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.content, 'lxml')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'aside']):
            tag.decompose()
        
        # Try to find main content
        content = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
        if content:
            paragraphs = content.find_all('p')
            text = '\n\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
            return text[:3000]  # Limit content length
        
        return None
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return None

def extract_image_from_url(url):
    """Extract featured image from article URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)'}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.content, 'lxml')
        
        # Try og:image first
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            img_url = og_image['content']
            img_resp = requests.get(img_url, headers=headers, timeout=10)
            img_resp.raise_for_status()
            return img_resp.content
        
        # Try first large image
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and not src.startswith('data:'):
                if not src.startswith('http'):
                    continue
                img_resp = requests.get(src, headers=headers, timeout=10)
                if img_resp.status_code == 200 and len(img_resp.content) > 10000:
                    return img_resp.content
        
        return None
    except Exception as e:
        logger.error(f"Failed to extract image from {url}: {e}")
        return None

def detect_betting_context(title, content):
    """Detect if article needs betting tips section"""
    text = f"{title} {content}".lower()
    
    betting_contexts = {
        'ucl': 'UEFA Champions League betting tips',
        'champions league': 'Champions League betting odds',
        'premier league': 'Premier League betting predictions',
        'ipl': 'IPL betting tips and odds',
        'world cup': 'World Cup betting predictions',
        'cricket': 'cricket betting tips',
        'football': 'football betting odds',
        'final': 'match betting predictions',
        'semi-final': 'semi-final betting tips'
    }
    
    for keyword, context in betting_contexts.items():
        if keyword in text:
            return context
    
    return None

def create_seo_article(title, content, keywords, source):
    """Generate SEO-optimized article with betting section for Nepal/India audience"""
    
    # Detect betting context
    betting_context = detect_betting_context(title, content)
    
    prompt = f"""Rewrite this sports news article for Nepal and India audience with SEO optimization and sports betting focus:

Original Title: {title}
Source: {source}
Content: {content[:1500]}

Trending Keywords: {', '.join(keywords[:5])}

CRITICAL REQUIREMENTS:
1. Create engaging title (50-60 chars) - Focus on Cricket/Football (NOT American sports)
2. Write 800-1200 word article in professional tone
3. Include keywords naturally: {', '.join(keywords[:3])}
4. Target audience: Nepal and India sports betting enthusiasts

5. **MANDATORY BETTING SECTION** (if relevant):
   - Add dedicated paragraph about betting tips/odds
   - Context: {betting_context or 'sports betting opportunities'}
   - Include specific betting predictions or odds analysis
   - Mention {BETTING_BRAND} naturally in context
   - End with: {BETTING_DISCLAIMER}
   
6. Use HTML formatting: <h2>, <p>, <strong>, <ul>, <blockquote>
7. Include meta description (150-160 chars) with betting keywords
8. Make it unique and plagiarism-free
9. Add internal linking opportunities for betting-related terms

Format:
TITLE: [new title with Nepal/India context]
META: [meta description with betting keywords]
CONTENT: [full HTML article with betting section]

Example betting section format:
<h2>Betting Tips and Predictions</h2>
<p>[Analysis of betting opportunities for this match/event]</p>
<p>For the latest odds and betting options, visit <a href="https://{BETTING_BRAND}" target="_blank" rel="nofollow">{BETTING_BRAND}</a>.</p>
<p><em>{BETTING_DISCLAIMER}</em></p>"""

    or_client = OpenRouterClient()
    response = or_client.generate(prompt, max_tokens=2500)
    
    # Parse response
    lines = response.split('\n')
    new_title = title
    meta_desc = ""
    html_content = response
    
    for i, line in enumerate(lines):
        if line.startswith('TITLE:'):
            new_title = line.replace('TITLE:', '').strip()
        elif line.startswith('META:'):
            meta_desc = line.replace('META:', '').strip()
        elif line.startswith('CONTENT:'):
            html_content = '\n'.join(lines[i+1:])
            break
    
    # Ensure betting disclaimer is present if betting context detected
    if betting_context and BETTING_BRAND not in html_content:
        html_content += f"""
<h2>Betting Tips and Predictions</h2>
<p>This match presents exciting betting opportunities. For the latest odds and predictions, check <a href="https://{BETTING_BRAND}" target="_blank" rel="nofollow">{BETTING_BRAND}</a>.</p>
<p><em>{BETTING_DISCLAIMER}</em></p>
"""
    
    return {
        'title': new_title,
        'content': sanitize_html(html_content),
        'meta': meta_desc
    }

def add_analytics_tracking(content, post_url):
    """Add Google Analytics and Search Console meta tags"""
    ga_id = os.getenv('GA_MEASUREMENT_ID')
    
    analytics_code = ""
    
    # Google Analytics 4
    if ga_id:
        analytics_code += f"""
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{ga_id}');
</script>
"""
    
    # Schema.org markup for better SEO
    analytics_code += f"""
<!-- Schema.org Markup -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "{post_url}",
  "datePublished": "{time.strftime('%Y-%m-%d')}",
  "author": {{
    "@type": "Organization",
    "name": "Sports News Bot"
  }}
}}
</script>
"""
    
    return analytics_code + content

def process_article(article, serper, cf_client, wp_client):
    """Process single article: scrape, rewrite, publish with betting focus"""
    try:
        logger.info(f"Processing (Priority {article['priority']}): {article['title']}")
        
        # Get trending keywords (Nepal/India specific)
        trends = serper.get_trends("cricket betting Nepal India")
        keywords = [t['title'] for t in trends]
        
        # Add betting-specific keywords
        keywords.extend(['betting Nepal', 'betting tips', 'sports betting'])
        
        # Scrape full content
        full_content = scrape_article_content(article['link'])
        if not full_content:
            full_content = article['summary']
        
        # Generate SEO article with betting section
        seo_article = create_seo_article(article['title'], full_content, keywords, article['source'])
        
        # ALWAYS generate copyright-free image with Cloudflare Flux (Priority 1)
        image_data = None
        media_id = None
        
        if cf_client.enabled:
            logger.info("Generating copyright-free image with Cloudflare Flux")
            image_data = cf_client.generate_image(seo_article['title'])
        
        # Fallback: Extract from source only if allowed and Cloudflare fails
        if not image_data and ALLOW_SOURCE_IMAGES:
            logger.warning("Cloudflare unavailable, extracting image from source (COPYRIGHT RISK)")
            image_data = extract_image_from_url(article['link'])
        elif not image_data:
            logger.warning("No Cloudflare image generated and source images disabled (safe mode)")
        
        # Optimize and upload image
        if image_data:
            optimized = optimize_image(image_data)
            if optimized:
                media_id = wp_client.upload_media(optimized, 'featured.avif')
                logger.info(f"Uploaded copyright-free featured image")
        else:
            logger.warning("Publishing article without image (no copyright risk)")
        
        # Add analytics tracking
        final_content = add_analytics_tracking(seo_article['content'], seo_article['title'])
        
        # Publish to WordPress
        post_id, post_url = wp_client.create_post(
            title=seo_article['title'],
            content=final_content,
            featured_media=media_id
        )
        
        # Mark as processed
        mark_processed(article['link'], seo_article['title'], post_id)
        
        logger.info(f"Published with betting content: {post_url}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to process article: {e}")
        return False

def main():
    """Main execution flow"""
    try:
        # Validate environment
        validate_startup()
        
        # Initialize database
        init_database()
        
        # Initialize clients
        serper = SerperClient()
        cf_client = CloudflareClient()
        wp_client = WordPressClient()
        
        logger.info("Starting Nepal Sports News Bot")
        
        # Fetch articles from RSS
        articles = fetch_rss_articles()
        logger.info(f"Found {len(articles)} new articles")
        
        if not articles:
            logger.info("No new articles to process")
            return
        
        # Process articles
        success_count = 0
        for article in articles:
            if process_article(article, serper, cf_client, wp_client):
                success_count += 1
                time.sleep(ARTICLE_DELAY_SECONDS)  # Rate limiting
        
        logger.info(f"Completed: {success_count}/{len(articles)} articles published")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
