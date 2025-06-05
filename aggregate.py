import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import pytz
import time

# Your RSS feeds
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
    
    # Additional Quality Sources
    'https://www.wired.com/feed/category/ai/latest/rss',
    'https://venturebeat.com/category/ai/feed/',
    'https://www.technologyreview.com/feed/',
    'https://blogs.nvidia.com/ai/feed/',
    'https://www.kdnuggets.com/feed',
    'https://bair.berkeley.edu/blog/feed.xml',
]

def aggregate_feeds():
    print("Starting feed aggregation...")
    print(f"Processing {len(FEEDS)} feeds")
    
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
            
            entries_added = 0
            for entry in feed.entries[:10]:  # Max 10 per feed
                # Skip if we've seen this URL
                link = entry.get('link', '')
                if link in seen_urls or not link:
                    continue
                    
                seen_urls.add(link)
                
                # Extract full content from various possible fields
                content = None
                
                # Try different content fields in order of preference
                if 'content' in entry and entry.content:
                    content = entry.content[0].get('value', '')
                elif 'content_encoded' in entry:
                    content = entry.content_encoded
                elif 'description' in entry:
                    content = entry.description
                elif 'summary' in entry:
                    content = entry.summary
                else:
                    content = 'No content available'
                
                # Clean up content if needed
                if not content or content.strip() == '':
                    content = entry.get('summary', entry.get('description', 'No content available'))
                
                # Extract and clean data
                entry_data = {
                    'title': entry.get('title', 'No title'),
                    'link': link,
                    'content': content,  # Full content
                    'published': entry.get('published_parsed'),
                    'source': feed.feed.get('title', 'Unknown Source')
                }
                
                all_entries.append(entry_data)
                entries_added += 1
                
            print(f"  Added {entries_added} entries from {feed_url}")
                
        except Exception as e:
            print(f"Error with {feed_url}: {str(e)}")
            continue
        
        # Small delay to be nice to servers
        time.sleep(0.5)
    
    print(f"Total collected: {len(all_entries)} unique entries")
    
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
        
        # Use full content, no truncation
        fe.description(entry['content'])
        
        # Add content in content tag as well for better compatibility
        fe.content(entry['content'], type='html')
        
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
    print("Feed saved to feed.xml")
    
    # Verify file was created
    import os
    if os.path.exists('feed.xml'):
        file_size = os.path.getsize('feed.xml')
        print(f"Success! Feed file created: {file_size} bytes")
    else:
        print("ERROR: feed.xml was not created!")

# THIS IS THE CRUCIAL PART THAT WAS MISSING!
if __name__ == '__main__':
    print("=== RSS Aggregator Starting ===")
    try:
        aggregate_feeds()
        print("=== RSS Aggregator Completed Successfully ===")
    except Exception as e:
        print(f"=== ERROR: {str(e)} ===")
        raise
