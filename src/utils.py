# (Security/DB/Logging)
import os
import sqlite3
import hashlib
import re
import logging
from contextlib import contextmanager

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
    """Clean HTML and remove unwanted content"""
    if not content:
        return ""
    
    # Remove script tags
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove dangerous attributes
    content = re.sub(r'\s(on\w+)="[^"]*"', '', content, flags=re.IGNORECASE)
    
    # Remove copyright notices and footers
    content = re.sub(r'©\s*\d{4}[^<]*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'Copyright\s*\d{4}[^<]*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<footer[^>]*>.*?</footer>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove "Sports News" or similar generic footers
    content = re.sub(r'©.*?Sports News.*?(?=<|$)', '', content, flags=re.IGNORECASE)
    
    # Remove empty paragraphs
    content = re.sub(r'<p>\s*</p>', '', content)
    content = re.sub(r'<p>\s*&nbsp;\s*</p>', '', content)
    
    # Remove multiple consecutive line breaks
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip()
