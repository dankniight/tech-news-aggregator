import feedparser
import requests
import json
import os
from datetime import datetime
from typing import List, Dict
import time
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RSS Feed URLs for tech news sources (removed Wired)
RSS_FEEDS = {
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "The Register": "https://www.theregister.com/headlines.atom",
    "TechCrunch": "https://techcrunch.com/feed/",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
    "Futurism": "https://futurism.com/feed"
}

# Number of articles to fetch per source
ARTICLES_PER_SOURCE = 15

# Timeout for HTTP requests
REQUEST_TIMEOUT = 10

def extract_image_from_html(html_content: str) -> str:
    """Extract the first image URL from HTML content"""
    if not html_content:
        return None
    
    # Look for img tags with src attributes
    img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
    match = re.search(img_pattern, html_content, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return None

def extract_image_from_summary(summary: str) -> str:
    """Extract image URL from summary/content"""
    if not summary:
        return None
    
    # Try to extract from img tag in summary
    image_url = extract_image_from_html(summary)
    if image_url:
        return image_url
    
    return None

def extract_featured_image_from_page(url: str) -> str:
    """Extract featured image from the actual article page"""
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
        response.raise_for_status()
        
        # Look for common featured image patterns
        # Open Graph image
        og_image_pattern = r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']'
        match = re.search(og_image_pattern, response.text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Twitter image
        twitter_image_pattern = r'<meta[^>]*name=["\']twitter:image["\'][^>]*content=["\']([^"\']+)["\']'
        match = re.search(twitter_image_pattern, response.text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Article image with common classes
        article_img_pattern = r'<img[^>]*class=["\'][^"\']*(?:featured|hero|main|lead)[^"\']*["\'][^>]*src=["\']([^"\']+)["\']'
        match = re.search(article_img_pattern, response.text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # First image in article content
        content_img_pattern = r'<article[^>]*>.*?<img[^>]+src=["\']([^"\']+)["\']'
        match = re.search(content_img_pattern, response.text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
        
        # Any image in the body
        body_img_pattern = r'<body[^>]*>.*?<img[^>]+src=["\']([^"\']+)["\']'
        match = re.search(body_img_pattern, response.text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
            
    except Exception as e:
        logger.warning(f"Error extracting image from page {url}: {str(e)}")
    
    return None

def fetch_rss_feed(url: str, source_name: str) -> List[Dict]:
    """Fetch and parse RSS feed, returning list of articles with better image extraction"""
    try:
        feed = feedparser.parse(url)
        articles = []
        
        for entry in feed.entries[:ARTICLES_PER_SOURCE]:
            # Extract image URL if available using multiple methods
            image_url = None
            
            # Method 1: Check media_content
            if hasattr(entry, 'media_content') and entry.media_content:
                image_url = entry.media_content[0].get('url')
            
            # Method 2: Check enclosures
            if not image_url and hasattr(entry, 'enclosures') and entry.enclosures:
                for enclosure in entry.enclosures:
                    if enclosure.type.startswith('image/'):
                        image_url = enclosure.href
                        break
            
            # Method 3: Check for media_thumbnail
            if not image_url and hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                image_url = entry.media_thumbnail[0].get('url')
            
            # Method 4: Extract from content/summary
            if not image_url:
                # Check content first (if available)
                if hasattr(entry, 'content') and entry.content:
                    for content_item in entry.content:
                        if content_item.type == 'text/html':
                            image_url = extract_image_from_html(content_item.value)
                            if image_url:
                                break
                
                # If still no image, check summary
                if not image_url and hasattr(entry, 'summary'):
                    image_url = extract_image_from_summary(entry.summary)
            
            # Method 5: Extract from the actual article page if no image found yet
            if not image_url:
                image_url = extract_featured_image_from_page(entry.link)
            
            article = {
                "title": entry.title,
                "link": entry.link,
                "summary": getattr(entry, 'summary', ''),
                "published": getattr(entry, 'published', ''),
                "source": source_name,
                "image_url": image_url
            }
            articles.append(article)
        
        logger.info(f"Fetched {len(articles)} articles from {source_name}")
        return articles
    except Exception as e:
        logger.error(f"Error fetching feed from {source_name}: {str(e)}")
        return []

def aggregate_news() -> List[Dict]:
    """Aggregate news from all sources in chronological order"""
    all_articles = []
    
    for source_name, url in RSS_FEEDS.items():
        articles = fetch_rss_feed(url, source_name)
        all_articles.extend(articles)
        # Be respectful to servers by adding a small delay
        time.sleep(1)
    
    # Sort articles by published date (newest first)
    # Filter out articles without publication dates
    dated_articles = [a for a in all_articles if a['published']]
    dated_articles.sort(key=lambda x: x['published'], reverse=True)
    
    # If articles don't have dates, add them to the end
    undated_articles = [a for a in all_articles if not a['published']]
    dated_articles.extend(undated_articles)
    
    return dated_articles

def save_news_data(articles: List[Dict]):
    """Save aggregated news to JSON file"""
    data = {
        "lastUpdated": datetime.now().isoformat(),
        "articles": articles
    }
    
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    """Main function to run the news aggregator"""
    logger.info("Starting news aggregation")
    articles = aggregate_news()
    save_news_data(articles)
    logger.info(f"Aggregated {len(articles)} articles and saved to news.json")

if __name__ == "__main__":
    main()