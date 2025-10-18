# Import the tool from your services module
from app.services.content_extractor import get_youtube_transcript

# Define a test URL
TEST_URL = "https://www.youtube.com/watch?v=1w5cCXlh7JQ"

# Call the function just like any other Python function
print("Testing the YouTube transcript tool...")
transcript = get_youtube_transcript.invoke({"youtube_url": TEST_URL})

# Print the output
print("\n--- TRANSCRIPT ---")
print(transcript)