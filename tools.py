"""
The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.
    """
    # 1. Load all listings with load_listings()
    all_listings = load_listings()
    filtered_listings = []
    
    search_words = description.lower().split() if description else []

    # 2. Filter by max_price and size (if provided)
    for item in all_listings:
        if max_price is not None and float(item.get("price", 0)) > float(max_price):
            continue
            
        if size and item.get("size", "").strip().lower() != size.strip().lower():
            continue

        # 3. Score each remaining listing by keyword overlap with `description`
        title_desc_text = f"{item.get('title', '')} {item.get('description', '')}".lower()
        score = 0
        for word in search_words:
            if word in title_desc_text:
                score += 1

        # 4. Drop any listings with a score of 0 (no relevant matches)
        if search_words and score == 0:
            continue

        # Store the score temporarily in the item dict to help with sorting
        item_copy = item.copy()
        item_copy["_search_score"] = score
        filtered_listings.append(item_copy)

    # 5. Sort by score, highest first, and return the listing dicts
    filtered_listings.sort(key=lambda x: x.get("_search_score", 0), reverse=True)

    # Clean up the internal score keys before returning to keep the data pristine
    for item in filtered_listings:
        item.pop("_search_score", None)

    return filtered_listings


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.
    """
    try:
        client = _get_groq_client()
    except ValueError as e:
        return str(e)

    if not new_item:
        return "No item provided to build an outfit suggestion."

    # 1. Check whether wardrobe['items'] is empty
    wardrobe_items = wardrobe.get("items", []) if wardrobe else []

    # 2 & 3. Build conditional prompts based on whether wardrobe contains elements
    if not wardrobe_items:
        prompt = f"""
        You are FitFindr, an expert thrift-fashion AI stylist. 
        The user's personal wardrobe is currently empty. 
        
        Provide creative general styling advice, matching vibes, and styling tips (like sleeve rolls or tuck styles) for this specific item:
        Item: {new_item.get('title')}
        Description: {new_item.get('description')}
        Style Tags: {', '.join(new_item.get('style_tags', []))}
        
        Write a smooth paragraph. Do not use bullet points or markdown headings.
        """
    else:
        wardrobe_lines = []
        for item in wardrobe_items:
            wardrobe_lines.append(f"- {item.get('title', 'Unknown Piece')} ({item.get('color', '')} {item.get('category', '')})")
        wardrobe_context = "\n".join(wardrobe_lines)

        prompt = f"""
        You are FitFindr, an expert thrift-fashion AI stylist.
        Suggest 1-2 complete outfit combinations using the new item mixed with named pieces from the user's wardrobe.
        
        New Item to Style:
        - {new_item.get('title')}: {new_item.get('description')}
        
        Available Wardrobe Pieces:
        {wardrobe_context}
        
        Provide specific matching tips, how to layer or adjust them, and focus on clean cohesion. 
        Write your advice as a casual paragraph response without list points or headers.
        """

    # 4. Call the LLM and return the response string
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error contacting AI styling service: {str(e)}"


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.
    """
    # 1. Guard against an empty or whitespace-only outfit string
    if not outfit or outfit.strip() == "":
        return "Could not generate a fit card because no outfit recommendation was provided."

    try:
        client = _get_groq_client()
    except ValueError as e:
        return str(e)

    # 2. Build a prompt matching social style guidelines
    prompt = f"""
    Convert the following styling recommendations into a very short, casual, and authentic social media caption (2-4 sentences).
    
    Style Requirements:
    - Feel casual and authentic (lowercase aesthetic vibe, regular conversational wording, no artificial sales pitch).
    - Mention the item name ("{new_item.get('title')}"), its price ("${new_item.get('price')}"), and the platform it was found on ("{new_item.get('platform')}") naturally exactly once each.
    - Capture the overall outfit vibe in specific terms.
    
    Styling Advice Context:
    {outfit}
    
    Return ONLY the final caption text. Do not include quotes or conversational preamble intro text.
    """

    # 3. Call the LLM (using high temperature for creative variety) and return response
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.95
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating fit card caption: {str(e)}"