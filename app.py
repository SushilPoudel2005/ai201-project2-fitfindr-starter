"""
FitFindr User Interface. Connects the Gradio UI panels to the agent planning loop.
"""

import gradio as gr
from agent import run_agent

def handle_query(query: str, size: str, max_price: float, wardrobe_setting: str):
    """
    Takes the inputs from the Gradio interface, maps them to the agent's parameters,
    executes the planning loop, and returns the results to the UI display panels.
    """
    # 1. Clean up optional inputs from the interface defensively
    query_clean = query.strip() if query else ""
    size_filter = size.strip() if size and size.strip() != "" else None
    
    try:
        price_filter = float(max_price) if max_price and float(max_price) > 0 else None
    except (ValueError, TypeError):
        price_filter = None

    # 2. Map the wardrobe dropdown selection to a boolean flag
    use_example = (wardrobe_setting == "Use Example Wardrobe")

    # 3. Execute the core agent planning loop
    session = run_agent(
        query=query_clean,
        size=size_filter,
        max_price=price_filter,
        use_example_wardrobe=use_example
    )

    # 4. Handle the error branch path dynamically for the UI
    if session["error"]:
        error_msg = f"❌ Agent Stopped Early:\n{session['error']}"
        return (
            error_msg,               # Panel 1: Selected Item Display
            "No outfit generated.",  # Panel 2: Outfit Suggestion Display
            "No fit card generated." # Panel 3: Shareable Caption Display
        )

    # 5. Handle the happy path (Format data cleanly for display)
    item = session["selected_item"]
    item_display = (
        f"🏷️ Title: {item.get('title')}\n"
        f"💰 Price: ${item.get('price')} on {item.get('platform')}\n"
        f"📏 Size: {item.get('size')} | Condition: {item.get('condition')}\n"
        f"📝 Description: {item.get('description')}"
    )

    outfit_display = session["outfit_suggestion"]
    fit_card_display = session["fit_card"]

    return item_display, outfit_display, fit_card_display


# ── Gradio Layout Launcher ──────────────────────────────────────────────────
if __name__ == "__main__":
    with gr.Blocks(title="FitFindr - AI Thrift Stylist") as demo:
        gr.Markdown("# 🛍️ FitFindr: Multi-Tool Thrift Agent")
        gr.Markdown("Search secondhand listings, match pieces with your wardrobe, and generate social media captions.")
        
        with gr.Row():
            with gr.Column():
                query_input = gr.Textbox(label="What item are you looking for?", placeholder="e.g., vintage graphic tee")
                size_input = gr.Textbox(label="Size (Optional)", placeholder="e.g., M")
                price_input = gr.Number(label="Max Price (Optional)", value=0)
                wardrobe_input = gr.Dropdown(
                    label="Wardrobe State", 
                    choices=["Use Example Wardrobe", "Use Empty Wardrobe"], 
                    value="Use Example Wardrobe"
                )
                submit_btn = gr.Button("Find My Fit", variant="primary")
            
            with gr.Column():
                item_output = gr.Textbox(label="Step 1: Found Listing Match", interactive=False)
                outfit_output = gr.Textbox(label="Step 2: AI Styling Suggestion", interactive=False)
                fit_card_output = gr.Textbox(label="Step 3: Shareable Fit Card Caption", interactive=False)
        
        submit_btn.click(
            fn=handle_query,
            inputs=[query_input, size_input, price_input, wardrobe_input],
            outputs=[item_output, outfit_output, fit_card_output]
        )
        
    demo.launch(server_name="127.0.0.1", server_port=7860, share=True)