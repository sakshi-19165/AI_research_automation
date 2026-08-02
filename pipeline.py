import os
import json
import asyncio
from playwright.async_api import async_playwright
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# 1. PLAYWRIGHT SCRAPING
async def scrape_article_with_playwright(url: str) -> dict:
    async with async_playwright() as p:
        
        # Launch headless browser (headless=True for production background tasks)
        browser = await p.chromium.launch(headless=True)
        
        # User-agent helps prevent simple bot detection blocks
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"   [Browser] Navigating to {url}...")
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        
        
        title = await page.title()
        paragraphs = await page.locator("p").all_inner_texts()
        
      
        clean_text = " ".join([p.strip() for p in paragraphs if len(p.strip()) > 40])
        
        await browser.close()
        
        return {
            "title": title,
            "body": clean_text
        }

# 2. LLM GENERATION STAGE
def generate_research_brief(title: str, body: str) -> dict:
    prompt = f"""
    Create an executive research brief based on this article.
    
    Title: {title}
    Body: {body[:3000]}  # Truncate to save tokens

    Respond strictly in JSON:
    {{
        "title": "{title}",
        "executive_summary": "1 sentence high-level takeaway.",
        "key_insights": ["point 1", "point 2"],
        "action_item": "Suggested next step or follow-up area."
    }}
    """
    
    res = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=600,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(res.content[0].text)

# 3. ORCHESTRATION PIPELINE
async def run_research_pipeline(target_url: str):
    print("🚀 Starting Playwright-Powered Research Automation Pipeline...")
    
    print("[1/2] Fetching & rendering page via Playwright...")
    scraped_data = await scrape_article_with_playwright(target_url)
    
    if not scraped_data["body"]:
        print("Error: No content could be extracted")
        return

    print(f"      Title Extracted: '{scraped_data['title']}'")
    
    print("[2/2] Generating executive brief via LLM...")
    brief = generate_research_brief(scraped_data["title"], scraped_data["body"])
    
    # Display Output
    print("\n" + "="*40 + " RESEARCH BRIEF " + "="*40)
    print(json.dumps(brief, indent=2))

if __name__ == "__main__":
   
    sample_url = "https://news.ycombinator.com/" 
    asyncio.run(run_research_pipeline(sample_url))