# In test_extractor_node.py

from app.ai_core.nodes import extract_content
from app.ai_core.graph import EchoWriteState

# --- Define URLs for testing each tool ---
# Use a short video to make transcription faster
YOUTUBE_URL = "https://www.youtube.com/watch?v=Mdcw3_b24_w"
# A standard news or blog article
ARTICLE_URL = "https://www.theverge.com/2024/10/17/24271424/microsoft-windows-11-24h2-recall-ai-feature-copilot"

def run_test():
    """
    Initializes a state and invokes the extract_content node to test its functionality.
    """
    print("==================================================")
    print("🧪 TESTING EXTRACTOR NODE WITH YOUTUBE URL...")
    print("==================================================")

    # 1. Create the initial state with a YouTube URL
    initial_youtube_state: EchoWriteState = {
        "url": YOUTUBE_URL,
        "source_text": None,
        "key_insights": None,
        "blog_post": None,
        "twitter_thread": None,
        "linkedin_post": None,
        "error": None
    }

    # 2. Call the node function directly
    final_youtube_state = extract_content(initial_youtube_state)

    # 3. Check the output
    print("\n--- FINAL YOUTUBE STATE ---")
    if final_youtube_state.get("error"):
        print(f"❌ ERROR: {final_youtube_state['error']}")
    else:
        print(f"✅ SUCCESS: Source text was populated.")
        print(f"Text Length: {len(final_youtube_state.get('source_text', ''))}")


    print("\n==================================================")
    print("🧪 TESTING EXTRACTOR NODE WITH ARTICLE URL...")
    print("==================================================")

    initial_article_state: EchoWriteState = {
        "url": ARTICLE_URL,
        "source_text": None,
        "key_insights": None,
        "blog_post": None,
        "twitter_thread": None,
        "linkedin_post": None,
        "error": None
    }

    final_article_state = extract_content(initial_article_state)

    print("\n--- FINAL ARTICLE STATE ---")
    if final_article_state.get("error"):
        print(f"❌ ERROR: {final_article_state['error']}")
    else:
        print(f"✅ SUCCESS: Source text was populated.")
        print(f"Text Length: {len(final_article_state.get('source_text', ''))}")


if __name__ == "__main__":
    # Make sure your local Whisper service is running before you execute this
    run_test()