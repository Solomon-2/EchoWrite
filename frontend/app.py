import json
import os
import requests
import streamlit as st
from datetime import datetime, timedelta

# Backend configuration
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8080")
REPURPOSE_URL = f"{BACKEND_BASE_URL}/repurpose"
AUTH_REGISTER_URL = f"{BACKEND_BASE_URL}/auth/register"
AUTH_LOGIN_URL = f"{BACKEND_BASE_URL}/auth/login"
AUTH_DEMO_URL = f"{BACKEND_BASE_URL}/auth/demo"

# Page config
st.set_page_config(page_title="EchoWrite AI: Content Repurposing Engine", layout="centered")

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "token" not in st.session_state:
    st.session_state.token = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "is_demo" not in st.session_state:
    st.session_state.is_demo = False
if "token_expiry" not in st.session_state:
    st.session_state.token_expiry = None

def logout():
    """Clear authentication state"""
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user_id = None
    st.session_state.is_demo = False
    st.session_state.token_expiry = None
    st.rerun()

def is_token_expired():
    """Check if current token is expired"""
    if not st.session_state.token_expiry:
        return True
    return datetime.now() > st.session_state.token_expiry

def authenticate_user(username, password, is_register=False):
    """Authenticate user with backend"""
    try:
        url = AUTH_REGISTER_URL if is_register else AUTH_LOGIN_URL
        payload = {"username": username, "password": password}
        
        if is_register:
            email = st.session_state.get("register_email", "")
            payload["email"] = email
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Set authentication state
            st.session_state.authenticated = True
            st.session_state.token = data["access_token"]
            st.session_state.user_id = data["user_id"]
            st.session_state.is_demo = data["is_demo"]
            
            # Calculate expiry time
            expires_in = data.get("expires_in", 24 * 3600)  # Default 24 hours
            st.session_state.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            return True, "Success!"
        else:
            error_data = response.json() if response.headers.get("content-type") == "application/json" else {}
            return False, error_data.get("detail", f"Error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        return False, f"Network error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def get_demo_access():
    """Get demo account access"""
    try:
        response = requests.post(AUTH_DEMO_URL, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Set authentication state
            st.session_state.authenticated = True
            st.session_state.token = data["access_token"]
            st.session_state.user_id = data["user_id"]
            st.session_state.is_demo = data["is_demo"]
            
            # Calculate expiry time
            expires_in = data.get("expires_in", 24 * 3600)
            st.session_state.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            return True, "Demo access granted!"
        else:
            return False, "Failed to get demo access"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

# Check token expiry
if st.session_state.authenticated and is_token_expired():
    st.warning("Your session has expired. Please log in again.")
    logout()

# Title
st.title("EchoWrite AI: Content Repurposing Engine")

# Authentication UI
if not st.session_state.authenticated:
    st.markdown("### Please log in to continue")
    
    # Login/Register tabs
    auth_tab1, auth_tab2 = st.tabs(["Login", "Register"])
    
    with auth_tab1:
        st.subheader("Login")
        with st.form("login_form"):
            login_username = st.text_input("Username or Email")
            login_password = st.text_input("Password", type="password")
            login_submit = st.form_submit_button("Login")
            
            if login_submit:
                if login_username and login_password:
                    success, message = authenticate_user(login_username, login_password, is_register=False)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter both username and password.")
    
    with auth_tab2:
        st.subheader("Register")
        with st.form("register_form"):
            register_username = st.text_input("Username", key="reg_username")
            register_email = st.text_input("Email", key="reg_email")
            register_password = st.text_input("Password", type="password", key="reg_password")
            register_submit = st.form_submit_button("Register")
            
            if register_submit:
                if register_username and register_email and register_password:
                    # Store email in session state for the authenticate_user function
                    st.session_state.register_email = register_email
                    success, message = authenticate_user(register_username, register_password, is_register=True)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please fill in all fields.")
    
    # Demo access
    st.markdown("---")
    st.markdown("### Try Demo Mode")
    st.info("Get temporary access to try the service with limited features.")
    
    if st.button("Access Demo", type="secondary"):
        success, message = get_demo_access()
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

else:
    # Main application (authenticated users)
    
    # Header with user info and logout
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.session_state.is_demo:
            st.info("🧪 Demo Mode - Limited functionality")
        else:
            st.success(f"👋 Welcome, {st.session_state.user_id}!")
    
    with col2:
        if st.button("Logout", type="secondary"):
            logout()
    
    st.markdown("---")
    
    # Main content repurposing interface
    st.markdown("### Content Repurposing")
    
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
                    # Make API call to backend with authentication
                    payload = {"url": url}
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {st.session_state.token}"
                    }
                    
                    response = requests.post(
                        REPURPOSE_URL, 
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
                            
                    elif response.status_code == 401:
                        st.error("Your session has expired. Please log in again.")
                        logout()
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
