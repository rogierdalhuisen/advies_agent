# Insurance Website Scraping Module

This module provides robust web scraping for insurance company documentation pages using **crawl4ai** for scraping and **Gemini Flash** for LLM-based content extraction.

## 🎯 Why LLM-based parsing?

Instead of using brittle CSS selectors that break when pages are redesigned, we use an LLM to intelligently extract clean markdown content. This approach:

- ✅ Works across different page structures with one implementation
- ✅ Robust to page redesigns
- ✅ Filters out navigation, ads, cookie banners automatically
- ✅ Preserves important structure (headings, tables, lists)
- ✅ Extracts only relevant insurance content

## 📁 Module Structure

```
src/ingestion/scraping/
├── __init__.py           # Module exports
├── config.py             # URL configuration for all insurances
├── llm_parser.py         # Gemini Flash-based HTML → Markdown parser
├── scraper.py            # Main scraping logic using crawl4ai
└── README.md             # This file
```

## 🔧 Setup

1. Add crawl4ai dependency (already in pyproject.toml):
   ```bash
   uv pip install crawl4ai
   ```

2. Make sure you have `GEMINI_API_KEY` in your `.env` file:
   ```bash
   GEMINI_API_KEY=your_api_key_here
   ```

3. Configure URLs in `config.py` for each insurance provider

## 📝 Configuration

Edit `src/ingestion/scraping/config.py` to add the URL for each insurance provider (one URL per provider):

```python
"goudse_expat_pakket": InsuranceURLConfig(
    provider_name="Goudse Expat Pakket",
    provider_slug="goudse_expat_pakket",
    url="https://www.goudse.nl/expat-insurance",
    description="Goudse expat insurance package"
),
```

## 🚀 Usage

### CLI Tool

Use the provided CLI script to scrape insurance data:

```bash
# List all configured providers
python scripts/scrape_insurance_data.py --list-providers

# Scrape all providers
python scripts/scrape_insurance_data.py

# Scrape specific provider
python scripts/scrape_insurance_data.py --provider goudse_expat_pakket

# Dry run (don't save files)
python scripts/scrape_insurance_data.py --dry-run
```

### Programmatic Usage

```python
import asyncio
from src.ingestion.scraping import InsuranceScraper

async def scrape_insurance():
    scraper = InsuranceScraper()

    # Scrape single provider
    results = await scraper.scrape_provider("goudse_expat_pakket")

    # Or scrape all providers
    all_results = await scraper.scrape_all_providers()

asyncio.run(scrape_insurance())
```

## 📂 Output

Scraped markdown files are saved to:
```
data/documents/{provider_slug}/webpage_{timestamp}.md
```

The filename uses "webpage" to make it clear the data comes from the scraped webpage.

For example:
```
data/documents/goudse_expat_pakket/webpage_20260120.md
```

## 🔄 Monthly Updates

To keep the knowledge base current:

1. **Run scraper monthly** to update all insurance documentation
2. **Re-ingest documents** into Qdrant after scraping:
   ```bash
   python scripts/scrape_insurance_data.py
   python scripts/ingest_documents.py --recreate
   ```

### Automation

You can set up a cron job or scheduled task:

```bash
# Run on the 1st of each month at 2 AM
0 2 1 * * cd /path/to/advies_agent && ./scripts/scrape_and_reingest.sh
```

## 🧪 Testing

Test the scraper with a single provider first:

```python
import asyncio
from src.ingestion.scraping import scrape_insurance_data

# Scrape one provider
results = asyncio.run(scrape_insurance_data("goudse_expat_pakket"))
print(results)
```

## 🛠️ Troubleshooting

### "crawl4ai not installed"
```bash
uv pip install crawl4ai
```

### "GEMINI_API_KEY not found"
Add to your `.env` file:
```bash
GEMINI_API_KEY=your_key_here
```

### Scraping fails for specific pages
- Check if the URL is accessible
- Check if the page has anti-scraping protections
- Review logs for specific error messages

### LLM returns empty content
- The page might be too large (truncated at 100k chars)
- The page might be mostly JavaScript (crawl4ai may not render it fully)
- Try adjusting the prompt in `llm_parser.py`

## 📊 Cost Considerations

Using Gemini Flash for parsing is cost-effective:
- **Gemini 2.0 Flash**: Very cheap per token
- Typical page: ~50k tokens input, ~2k tokens output
- Monthly cost for 15 providers × 3 pages = ~$1-2/month

## 🔐 Security

- Never commit API keys (use `.env`)
- Review scraped content before ingestion
- Be respectful of rate limits
- Follow robots.txt guidelines
