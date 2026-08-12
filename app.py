import base64

import streamlit as st
from google import genai
from google.genai import types

GEMINI_TEXT_MODEL = "gemini-3.6-flash"
GEMINI_IMAGE_MODEL = "gemini-3.1-flash-image"


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


def use_generated_image_as_reference(image_bytes: bytes, mime_type: str = "image/png", name: str = "creator_flow_generated.png") -> None:
    st.session_state.selected_image_bytes = image_bytes
    st.session_state.selected_image_name = name
    st.session_state.selected_image_type = mime_type or "image/png"
    st.session_state.video_stage = "ready"
    st.session_state.video_prompt_result = ""
    st.session_state.image_stage = "selected"


def generate_gemini_text(api_key: str, prompt: str, image_bytes: bytes | None = None, mime_type: str = "image/png") -> str:
    api_key = api_key.strip()
    if not api_key:
        raise ValueError("API key Gemini belum diisi.")

    client = genai.Client(api_key=api_key)
    if image_bytes:
        input_data = [
            {"type": "text", "text": prompt},
            {
                "type": "image",
                "data": base64.b64encode(image_bytes).decode("utf-8"),
                "mime_type": mime_type or "image/png",
            },
        ]
    else:
        input_data = prompt

    interaction = client.interactions.create(model=GEMINI_TEXT_MODEL, input=input_data)
    text = (interaction.output_text or "").strip()
    if not text:
        raise RuntimeError("Gemini tidak mengembalikan teks. Coba lagi dengan brief yang lebih jelas.")
    return text


def generate_gemini_image(api_key: str, prompt: str, product_photo: bytes, mime_type: str, aspect_ratio: str) -> bytes:
    api_key = api_key.strip()
    if not api_key:
        raise ValueError("API key Gemini belum diisi.")

    ratio = {
        "9:16 — TikTok / Reels / Shorts": "9:16",
        "16:9 — YouTube": "16:9",
        "1:1 — Square": "1:1",
    }.get(aspect_ratio, "9:16")

    client = genai.Client(api_key=api_key)
    product_part = types.Part.from_bytes(data=product_photo, mime_type=mime_type or "image/png")
    response = client.models.generate_content(
        model=GEMINI_IMAGE_MODEL,
        contents=[prompt, product_part],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            response_format={"image": {"aspect_ratio": ratio, "image_size": "1K"}},
        ),
    )

    for part in response.parts:
        if getattr(part, "inline_data", None) is not None:
            data = part.inline_data.data
            if data:
                return data

    raise RuntimeError("Gemini tidak mengembalikan file gambar. Coba lagi dengan foto/brief yang lebih jelas.")


st.set_page_config(page_title="Creator Flow AI", page_icon="🎬", layout="centered")
initialize_image_video_state()

st.title("🎬 Creator Flow AI")
st.caption("📸 Foto Produk → 📝 Brief → 🤖 AI → 🖼️ Gambar → 🎞️ Video")

with st.sidebar:
    st.header("⚙️ Pengaturan AI")
    api_key = st.text_input("Google Gemini API Key", type="password")
    st.info("API key hanya digunakan untuk request dan tidak ditulis ke source code.")

st.header("1. 📸 Foto Produk")
st.write("Upload foto produk terlebih dahulu. Foto ini menjadi referensi utama agar identitas produk tetap konsisten.")
product_photo = st.file_uploader(
    "Upload foto produk",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=False,
    key="product_photo_uploader",
    help="Pilih foto produk yang jelas, tidak buram, dan menampilkan detail produk.",
)
if product_photo is not None:
    save_product_photo(product_photo)

if st.session_state.product_photo_bytes:
    st.image(st.session_state.product_photo_bytes, caption=st.session_state.product_photo_name, use_container_width=True)
    st.success("✅ Foto produk siap menjadi referensi AI.")
else:
    st.warning("Upload foto produk untuk mulai.")

st.header("2. 📝 Brief")
brief = st.text_area(
    "Apa yang ingin dibuat?",
    placeholder="Contoh: Buat iklan affiliate sepatu olahraga untuk TikTok. Pria muda memakai sepatu di taman, premium tetapi natural, hook kuat dan CTA cek keranjang kuning.",
    height=140,
    key="brief",
)

col1, col2 = st.columns(2)
with col1:
    style = st.selectbox("Gaya visual", ["Photorealistic / Cinematic", "Natural UGC / TikTok", "Commercial Product Ad", "Luxury Product Ad", "Anime / Manga", "3D Animation"], key="style")
    aspect_ratio = st.selectbox("Aspect ratio", ["9:16 — TikTok / Reels / Shorts", "16:9 — YouTube", "1:1 — Square"], key="aspect_ratio")
with col2:
    camera = st.selectbox("Kamera", ["Natural handheld", "Cinematic wide shot", "Medium shot", "Close-up product", "POV", "Top-down / Bird-eye"], key="camera")
    lighting = st.selectbox("Lighting", ["Natural daylight", "Golden hour", "Soft studio light", "Moody cinematic", "Neon"], key="lighting")

st.header("3. 🖼️ Buat Gambar")
st.info("AI akan memakai foto produk + brief. Hasil gambar ditampilkan langsung di aplikasi, bukan hanya sebagai prompt.")

