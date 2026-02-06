#!/usr/bin/env python3
import os, sys, time, feedparser, requests, re, json
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from tenacity import RetryError
from utils import logger, validate_env, init_database, is_duplicate, mark_processed, sanitize_html
from api_clients import SerperClient, OpenRouterClient, CloudflareClient, WordPressClient, optimize_image
from apifree_client import APIFreeClient
from article_extractor import extract_article
from thumbnail_spec import ThumbnailSpecBuilder
from prompt_builder import PromptBuilder
from config import (RSS_FEEDS, MAX_ARTICLES_PER_RUN, ARTICLE_DELAY_SECONDS, LOCAL_KEYWORDS,
                    PRIORITY_SPORTS, BETTING_TRIGGERS, BETTING_BRAND, BETTING_DISCLAIMER,
                    ALLOW_SOURCE_IMAGES)

# Load environment variables from .env file (for local testing)
load_dotenv()

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
    
    # Check sport priority (Cricket: +5, Football: +3, Other: +2)
    sport_found = False
    for sport, priority in PRIORITY_SPORTS.items():
        if sport in text:
            score += priority
            sport_found = True
            break
    
    # If no specific sport found, check for general sports indicators
    if not sport_found:
        # Football team names and leagues
        football_indicators = ['arsenal', 'chelsea', 'manchester', 'liverpool', 'barcelona', 
                              'real madrid', 'psg', 'bayern', 'juventus', 'milan',
                              'premier league', 'la liga', 'serie a', 'bundesliga', 'ligue 1']
        if any(indicator in text for indicator in football_indicators):
            score += 3  # Football priority
            sport_found = True
        
        # Cricket team names and tournaments
        cricket_indicators = ['india', 'pakistan', 'australia', 'england', 'test match',
                            'odi', 't20', 'ipl', 'bbl', 'psl', 'wicket', 'batting', 'bowling']
        if any(indicator in text for indicator in cricket_indicators):
            score += 5  # Cricket priority
            sport_found = True
    
    # Boost for betting-relevant content
    for trigger in BETTING_TRIGGERS:
        if trigger in text:
            score += 2
            break
    
    # Boost for Nepal/India mentions
    if 'nepal' in text or 'india' in text:
        score += 5
    
    return score

