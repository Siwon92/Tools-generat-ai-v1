import streamlit as st
from google import genai

from image_to_video_state import (
    clear_selected_image,
    continue_to_video,
    initialize_image_video_state,
    save_image_prompt,
    save_selected_image,
)

GEMINI_MODEL = "gemini-3.6-flash"
IMAGE_STAGE = "🖼️ 1. Buat Prompt Gambar"
SELECT_STAGE = "🖼️ 2. Pilih Gambar Utama"
VIDEO_STAGE = "🎬 3. Buat Prompt Video"


def generate_gemini_text(api_key: str, prompt: str) -> str:
    api_key = api_key.strip()
    if not api_key:
        raise ValueError("API key Gemini belum diisi.")
    client = genai.Client(api_key=api_key)
    interaction = client.interactions.create(model=GEMINI_MODEL, input=prompt)
    text = (interaction.output_text or "").strip()
    if not text:
        raise RuntimeError("Gemini tidak mengembalikan teks. Coba lagi dengan input yang lebih jelas.")
    return text


def save_prompt_callback() -> None:
    st.session_state.prompt_save_ok = save_image_prompt()


def select_image_callback() -> None:
    save_selected_image(st.session_state.image_uploader)


def reset_image_callback() -> None:
    clear_selected_image()


def go_video_callback() -> None:
    st.session_state.video_ready_ok = continue_to_video()


st.set_page_config(page_title="Creator Flow AI", page_icon="🎬", layout="centered")
initialize_image_video_state()

st.title("🎬 Creator Flow AI")
st.caption("Image → Select → Video workflow untuk Google Flow")

with st.sidebar:
    st.header("⚙️ Pengaturan")
    api_key = st.text_input("Google Gemini API Key", type="password")
    st.info("API key hanya digunakan saat request dan tidak ditulis ke source code.")

st.subheader("1. Produk / Subjek")
subject = st.text_area(
    "Deskripsikan produk atau subjek",
    placeholder="Contoh: sepatu olahraga pria warna hitam, desain casual, nyaman digunakan untuk olahraga.",
    height=100,
    key="subject",
)

st.subheader("2. Gaya Visual")
col1, col2 = st.columns(2)
with col1:
    style = st.selectbox(
        "Style",
        ["Photorealistic / Cinematic", "Natural UGC / TikTok", "Commercial Product Ad", "Anime / Manga", "3D Animation", "Cyberpunk", "Vintage Film"],
        key="style",
    )
    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        ["9:16 — TikTok / Reels / Shorts", "16:9 — YouTube", "1:1 — Square"],
        key="aspect_ratio",
    )
with col2:
    camera = st.selectbox(
        "Camera",
        ["Natural handheld", "Cinematic wide shot", "Medium shot", "Close-up product", "POV", "Top-down / Bird-eye"],
        key="camera",
    )
    lighting = st.selectbox(
        "Lighting",
        ["Natural daylight", "Golden hour", "Soft studio light", "Moody cinematic", "Neon"],
        key="lighting",
    )

st.subheader("3. Pipeline Produksi")
production_mode = st.radio(
    "Pilih tahap",
    [IMAGE_STAGE, SELECT_STAGE, VIDEO_STAGE],
    key="production_mode",
)

st.subheader("4. Jenis Konten")
content_type = st.selectbox(
    "Jenis konten",
    ["TikTok Affiliate — 3 Scene", "Storyboard — 3 sampai 5 Scene", "Prompt Video", "Ide Konten + Hook"],
    key="content_type",
)
story = st.text_area(
    "5. Ide / Informasi Produk / Alur",
    placeholder="Contoh: creator memakai sepatu, menunjukkan detail produk, lalu mengajak penonton cek keranjang kuning.",
    height=120,
    key="story",
)