if st.button("🖼️ AI BUAT GAMBAR", type="primary", use_container_width=True, key="generate_image"):
    if not api_key.strip():
        st.error("Masukkan Google Gemini API Key terlebih dahulu.")
    elif not st.session_state.product_photo_bytes:
        st.warning("Upload foto produk terlebih dahulu.")
    elif not brief.strip():
        st.warning("Brief belum diisi.")
    else:
        image_prompt = f"""
Create a polished commercial image using the supplied product photo as the primary reference.
Preserve the exact product identity: shape, proportions, colors, materials, texture, logo, label,
packaging and distinctive details. Do not replace, redesign, duplicate, or invent the product.

BRIEF:
{brief}

STYLE: {style}
ASPECT RATIO: {aspect_ratio}
CAMERA: {camera}
LIGHTING: {lighting}

Create a believable advertising scene suitable for social media. Keep the product clearly visible,
with realistic shadows, anatomy and reflections. No watermark, random text, extra logos, or distorted product details.
"""
        try:
            with st.spinner("🤖 Gemini sedang membuat gambar nyata dari foto produk..."):
                generated = generate_gemini_image(
                    api_key,
                    image_prompt,
                    st.session_state.product_photo_bytes,
                    st.session_state.product_photo_type,
                    aspect_ratio,
                )
            st.session_state.generated_image_bytes = generated
            st.session_state.generated_image_type = "image/png"
            st.session_state.video_prompt_result = ""
            st.success("✅ Gambar berhasil dibuat.")
        except Exception as exc:
            st.error(f"Gagal membuat gambar: {exc}")

if st.session_state.generated_image_bytes:
    st.subheader("🖼️ Hasil Gambar AI")
    st.image(st.session_state.generated_image_bytes, caption="Hasil gambar AI", use_container_width=True)
    st.download_button(
        "📥 DOWNLOAD GAMBAR HASIL",
        data=st.session_state.generated_image_bytes,
        file_name="creator_flow_ai_image.png",
        mime="image/png",
        use_container_width=True,
        on_click="ignore",
    )
    if st.button("✅ PILIH GAMBAR INI UNTUK VIDEO", use_container_width=True, key="select_generated"):
        use_generated_image_as_reference(
            st.session_state.generated_image_bytes,
            st.session_state.generated_image_type,
            "creator_flow_ai_image.png",
        )
        st.success("✅ Gambar dipilih. Sekarang lanjut ke tahap video.")

st.subheader("📤 Atau pilih gambar dari Google Flow")
flow_image = st.file_uploader(
    "Upload gambar final yang ingin dijadikan referensi video",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=False,
    key="flow_image_uploader",
)
if flow_image is not None:
    st.session_state.selected_image_bytes = flow_image.getvalue()
    st.session_state.selected_image_name = flow_image.name
    st.session_state.selected_image_type = flow_image.type or "image/png"
    st.session_state.video_stage = "ready"
    st.success("✅ Gambar dari Google Flow sudah dipilih sebagai referensi video.")

st.header("4. 🎬 Video")
if st.session_state.selected_image_bytes:
    st.image(st.session_state.selected_image_bytes, caption="Gambar terpilih untuk video", use_container_width=True)
    st.success("✅ Gambar utama sudah dipilih. AI siap menyusun video berdasarkan gambar ini + brief.")

    duration = st.selectbox("Durasi setiap scene", ["8 detik", "10 detik"], key="duration_video")
    voice = st.selectbox("Voice Over", ["Pria dewasa Indonesia, natural", "Wanita dewasa Indonesia, natural", "Tanpa voice over"], key="voice_video")

    if st.button("🎬 AI SUSUN VIDEO", type="primary", use_container_width=True, key="generate_video"):
        if not api_key.strip():
            st.error("Masukkan Google Gemini API Key terlebih dahulu.")
        elif not brief.strip():
            st.warning("Brief belum diisi.")
        else:
            video_prompt = f"""
You are a senior commercial video director and Google Flow / Veo prompt engineer.
Use the selected reference image as the visual source of truth for the product.
Preserve product shape, proportions, colors, logo, label, materials, texture and distinctive details.

BRIEF:
{brief}
STYLE: {style}
ASPECT RATIO: {aspect_ratio}
CAMERA: {camera}
LIGHTING: {lighting}
DURATION PER SCENE: {duration}
VOICE OVER: {voice}

Create EXACTLY 3 connected scenes for a social-media product video.
For each scene provide:
### Scene N — title
**Tujuan:** concise purpose
**Aksi Visual:** what the person/product does
**Prompt Video:** a complete English Google Flow / Veo-ready prompt describing subject, action, camera movement, composition, lighting, continuity and realistic motion
**Voice Over:** Indonesian line if requested
**SFX / Audio:** concise sound direction

Continuity rules:
- The selected reference image is the source of truth.
- Never change the product or add a different product.
- Keep motion physically plausible.
- No watermark, random text, fake logo, or product deformation.
- Prompts are English; voice-over is Indonesian.
"""
            try:
                with st.spinner("🤖 AI sedang menyusun 3 scene video..."):
                    st.session_state.video_prompt_result = generate_gemini_text(
                        api_key,
                        video_prompt,
                        st.session_state.selected_image_bytes,
                        st.session_state.selected_image_type,
                    )
                st.success("✅ Prompt video siap digunakan di Google Flow.")
            except Exception as exc:
                st.error(f"Gagal menyusun video: {exc}")

    if st.session_state.video_prompt_result:
        st.subheader("🎬 Hasil Rencana Video")
        st.markdown(st.session_state.video_prompt_result)
        st.download_button(
            "📥 DOWNLOAD PROMPT VIDEO",
            data=st.session_state.video_prompt_result,
            file_name="creator_flow_video_prompt.txt",
            mime="text/plain",
            use_container_width=True,
            on_click="ignore",
        )
else:
    st.info("Belum ada gambar terpilih. Buat gambar AI terlebih dahulu, lalu tekan **PILIH GAMBAR INI UNTUK VIDEO**, atau upload gambar final dari Google Flow.")

st.divider()
st.caption("Creator Flow AI • Foto Produk → Brief → Gambar → Pilih Gambar → Video • Gemini 3.6 Flash")
