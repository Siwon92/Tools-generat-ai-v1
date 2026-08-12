import base64

import streamlit as st
from google import genai

from image_to_video_state import (
    clear_selected_image,
    continue_to_video,
    initialize_image_video_state,
    save_image_prompt,
    save_product_photo,
    save_selected_image,
    use_generated_image_as_reference,
)

GEMINI_TEXT_MODEL = "gemini-3.6-flash"
GEMINI_IMAGE_MODEL = "gemini-3.1-flash-image"


def generate_gemini_text(
    api_key: str,
    prompt: str,
    image_bytes: bytes | None = None,
    mime_type: str = "image/png",
) -> str:
    api_key = api_key.strip()
    if not api_key:
        raise ValueError("API key Gemini belum diisi.")

    client = genai.Client(api_key=api_key)
    if image_bytes:
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        input_data = [
            {"type": "text", "text": prompt},
            {"type": "image", "data": image_b64, "mime_type": mime_type or "image/png"},
        ]
    else:
        input_data = prompt

    interaction = client.interactions.create(model=GEMINI_TEXT_MODEL, input=input_data)
    text = (interaction.output_text or "").strip()
    if not text:
        raise RuntimeError("Gemini tidak mengembalikan teks. Coba lagi dengan brief yang lebih jelas.")
    return text


def generate_gemini_image(
    api_key: str,
    prompt: str,
    product_photo: bytes,
    mime_type: str,
) -> bytes:
    api_key = api_key.strip()
    if not api_key:
        raise ValueError("API key Gemini belum diisi.")

    client = genai.Client(api_key=api_key)
    image_b64 = base64.b64encode(product_photo).decode("utf-8")
    interaction = client.interactions.create(
        model=GEMINI_IMAGE_MODEL,
        input=[
            {"type": "text", "text": prompt},
            {"type": "image", "data": image_b64, "mime_type": mime_type or "image/png"},
        ],
    )
    generated = getattr(interaction, "output_image", None)
    if not generated or not getattr(generated, "data", None):
        raise RuntimeError("Gemini tidak mengembalikan gambar. Coba lagi dengan brief yang lebih jelas.")
    return base64.b64decode(generated.data)


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
st.caption("Foto Produk → Brief → AI → Gambar / Video")

with st.sidebar:
    st.header("⚙️ Pengaturan AI")
    api_key = st.text_input("Google Gemini API Key", type="password")
    st.info("API key hanya digunakan saat request dan tidak ditulis ke source code.")

# -----------------------------------------------------------------------------
# 1. PRODUCT PHOTO
# -----------------------------------------------------------------------------
st.header("1. 📸 Foto Produk")
st.write("Upload foto produk terlebih dahulu. Foto ini menjadi referensi utama agar AI menjaga bentuk, warna, logo, label, dan detail produk.")

product_photo = st.file_uploader(
    "Upload foto produk",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=False,
    key="product_photo_uploader",
    help="Gunakan foto produk yang jelas dan tidak buram.",
)
if product_photo is not None:
    save_product_photo(product_photo)

if st.session_state.product_photo_bytes:
    st.image(
        st.session_state.product_photo_bytes,
        caption=f"Foto produk: {st.session_state.product_photo_name}",
        use_container_width=True,
    )
    st.success("✅ Foto produk sudah menjadi referensi AI.")
else:
    st.warning("Upload foto produk sebelum menjalankan AI.")

# -----------------------------------------------------------------------------
# 2. BRIEF
# -----------------------------------------------------------------------------
st.header("2. 📝 Brief")
st.write("Tulis brief singkat. Tidak perlu membuat prompt teknis — AI yang menyusun prompt berdasarkan foto produk dan brief Anda.")

brief = st.text_area(
    "Brief kampanye / kebutuhan konten",
    placeholder=(
        "Contoh: Buat konten affiliate sepatu olahraga untuk TikTok. Tampilkan produk dipakai pria muda di taman, "
        "terlihat premium tetapi natural, ada hook di awal dan CTA untuk cek keranjang kuning."
    ),
    height=150,
    key="brief",
)

