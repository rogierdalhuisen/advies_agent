#!/bin/bash
# Monthly update script: Scrape insurance websites and re-ingest into Qdrant
#
# This script should be run monthly to keep the knowledge base up-to-date.
# It can be automated via cron:
#   0 2 1 * * /path/to/advies_agent/scripts/monthly_update.sh

set -e  # Exit on error

echo "🗓️  Starting monthly insurance data update"
echo "=========================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Step 1: Scrape insurance websites
echo "📡 Step 1: Scraping insurance websites..."
python scripts/scrape_insurance_data.py

if [ $? -ne 0 ]; then
    echo "❌ Scraping failed. Aborting update."
    exit 1
fi

echo ""
echo "✅ Scraping complete"
echo ""

# Step 2: Re-ingest documents into Qdrant
echo "💾 Step 2: Re-ingesting documents into Qdrant..."
python scripts/ingest_documents.py --recreate

if [ $? -ne 0 ]; then
    echo "❌ Ingestion failed. Please check the logs."
    exit 1
fi

echo ""
echo "✅ Ingestion complete"
echo ""

# Step 3: Verify collection
echo "🔍 Step 3: Verifying Qdrant collection..."
python -c "
from src.retrieval.qdrant_client import QdrantRetriever
retriever = QdrantRetriever()
result = retriever.search('test query', top_k=1)
print(f'✅ Collection is queryable. Found {len(result)} results.')
"

echo ""
echo "=========================================="
echo "✅ Monthly update complete!"
echo ""
echo "📊 Summary:"
echo "  • Insurance websites scraped"
echo "  • Documents re-ingested into Qdrant"
echo "  • Knowledge base is up-to-date"
echo ""