if production_mode == IMAGE_STAGE:
    st.info("Buat 3 prompt gambar, pilih/edit satu, lalu simpan sebelum membuat gambar di Google Flow.")
    image_scene = st.text_area(
        "Adegan gambar",
        placeholder="Contoh: creator pria Indonesia sedang memakai sepatu di ruang tamu modern.",
        height=100,
        key="image_scene",
    )

    if st.button("🖼️ GENERATE 3 PROMPT GAMBAR", type="primary", use_container_width=True):
        if not api_key:
            st.error("Masukkan Google Gemini API Key terlebih dahulu.")
        elif not subject.strip():
            st.warning("Deskripsi produk belum diisi.")
        elif not image_scene.strip():
            st.warning("Adegan gambar belum diisi.")
        else:
            request = f"""
You are a professional Visual Director and Prompt Engineer for Google Flow.
Create EXACTLY 3 copy-paste-ready image prompts in English.

PRODUCT/SUBJECT:
{subject}
SCENE:
{image_scene}
STYLE:
{style}
ASPECT RATIO:
{aspect_ratio}
CAMERA:
{camera}
LIGHTING:
{lighting}
CONTENT IDEA:
{story}

RULES:
- Preserve product identity exactly: shape, color, logo, label, texture, material and details.
- If a person appears, use natural appearance and realistic anatomy.
- Keep the product clear and prominent.
- Avoid random text, watermarks, extra logos, malformed hands/fingers, distortion and AI artifacts.
- Use English only for the prompts.
- Make the three variations different mainly in framing/composition while keeping identity consistent.

FORMAT:
### IMAGE PROMPT 1
[complete English prompt]
### IMAGE PROMPT 2
[complete English prompt]
### IMAGE PROMPT 3
[complete English prompt]
"""
            try:
                with st.spinner("🖼️ Gemini sedang menyusun 3 prompt gambar..."):
                    st.session_state.image_prompts = generate_gemini_text(api_key, request)
                st.session_state.selected_image_prompt = ""
                st.session_state.image_prompt_editor = ""
                st.session_state.video_prompt_result = ""
                clear_selected_image()
                st.session_state.image_stage = "prompt"
                st.success("✅ 3 prompt gambar berhasil dibuat.")
            except Exception as exc:
                st.error(f"Terjadi kesalahan Gemini: {exc}")

    if st.session_state.image_prompts:
        st.divider()
        st.subheader("🖼️ Hasil Prompt Gambar")
        st.markdown(st.session_state.image_prompts)
        st.text_area(
            "Prompt gambar terpilih / hasil revisi",
            key="image_prompt_editor",
            placeholder="Salin prompt terbaik dari hasil di atas, lalu edit jika diperlukan.",
            height=200,
        )
        st.button("💾 SIMPAN PROMPT TERPILIH", on_click=save_prompt_callback, use_container_width=True)
        if st.session_state.get("prompt_save_ok"):
            st.success("✅ Prompt tersimpan. Buat gambar tersebut di Google Flow, lalu lanjut ke tahap 2.")
            st.download_button(
                "📥 Download Prompt Gambar",
                data=st.session_state.selected_image_prompt,
                file_name="creator_flow_image_prompt.txt",
                mime="text/plain",
                use_container_width=True,
            )

elif production_mode == SELECT_STAGE:
    st.info("Upload hasil gambar dari Google Flow. Gambar akan disalin ke Session State agar tidak bergantung pada state sementara uploader.")
    if not st.session_state.selected_image_prompt:
        st.warning("Simpan prompt gambar terlebih dahulu pada tahap 1.")
    else:
        st.text_area("📝 Prompt Gambar Terpilih", value=st.session_state.selected_image_prompt, height=160, disabled=True)
        uploaded = st.file_uploader(
            "Upload gambar hasil Google Flow",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=False,
            key="image_uploader",
            help="Pilih satu keyframe/gambar utama untuk kontinuitas video.",
        )
        if uploaded is not None:
            st.image(uploaded, caption="Preview gambar", use_container_width=True)
            st.button("⭐ JADIKAN GAMBAR UTAMA", on_click=select_image_callback, use_container_width=True)

        if st.session_state.selected_image_bytes:
            st.divider()
            st.subheader("⭐ Gambar Utama")
            st.image(st.session_state.selected_image_bytes, caption=st.session_state.selected_image_name, use_container_width=True)
            st.success("Gambar utama tersimpan di sesi ini.")
            c1, c2 = st.columns(2)
            with c1:
                st.button("🔄 Ganti Gambar Utama", on_click=reset_image_callback, use_container_width=True)
            with c2:
                st.button("➡️ LANJUT KE VIDEO", on_click=go_video_callback, type="primary", use_container_width=True)
            if st.session_state.get("video_ready_ok"):
                st.success("✅ Gambar utama siap. Buka tahap 3 untuk membuat prompt video.")

