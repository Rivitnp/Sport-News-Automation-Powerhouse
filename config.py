"""Configuration for Nepal Sports News Bot"""

# RSS Feeds - Prioritized for Cricket & Football (Nepal/India focus)
RSS_FEEDS = [
    # Cricket (Priority 1)
    'https://www.espncricinfo.com/rss/content/story/feeds/0.xml',
    'https://www.cricbuzz.com/rss-feed/cricket-news',
    'https://sports.ndtv.com/rss/cricket',
    
    # Football (Priority 2)
    'https://www.goal.com/feeds/en/news',
    'https://www.espn.com/espn/rss/soccer/news',
    'https://www.bbc.co.uk/sport/football/rss.xml',
    
    # General Sports (Lower priority)
    'https://sports.yahoo.com/rss/',
    'https://www.theguardian.com/sport/rss',
]

# Sport Priority (for filtering)
PRIORITY_SPORTS = {
    'cricket': 10,      # Highest priority
    'football': 9,      # High priority
    'soccer': 9,        # Same as football
    'ipl': 10,          # Indian Premier League
    'ucl': 9,           # UEFA Champions League
    'premier league': 9,
    'world cup': 10,
    'basketball': 3,    # Lower priority
    'american football': 1,  # Lowest priority
    'nfl': 1,
}

# Betting-related keywords to detect betting opportunities
BETTING_TRIGGERS = [
    'match', 'final', 'semi-final', 'tournament', 'championship',
    'vs', 'defeat', 'win', 'loss', 'upset', 'odds', 'prediction',
    'ucl', 'champions league', 'premier league', 'ipl', 'world cup'
]

# Processing limits (Optimized for 10k visitors/month)
MAX_ARTICLES_PER_RUN = 10  # Increased from 5 to 10
MAX_CONTENT_LENGTH = 3000
MAX_IMAGE_SIZE_MB = 2
ARTICLE_DELAY_SECONDS = 3  # Reduced from 5 to 3 for faster processing

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

# Keywords for Nepal/India context
NEPAL_KEYWORDS = [
    'Nepal cricket betting',
    'India cricket betting',
    'betting site Nepal',
    'football betting tips',
    'UCL betting odds',
    'IPL betting predictions',
    'sports betting Nepal'
]

# Betting branding (customize for your site)
BETTING_BRAND = 'yoursite.com'  # Change to your betting site
BETTING_DISCLAIMER = '⚠️ <strong>18+ Only</strong> | Gamble Responsibly | <a href="https://yoursite.com" target="_blank" rel="nofollow">yoursite.com</a>'

# Google Analytics & SEO
GOOGLE_ANALYTICS_ID = None  # Set via env: GA_MEASUREMENT_ID
GOOGLE_SEARCH_CONSOLE = True  # Enable GSC integration
