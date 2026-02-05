"""
Advanced Article Extraction Module
Uses multiple professional libraries to extract full article content
"""

import requests
from newspaper import Article
import trafilatura
from readability import Document
from bs4 import BeautifulSoup
import re
from utils import logger


class ArticleExtractor:
    """
    Multi-strategy article extractor using professional libraries
    Tries multiple methods to ensure we get the full article
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def extract(self, url):
        """
        Extract full article using multiple strategies
        Returns the longest/best extraction
        """
        logger.info(f"Extracting article from: {url}")
        
        results = []
        
        # Strategy 1: newspaper3k (best for news sites)
        try:
            content = self._extract_with_newspaper(url)
            if content:
                results.append(('newspaper3k', content))
                logger.info(f"newspaper3k extracted: {len(content)} chars")
        except Exception as e:
            logger.debug(f"newspaper3k failed: {e}")
        
        # Strategy 2: trafilatura (excellent for general articles)
        try:
            content = self._extract_with_trafilatura(url)
            if content:
                results.append(('trafilatura', content))
                logger.info(f"trafilatura extracted: {len(content)} chars")
        except Exception as e:
            logger.debug(f"trafilatura failed: {e}")
        
        # Strategy 3: readability (good for complex layouts)
        try:
            content = self._extract_with_readability(url)
            if content:
                results.append(('readability', content))
                logger.info(f"readability extracted: {len(content)} chars")
        except Exception as e:
            logger.debug(f"readability failed: {e}")
        
        # Strategy 4: Custom BeautifulSoup (fallback)
        try:
            content = self._extract_with_beautifulsoup(url)
            if content:
                results.append(('beautifulsoup', content))
                logger.info(f"beautifulsoup extracted: {len(content)} chars")
        except Exception as e:
            logger.debug(f"beautifulsoup failed: {e}")
        
        # Return the longest extraction (usually the most complete)
        if results:
            best_method, best_content = max(results, key=lambda x: len(x[1]))
            logger.info(f"✅ Best extraction: {best_method} with {len(best_content)} chars")
            return best_content
        
        logger.warning(f"❌ All extraction methods failed for {url}")
        return None
    
    def _extract_with_newspaper(self, url):
        """
        Extract using newspaper3k library
        Excellent for news sites, handles JavaScript
        """
        article = Article(url)
        article.download()
        article.parse()
        
        # Get full text
        text = article.text
        
        # Add title if not in text
        if article.title and article.title not in text:
            text = f"{article.title}\n\n{text}"
        
        # Clean and validate
        text = self._clean_text(text)
        
        if len(text) > 300:
            return text
        return None
    
    def _extract_with_trafilatura(self, url):
        """
        Extract using trafilatura library
        Excellent for general articles, very accurate
        """
        # Download page
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None
        
        # Extract with all features enabled
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            favor_precision=False,  # Favor recall to get more content
            favor_recall=True
        )
        
        if text:
            text = self._clean_text(text)
            if len(text) > 300:
                return text
        
        return None
    
    def _extract_with_readability(self, url):
        """
        Extract using readability-lxml
        Good for complex layouts and paywalls
        """
        response = self.session.get(url, timeout=20)
        response.raise_for_status()
        
        # Use readability to extract main content
        doc = Document(response.content)
        html_content = doc.summary()
        
        # Parse HTML to text
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'aside']):
            tag.decompose()
        
        # Get text from paragraphs
        paragraphs = soup.find_all('p')
        text = '\n\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])
        
        # Add title if available
        title = doc.title()
        if title and title not in text:
            text = f"{title}\n\n{text}"
        
        text = self._clean_text(text)
        
        if len(text) > 300:
            return text
        return None
    
    def _extract_with_beautifulsoup(self, url):
        """
        Custom extraction using BeautifulSoup
        Fallback method with multiple strategies
        """
        response = self.session.get(url, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'aside', 'header', 'iframe']):
            tag.decompose()
        
        # Remove ads and widgets
        for class_name in ['ad', 'advertisement', 'social', 'related', 'comments', 'sidebar']:
            for tag in soup.find_all(class_=lambda x: x and class_name in str(x).lower()):
                tag.decompose()
        
        text = None
        
        # Try article tag
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            text = '\n\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])
        
        # Try main tag
        if not text or len(text) < 300:
            main = soup.find('main')
            if main:
                paragraphs = main.find_all('p')
                text = '\n\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])
        
        # Try content divs
        if not text or len(text) < 300:
            content_divs = soup.find_all('div', class_=re.compile(r'(content|article|story|post)', re.I))
            for div in content_divs:
                paragraphs = div.find_all('p')
                temp_text = '\n\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])
                if len(temp_text) > len(text or ''):
                    text = temp_text
        
        # Try all paragraphs as last resort
        if not text or len(text) < 300:
            all_paragraphs = soup.find_all('p')
            text = '\n\n'.join([p.get_text().strip() for p in all_paragraphs if len(p.get_text().strip()) > 50])
        
        if text:
            text = self._clean_text(text)
            if len(text) > 300:
                return text
        
        return None
    
    def _clean_text(self, text):
        """Clean extracted text"""
        if not text:
            return None
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove common boilerplate
        boilerplate_patterns = [
            r'Click here to.*?(?=\n|$)',
            r'Read more:.*?(?=\n|$)',
            r'Subscribe to.*?(?=\n|$)',
            r'Follow us on.*?(?=\n|$)',
            r'Sign up for.*?(?=\n|$)',
            r'Advertisement\s*',
            r'ADVERTISEMENT\s*',
        ]
        
        for pattern in boilerplate_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '', text)
        
        # Clean up spacing
        text = text.strip()
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text


# Global instance
_extractor = None

def get_extractor():
    """Get or create global extractor instance"""
    global _extractor
    if _extractor is None:
        _extractor = ArticleExtractor()
    return _extractor


def extract_article(url):
    """
    Extract full article content from URL
    
    Args:
        url: Article URL
    
    Returns:
        str: Full article text (500-5000 chars typically)
        None: If extraction failed
    """
    extractor = get_extractor()
    return extractor.extract(url)
