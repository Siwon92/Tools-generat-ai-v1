"""Helpers for preserving image-to-video state in Streamlit.

Kept separate so the UI can use stable, non-widget session-state keys for
values that must survive reruns and widget visibility changes.
"""

import streamlit as st


def initialize_image_video_state() -> None:
    defaults = {
        "image_prompts": "",
        "selected_image_prompt": "",
        "image_stage": "prompt",
        "selected_image_name": "",
        "selected_image_bytes": None,
        "selected_image_type": "image/png",
        "video_stage": "locked",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_selected_image(uploaded_file) -> None:
    """Copy uploaded image bytes into permanent session state."""
    if uploaded_file is None:
        return
    st.session_state.selected_image_bytes = uploaded_file.getvalue()
    st.session_state.selected_image_name = uploaded_file.name
    st.session_state.selected_image_type = uploaded_file.type or "image/png"
    st.session_state.image_stage = "selected"
    st.session_state.video_stage = "ready"


def clear_selected_image() -> None:
    st.session_state.selected_image_bytes = None
    st.session_state.selected_image_name = ""
    st.session_state.selected_image_type = "image/png"
    st.session_state.video_stage = "locked"


def save_image_prompt() -> None:
    st.session_state.selected_image_prompt = st.session_state.image_prompt_editor
    st.session_state.image_stage = "saved"


def continue_to_video() -> bool:
    if not st.session_state.selected_image_prompt.strip():
        return False
    if not st.session_state.selected_image_bytes:
        return False
    st.session_state.image_stage = "video"
    st.session_state.video_stage = "ready"
    return True
