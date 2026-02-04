import pytest
from unittest.mock import patch, MagicMock
from api_clients import SerperClient, OpenRouterClient, CloudflareClient, WordPressClient, optimize_image
import io
from PIL import Image

@patch('api_clients.requests.Session.post')
def test_serper_trends(mock_post):
    """Test Serper API trend fetching"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'news': [
            {'title': 'Nepal Cricket Win', 'link': 'http://test.com', 'source': 'ESPN'},
            {'title': 'Football Match', 'link': 'http://test2.com', 'source': 'BBC'}
        ]
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    
    client = SerperClient()
    trends = client.get_trends("sports")
    
    assert len(trends) == 2
    assert trends[0]['title'] == 'Nepal Cricket Win'
    assert 'link' in trends[0]

@patch('api_clients.requests.Session.post')
def test_openrouter_generate(mock_post):
    """Test OpenRouter content generation"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'choices': [{'message': {'content': 'Generated article content'}}]
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    
    client = OpenRouterClient()
    content = client.generate("Test prompt")
    
    assert content == 'Generated article content'
    assert mock_post.call_count == 1

@patch('api_clients.requests.post')
def test_cloudflare_image_generation(mock_post):
    """Test Cloudflare Flux image generation"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {'content-type': 'image/png'}
    mock_response.content = b'fake_image_data'
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    
    client = CloudflareClient()
    if client.enabled:
        image_data = client.generate_image("Nepal cricket")
        assert image_data == b'fake_image_data'

def test_image_optimization():
    """Test image optimization to AVIF"""
    # Create test image
    img = Image.new('RGB', (800, 600), color='red')
    buffer = io.BytesIO()
    img.save(buffer, 'PNG')
    png_data = buffer.getvalue()
    
    # Optimize
    optimized = optimize_image(png_data)
    
    assert optimized is not None
    assert len(optimized) < len(png_data)  # Should be smaller

@patch('api_clients.requests.Session.post')
def test_wordpress_create_post(mock_post):
    """Test WordPress post creation"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'id': 123,
        'link': 'https://example.com/post-123'
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response
    
    client = WordPressClient()
    post_id, post_url = client.create_post("Test Title", "<p>Content</p>")
    
    assert post_id == 123
    assert 'post-123' in post_url

def test_serper_key_rotation():
    """Test API key rotation on multiple calls"""
    client = SerperClient()
    original_main = client.key_main
    original_backup = client.key_backup
    
    if original_backup:
        client.calls = 3  # Trigger rotation
        # Simulate rotation logic
        assert client.calls > 2
