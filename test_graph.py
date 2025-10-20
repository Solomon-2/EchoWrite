# In test_graph.py

from app.ai_core.graph import graph, EchoWriteState

# --- Define Test URLs ---
# One for each tool your agent has
YOUTUBE_URL = "https://www.youtube.com/watch?v=mL439g_9-ds" # A short video is best
ARTICLE_URL = "https://www.theverge.com/2024/2/15/24074218/openai-sora-text-to-video-generator-ai"

def run_test():
    """Runs the graph with different inputs to test the extractor node."""
    
    print("==================================================")
    print("🧪 TESTING WITH YOUTUBE URL...")
    print("==================================================")
    
    # 1. Define the initial state for the YouTube test
    initial_youtube_state: EchoWriteState = {"url": YOUTUBE_URL}
    
    # 2. Invoke the graph
    # The graph will start at the 'extractor' node
    final_youtube_state = graph.invoke(initial_youtube_state)
    
    # 3. Print the final state to see the result
    print("\n--- FINAL YOUTUBE STATE ---")
    if final_youtube_state.get("error"):
        print(f"ERROR: {final_youtube_state['error']}")
    else:
        print(f"Source Text Length: {len(final_youtube_state.get('source_text', ''))}")
        # print(final_youtube_state.get('source_text')) # Uncomment to see full text


    print("\n==================================================")
    print("🧪 TESTING WITH ARTICLE URL...")
    print("==================================================")

    initial_article_state: EchoWriteState = {"url": ARTICLE_URL}
    final_article_state = graph.invoke(initial_article_state)

    print("\n--- FINAL ARTICLE STATE ---")
    if final_article_state.get("error"):
        print(f"ERROR: {final_article_state['error']}")
    else:
        print(f"Source Text Length: {len(final_article_state.get('source_text', ''))}")
        # print(final_article_state.get('source_text')) # Uncomment to see full text

if __name__ == "__main__":
    run_test()