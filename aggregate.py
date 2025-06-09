import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone, timedelta
import pytz
import time
import json
import os

# Your Full-Text RSS feeds via BazQux
FEEDS = [
    # Tech News - Full Text
    'https://ftr.bazqux.com/makefulltextfeed.php?url=https%3A%2F%2Ftechcrunch.com%2Fcategory%2Fartificial-intelligence%2Ffeed%2F&max=20&links=remove&exc=',
    'https://ftr.bazqux.com/makefulltextfeed.php?url=https%3A%2F%2Fventurebeat.com%2Fcategory%2Fai%2Ffeed%2F&max=20&links=remove&exc=',
    'https://ftr.bazqux.com/makefulltextfeed.php?url=https%3A%2F%2Faisafety.substack.com%2Ffeed&max=20&links=preserve&exc=',
    'https://ftr.bazqux.com/makefulltextfeed.php?url=https%3A%2F%2Fwww.technologyreview.com%2Ftopic%2Fartificial-intelligence%2Ffeed%2F&max=20&links=remove&exc=',
    'https://ftr.bazqux.com/makefulltextfeed.php?url=https%3A%2F%2Fwww.wired.com%2Ffeed%2Fcategory%2Fartificial-intelligence%2Frss&max=20&links=remove&exc=',
    'https://ftr.bazqux.com/makefulltextfeed.php?url=https%3A%2F%2Fwww.unite.ai%2Ffeed%2F&max=20&links=remove&exc=',
    
    # AI Company Blogs - Full Text
    'https://ftr.bazqux.com/makefulltextfeed.php?url=googleaiblog.blogspot.com%2Fatom.xml&max=20&links=remove&exc=',
    'https://ftr.bazqux.com/makefulltextfeed.php?url=https%3A%2F%2Fdeepmind.com%2Fblog%2Ffeed%2Fbasic%2F&max=20&links=remove&exc=',
    'https://ftr.bazqux.com/makefulltextfeed.php?url=https%3A%2F%2Fhuggingface.co%2Fblog%2Ffeed.xml&max=20&links=remove&exc=',
    'https://ftr.bazqux.com/makefulltextfeed.php?url=https%3A%2F%2Ffeeds.feedburner.com%2Fnvidiablog&max=20&links=remove&exc=',
    
    # Research & Academic - Full Text
    'https://ftr.bazqux.com/makefulltextfeed.php?url=https%3A%2F%2Fwww.microsoft.com%2Fen-us%2Fresearch%2Ffeed%2F&max=20&links=remove&exc=',
    'https://ftr.bazqux.com/makefulltextfeed.php?url=https%3A%2F%2Fnews.mit.edu%2Frss%2Ftopic%2Fartificial-intelligence2&max=20&links=remove&exc=',
    'https://ftr.bazqux.com/makefulltextfeed.php?url=https%3A%2F%2Fbair.berkeley.edu%2Fblog%2Ffeed.xml&max=20&links=remove&exc=',
    'https://ftr.bazqux.com/makefulltextfeed.php?url=https%3A%2F%2Fthegradient.pub%2Frss%2F&max=20&links=remove&exc=',
    'https://ftr.bazqux.com/makefulltextfeed.php?url=https%3A%2F%2Fresearch.google%2Fblog%2Frss&max=20&links=remove&exc=',
    'https://ftr.bazqux.com/makefulltextfeed.php?url=https%3A%2F%2Fwww.technologyreview.com%2Ffeed%2F&max=20&links=remove&exc=',
]

# Configuration
HOURS_TO_KEEP = 12  # Keep articles from last 12 hours
MAX_ARTICLES = 100  # Maximum articles to keep in feed

def load_processed_articles():
    """Load the list of articles we've already seen"""
    if os.path.exists('processed_articles.json'):
        with open('processed_articles.json', 'r') as f:
            return json.load(f)
    return {'seen_urls': set(), 'last_update': None}

def save_processed_articles(data):
    """Save the list of processed articles"""
    # Convert set to list for JSON serialization
    data['seen_urls'] = list(data['seen_urls'])
    with open('processed_articles.json', 'w') as f:
        json.dump(data, f, indent=2)

