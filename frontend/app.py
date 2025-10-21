import os
import json
import threading
import time
from typing import Optional

import requests
import streamlit as st

# Backend configuration
BACKEND_URL = os.getenv("ECHO_BACKEND_URL", "http://127.0.0.1:8080/repurpose")

# Page config
st.set_page_config(page_title="EchoWrite AI: Content Repurposing Engine", layout="centered")

# Title and description
st.title("EchoWrite AI: Content Repurposing Engine")
st.caption("Turn a single URL into a blog post, Twitter thread, and LinkedIn post.")

# ---- Session state ----
if "job_running" not in st.session_state:
    st.session_state.job_running = False
if "cancel_requested" not in st.session_state:
    st.session_state.cancel_requested = False
if "job_result" not in st.session_state:
    st.session_state.job_result = None
if "job_error" not in st.session_state:
    st.session_state.job_error = None
if "last_url" not in st.session_state:
    st.session_state.last_url = ""


def _run_job(url: str):
    """Background worker that calls the backend and stores result/error in session_state."""
    try:
        payload = {"url": url}
        headers = {"Content-Type": "application/json"}
        # Long timeout since backend may take time
        resp = requests.post(BACKEND_URL, headers=headers, data=json.dumps(payload), timeout=600)

        if st.session_state.cancel_requested:
            # If user requested cancel, drop results
            return

        if resp.status_code != 200:
            try:
                detail = resp.json().get("detail")
            except Exception:
                detail = None
            st.session_state.job_error = detail or f"Backend returned {resp.status_code}. Please try again."
            st.session_state.job_result = None
        else:
            data = resp.json()
            st.session_state.job_result = data
            st.session_state.job_error = None
    except requests.exceptions.RequestException as e:
        if not st.session_state.cancel_requested:
            st.session_state.job_error = f"Network error: {e}"
            st.session_state.job_result = None
    except Exception as e:
        if not st.session_state.cancel_requested:
            st.session_state.job_error = f"Unexpected error: {e}"
            st.session_state.job_result = None
    finally:
        st.session_state.job_running = False

# Input section
with st.container():
    url = st.text_input(
        "Enter a YouTube or article URL",
        key="content_url",
        placeholder="https://...",
        help="Paste the link to a YouTube video or a webpage article.",
        value=st.session_state.last_url or ""
    )
    consent = st.checkbox(
        "I confirm that I own or have permission to use this content.",
        key="consent_checkbox",
    )

    # Buttons row
    cols = st.columns([1, 1, 3])
    submit_disabled = (not consent) or (not url) or st.session_state.job_running
    with cols[0]:
        submit = st.button("Repurpose Content", type="primary", disabled=submit_disabled)
    with cols[1]:
        cancel = st.button("Cancel", disabled=not st.session_state.job_running)

# Validation messages
if not consent and not st.session_state.job_running:
    st.info("Please confirm you have rights to use the content before proceeding.")

if submit and not st.session_state.job_running:
    if not consent:
        st.warning("You must confirm content rights to proceed.")
    elif not url:
        st.warning("Please enter a valid URL.")
    else:
        # Initialize state and start background job
        st.session_state.job_running = True
        st.session_state.cancel_requested = False
        st.session_state.job_result = None
        st.session_state.job_error = None
        st.session_state.last_url = url

        thread = threading.Thread(target=_run_job, args=(url,), daemon=True)
        thread.start()

if cancel and st.session_state.job_running:
    # Signal cancel and clear state; backend request cannot be forcefully killed,
    # but we stop waiting for it and ignore its results when it finishes.
    st.session_state.cancel_requested = True
    st.session_state.job_running = False
    st.session_state.job_result = None
    st.session_state.job_error = None

# Live status / results rendering
if st.session_state.job_running:
    with st.spinner("Transcribing and generating content... This may take a few minutes."):
        st.info("Your repurposing job is running. You can cancel anytime.")

if st.session_state.job_error and not st.session_state.job_running:
    st.error(st.session_state.job_error)

if st.session_state.job_result and not st.session_state.job_running:
    data = st.session_state.job_result
    # Support either flattened or nested response shapes
    blog_post = data.get("blog_post") or (data.get("content") or {}).get("blog_post") or ""
    twitter_thread = data.get("twitter_thread") or (data.get("content") or {}).get("twitter_thread") or []
    linkedin_post = data.get("linkedin_post") or (data.get("content") or {}).get("linkedin_post") or ""

    # Normalize twitter thread to string
    if isinstance(twitter_thread, list):
        twitter_text = "\n\n".join(twitter_thread)
    else:
        twitter_text = str(twitter_thread)

    st.success("Content generated successfully!")
    tabs = st.tabs(["Blog Post", "Twitter Thread", "LinkedIn Post"])

    with tabs[0]:
        st.subheader("Blog Post")
        st.text_area("", value=blog_post, height=500)

    with tabs[1]:
        st.subheader("Twitter Thread")
        st.text_area("", value=twitter_text, height=400)

    with tabs[2]:
        st.subheader("LinkedIn Post")
        st.text_area("", value=linkedin_post, height=400)

# Footer / tips
st.divider()
st.caption("Tip: Update BACKEND_URL via env var ECHO_BACKEND_URL if your API isn't on 127.0.0.1:8000.")
