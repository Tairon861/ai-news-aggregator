name: RSS Aggregator
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:      # Allows manual trigger

jobs:
  aggregate:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Cache pip packages
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install RSS dependencies
      run: |
        python -m pip install --upgrade pip
        pip install feedparser feedgen pytz
    
    - name: Run RSS aggregator
      run: |
        echo "Starting RSS aggregation..."
        python aggregate.py
    
    - name: Install Vector DB dependencies
      run: |
        echo "Installing vector database dependencies..."
        pip install sentence-transformers pinecone-client feedparser
    
    - name: Update Vector Database
      env:
        PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
        PINECONE_ENV: us-east-1
      run: |
        echo "Updating vector database..."
        python vector.dp.py
    
    - name: Commit and push changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        
        # Add all tracking files
        git add feed.xml processed_articles.json processed_vectors.json
        
        # Check if there are changes to commit
        if git diff --staged --quiet; then
          echo "No changes to commit"
        else
          git commit -m "Update RSS feed - $(date +'%Y-%m-%d %H:%M:%S')"
          git push
        fi
    
    - name: Show summary
      run: |
        echo "Workflow completed!"
        echo "Files updated:"
        ls -la feed.xml processed_articles.json processed_vectors.json 2>/dev/null || true
