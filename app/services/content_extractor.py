from langchain_core.tools import tool
from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup


import os
from dotenv import load_dotenv

load_dotenv()

class YoutubeURLInput(BaseModel):
    youtube_url: str = Field(..., description="The URL of the YouTube video to extract the transcript from.")

class WebpageURLInput(BaseModel):
    webpage_url: str = Field(..., description="The URL of the webpage to scrape text content from.")

@tool(args_schema=YoutubeURLInput)
def get_youtube_transcript(youtube_url: str) -> str:
    """"
    Use this tool ONLY to get the text transcript of a YouTube video.
    The input must be a full, valid YouTube URL.
    """
    whisper_api_url = os.getenv("WHISPER_API_URL")
    try:

        response = requests.post(whisper_api_url, data={"url": youtube_url})

        if response.status_code == 200:
            
            return response.text
        else:
            return f"Error: Failed to retrieve transcript. Status code: {response.status_code}"
    
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to the transcription service. Details: {e}"
    

@tool(args_schema=WebpageURLInput)
def scrape_webpage_text(webpage_url: str) -> str:
    """
    Use this tool ONLY to scrape and extract text content from a webpage.
    The input must be a full, valid webpage URL.
    """
    try:
        response = requests.get(webpage_url)

        if response.status_code == 200:

            soup = BeautifulSoup(response.content, "html.parser")
            texts = soup.stripped_strings
            full_text = "\n".join(texts)
            return full_text
        else:
            return f"Error: Failed to retrieve webpage content. Status code: {response.status_code}"
    
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to the webpage. Details: {e}"




