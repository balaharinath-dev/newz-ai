from langchain_google_vertexai import ChatVertexAI
from langchain.agents import create_agent
from langchain.tools import tool
from dotenv import load_dotenv
from datetime import datetime
import feedparser
import requests
import os

load_dotenv()

@tool
def fetch_top_news():
    """
    Returns curated news:
    - 3 global enterprise tech
    - 3 world politics
    - 2 Indian politics
    - 2 business/market
    """
    feeds = {
        "global_enterprise_tech": [
            "https://www.techmeme.com/feed.xml",
            "https://feeds.arstechnica.com/arstechnica/technology-lab",
            "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
        ],
        "world_politics": [
            "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
            "https://feeds.bbci.co.uk/news/world/rss.xml",
        ],
        "indian_politics": [
            "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
            "https://www.thehindu.com/news/national/feeder/default.rss",
        ],
        "business_market": [
            "https://feeds.bbci.co.uk/news/business/rss.xml",
            "https://www.livemint.com/rss/companies",
            "https://www.moneycontrol.com/rss/latestnews.xml"
        ],
    }
    
    def pull(feed_list, limit):
        items = []
        for url in feed_list:
            try:
                parsed = feedparser.parse(url)
                for entry in parsed.entries[:10]:  # pull more then trim
                    items.append({
                        "title": entry.get("title"),
                        "summary": entry.get("summary", ""),
                        "link": entry.get("link"),
                        "published": entry.get("published", ""),
                        "source": url
                    })
            except Exception:
                continue
        return items[:limit]
    
    return {
        "global_enterprise_tech": pull(feeds["global_enterprise_tech"], 3),
        "world_politics": pull(feeds["world_politics"], 3),
        "indian_politics": pull(feeds["indian_politics"], 2),
        "business_market": pull(feeds["business_market"], 2),
    }
    
@tool
def search_tool(query: str, num: int = 5):
    """
    Perform a Google Custom Search query.

    :param query: Search query string
    :param api_key: Google API key
    :param cse_id: Custom Search Engine ID (cx)
    :param num: Number of results (1–10)
    :return: List of result dictionaries
    """
    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "q": query,
        "key": os.getenv("GOOGLE_API_KEY"),
        "cx": os.getenv("GOOGLE_CSE_ID"),
        "num": num
    }

    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise error for any API issues

    data = response.json()
    return data.get("items", [])


system_prompt = (
                    f"""
                        You are an intelligent news curator and analyst. Your job is to provide well-structured, contextual news summaries that can be read and fully understood in a maximum of 15 minutes.
                        
                        Current Date: {datetime.now().strftime("%Y-%m-%d")}

                        CRITICAL CONSTRAINT:
                        - The entire news report must be readable in 15 minutes or less
                        - Balance depth with brevity - be comprehensive but concise
                        - Each tech item: ~1-2 minutes reading time (150-250 words)
                        - Each political item: ~2-3 minutes reading time (250-400 words)
                        - Each business item: ~2-3 minutes reading time (250-400 words)
                        - Total: approximately 10 items should fit comfortably within 15 minutes

                        WORKFLOW:
                        1. Call the fetch_top_news() tool to retrieve all current news items
                        2. For EACH news item, use search_tool to gather additional context and recent developments
                        3. Structure your final output as a clean JSON object with enhanced information

                        OUTPUT FORMAT REQUIREMENTS:

                        For GLOBAL ENTERPRISE TECH news:
                        {{
                        "title": "original title",
                        "summary": "original summary",
                        "link": "original link",
                        "published": "date",
                        "context": "A concise 2-liner explaining what this technology/development is and why it matters in the broader tech landscape.",
                        "related_developments": "Brief mention of related recent news found via search"
                        }}

                        For WORLD POLITICS and INDIAN POLITICS news:
                        {{
                        "title": "original title",
                        "summary": "original summary",
                        "link": "original link",
                        "published": "date",
                        "background": "Historical context - what led to this situation? What are the root causes?",
                        "key_players": "Who are the main actors/countries/parties involved?",
                        "connections": "How does this connect to other ongoing events or long-term political dynamics?",
                        "impact_analysis": "What are the immediate and potential long-term impacts? Who is affected?",
                        "complete_picture": "A synthesized narrative that ties everything together so the reader fully understands the situation"
                        }}

                        For BUSINESS/MARKET news:
                        {{
                        "title": "original title",
                        "summary": "original summary", 
                        "link": "original link",
                        "published": "date",
                        "what_it_is": "Clear explanation of the business/market event",
                        "why_it_matters": "Significance for the company/sector/economy",
                        "impact_analysis": "Who wins, who loses? Short-term and long-term implications",
                        "market_context": "How does this fit into current market trends and economic conditions?",
                        "investor_perspective": "What should investors/stakeholders know about this?"
                        }}

                        FINAL OUTPUT STRUCTURE:
                        {{
                        "global_enterprise_tech": [array of 3 enhanced tech news items],
                        "world_politics": [array of 3 enhanced political news items],
                        "indian_politics": [array of 2 enhanced Indian political news items],
                        "business_market": [array of 2 enhanced business/market news items],
                        "generated_at": "timestamp of when this report was created"
                        }}

                        IMPORTANT GUIDELINES:
                        - ALWAYS use search_tool for each news item to get current context
                        - Write in clear, accessible language - assume the reader wants to understand, not just skim
                        - For politics and business, go deep enough that someone with no background can grasp the full picture
                        - Keep tech explanations concise but informative (2-3 sentences max for context)
                        - Focus on IMPACT and CONNECTIVITY - help readers see the bigger picture
                        - Return ONLY valid JSON, no markdown formatting or additional text
                        - Ensure all fields are properly escaped for JSON compatibility
                        - MAINTAIN THE 15-MINUTE READING TIME LIMIT: Be thorough but economical with words
                        - Prioritize the most impactful information - cut fluff, keep substance
                        - Each explanation should be dense with insight, not padded with unnecessary details
                    """
                )

model = ChatVertexAI(
    model="gemini-2.5-pro",
    temperature=0
)

news_agent = create_agent(
    model=model,
    system_prompt=system_prompt,
    tools=[fetch_top_news, search_tool]
)