def aggregate_feeds():
    print("Starting feed aggregation...")
    print(f"Processing {len(FEEDS)} full-text feeds")
    
    # Load processed articles history
    processed_data = load_processed_articles()
    seen_urls = set(processed_data.get('seen_urls', []))
    print(f"Previously seen articles: {len(seen_urls)}")
    
    # Calculate cutoff date
    cutoff_date = datetime.now(timezone.utc) - timedelta(hours=HOURS_TO_KEEP)
    print(f"Keeping articles newer than: {cutoff_date}")
    
    fg = FeedGenerator()
    fg.id('https://github.com/Tairon861/ai-news-aggregator')
    fg.title('AI News Aggregator - Full Text')
    fg.link(href='https://Tairon861.github.io/ai-news-aggregator/feed.xml', rel='self')
    fg.description('Recent AI News with Full Content')
    fg.language('en')
    
    all_entries = []
    current_run_urls = set()
    
    for feed_url in FEEDS:
        try:
            print(f"Fetching: BazQux full-text feed...")
            feed = feedparser.parse(feed_url)
            
            if hasattr(feed, 'bozo') and feed.bozo:
                print(f"Warning: Feed might have errors")
            
            entries_added = 0
            
            for entry in feed.entries[:10]:  # Max 10 per feed
                # Skip if we've already processed this URL in this run
                link = entry.get('link', '')
                if link in current_run_urls or not link:
                    continue
                    
                current_run_urls.add(link)
                
                # Check if article is recent enough
                published = entry.get('published_parsed')
                if published:
                    pub_date = datetime.fromtimestamp(
                        time.mktime(published),
                        tz=timezone.utc
                    )
                    if pub_date < cutoff_date:
                        print(f"  Skipping old article: {entry.get('title', '')[:50]}...")
                        continue
                
                # Get content - BazQux provides full content
                content = (
                    entry.get('content', [{}])[0].get('value', '') or
                    entry.get('description', '') or
                    entry.get('summary', 'No content available')
                )
                
                # Extract source from title or feed
                source = feed.feed.get('title', 'Unknown Source')
                # Clean BazQux prefix from source if present
                if source.startswith('FTR: '):
                    source = source[5:]
                
                # CHECK IF THIS IS A NEW ARTICLE
                is_new = link not in seen_urls
                
                # Extract and clean data
                entry_data = {
                    'title': entry.get('title', 'No title'),
                    'link': link,
                    'content': content,  # Full content from BazQux
                    'published': published,
                    'source': source,
                    'is_new': is_new  # Mark if this is completely new
                }
                
                all_entries.append(entry_data)
                entries_added += 1
                
            print(f"  Added {entries_added} entries")
                
        except Exception as e:
            print(f"Error with feed: {str(e)}")
            continue
        
        # Small delay to be nice to servers
        time.sleep(0.5)
    
    print(f"Total collected: {len(all_entries)} articles")
    
    # Sort by date (newest first)
    all_entries.sort(
        key=lambda x: x['published'] if x['published'] else 0, 
        reverse=True
    )
    
    # Keep only the most recent articles
    all_entries = all_entries[:MAX_ARTICLES]
    
    # Count new articles
    new_articles = sum(1 for entry in all_entries if entry.get('is_new', False))
    print(f"Brand new articles: {new_articles}")
    
    # Add entries to feed
    for entry in all_entries:
        fe = fg.add_entry()
        fe.id(entry['link'])
        
        # Mark NEW articles clearly in title
        title = entry['title']
        if entry.get('is_new', False):
            title = "[NEW] " + title
        
        # Add source
        title = f"{title} ({entry['source']})"
        
        fe.title(title)
        fe.link(href=entry['link'])
        
        # Full content
        fe.description(entry['content'])
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
    
    # Update seen URLs - add all current URLs to the set
    for entry in all_entries:
        seen_urls.add(entry['link'])
    
    # Save updated tracking data
    processed_data = {
        'seen_urls': seen_urls,
        'last_update': datetime.now(timezone.utc).isoformat(),
        'total_seen': len(seen_urls),
        'new_this_run': new_articles
    }
    save_processed_articles(processed_data)
    
    # Save feed
    fg.rss_file('feed.xml')
    print("Feed saved to feed.xml")
    
    # Verify file was created
    if os.path.exists('feed.xml'):
        file_size = os.path.getsize('feed.xml')
        print(f"Success! Feed file created: {file_size} bytes")
        print(f"Feed contains {len(all_entries)} articles (max {MAX_ARTICLES})")
        print(f"Articles marked as [NEW]: {new_articles}")
    else:
        print("ERROR: feed.xml was not created!")

# Run the script
if __name__ == '__main__':
    print("=== RSS Aggregator Starting ===")
    try:
        aggregate_feeds()
        print("=== RSS Aggregator Completed Successfully ===")
    except Exception as e:
        print(f"=== ERROR: {str(e)} ===")
        raise
