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
]

def aggregate_feeds():
    print("Starting feed aggregation...")
    
    fg = FeedGenerator()
    fg.id('https://github.com/Tairon861/ai-news-aggregator')
    fg.title('AI News Aggregator')
    fg.link(href='https://Tairon861.github.io/ai-news-aggregator/feed.xml', rel='self')
    fg.description('Aggregated AI News from Top Sources')
    fg.language('en')
    
    all_entries = []
    seen_urls = set()
    
    for feed_url in FEEDS:
        try:
            print(f"Fetching: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            # Check if feed was parsed successfully
            if hasattr(feed, 'bozo') and feed.bozo:
                print(f"Warning: Feed might have errors: {feed_url}")
            
            for entry in feed.entries[:10]:  # Max 10 per feed
                # Skip if we've seen this URL
                link = entry.get('link', '')
                if link in seen_urls or not link:
                    continue
                    
                seen_urls.add(link)
                
                # Extract and clean data
                entry_data = {
                    'title': entry.get('title', 'No title'),
                    'link': link,
                    'summary': entry.get('summary', entry.get('description', 'No summary')),
                    'published': entry.get('published_parsed'),
                    'source': feed.feed.get('title', 'Unknown Source')
                }
                
                all_entries.append(entry_data)
                
        except Exception as e:
            print(f"Error with {feed_url}: {str(e)}")
            continue
        
        # Small delay to be nice to servers
        time.sleep(0.5)
    
    print(f"Collected {len(all_entries)} unique entries")
    
    # Sort by date (newest first)
    all_entries.sort(
        key=lambda x: x['published'] if x['published'] else 0, 
        reverse=True
    )
    
    # Add entries to feed
    for entry in all_entries[:100]:  # Top 100 items
        fe = fg.add_entry()
        fe.id(entry['link'])
        fe.title(f"{entry['title']} ({entry['source']})")
        fe.link(href=entry['link'])
        fe.description(entry['summary'][:500] + '...' if len(entry['summary']) > 500 else entry['summary'])
        
        if entry['published']:
            try:
                dt = datetime.fromtimestamp(
                    time.mktime(entry['published']),
                    tz=timezone.utc
                )
                fe.published(dt)
            except:
                pass
    
    # Save feed
    fg.rss_file('feed.xml')
    print("Feed generated successfully!")

if __name__ == '__main__':
    aggregate_feeds()