col1, col2 = st.columns(2)
with col1:
    style = st.selectbox(
        "Gaya visual",
        [
            "Photorealistic / Cinematic",
            "Natural UGC / TikTok",
            "Commercial Product Ad",
            "Luxury Product Ad",
            "Anime / Manga",
            "3D Animation",
            "Vintage Film",
        ],
        key="style",
    )
    aspect_ratio = st.selectbox(
        "Aspect ratio",
        ["9:16 — TikTok / Reels / Shorts", "16:9 — YouTube", "1:1 — Square"],
        key="aspect_ratio",
    )
with col2:
    camera = st.selectbox(
        "Kamera",
        ["Natural handheld", "Cinematic wide shot", "Medium shot", "Close-up product", "POV", "Top-down / Bird-eye"],
        key="camera",
    )
    lighting = st.selectbox(
        "Lighting",
        ["Natural daylight", "Golden hour", "Soft studio light", "Moody cinematic", "Neon"],
        key="lighting",
    )

# -----------------------------------------------------------------------------
# 3. CHOOSE OUTPUT
# -----------------------------------------------------------------------------
st.header("3. 🤖 Pilih Hasil AI")
output_mode = st.radio(
    "AI mau membuat apa?",
    ["Gambar", "Video"],
    horizontal=True,
    key="output_mode",
)

if output_mode == "Gambar":
    st.info("AI akan membaca foto produk + brief, lalu membuat gambar iklan baru dengan produk tetap konsisten.")

    if st.button("🖼️ AI BUAT GAMBAR", type="primary", use_container_width=True):
        if not api_key.strip():
            st.error("Masukkan Google Gemini API Key terlebih dahulu.")
        elif not st.session_state.product_photo_bytes:
            st.warning("Upload foto produk terlebih dahulu.")
        elif not brief.strip():
            st.warning("Brief belum diisi.")
        else:
            image_prompt = f"""
Create a professional commercial image using the provided product photo as the primary product reference.
The product identity must remain faithful to the reference: preserve its exact shape, proportions, colors,
materials, texture, logo, label, packaging and distinctive details. Do not invent or replace the product.

BRIEF:
{brief}

VISUAL STYLE: {style}
ASPECT RATIO: {aspect_ratio}
CAMERA: {camera}
LIGHTING: {lighting}

Create a polished, realistic scene suitable for social-media advertising. Make the product clearly visible and
use natural composition, realistic shadows, believable hands/body anatomy if a person appears, and clean visual
hierarchy. No watermark, no random text, no extra logos, no distorted product details.
"""
            try:
                with st.spinner("🤖 AI sedang membuat gambar dari foto produk + brief..."):
                    generated = generate_gemini_image(
                        api_key,
                        image_prompt,
                        st.session_state.product_photo_bytes,
                        st.session_state.product_photo_type,
                    )
                st.session_state.generated_image_bytes = generated
                st.session_state.generated_image_type = "image/png"
                st.success("✅ Gambar berhasil dibuat oleh AI.")
            except Exception as exc:
                st.error(f"Gagal membuat gambar: {exc}")

    if st.session_state.generated_image_bytes:
        st.divider()
        st.subheader("🖼️ Hasil Gambar AI")
        st.image(st.session_state.generated_image_bytes, caption="Hasil gambar AI", use_container_width=True)
        st.download_button(
            "📥 DOWNLOAD GAMBAR HASIL",
            data=st.session_state.generated_image_bytes,
            file_name="creator_flow_ai_image.png",
            mime="image/png",
            use_container_width=True,
        )

        if st.button("➡️ GUNAKAN GAMBAR INI UNTUK VIDEO", type="secondary", use_container_width=True):
            use_generated_image_as_reference(
                st.session_state.generated_image_bytes,
                st.session_state.generated_image_type,
                "creator_flow_ai_image.png",
            )
            st.success("✅ Gambar AI dijadikan gambar utama untuk tahap video.")

