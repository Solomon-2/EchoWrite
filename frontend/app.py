import json
import requests
import streamlit as st

# Backend configuration
BACKEND_URL = "http://127.0.0.1:8080/repurpose"

# Page config
st.set_page_config(page_title="EchoWrite AI: Content Repurposing Engine", layout="centered")

# Title
st.title("EchoWrite AI: Content Repurposing Engine")

# URL Input
url = st.text_input(
    "Enter a YouTube or article URL",
    placeholder="https://...",
    help="Paste the link to a YouTube video or a webpage article."
)

# Disclaimer checkbox
consent = st.checkbox("I confirm that I own or have permission to use this content.")

# Submit button (disabled if checkbox not ticked)
submit_button = st.button("Repurpose Content", type="primary", disabled=not consent)

# Handle form submission
if submit_button:
    if not url:
        st.warning("Please enter a valid URL.")
    elif not consent:
        st.warning("You must confirm content rights to proceed.")
    else:
        # Show loading spinner while processing
        with st.spinner("Transcribing and generating content... This may take a few minutes."):
            try:
                # Make API call to backend
                payload = {"url": url}
                headers = {"Content-Type": "application/json"}
                
                response = requests.post(
                    BACKEND_URL, 
                    headers=headers, 
                    data=json.dumps(payload), 
                    timeout=600  # 10 minutes timeout
                )
                
                if response.status_code == 200:
                    # Success - display results
                    data = response.json()
                    
                    # Extract content from response (handle nested structure)
                    blog_post = data.get("blog_post") or (data.get("content") or {}).get("blog_post") or ""
                    twitter_thread = data.get("twitter_thread") or (data.get("content") or {}).get("twitter_thread") or ""
                    linkedin_post = data.get("linkedin_post") or (data.get("content") or {}).get("linkedin_post") or ""
                    
                    # Handle twitter thread format (could be list or string)
                    if isinstance(twitter_thread, list):
                        twitter_text = "\n\n".join(twitter_thread)
                    else:
                        twitter_text = str(twitter_thread)
                    
                    st.success("Content generated successfully!")
                    
                    # Display results in tabs
                    tabs = st.tabs(["Blog Post", "Twitter Thread", "LinkedIn Post"])
                    
                    with tabs[0]:
                        st.subheader("Blog Post")
                        st.text_area("", value=blog_post, height=500, label_visibility="collapsed", key="blog_post_area")
                    
                    with tabs[1]:
                        st.subheader("Twitter Thread")
                        st.text_area("", value=twitter_text, height=400, label_visibility="collapsed", key="twitter_thread_area")
                    
                    with tabs[2]:
                        st.subheader("LinkedIn Post")
                        st.text_area("", value=linkedin_post, height=400, label_visibility="collapsed", key="linkedin_post_area")
                        
                else:
                    # Error handling
                    try:
                        error_data = response.json()
                        error_message = error_data.get("detail", f"Backend returned status {response.status_code}")
                    except:
                        error_message = f"Backend returned status {response.status_code}. Please try again."
                    
                    st.error(error_message)
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Network error: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