else:
    st.info("Tahap video membutuhkan prompt gambar tersimpan dan satu gambar utama hasil Google Flow.")
    if not st.session_state.selected_image_prompt:
        st.warning("Belum ada prompt gambar terpilih. Kembali ke tahap 1.")
    elif not st.session_state.selected_image_bytes:
        st.warning("Belum ada gambar utama. Kembali ke tahap 2 dan upload hasil Google Flow.")
    else:
        st.subheader("⭐ Referensi Gambar Utama")
        st.image(st.session_state.selected_image_bytes, caption=st.session_state.selected_image_name, use_container_width=True)
        st.text_area("📝 Prompt Gambar sebagai sumber kontinuitas", value=st.session_state.selected_image_prompt, height=150, disabled=True)
        duration = st.selectbox("Durasi per Scene", ["8 detik", "10 detik"], key="duration_video")
        voice = st.selectbox("Voice Over", ["Pria dewasa Indonesia, natural", "Wanita dewasa Indonesia, natural", "Tanpa voice over"], key="voice_video")

        if st.button("🎬 GENERATE PROMPT VIDEO", type="primary", use_container_width=True):
            prompt = f"""
You are a Creative Director and Prompt Engineer for generative video.
Create video prompts that preserve continuity from the selected main image.

PRODUCT/SUBJECT:
{subject}
MAIN IMAGE PROMPT:
{st.session_state.selected_image_prompt}
CONTENT TYPE:
{content_type}
IDE/STORY:
{story}
STYLE:
{style}
ASPECT RATIO:
{aspect_ratio}
CAMERA:
{camera}
LIGHTING:
{lighting}
DURATION PER SCENE:
{duration}
VOICE OVER:
{voice}

CONTINUITY RULES:
1. Preserve the product, character, face, clothing, location, colors, materials, lighting and visual identity from the main image.
2. Never introduce a different product or alter the product shape, color or logo.
3. Motion must be natural, physically plausible and realistic.
4. Camera movement must be clear and controlled.
5. Video prompts must be written in English; voice-over must be Indonesian.
6. For TikTok Affiliate — 3 Scene, create EXACTLY 3 scenes: HOOK → PROBLEM/PROOF → BENEFIT/CTA.
7. Each scene must reference continuity from the keyframe and provide an ending state suitable for the next scene.

FORMAT:
### Scene 1
**Tujuan:** ...
**Aksi Visual:** ...
**Prompt Video:** [complete English prompt]
**Voice Over:** ...
**SFX / Audio:** ...

### Scene 2
**Tujuan:** ...
**Aksi Visual:** ...
**Prompt Video:** [complete English prompt]
**Voice Over:** ...
**SFX / Audio:** ...

### Scene 3
**Tujuan:** ...
**Aksi Visual:** ...
**Prompt Video:** [complete English prompt]
**Voice Over:** ...
**SFX / Audio:** ...
"""
            try:
                with st.spinner("🎬 Gemini sedang menyusun prompt video..."):
                    st.session_state.video_prompt_result = generate_gemini_text(api_key, prompt)
                st.success("✅ Prompt video siap digunakan di Google Flow.")
            except Exception as exc:
                st.error(f"Terjadi kesalahan Gemini: {exc}")

        if st.session_state.video_prompt_result:
            st.divider()
            st.subheader("🎬 Hasil Prompt Video")
            st.markdown(st.session_state.video_prompt_result)
            st.download_button(
                "📥 Download Prompt Video",
                data=st.session_state.video_prompt_result,
                file_name="creator_flow_video_prompt.txt",
                mime="text/plain",
                use_container_width=True,
            )

st.divider()
st.caption("Creator Flow AI • Image → Select → Video • Gemini 3.6 Flash")
