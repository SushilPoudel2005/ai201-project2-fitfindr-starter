# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

FitFindr takes a user's natural language request to search a mock thrift listings dataset using `search_listings`, automatically isolating the top result if relevant matches are found. It then uses `suggest_outfit` to generate an outfit combination using the selected item matched against the user's current wardrobe structure. Finally, it calls `create_fit_card` to produce a short, creative, social-media-ready caption for the look. If any step fails (such as no listings matching the search constraints), the agent halts early and reports a clear, helpful fallback message to the user rather than crashing.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Filters the mock database (`data/listings.json`) by matching keywords against titles/descriptions, filtering by size, and applying a maximum price ceiling.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): ... Search keywords or item type (e.g., "vintage graphic tee").
- `size` (str): ... The requested clothing size filter (e.g., "M").
- `max_price` (float): ... Maximum allowed price for an item.

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->

An array of matching item objects. Each item dictionary contains fields like `id`, `title`, `description`, `price`, `size`, and `platform`.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->

If the returned list is empty `[]`, the tool returns an empty list without throwing an exception. The agent catches this empty response, notifies the user that no items matched their exact parameters, and gracefully stops execution without calling subsequent tools.
---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Sends a structured prompt to the Groq LLM combining the discovered item data with the user's current wardrobe collection to generate a stylized outfit combination.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): ... The single dictionary representing the chosen top item match from the search phase.
- `wardrobe` (dict): ... The user's parsed wardrobe JSON object containing an array of existing wardrobe items.

**What it returns:**
<!-- Describe the return value -->
A descriptive paragraph detailing specific styling suggestions and combinations.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->

If the user's wardrobe is empty (`wardrobe["items"]` is empty or missing), the tool handles it by falling back to a general styling guide that details how to style the item standalone or with generic basics, ensuring the agent remains functional.

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Prompts the Groq LLM using a high temperature configuration to generate a punchy, casual, short social media description/caption based on the recommended outfit.
**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (...): ...The descriptive styling paragraph output from `suggest_outfit`.
- `new_item` (dict): The selected item dictionary (used to dynamically pull price and platform details).

**What it returns:**
<!-- Describe the return value -->
A casual, shareable caption.
**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
If the incoming `outfit` string is empty, the tool guards against crashing by returning a fallback error message string: `"Could not generate a fit card because no outfit recommendation was provided."`
---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | |
| suggest_outfit | Wardrobe is empty | |
| create_fit_card | Outfit input is missing or incomplete | |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

Conditional Logic Flow
1. **Initialize State:** Establish a session dictionary containing keys for `selected_item`, `outfit_suggestion`, `fit_card`, and `error`.
2. **Execute Search:** Call `search_listings` using parameters parsed out of the user's query text.
3. **Evaluate Results Branch:**
    * **Branch A (Empty Results):** If the returned list is empty, set `session["error"]` to a helpful user prompt (e.g., *"No listings found matching your constraints. Try broadening your size or price filters!"*), leave downstream keys as `None`, and terminate execution early.
    * **Branch B (Results Found):** If items exist, store the top result in `session["selected_item"] = results[0]` and proceed.
4. **Generate Suggestions:** Call `suggest_outfit(session["selected_item"], wardrobe)`. Save the generated text response directly into `session["outfit_suggestion"]`.
5. **Generate Social Post:** Call `create_fit_card(session["outfit_suggestion"], session["selected_item"])` and save the response string into `session["fit_card"]`.
6. **Return Session:** Finalize the state and pass the session dictionary back to the UI handler.

### Agent Flow Diagram
```text
User query
    │
    ▼
Planning Loop ───────────────────────────────────────────┐
    │                                                    │
    ├─► search_listings(description, size, max_price)    │
    │       │ results=[]                                 │
    │       ├──► [ERROR] "No listings found..." → return │
    │       │                                            │
    │       │ results=[item, ...]                        │
    │       ▼                                            │
    │   Session: selected_item = results[0]              │
    │       │                                            │
    ├─► suggest_outfit(selected_item, wardrobe)          │
    │       │                                            │
    │   Session: outfit_suggestion = "..."               │
    │       │                                            │
    └─► create_fit_card(outfit_suggestion, selected_item)│
            │                                            │
        Session: fit_card = "..."                        │
            │                                            └─ error path returns here
            ▼
        Return session
        
---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**
AI Assistant: Claude / ChatGPT

Inputs Provided: Paste the complete Tool Inventory block from this spec along with function stubs from tools.py.

Expected Output: Separate, functional Python implementations for search_listings, suggest_outfit, and create_fit_card.

Verification: Review code to confirm parameters match the spec exactly, verify that Groq API connections use environment variables correctly, and execute standalone unit tests in tests/test_tools.py via pytest.

**Milestone 4 — Planning loop and state management:**

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
Parsing & Search
Action: The planning loop extracts parameters and triggers search_listings(description="vintage graphic tee", size="M", max_price=30.0).

Mock Database Response: Returns a list of matches. The loop selects the top entry: {"id": 101, "title": "Faded Band Tee", "price": 22.0, "size": "M", "platform": "Depop", "condition": "Good"}.

State Saved: session["selected_item"] is populated with this dictionary.

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->
Styling Recommendations
Action: The loop reads the active item from the state object and invokes suggest_outfit(session["selected_item"], wardrobe).

LLM Response: "Pair this Faded Band Tee with your wide-leg jeans and platform sneakers for a classic 90s grunge look. Roll the sleeves once for shape."

State Saved: session["outfit_suggestion"] is populated with this string.

**Step 3:**
<!-- Continue until the full interaction is complete -->
Caption Formatting

Action: The loop triggers create_fit_card(session["outfit_suggestion"], session["selected_item"]).

LLM Response: "thrifted this faded band tee off depop for $22 and honestly it was made for my wide-legs 🖤 full look in my stories"

State Saved: session["fit_card"] is populated with this string.

**Final output to user:**
<!-- What does the user actually see at the end? -->
Action: The planning loop concludes. app.py reads the completed session dictionary and renders the compiled results across the three respective Gradio display panels. 