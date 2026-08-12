"""Helpers for preserving image-to-video state in Streamlit.

Values that must survive widget reruns live in stable, non-widget session-state keys.
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
        "video_prompt_result": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_selected_image(uploaded_file) -> None:
    """Copy the uploaded image into persistent session state."""
    if uploaded_file is None:
        return
    image_bytes = uploaded_file.getvalue()
    if not image_bytes:
        return
    st.session_state.selected_image_bytes = image_bytes
    st.session_state.selected_image_name = uploaded_file.name
    st.session_state.selected_image_type = uploaded_file.type or "image/png"
    st.session_state.video_stage = "ready"
    st.session_state.video_prompt_result = ""
    st.session_state.image_stage = "selected"


def clear_selected_image() -> None:
    st.session_state.selected_image_bytes = None
    st.session_state.selected_image_name = ""
    st.session_state.selected_image_type = "image/png"
    st.session_state.video_stage = "locked"
    st.session_state.video_prompt_result = ""
    st.session_state.image_stage = "saved"


def save_image_prompt() -> bool:
    prompt = st.session_state.get("image_prompt_editor", "").strip()
    if not prompt:
        return False
    st.session_state.selected_image_prompt = prompt
    st.session_state.video_prompt_result = ""
    st.session_state.video_stage = "locked" if not st.session_state.selected_image_bytes else "ready"
    st.session_state.image_stage = "saved"
    return True


def continue_to_video() -> bool:
    if not st.session_state.get("selected_image_prompt", "").strip():
        return False
    if not st.session_state.get("selected_image_bytes"):
        return False
    st.session_state.image_stage = "video"
    st.session_state.video_stage = "ready"
    return True
