import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import pytz
import time

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

def aggregate_feeds():
    print("Starting feed aggregation...")
    print(f"Processing {len(FEEDS)} full-text feeds")
    
    fg = FeedGenerator()
    fg.id('https://github.com/Tairon861/ai-news-aggregator')
    fg.title('AI News Aggregator - Full Text')
    fg.link(href='https://Tairon861.github.io/ai-news-aggregator/feed.xml', rel='self')
    fg.description('Aggregated AI News with Full Content')
    fg.language('en')
    
    all_entries = []
    seen_urls = set()
    
    for feed_url in FEEDS:
        try:
            print(f"Fetching: BazQux full-text feed...")
            feed = feedparser.parse(feed_url)
            
            if hasattr(feed, 'bozo') and feed.bozo:
                print(f"Warning: Feed might have errors")
            
            entries_added = 0
            
            for entry in feed.entries[:10]:  # Max 10 per feed
                # Skip if we've seen this URL
                link = entry.get('link', '')
                if link in seen_urls or not link:
                    continue
                    
                seen_urls.add(link)
                
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
                
                # Extract and clean data
                entry_data = {
                    'title': entry.get('title', 'No title'),
                    'link': link,
                    'content': content,  # Full content from BazQux
                    'published': entry.get('published_parsed'),
                    'source': source
                }
                
                all_entries.append(entry_data)
                entries_added += 1
                
            print(f"  Added {entries_added} entries")
                
        except Exception as e:
            print(f"Error with feed: {str(e)}")
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
        
        # Full content - no truncation needed!
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
    
    # Save feed
    fg.rss_file('feed.xml')
    print("Feed saved to feed.xml")
    
    # Verify file was created
    import os
    if os.path.exists('feed.xml'):
        file_size = os.path.getsize('feed.xml')
        print(f"Success! Feed file created: {file_size} bytes")
        with open('feed.xml', 'r', encoding='utf-8') as f:
            content_preview = f.read(500)
            print(f"Preview: {content_preview[:200]}...")
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
