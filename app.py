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


st.set_page_config(page_title="Creator Flow AI", page_icon="🎬", layout="centered", initial_sidebar_state="collapsed")
initialize_image_video_state()

# Modern Android-style UI: compact, rounded, touch-friendly and optimized for mobile.
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root { --cf-bg:#090b10; --cf-card:#151821; --cf-card2:#1b1f2a; --cf-text:#f7f8fb; --cf-muted:#9da5b5; --cf-accent:#8b5cf6; --cf-accent2:#6d5dfc; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: radial-gradient(circle at 50% -10%, #25213d 0, var(--cf-bg) 35%); color:var(--cf-text); }
.block-container { max-width: 760px; padding: 1rem 1rem 5rem; }
header[data-testid="stHeader"] { background:transparent; }
[data-testid="stToolbar"] { display:none; }

.cf-hero { padding: 12px 4px 18px; }
.cf-brand { display:flex; align-items:center; gap:12px; font-size:29px; font-weight:800; letter-spacing:-1px; }
.cf-logo { width:46px; height:46px; display:grid; place-items:center; border-radius:15px; background:linear-gradient(135deg,#8b5cf6,#ec4899); box-shadow:0 8px 28px rgba(139,92,246,.28); font-size:24px; }
.cf-sub { color:var(--cf-muted); margin-top:7px; font-size:13px; }
.cf-flow { display:flex; gap:6px; overflow:hidden; margin-top:15px; }
.cf-pill { white-space:nowrap; padding:7px 10px; border-radius:999px; background:#171a24; color:#b8bfce; font-size:11px; border:1px solid #262b38; }
.cf-pill.active { color:#fff; background:#292143; border-color:#6046a9; }

h1,h2,h3 { letter-spacing:-.5px; }
h2 { font-size:20px !important; margin-top:24px !important; margin-bottom:10px !important; }
h3 { font-size:17px !important; }

[data-testid="stFileUploader"] { background:var(--cf-card); border:1px solid #292e3b; border-radius:20px; padding:6px; }
[data-testid="stFileUploaderDropzone"] { border:1px dashed #4a5060; border-radius:16px; background:#10131a; min-height:120px; }
[data-testid="stFileUploaderDropzoneInstructions"] { color:#b9c0cd; }

[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input, [data-testid="stSelectbox"] div[data-baseweb="select"] > div { background:#171a23 !important; color:#f7f8fb !important; border-color:#2b3040 !important; border-radius:15px !important; }
[data-testid="stTextArea"] textarea { min-height:130px; }
label { color:#c8ced9 !important; font-weight:600 !important; font-size:13px !important; }

button[kind="primary"], .stButton > button[kind="primary"] { border:0 !important; border-radius:16px !important; min-height:52px !important; font-weight:800 !important; background:linear-gradient(135deg,#8b5cf6,#6d5dfc) !important; box-shadow:0 8px 24px rgba(109,93,252,.25); }
.stButton > button, .stDownloadButton > button { border-radius:15px !important; min-height:48px !important; font-weight:700 !important; border:1px solid #343a49 !important; background:#1b1f29 !important; color:#f7f8fb !important; }
.stButton > button:hover, .stDownloadButton > button:hover { border-color:#7564d8 !important; }

[data-testid="stAlert"] { border-radius:16px; border:1px solid #303646; }
[data-testid="stImage"] { border-radius:20px; overflow:hidden; border:1px solid #2a2f3c; background:#11141b; }
[data-testid="stExpander"] { background:var(--cf-card); border:1px solid #292e3b; border-radius:18px; }
[data-testid="stExpander"] summary { font-weight:700; }
[data-testid="stHorizontalBlock"] { gap:10px; }
hr { border-color:#272c37 !important; margin:28px 0 !important; }

.cf-card { background:linear-gradient(180deg,#171a23,#12151c); border:1px solid #292e3b; border-radius:20px; padding:16px; margin:10px 0; }
.cf-label { color:#9da5b5; font-size:12px; font-weight:600; }
.cf-title { font-size:16px; font-weight:800; margin-top:3px; }
.cf-note { color:#9da5b5; font-size:12px; line-height:1.5; }

@media (max-width: 600px) {
  .block-container { padding: .75rem .8rem 4rem; }
  .cf-brand { font-size:25px; }
  .cf-logo { width:42px; height:42px; }
  h2 { font-size:19px !important; }
  [data-testid="stHorizontalBlock"] { flex-direction:column; }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="cf-hero">
  <div class="cf-brand"><div class="cf-logo">🎬</div><div>Creator Flow AI</div></div>
  <div class="cf-sub">Buat konten produk dari foto sampai video, langkah demi langkah.</div>
  <div class="cf-flow">
    <span class="cf-pill active">1 Foto</span><span class="cf-pill">2 Brief</span><span class="cf-pill">3 Gambar</span><span class="cf-pill">4 Video</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

with st.expander("⚙️ Pengaturan AI", expanded=False):
    api_key = st.text_input("Google Gemini API Key", type="password", help="API key hanya digunakan untuk request dan tidak ditulis ke source code.")
    st.caption("🔒 API key tidak disimpan di source code aplikasi.")

st.header("1. 📸 Foto Produk")
st.caption("Upload foto produk terlebih dahulu. Foto ini menjadi referensi utama agar identitas produk tetap konsisten.")
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
    st.success("Foto produk siap menjadi referensi AI.")
else:
    st.info("📷 Tambahkan foto produk untuk memulai.")

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
st.caption("AI memakai foto produk + brief. Hasil gambar ditampilkan langsung di aplikasi.")

if st.button("🖼️  BUAT GAMBAR DENGAN AI", type="primary", use_container_width=True, key="generate_image"):
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
            st.success("Gambar berhasil dibuat.")
        except Exception as exc:
            st.error(f"Gagal membuat gambar: {exc}")

if st.session_state.generated_image_bytes:
    st.subheader("Hasil Gambar AI")
    st.image(st.session_state.generated_image_bytes, caption="Hasil gambar AI", use_container_width=True)
    st.download_button(
        "📥  SIMPAN GAMBAR",
        data=st.session_state.generated_image_bytes,
        file_name="creator_flow_ai_image.png",
        mime="image/png",
        use_container_width=True,
        on_click="ignore",
    )
    if st.button("✅  PILIH GAMBAR INI UNTUK VIDEO", use_container_width=True, key="select_generated"):
        use_generated_image_as_reference(
            st.session_state.generated_image_bytes,
            st.session_state.generated_image_type,
            "creator_flow_ai_image.png",
        )
        st.success("Gambar dipilih. Sekarang lanjut ke tahap video.")

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
    st.success("Gambar dari Google Flow sudah dipilih sebagai referensi video.")

st.header("4. 🎬 Video")
if st.session_state.selected_image_bytes:
    st.image(st.session_state.selected_image_bytes, caption="Gambar terpilih untuk video", use_container_width=True)
    st.success("Gambar utama sudah dipilih. AI siap menyusun video berdasarkan gambar ini + brief.")

    duration = st.selectbox("Durasi setiap scene", ["8 detik", "10 detik"], key="duration_video")
    voice = st.selectbox("Voice Over", ["Pria dewasa Indonesia, natural", "Wanita dewasa Indonesia, natural", "Tanpa voice over"], key="voice_video")

    if st.button("🎬  SUSUN VIDEO DENGAN AI", type="primary", use_container_width=True, key="generate_video"):
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
                st.success("Prompt video siap digunakan di Google Flow.")
            except Exception as exc:
                st.error(f"Gagal menyusun video: {exc}")

    if st.session_state.video_prompt_result:
        st.subheader("🎬 Hasil Rencana Video")
        st.markdown(st.session_state.video_prompt_result)
        st.download_button(
            "📥  SIMPAN PROMPT VIDEO",
            data=st.session_state.video_prompt_result,
            file_name="creator_flow_video_prompt.txt",
            mime="text/plain",
            use_container_width=True,
            on_click="ignore",
        )
else:
    st.info("Belum ada gambar terpilih. Buat gambar AI terlebih dahulu, lalu pilih hasilnya untuk video, atau upload gambar final dari Google Flow.")

st.divider()
st.caption("Creator Flow AI  •  Foto Produk → Brief → Gambar → Pilih Gambar → Video  •  Gemini 3.6 Flash")
