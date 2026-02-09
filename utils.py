# (Security/DB/Logging)
import os, sqlite3, hashlib, re, logging
from contextlib import contextmanager
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DB_PATH = os.getenv('DB_PATH', 'news_cache.db')

@contextmanager
def get_db():
    """Database context manager with proper error handling"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        conn.close()

def init_database():
    """Initialize database schema"""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY,
                url_hash TEXT UNIQUE,
                title TEXT,
                published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                wp_post_id INTEGER
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_url_hash ON articles(url_hash)')
        logger.info("Database initialized")

def is_duplicate(url):
    """Check if article already processed"""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    with get_db() as conn:
        result = conn.execute('SELECT 1 FROM articles WHERE url_hash = ?', (url_hash,)).fetchone()
        return result is not None

def mark_processed(url, title, wp_post_id=None):
    """Mark article as processed"""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    with get_db() as conn:
        conn.execute('INSERT OR IGNORE INTO articles (url_hash, title, wp_post_id) VALUES (?, ?, ?)',
                     (url_hash, title, wp_post_id))

def validate_env(var, required=True):
    """Validate environment variable"""
    val = os.getenv(var)
    if required and not val:
        logger.error(f"Missing required env: {var}")
        raise ValueError(f"{var} required")
    return val

def sanitize_html(content):
    """Basic HTML sanitization"""
    if not content:
        return ""
    # Remove script tags
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    # Remove dangerous attributes
    content = re.sub(r'\s(on\w+)="[^"]*"', '', content, flags=re.IGNORECASE)
    return content.strip()