def fetch_rss_articles(max_articles=MAX_ARTICLES_PER_RUN):
    """Fetch articles from RSS feeds with priority filtering"""
    articles = []
    total_fetched = 0
    total_filtered = 0
    
    for feed_url in RSS_FEEDS:
        try:
            # Fetch with requests first (feedparser has issues with some feeds)
            resp = requests.get(feed_url, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            total_fetched += len(feed.entries)
            
            for entry in feed.entries:
                if not is_duplicate(entry.link):
                    title = entry.title
                    summary = entry.get('summary', '')
                    priority = calculate_article_priority(title, summary)
                    
                    # Skip low-priority sports (American football, etc.)
                    if priority < 3:
                        total_filtered += 1
                        logger.debug(f"Filtered low priority ({priority}): {title[:50]}")
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
    
    logger.info(f"RSS Summary: {total_fetched} total, {total_filtered} filtered, {len(articles)} priority articles")
    if articles:
        logger.info(f"Top priority: {articles[0]['priority']} - {articles[0]['title'][:60]}")
    
    return articles[:max_articles]

def scrape_article_content(url):
    """
    Scrape full article content from URL with advanced extraction
    Extracts complete article text for use as source material
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        resp = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.content, 'lxml')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'aside', 'header', 'iframe', 'noscript']):
            tag.decompose()
        
        # Remove ads and social media widgets
        for class_name in ['ad', 'advertisement', 'social-share', 'related-articles', 'comments', 'sidebar']:
            for tag in soup.find_all(class_=lambda x: x and class_name in x.lower()):
                tag.decompose()
        
        # Try multiple strategies to find article content
        article_text = None
        
        # Strategy 1: Look for article tag
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            article_text = '\n\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])
        
        # Strategy 2: Look for main content area
        if not article_text or len(article_text) < 500:
            main = soup.find('main') or soup.find('div', class_=re.compile(r'(content|article|story|post-body)', re.I))
            if main:
                paragraphs = main.find_all('p')
                article_text = '\n\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])
        
        # Strategy 3: Look for specific content classes
        if not article_text or len(article_text) < 500:
            content_divs = soup.find_all('div', class_=re.compile(r'(article-body|story-body|entry-content|post-content)', re.I))
            for div in content_divs:
                paragraphs = div.find_all('p')
                text = '\n\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])
                if len(text) > len(article_text or ''):
                    article_text = text
        
        # Strategy 4: Find all paragraphs with substantial text
        if not article_text or len(article_text) < 500:
            all_paragraphs = soup.find_all('p')
            # Filter paragraphs that are likely article content (longer paragraphs)
            content_paragraphs = [p.get_text().strip() for p in all_paragraphs if len(p.get_text().strip()) > 50]
            if content_paragraphs:
                article_text = '\n\n'.join(content_paragraphs)
        
        # Clean up the text
        if article_text:
            # Remove excessive whitespace
            article_text = re.sub(r'\s+', ' ', article_text)
            article_text = re.sub(r'\n\s*\n', '\n\n', article_text)
            
            # Remove common boilerplate phrases
            boilerplate = [
                r'Click here to.*?(?=\n|$)',
                r'Read more:.*?(?=\n|$)',
                r'Subscribe to.*?(?=\n|$)',
                r'Follow us on.*?(?=\n|$)',
                r'Sign up for.*?(?=\n|$)',
            ]
            for pattern in boilerplate:
                article_text = re.sub(pattern, '', article_text, flags=re.IGNORECASE)
            
            article_text = article_text.strip()
            
            # Return full article (no length limit - we need complete context)
            if len(article_text) > 500:
                logger.info(f"Extracted {len(article_text)} chars of article content")
                return article_text
            else:
                logger.warning(f"Extracted content too short: {len(article_text)} chars")
                return None
        
        logger.warning("Could not extract article content using any strategy")
        return None
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            logger.warning(f"Access forbidden (403) for {url} - site blocking scraping")
        else:
            logger.warning(f"HTTP error scraping {url}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Could not scrape {url}: {e}")
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

def detect_categories_and_tags(title, content):
    """Detect appropriate categories and generate tags from article"""
    text = f"{title} {content}".lower()
    
    # Category detection (sport-based) - ONLY assign if clearly present
    categories_map = {
        'cricket': ['cricket', 'ipl', 't20', 'test', 'odi', 'wicket', 'batting', 'bowling', 'bcci', 'icc'],
        'football': ['football', 'soccer', 'premier league', 'champions league', 'ucl', 'goal', 'fifa', 'uefa'],
        'sports betting': ['betting', 'odds', 'prediction', 'tips', 'bookmaker', 'wager'],
    }
    
    detected_categories = []
    for category, keywords in categories_map.items():
        # Require at least 2 keyword matches for category assignment (stricter)
        matches = sum(1 for kw in keywords if kw in text)
        if matches >= 2:
            detected_categories.append(category)
    
    # Default to 'Sports News' if no specific category (but don't add multiple defaults)
    if not detected_categories:
        detected_categories.append('sports news')
    
    # Tag generation (extract key entities)
    tags = []
    
    # Team names
    teams = ['india', 'pakistan', 'australia', 'england', 'south africa', 'new zealand',
             'liverpool', 'manchester united', 'manchester city', 'chelsea', 'arsenal',
             'barcelona', 'real madrid', 'bayern munich', 'psg']
    for team in teams:
        if team in text:
            tags.append(team.title())
    
    # Tournaments
    tournaments = ['world cup', 'ipl', 't20', 'premier league', 'champions league', 'ucl']
    for tournament in tournaments:
        if tournament in text:
            tags.append(tournament.upper() if tournament in ['ipl', 'ucl', 't20'] else tournament.title())
    
    # Player names (common ones)
    players = ['kohli', 'rohit', 'bumrah', 'dhoni', 'babar', 'miller', 'salah', 'haaland', 'mbappe', 'ronaldo', 'messi']
    for player in players:
        if player in text:
            tags.append(player.title())
    
    # Add location tags
    if 'nepal' in text:
        tags.append('Nepal')
    if 'india' in text:
        tags.append('India')
    
    # Limit to 8 tags max
    tags = list(set(tags))[:8]
    
    return detected_categories, tags

def create_seo_article(title, content, keywords, source, source_url=""):
    """Generate SEO-optimized article with betting section for Nepal/India audience"""
    
    # Detect betting context
    betting_context = detect_betting_context(title, content)
    
    # Get current date for context
    from datetime import datetime
    current_date = datetime.utcnow().strftime('%B %d, %Y')
    
    # ULTRA-SPECIFIC PROMPT FOR CLAUDE 3.5 SONNET
    # Designed to produce natural, engaging, SEO-optimized content with FACT-CHECKING
    prompt = f"""You are writing a sports news article targeting cricket and football fans.

SOURCE MATERIAL (Use this as your factual basis):
Title: {title}
Full Article Content: {content[:3000]}
Source: {source}
Source URL: {source_url}
Keywords: {', '.join(keywords[:5]) if keywords else 'cricket, football, sports betting'}
Current Date: {current_date}

YOUR TASK:
Rewrite this article with your own unique angle, focusing on Nepal/India audience and adding betting insights. Use ALL facts from the source material but present them in an engaging, original way.

🎯 REWRITING APPROACH:
- Use ALL factual information from source (scores, names, dates, quotes, statistics)
- Rewrite in your own words with fresh perspective
- Add Nepal/India local angle and context
- Integrate betting insights naturally
- Maintain journalistic integrity - cite source for key facts
- Create original analysis and commentary

🚨 MANDATORY FACT-CHECKING REQUIREMENTS:
1. VERIFY TOURNAMENT NAMES: Check if it's "T20 World Cup", "ODI World Cup", "Champions Trophy", etc. - use EXACT name from source
2. VERIFY TEAM RELATIONSHIPS: If story is "Team A boycotts Team B match in solidarity with Team C", make this crystal clear in title and content
3. VERIFY QUOTES: Only use quotes if they appear in the source material with attribution. NO fabricated quotes.
4. VERIFY QUOTE CONTEXT: If a quote has cultural/political context (memes, elections, viral moments), EITHER omit it OR explain the context. Never present quotes as if the speaker is talking about the current topic when they were talking about something else.
5. VERIFY DATES/EVENTS: Only reference events mentioned in source material. NO speculation about future events without source confirmation.
6. VERIFY TOURNAMENT DETAILS: Include host countries, start AND end dates (clarify which is final), venue cities for major matches
7. ADD CONTEXT: If story requires background (e.g., why something happened), add a "Background" section with facts from source
8. SOURCE CITATIONS: Include source name and ideally URL for key facts
9. VERIFY STATISTICS: If using specific stats (e.g., "21 T20 internationals in January produced X runs"), cite the source or soften the language if unverifiable

🚨 QUOTE VERIFICATION CRITICAL:
- If quote is a meme, viral moment, or political reference (e.g., "Brenda from Bristol"), DO NOT use it unless you explain the context
- Example BAD: "Not another one." – Brenda from Bristol (misleading - this is a 2017 UK election meme, not a cricket quote)
- Example GOOD: Either omit the quote OR add context: "As the cricket columnist noted, some fans echo the sentiment of the famous 'Brenda from Bristol' reaction to frequent elections"
- When in doubt about quote context, OMIT THE QUOTE

CRITICAL REQUIREMENTS:

1. TITLE (50-60 characters):
   - MUST accurately reflect the story (no misleading phrasing)
   - Start with the primary keyword (team name, tournament, or sport)
   - Use EXACT tournament name from source (T20 World Cup 2026, not just "World Cup")
   - Make it compelling but not clickbait
   - Example: "India vs Pakistan T20: Kohli's 89 Seals Victory"
   - BAD Example: "Pakistan PM Backs Bangladesh Boycott" (confusing - who is boycotting whom?)
   - GOOD Example: "Pakistan PM Backs India Match Boycott in Solidarity with Bangladesh"

2. META DESCRIPTION (150-160 characters):
   - Include primary keyword + secondary keyword
   - Add a call to action
   - Must match article content accurately
   - Example: "India defeats Pakistan by 6 wickets in T20 World Cup thriller. Kohli's masterclass and Bumrah's spell seal the win. Read full match analysis and betting insights."

3. ARTICLE STRUCTURE (MINIMUM 800 words - STRICT REQUIREMENT):

PUBLISH DATE (at very top):
<p><em>Published: {current_date}</em></p>

OPENING (100-150 words):
- Start with a hook: surprising stat, dramatic moment, or key question
- Answer: Who won? What happened? When? Where?
- Include primary keyword in first sentence
- Add local context (Nepal/India viewing angle)
- For tournaments: Include host countries, precise dates (start date to final date), venue cities
- Example: "The T20 World Cup 2026, co-hosted by India and Sri Lanka from February 7 to March 8..."
- ONLY use facts from source material

<h2>Background</h2> (IF STORY REQUIRES CONTEXT - 100-150 words):
- Add this section ONLY if story needs explanation (e.g., political boycott, controversy, rule change)
- Explain: Why did this happen? What led to this situation?
- Use facts from source material only
- Example: "Bangladesh was excluded from T20 World Cup 2026 after refusing to travel to India citing security concerns. The ICC Board voted 14-2 to replace them with Scotland."

<h2>Match Summary</h2> OR <h2>Story Details</h2> (150-200 words):
- For match reports: Final score with specific details, key moments with timestamps
- For news stories: Core facts, official statements, key developments
- Venue, date, key participants
- Story-deciding factors
- ONLY use verifiable information from source

<h2>Key Moments That Decided the Match</h2>:
<ul>
<li><strong>[Time/Over]:</strong> [Specific event with player names and impact]</li>
<li><strong>[Time/Over]:</strong> [Another crucial moment]</li>
<li><strong>[Time/Over]:</strong> [Third key moment]</li>
</ul>

<h2>Team Analysis</h2>:
<h3>[Winning Team]</h3> (100-150 words):
- Performance stats (possession %, strike rate, etc.)
- What worked well
- Key players' contributions

<h3>[Losing Team]</h3> (100-150 words):
- Where they fell short
- Missed opportunities
- Individual performances

<h2>Star Performers</h2>:
<ul>
<li><strong>[Player 1]:</strong> [Stats and impact - 2-3 sentences]</li>
<li><strong>[Player 2]:</strong> [Stats and impact - 2-3 sentences]</li>
<li><strong>[Player 3]:</strong> [Stats and impact - 2-3 sentences]</li>
</ul>

<h2>What This Means for [Tournament/League]</h2> (100-150 words):
- Standings implications
- Qualification scenarios
- Upcoming fixtures
- Local angle for Nepal/India fans

<h2>Expert Analysis</h2> (100-150 words):
- Tactical breakdown
- What worked/didn't work
- Predictions for next matches
- ONLY include quotes if they appear in source material with proper attribution

<blockquote>
<p>"[ONLY add quote if it appears in source material with attribution. Format: Quote text - Speaker Name, Source Name]"</p>
<p><em>Source: [Source Name + URL if available]</em></p>
</blockquote>

🚨 QUOTE RULES:
- NO quotes unless they appear in source material
- MUST include attribution: Speaker name + Source
- MUST include source citation below quote
- If no quotes in source, skip the blockquote entirely

<h2>Betting Insights and Odds</h2> (100-150 words):
- Pre-match odds and how they played out
- Betting trends
- Mention: "For live odds and expert betting tips, visit <a href="https://{BETTING_BRAND}" target="_blank" rel="nofollow">{BETTING_BRAND}</a>"
- Add: "<em>{BETTING_DISCLAIMER}</em>"

<h2>What's Next?</h2> (80-100 words):
- Upcoming fixtures with dates/times in IST (ONLY if mentioned in source)
- What to watch for
- Viewing information for Nepal/India (broadcast channels, streaming)
- Travel info if relevant (e.g., "Sri Lankan venues are easily accessible for Nepal/India fans")
- India vs Pakistan fixtures if applicable (always trending!)
- NO placeholder text like "[Next scheduled matches pending ICC review]"
- If no specific fixtures mentioned in source, write: "Stay tuned for official announcements on upcoming fixtures."

CLOSING:
<p><strong>What did you think of this [match/story]? Share your thoughts in the comments below!</strong></p>

4. WRITING STYLE:
   - Use active voice: "India won" NOT "The match was won by India"
   - Short paragraphs: 3-4 sentences maximum
   - Conversational but professional tone
   - NO robotic phrases like "delve into", "in conclusion", "it's worth noting", "in the realm of"
   - Include specific numbers, names, times throughout
   - Natural keyword integration (don't force keywords)
   - FACT-CHECK: Every claim must be traceable to source material

5. SEO OPTIMIZATION:
   - Primary keyword in first 100 words
   - Use 6-12 secondary keywords naturally (cricket, India, Pakistan, World Cup, betting, odds, IST, streaming, etc.)
   - Include local keywords: "Nepal", "India", "IST time", "live streaming"
   - Add specific facts: scores, minutes/overs, player stats, possession %, head-to-head records
   - ONLY use facts from source material

6. GOOGLE DISCOVER ELIGIBILITY:
   - Story-driven narrative, not just stats
   - Original analysis and insights
   - No clickbait - title must match content EXACTLY
   - Include proper quotes with attribution (only if in source)
   - NO misleading headlines or images

7. AI SEARCH OPTIMIZATION (Gemini, Grok, Perplexity, ChatGPT):
   - Direct answers to questions: "Who won?", "What was the score?", "When is the next match?"
   - Clear H2/H3 hierarchy
   - Fact-dense content with timelines and statistics
   - Source-backed claims with citations

8. RESPONSIBLE BETTING:
   - NO guarantees or promises
   - Include risk warnings
   - Mention {BETTING_BRAND} naturally in betting section
   - Always add disclaimer: {BETTING_DISCLAIMER}

OUTPUT FORMAT:
Return your response in this exact format:

TITLE: Your 50-60 char title - MUST accurately reflect story

META: Your 150-160 char meta description

THUMBNAILSPEC:
{{
  "topic": "NCAAB/Cricket/Football matchup or news type",
  "headline_text": "Article headline, max 40 chars, UPPERCASE",
  "sub_text": "Subheading like BETTING INSIGHTS, max 30 chars",
  "layout": "lineup_5_figures or symbolic or action_moment",
  "aspect_ratio": "16:9",
  "team_left_color": "color description, e.g. royal blue and white",
  "team_right_color": "color description, e.g. deep red and white",
  "no_real_people": true,
  "no_team_logos": true,
  "style": "3D action-figure poster or cinematic editorial or action photography",
  "background": "dark gradient studio or stadium night floodlights or etc",
  "negative_space": "top for headline or sides for text or etc"
}}

CONTENT:
Your complete HTML article starting with publish date, then opening paragraph

CRITICAL RULES - VIOLATION WILL RESULT IN REJECTION:
- MINIMUM 800 words (strict requirement)
- NO copyright text or "© 2023" anywhere
- NO hallucinated facts - ONLY use verifiable information from source
- NO fabricated quotes - ONLY quotes that appear in source with attribution
- NO misleading quote context - verify quotes aren't memes/political references used out of context
- NO clickbait - title must accurately reflect content
- NO betting guarantees or promises
- NO placeholder text in published content
- Include specific statistics and data points throughout
- Make it engaging and natural - should pass the "read aloud" test
- VERIFY tournament names (T20 World Cup vs ODI World Cup vs Champions Trophy)
- VERIFY team relationships (who is playing/boycotting whom)
- VERIFY tournament details (host countries, start date, end date/final date, venue cities)
- VERIFY quote context (no memes or political quotes without proper context)
- ADD visible publish date at top of article
- ADD source citations for key facts
- ADD host country info for tournaments
- ADD precise dates (start to final, not just "begins on X")"""

    or_client = OpenRouterClient()
    response = or_client.generate(prompt, max_tokens=5000)
    
    # Parse response - extract TITLE, META, THUMBNAILSPEC, and CONTENT
    lines = response.split('\n')
    new_title = title
    meta_desc = ""
    thumbnail_spec = {}
    html_content = response
    
    i = 0
    while i < len(lines):
        line = lines[i]
        line_stripped = line.strip()
        
        # Extract TITLE
        if line_stripped.startswith('TITLE:') or line_stripped.startswith('**TITLE:'):
            new_title = re.sub(r'\*\*TITLE:\*\*|\*\*TITLE:|\bTITLE:\s*', '', line).strip()
            new_title = new_title.replace('**', '').strip()
        
        # Extract META
        elif line_stripped.startswith('META:') or line_stripped.startswith('**META:'):
            meta_desc = re.sub(r'\*\*META:\*\*|\*\*META:|\bMETA:\s*', '', line).strip()
            meta_desc = meta_desc.replace('**', '').strip()
        
        # Extract THUMBNAILSPEC (JSON block)
        elif line_stripped.startswith('THUMBNAILSPEC:') or line_stripped.startswith('**THUMBNAILSPEC:'):
            # Find the JSON block
            json_start = i + 1
            json_lines = []
            brace_count = 0
            
            for j in range(json_start, len(lines)):
                json_line = lines[j]
                json_lines.append(json_line)
                brace_count += json_line.count('{') - json_line.count('}')
                
                if brace_count == 0 and '{' in '\n'.join(json_lines):
                    # JSON block complete
                    try:
                        json_str = '\n'.join(json_lines)
                        thumbnail_spec = json.loads(json_str)
                        logger.info(f"Extracted ThumbnailSpec: {thumbnail_spec.get('topic', 'unknown')}")
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse ThumbnailSpec JSON: {e}")
                    
                    i = j
                    break
        
        # Extract CONTENT
        elif line_stripped.startswith('CONTENT:') or line_stripped.startswith('**CONTENT:'):
            html_content = '\n'.join(lines[i+1:])
            break
        
        i += 1
    
    # Remove any remaining markdown formatting from content
    html_content = re.sub(r'\*\*CONTENT:\*\*', '', html_content)
    html_content = re.sub(r'\*\*Title:\*\*.*?\n', '', html_content)
    html_content = re.sub(r'\*\*Meta:\*\*.*?\n', '', html_content)
    html_content = html_content.strip()
    
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
        'meta': meta_desc,
        'thumbnail_spec': thumbnail_spec
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

def process_article(article, serper, apifree_client, cf_client, wp_client):
    """Process single article: scrape, rewrite, publish with betting focus"""
    try:
        logger.info(f"Processing (Priority {article['priority']}): {article['title']}")
        
        # Get trending keywords (Nepal/India specific)
        trends = serper.get_trends("cricket betting Nepal India")
        keywords = [t['title'] for t in trends]
        
        # Add betting-specific keywords
        keywords.extend(['betting Nepal', 'betting tips', 'sports betting'])
        
        # Extract full article using professional extraction libraries
        logger.info("Extracting full article content...")
        full_content = extract_article(article['link'])
        
        if full_content and len(full_content) >= 500:
            logger.info(f"✅ Successfully extracted full article: {len(full_content)} chars")
            logger.info("Using full article as source material for factual rewrite")
        elif full_content and len(full_content) >= 300:
            logger.info(f"⚠️ Extracted partial content: {len(full_content)} chars (acceptable)")
        else:
            logger.info(f"❌ Extraction failed or insufficient content, using RSS summary as fallback")
            full_content = article['summary']
            
            # CRITICAL: Skip articles with insufficient source content to prevent hallucination
            if len(full_content) < 300:
                logger.warning(f"Insufficient source content ({len(full_content)} chars), skipping to prevent AI hallucination")
                logger.warning("Need minimum 300 chars of source material for quality article generation")
                return False
        
        # Generate SEO article with betting section
        seo_article = create_seo_article(article['title'], full_content, keywords, article['source'], article['link'])
        
        # Detect article type for image generation
        title_lower = seo_article['title'].lower()
        if any(kw in title_lower for kw in ['boycott', 'ban', 'suspended', 'controversy', 'protest', 'political']):
            article_type = "political"
        elif any(kw in title_lower for kw in ['transfer', 'signs', 'joins', 'deal', 'contract', '£', '$']):
            article_type = "transfer"
        elif any(kw in title_lower for kw in ['injury', 'injured', 'ruled out', 'sidelined', 'fitness']):
            article_type = "injury"
        elif any(kw in title_lower for kw in ['vs', 'v ', 'beat', 'defeat', 'win', 'loss', 'draw', 'final', 'semi-final']):
            article_type = "match"
        else:
            article_type = "news"
        
        logger.info(f"Article type detected: {article_type}")
        
        # NEW PIPELINE: Use ThumbnailSpec + PromptBuilder for perfect image generation
        image_data = None
        media_id = None
        
        # Extract ThumbnailSpec from seo_article (Claude generated it)
        thumbnail_spec = seo_article.get('thumbnail_spec', {})
        
        if thumbnail_spec:
            logger.info(f"Using ThumbnailSpec: {thumbnail_spec.get('topic', 'unknown')}")
            
            # Validate spec
            if PromptBuilder.validate_spec(thumbnail_spec):
                # Build Z-Image Turbo prompt from ThumbnailSpec
                prompt = PromptBuilder.build_prompt(thumbnail_spec)
                logger.info(f"Built prompt ({len(prompt)} chars) for {thumbnail_spec.get('layout', 'unknown')} layout")
                
                # Generate image with APIFree.ai
                if apifree_client.enabled:
                    logger.info("Generating image with APIFree.ai using ThumbnailSpec prompt")
                    image_data = apifree_client.generate_image(prompt, width=1280, height=720, num_inference_steps=8)
                    if image_data:
                        logger.info("✅ APIFree.ai image generated successfully with ThumbnailSpec")
            else:
                logger.warning("ThumbnailSpec validation failed, falling back to old method")
        
        # Fallback to old method if ThumbnailSpec not available or failed
        if not image_data and apifree_client.enabled:
            logger.info(f"Fallback: Generating {article_type} image with old method")
            image_data = apifree_client.generate_sports_image(seo_article['title'], article_type)
            if image_data:
                logger.info("APIFree.ai image generated successfully (fallback)")
        
        # Fallback to Cloudflare if APIFree fails
        if not image_data and cf_client.enabled:
            logger.info("APIFree.ai unavailable, using Cloudflare Flux fallback")
            image_data = cf_client.generate_image(seo_article['title'])
            if image_data:
                logger.info("Cloudflare Flux image generated successfully")
        
        # Last resort: Extract from source (if allowed - COPYRIGHT RISK)
        if not image_data and ALLOW_SOURCE_IMAGES:
            logger.warning("All AI generators unavailable, extracting from source (COPYRIGHT RISK)")
            image_data = extract_image_from_url(article['link'])
        elif not image_data:
            logger.warning("No image generated - all generators unavailable")
        
        # Optimize and upload image with SEO-friendly filename
        if image_data:
            optimized = optimize_image(image_data)
            if optimized:
                # Generate SEO-friendly filename from title
                # Convert title to lowercase, replace spaces with hyphens, remove special chars
                import re
                seo_filename = re.sub(r'[^a-z0-9-]', '', seo_article['title'].lower().replace(' ', '-').replace('--', '-'))
                seo_filename = seo_filename[:50]  # Limit length
                seo_filename = f"{seo_filename}.avif"
                
                try:
                    media_id = wp_client.upload_media(optimized, seo_filename)
                    logger.info(f"Uploaded featured image: {seo_filename}")
                except Exception as e:
                    logger.warning(f"Failed to upload image: {e}")
                    media_id = None
        else:
            logger.warning("Publishing article without image")
        
        # Add analytics tracking
        final_content = add_analytics_tracking(seo_article['content'], seo_article['title'])
        
        # Detect categories and tags
        detected_categories, detected_tags = detect_categories_and_tags(seo_article['title'], seo_article['content'])
        
        # Get WordPress categories
        wp_categories = wp_client.get_categories()
        category_ids = []
        for cat_name in detected_categories:
            if cat_name.lower() in wp_categories:
                category_ids.append(wp_categories[cat_name.lower()])
        
        # Get or create tags
        tag_ids = []
        for tag_name in detected_tags:
            tag_id = wp_client.get_or_create_tag(tag_name)
            if tag_id:
                tag_ids.append(tag_id)
        
        # Set publish date to current time
        from datetime import datetime
        publish_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        
        logger.info(f"Categories: {detected_categories} (IDs: {category_ids})")
        logger.info(f"Tags: {detected_tags} (IDs: {tag_ids})")
        
        # Publish to WordPress
        try:
            post_id, post_url = wp_client.create_post(
                title=seo_article['title'],
                content=final_content,
                featured_media=media_id,
                categories=category_ids,
                tags=tag_ids,
                date=publish_date
            )
            
            # Mark as processed
            mark_processed(article['link'], seo_article['title'], post_id)
            
            logger.info(f"Published with betting content: {post_url}")
            return True
        except RetryError as e:
            logger.error(f"WordPress API failed after retries: {e}")
            logger.error("This usually means: authentication failed, permission denied, or REST API is disabled")
            return False
        except Exception as e:
            logger.error(f"WordPress error: {e}")
            logger.error(f"Failed to create post: {seo_article['title'][:60]}")
            return False
        
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
        apifree_client = APIFreeClient()  # Primary image generator
        cf_client = CloudflareClient()    # Fallback image generator
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
            if process_article(article, serper, apifree_client, cf_client, wp_client):
                success_count += 1
                time.sleep(ARTICLE_DELAY_SECONDS)  # Rate limiting
        
        logger.info(f"Completed: {success_count}/{len(articles)} articles published")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
