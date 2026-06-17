# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

`ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies


## Setup

```bash
pip install -r requirements.txt
Set your Groq API key in a .env file (get a free key at console.groq.com):

Plaintext
GROQ_API_KEY=your_key_here
The Mock Listings Dataset
data/listings.json contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: id, title, description, category, style_tags, size, condition, price, colors, brand, and platform.

Load it with:

Python
from utils.data_loader import load_listings
listings = load_listings()
The Wardrobe Schema
data/wardrobe_schema.json defines the format your agent uses to represent a user's existing wardrobe. It includes:

schema: field definitions for a wardrobe item

example_wardrobe: a sample wardrobe with 10 items you can use for testing

empty_wardrobe: a starting template for a new user

Load an example wardrobe with:

Python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
Tool Inventory
Each tool inside FitFindr operates as an isolated, independently testable component designed with clean, predictable programmatic interfaces:

1. search_listings
Inputs: * description (str): Natural language keyword input outlining the targeted apparel piece.

size (str | None): Optional strict size matching filter.

max_price (float | None): Optional upper-bound numerical price threshold.

Outputs: list[dict]

Returns an array of dictionary items extracted from the database that successfully match the applied filters, ordered with the highest keyword relevance score first.

Purpose: Queries and ranks candidate thrifting pieces directly from data/listings.json.

2. suggest_outfit
Inputs:

new_item (dict): The specific structured item dictionary representing the target thrift purchase.

wardrobe (dict): The user's full wardrobe dictionary configuration.

Outputs: str

Returns a fully descriptive styling recommendation paragraph from the Groq LLM detailing custom garment layout pairings.

Purpose: Leverages llama-3.3-70b-versatile to blend a newly discovered item smoothly into an existing wardrobe.

3. create_fit_card
Inputs:

outfit (str): The comprehensive paragraph context generated directly by suggest_outfit.

new_item (dict): The targeted thrift garment data dictionary.

Outputs: str

Returns a short, lowercase aesthetic social media caption tailored cleanly for platforms like Instagram or TikTok.

Purpose: Automated copy creation featuring exact platform, price, and item callouts with a creative, varied tone.

How the Planning Loop Works
The core orchestration engine lives within run_agent() inside agent.py. Rather than blindly forcing every tool to run sequentially, the loop implements intentional conditional branching based on step-by-step state evaluation:

State Initialization: A clean session dictionary state tracking variables (selected_item, outfit_suggestion, fit_card, error) is constructed.

Search Traversal: The agent invokes search_listings() using parameters unpacked from user selections.

Conditional Branch Evaluation:

Branch A (Empty/No Results Match): If the search tool passes back an empty array ([]), the loop updates session["error"], immediately aborts downstream actions, skips calls to the LLM entirely, and returns the early state.

Branch B (Successful Match): If matching listings are recovered, the top candidate is securely saved into session["selected_item"] and execution advances.

Context Synthesis: The agent triggers suggest_outfit() passing the loaded state details and processes the textual results before calling create_fit_card() with an elevated LLM generation temperature configuration.

State Management Approach
FitFindr uses a unified state management dictionary object passed sequentially between orchestration stages. The system relies entirely on this state continuity to drive tool execution:

What is Stored: The active item dictionary data profile, the text block containing structural outfit guides, generated copy strings, and current run execution errors.

When and How: Data flows incrementally. The output of search_listings populates session["selected_item"], which is automatically drawn from state to serve as the critical input context for suggest_outfit. The resultant recommendation populates session["outfit_suggestion"], feeding cleanly down into create_fit_card. This removes all manual re-entry barriers for the user.

Error Handling Strategy
Defensive error guards are implemented across every tool to protect execution stability and prevent application crashes:

search_listings Guard: Handled gracefully via try-except parsing fallbacks. If an impossible search filter parameters match occurs (e.g., searching for a designer ballgown under $5), the tool suppresses exceptions, smoothly returns [], and the agent explicitly logs an informative message advising the user to relax constraints.

suggest_outfit Guard: If the user profile contains an completely blank clothing matrix (get_empty_wardrobe()), the system bypasses array iteration loops entirely. It structures a stylized prompt instructing the model to generate versatile stand-alone recommendations matching common basic essentials.

create_fit_card Guard: Checks for empty string arguments. If an empty outfit string is processed, it avoids sending a broken token batch to Groq and instantly passes back a descriptive string: "Could not generate a fit card because no outfit recommendation was provided."

Spec Reflection
Spec Advantages: Outlining structural constraints within planning.md prior to code generation enforced complete parameter definition parity across modules, which prevented typical data format conflicts between string outputs and dictionary payloads.

Implementation Divergences: Keyword processing in search_listings evolved from a strict word match into a multi-keyword token matching score loop. This change ensured complex descriptions like "vintage graphic tee" successfully pull matches when items are tagged simply as "vintage tee".

AI Usage Section
Tool Code Generation: Provided Claude with the specific structural stubs in tools.py alongside the markdown parameter lists. The generator produced accurate logic blocks, which were manually optimized to handle case-insensitive string parsing cleanly.

Planning Loop Architecture: Fed the full ASCII control diagram directly to the assistant to generate run_agent(). Modified the generated template to enforce explicit validation boundaries, ensuring downstream LLM API resources are never wasted if a tool step returns incomplete info.