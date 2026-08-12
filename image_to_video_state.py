"""Helpers for preserving Creator Flow state in Streamlit."""

import streamlit as st


def initialize_image_video_state() -> None:
    defaults = {
        "product_photo_bytes": None,
        "product_photo_name": "",
        "product_photo_type": "image/png",
        "brief": "",
        "output_mode": "Gambar",
        "image_prompts": "",
        "selected_image_prompt": "",
        "image_stage": "prompt",
        "selected_image_name": "",
        "selected_image_bytes": None,
        "selected_image_type": "image/png",
        "generated_image_bytes": None,
        "generated_image_type": "image/png",
        "generated_video_bytes": None,
        "video_stage": "locked",
        "video_prompt_result": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_product_photo(uploaded_file) -> None:
    """Persist a new product reference photo outside the uploader widget state."""
    if uploaded_file is None:
        return
    image_bytes = uploaded_file.getvalue()
    if not image_bytes:
        return

    is_new_photo = (
        image_bytes != st.session_state.get("product_photo_bytes")
        or uploaded_file.name != st.session_state.get("product_photo_name", "")
        or (uploaded_file.type or "image/png") != st.session_state.get("product_photo_type", "image/png")
    )
    if not is_new_photo:
        return

    st.session_state.product_photo_bytes = image_bytes
    st.session_state.product_photo_name = uploaded_file.name
    st.session_state.product_photo_type = uploaded_file.type or "image/png"
    st.session_state.generated_image_bytes = None
    st.session_state.generated_video_bytes = None
    st.session_state.video_prompt_result = ""
    st.session_state.selected_image_bytes = None
    st.session_state.selected_image_name = ""
    st.session_state.selected_image_type = "image/png"
    st.session_state.video_stage = "locked"


def save_selected_image(uploaded_file) -> None:
    """Copy a generated/Google Flow image into persistent session state."""
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


def use_generated_image_as_reference(
    image_bytes: bytes,
    mime_type: str = "image/png",
    name: str = "creator_flow_generated.png",
) -> None:
    """Promote the AI-generated image to the image-to-video reference slot."""
    st.session_state.selected_image_bytes = image_bytes
    st.session_state.selected_image_name = name
    st.session_state.selected_image_type = mime_type or "image/png"
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
    if not st.session_state.get("selected_image_bytes"):
        return False
    st.session_state.image_stage = "video"
    st.session_state.video_stage = "ready"
    return True
