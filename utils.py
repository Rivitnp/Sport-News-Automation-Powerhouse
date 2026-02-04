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

@context
