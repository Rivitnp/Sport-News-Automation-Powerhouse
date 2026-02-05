"""Configuration for Sports News Bot"""

import os

# RSS Feeds - Prioritized for sports content
RSS_FEEDS = [
    # Working feeds
    'https://www.bbc.co.uk/sport/football/rss.xml',
    'https://www.theguardian.com/sport/rss',
    'https://sports.yahoo.com/rss/',
    'https://www.skysports.com/rss/12040',
    
    # ESPN feeds (may block scraping)
    'https://www.espncricinfo.com/rss/content/story/feeds/0.xml',
    'https://www.espn.com/espn/rss/cricket/news',
]

# Sport Priority (for filtering)
# Cricket: +5 points, Football/Leagues: +3 points, Other sports: +2 points
PRIORITY_SPORTS = {
    'cricket': 5,       # Cricket priority
    'ipl': 5,           # Indian Premier League
    't20': 5,           # T20 cricket
    'test': 5,          # Test cricket
    'odi': 5,           # ODI cricket
    'football': 3,      # Football priority
    'soccer': 3,        # Same as football
    'ucl': 3,           # UEFA Champions League
    'champions league': 3,
    'premier league': 3,
    'la liga': 3,
    'serie a': 3,
    'bundesliga': 3,
    'basketball': 2,    # Other sports
    'tennis': 2,
    'badminton': 2,
    'hockey': 2,
    'american football': 1,  # Lowest priority
    'nfl': 1,
    'baseball': 1,
}

# Betting-related keywords to detect betting opportunities
BETTING_TRIGGERS = [
    'match', 'final', 'semi-final', 'tournament', 'championship',
    'vs', 'defeat', 'win', 'loss', 'upset', 'odds', 'prediction',
    'ucl', 'champions league', 'premier league', 'ipl', 'world cup'
]

# Processing limits (Optimized for hourly runs)
MAX_ARTICLES_PER_RUN = 1  # 1 article per hour = 24 articles/day
MAX_CONTENT_LENGTH = 3000
MAX_IMAGE_SIZE_MB = 2
ARTICLE_DELAY_SECONDS = 3  # Delay between articles (not needed for 1 article)

# Image settings
IMAGE_WIDTH = 1200
IMAGE_HEIGHT = 675
IMAGE_QUALITY = 85
USE_CLOUDFLARE_IMAGES = True  # Always use AI-generated images to avoid copyright
ALLOW_SOURCE_IMAGES = False   # Set to True only if you want to risk copyright issues

# SEO settings
TITLE_LENGTH = (50, 60)
META_DESC_LENGTH = (150, 160)
ARTICLE_LENGTH = (800, 1200)

# Retry settings
MAX_RETRIES = 3
RETRY_MIN_WAIT = 2
RETRY_MAX_WAIT = 10

# Keywords for local context
LOCAL_KEYWORDS = [
    'cricket betting',
    'football betting tips',
    'betting odds',
    'betting predictions',
    'sports betting'
]

# Betting branding
BETTING_BRAND = os.getenv('BETTING_BRAND', 'betting-site.com')
BETTING_DISCLAIMER = '⚠️ <strong>18+ Only</strong> | Gamble Responsibly'

# Google Analytics & SEO
GOOGLE_ANALYTICS_ID = None  # Set via env: GA_MEASUREMENT_ID
GOOGLE_SEARCH_CONSOLE = True  # Enable GSC integration