else:
    st.info("AI akan membaca foto produk + brief dan menyusun prompt video siap dipakai di Google Flow. Foto produk tetap menjadi referensi kontinuitas.")

    duration = st.selectbox("Durasi per scene", ["8 detik", "10 detik"], key="duration_video")
    voice = st.selectbox(
        "Voice Over",
        ["Pria dewasa Indonesia, natural", "Wanita dewasa Indonesia, natural", "Tanpa voice over"],
        key="voice_video",
    )

    if st.button("🎬 AI SUSUN VIDEO", type="primary", use_container_width=True):
        if not api_key.strip():
            st.error("Masukkan Google Gemini API Key terlebih dahulu.")
        elif not st.session_state.product_photo_bytes:
            st.warning("Upload foto produk terlebih dahulu.")
        elif not brief.strip():
            st.warning("Brief belum diisi.")
        else:
            video_prompt = f"""
You are a senior commercial video director and prompt engineer for Google Flow / Veo.
Analyze the provided product photo and create a production-ready image-to-video plan.
The product must remain exactly consistent with the reference image: shape, color, logo, label, materials,
texture and distinctive details must not change.

BRIEF:
{brief}
STYLE: {style}
ASPECT RATIO: {aspect_ratio}
CAMERA: {camera}
LIGHTING: {lighting}
DURATION PER SCENE: {duration}
VOICE OVER: {voice}

Create EXACTLY 3 scenes with the structure:
### Scene 1 — HOOK
**Tujuan:** ...
**Aksi Visual:** ...
**Prompt Video:** complete English prompt for Google Flow
**Voice Over:** Indonesian voice-over if requested
**SFX / Audio:** ...

### Scene 2 — DEMONSTRATION / PROOF
**Tujuan:** ...
**Aksi Visual:** ...
**Prompt Video:** complete English prompt for Google Flow
**Voice Over:** Indonesian voice-over if requested
**SFX / Audio:** ...

### Scene 3 — BENEFIT / CTA
**Tujuan:** ...
**Aksi Visual:** ...
**Prompt Video:** complete English prompt for Google Flow
**Voice Over:** Indonesian voice-over if requested
**SFX / Audio:** ...

Rules:
- Preserve product identity and continuity in every scene.
- Motion must be realistic and physically plausible.
- Use clear camera movement and natural lighting.
- Do not add random text, watermarks, extra logos or a different product.
- Prompts must be English; voice-over must be Indonesian.
"""
            try:
                with st.spinner("🤖 AI sedang membaca foto produk dan menyusun video..."):
                    st.session_state.video_prompt_result = generate_gemini_text(
                        api_key,
                        video_prompt,
                        st.session_state.product_photo_bytes,
                        st.session_state.product_photo_type,
                    )
                st.success("✅ Rencana video siap. Gunakan prompt ini di Google Flow untuk merender videonya.")
            except Exception as exc:
                st.error(f"Gagal menyusun video: {exc}")

    if st.session_state.video_prompt_result:
        st.divider()
        st.subheader("🎬 Hasil Video AI")
        st.markdown(st.session_state.video_prompt_result)
        st.download_button(
            "📥 DOWNLOAD PROMPT VIDEO (TXT)",
            data=st.session_state.video_prompt_result,
            file_name="creator_flow_video_prompt.txt",
            mime="text/plain",
            use_container_width=True,
        )

# -----------------------------------------------------------------------------
# Optional image-to-video reference handoff
# -----------------------------------------------------------------------------
if st.session_state.selected_image_bytes:
    st.divider()
    st.header("4. 🎞️ Gambar Utama untuk Video")
    st.image(
        st.session_state.selected_image_bytes,
        caption=st.session_state.selected_image_name,
        use_container_width=True,
    )
    st.success("✅ Gambar utama siap dipakai sebagai keyframe/referensi video.")
    st.download_button(
        "📥 DOWNLOAD GAMBAR UTAMA",
        data=st.session_state.selected_image_bytes,
        file_name=st.session_state.selected_image_name or "creator_flow_image.png",
        mime=st.session_state.selected_image_type or "image/png",
        use_container_width=True,
    )

st.divider()
st.caption("Creator Flow AI • Foto Produk → Brief → AI → Gambar / Video • Gemini 3.6 Flash")
