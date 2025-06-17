import os
import json
from pinecone import Pinecone
from datetime import datetime
from sentence_transformers import SentenceTransformer
import hashlib
import feedparser
import time

class FreeVectorDB:
    def __init__(self):
        # Initialize Pinecone with new API
        pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        self.index = pc.Index("ai-news-rag")
        
        # Free embedding model (384 dimensions)
        print("Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load processed articles tracking
        self.processed_file = 'processed_vectors.json'
        self.processed_ids = self.load_processed()
    
    def load_processed(self):
        """Load list of already processed article IDs"""
        if os.path.exists(self.processed_file):
            with open(self.processed_file, 'r') as f:
                return set(json.load(f))
        return set()
    
    def save_processed(self):
        """Save processed article IDs"""
        with open(self.processed_file, 'w') as f:
            json.dump(list(self.processed_ids), f)
    
    def process_articles(self, articles_file='feed.xml'):
        """Process new articles from RSS feed"""
        print(f"Processing articles from {articles_file}")

        # TEMPORARY: Reset for testing - REMOVE THIS AFTER TESTING!
        self.processed_ids = set()
        print("TESTING MODE: Reset processed IDs - all articles will be processed")
        
        # Parse RSS feed
        feed = feedparser.parse(articles_file)
        print(f"Found {len(feed.entries)} articles in feed")
        
        vectors = []
        new_articles = 0
        
        for entry in feed.entries:
            # Create unique ID from URL
            article_id = hashlib.md5(entry.link.encode()).hexdigest()[:16]
            
            # Skip if already processed
            if article_id in self.processed_ids:
                continue
            
            # Extract clean title (remove [NEW] marker if present)
            title = entry.title.replace('[NEW] ', '')
            
            # Extract source from title
            source = "Unknown"
            if '(' in title and ')' in title:
                source = title[title.rfind('(')+1:title.rfind(')')]
                title = title[:title.rfind('(')].strip()
            
            # Create text for embedding (title + beginning of content)
            embed_text = f"{title}\n\n{entry.description[:500]}"
            
            # Create embedding
            embedding = self.model.encode(embed_text).tolist()
            
            # Prepare metadata
            metadata = {
                "title": title[:200],  # Pinecone has metadata limits
                "url": entry.link[:500],
                "content": entry.description[:2000],  # Store first 2000 chars
                "source": source[:50],
                "date": entry.get('published', str(datetime.now()))[:50]
            }
            
            # Add to batch
            vectors.append({
                "id": article_id,
                "values": embedding,
                "metadata": metadata
            })
            
            self.processed_ids.add(article_id)
            new_articles += 1
            
            # Batch upload every 10 articles
            if len(vectors) >= 10:
                self.upload_batch(vectors)
                vectors = []
        
        # Upload remaining vectors
        if vectors:
            self.upload_batch(vectors)
        
        # Save processed IDs
        self.save_processed()
        
        print(f"Processing complete! Added {new_articles} new articles")
        print(f"Total articles in tracking: {len(self.processed_ids)}")
        
        # Show index stats
        stats = self.index.describe_index_stats()
        print(f"Total vectors in Pinecone: {stats.total_vector_count}")
    
    def upload_batch(self, vectors):
        """Upload batch of vectors to Pinecone"""
        try:
            print(f"Uploading batch of {len(vectors)} vectors...")
            self.index.upsert(vectors=vectors)
            time.sleep(1)  # Be nice to free tier
        except Exception as e:
            print(f"Error uploading batch: {e}")
    
    def search(self, query, top_k=10, date_filter=None):
        """Search for similar articles"""
        print(f"Searching for: {query}")
        
        # Create query embedding
        query_embedding = self.model.encode(query).tolist()
        
        # Build filter if date provided
        filter_dict = {}
        if date_filter:
            filter_dict["date"] = {"$gte": date_filter}
        
        # Search Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict if filter_dict else None
        )
        
        return results['matches']
    
    def get_stats(self):
        """Get index statistics"""
        return self.index.describe_index_stats()

if __name__ == "__main__":
    # Initialize database
    db = FreeVectorDB()
    
    # Process articles
    db.process_articles()
    
    # Test search
    print("\n=== Testing Search ===")
    results = db.search("OpenAI GPT", top_k=5)
    for i, match in enumerate(results):
        print(f"\n{i+1}. {match['metadata']['title']}")
        print(f"   Score: {match['score']:.3f}")
        print(f"   Source: {match['metadata']['source']}")
