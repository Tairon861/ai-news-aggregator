import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import pytz
import time

# Your RSS feeds - Start with these essential ones
FEEDS = [
    # AI Companies
    'https://openai.com/blog/rss.xml',
    'https://www.anthropic.com/rss.xml',
    'https://blog.google/technology/ai/rss/',
    'https://ai.meta.com/blog/rss/',
    'https://blogs.microsoft.com/ai/feed/',
    'https://huggingface.co/blog/feed.xml',
    
    # Tech News
    'https://techcrunch.com/category/artificial-intelligence/feed/',
    'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml',
    'https://www.artificialintelligence-news.com/feed/',
    
    # Research
    'https://arxiv.org/rss/cs.AI',
    'https://arxiv.org/rss/cs.LG',
    
    # European AI
    'https://digital-strategy.ec.europa.eu/en/library/rss.xml',
    
    # Add more feeds here as needed
    'https://www.wired.com/feed/category/ai/latest/rss',
    'https://venturebeat.com/category/ai/feed/',
    'https://www.technologyreview.com/feed/',
    'https://blogs.nvidia.com/ai/feed/',
]

def aggregate_feeds():
    print("Starting feed aggregation...")
    
    fg = FeedGenerator()
    fg.id('https://github.com/Tairon861/ai-news-aggregator')
    fg.title('AI News Aggregator')
    fg.link(href='https://Tairon861.github.io/ai-news-aggregator/feed.xml', rel='self')
    fg.descripti
