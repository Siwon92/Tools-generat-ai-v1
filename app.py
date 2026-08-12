import base64

import streamlit as st
from google import genai
from google.genai import types

GEMINI_TEXT_MODEL = "gemini-3.6-flash"
GEMINI_IMAGE_MODEL = "gemini-3.1-flash-image"
MAX_PRODUCT_PHOTOS = 7


def initialize_image_video_state() -> None:
    defaults = {
        "product_photos": [],
        "brief": "",
        "selected_image_bytes": None,
        "selected_image_name": "",
        "selected_image_type": "image/png",
        "generated_image_bytes": None,
        "generated_image_type": "image/png",
        "video_prompt_result": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Migrate the old single-photo session state if a user has an active session.
    if not st.session_state.product_photos and st.session_state.get("product_photo_bytes"):
        st.session_state.product_photos = [
            {
                "bytes": st.session_state.product_photo_bytes,
                "name": st.session_state.get("product_photo_name", "product.png"),
                "type": st.session_state.get("product_photo_type", "image/png"),
            }
        ]


def save_product_photos(uploaded_files) -> None:
    photos = []
    for uploaded_file in uploaded_files or []:
        image_bytes = uploaded_file.getvalue()
        if not image_bytes:
            continue
        photos.append(
            {
                "bytes": image_bytes,
                "name": uploaded_file.name,
                "type": uploaded_file.type or "image/png",
            }
        )

    # Streamlit reruns on upload; replace the selection with the current uploader state.
    if len(photos) > MAX_PRODUCT_PHOTOS:
        st.warning(f"Maksimal {MAX_PRODUCT_PHOTOS} foto produk. Foto setelah nomor {MAX_PRODUCT_PHOTOS} diabaikan.")
        photos = photos[:MAX_PRODUCT_PHOTOS]

    if photos != st.session_state.product_photos:
        st.session_state.product_photos = photos
        st.session_state.generated_image_bytes = None
        st.session_state.selected_image_bytes = None
        st.session_state.selected_image_name = ""
        st.session_state.video_prompt_result = ""


def use_generated_image_as_reference(image_bytes: bytes, mime_type: str = "image/png", name: str = "creator_flow_generated.png") -> None:
    st.session_state.selected_image_bytes = image_bytes
    st.session_state.selected_image_name = name
    st.session_state.selected_image_type = mime_type or "image/png"
    st.session_state.video_prompt_result = ""


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


def generate_gemini_image(api_key: str, prompt: str, product_photos: list[dict], aspect_ratio: str) -> bytes:
    api_key = api_key.strip()
    if not api_key:
        raise ValueError("API key Gemini belum diisi.")
    if not product_photos:
        raise ValueError("Minimal satu foto produk diperlukan.")

    ratio = {
        "9:16 — TikTok / Reels / Shorts": "9:16",
        "16:9 — YouTube": "16:9",
        "1:1 — Square": "1:1",
    }.get(aspect_ratio, "9:16")

    client = genai.Client(api_key=api_key)
    contents = [prompt]
    for photo in product_photos[:MAX_PRODUCT_PHOTOS]:
        contents.append(types.Part.from_bytes(data=photo["bytes"], mime_type=photo["type"] or "image/png"))

    response = client.models.generate_content(
        model=GEMINI_IMAGE_MODEL,
        contents=contents,
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

# ChatGPT-inspired mobile UI: quiet dark canvas, compact top bar, chat bubbles and composer-like controls.
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root{--bg:#0b0b0f;--surface:#17171c;--surface2:#212126;--border:#2b2b32;--text:#f5f5f7;--muted:#a7a7b0;--accent:#8b5cf6;}
html,body,[class*="css"]{font-family:Inter,system-ui,sans-serif}.stApp{background:var(--bg);color:var(--text)}
.block-container{max-width:760px;padding:0 14px 110px}.stApp>header{background:transparent}
[data-testid="stToolbar"]{display:none}
.cf-topbar{position:sticky;top:0;z-index:20;margin:0 -14px;padding:12px 14px 10px;background:rgba(11,11,15,.94);backdrop-filter:blur(18px);border-bottom:1px solid #1c1c21;display:flex;align-items:center;justify-content:space-between}
.cf-title{font-size:17px;font-weight:700}.cf-subtitle{font-size:11px;color:var(--muted);margin-top:2px}.cf-menu{font-size:20px;color:#d9d9df}
.cf-welcome{text-align:center;padding:34px 12px 24px}.cf-logo{width:48px;height:48px;margin:0 auto 12px;border-radius:16px;display:grid;place-items:center;background:#fff;color:#111;font-size:24px}.cf-welcome h1{font-size:26px;margin:0 0 7px;letter-spacing:-.7px}.cf-welcome p{color:var(--muted);font-size:13px;margin:0}
.cf-stepbar{display:flex;gap:7px;overflow-x:auto;padding:2px 0 12px;scrollbar-width:none}.cf-step{white-space:nowrap;padding:7px 10px;border:1px solid var(--border);border-radius:999px;background:#131318;color:#9e9ea7;font-size:11px}.cf-step.active{color:#fff;border-color:#5f47a7;background:#211a34}
.cf-bubble{background:var(--surface);border:1px solid #24242a;border-radius:18px;padding:15px;margin:10px 0 14px}.cf-bubble.user{background:#17171b}.cf-label{font-size:12px;font-weight:700;color:#c9c9d0;margin-bottom:8px}.cf-muted{color:var(--muted);font-size:12px;line-height:1.5}.cf-count{float:right;color:#9d8bea}
[data-testid="stFileUploader"]{background:transparent;border:0;padding:0}.stFileUploader>div{border:0}.stFileUploader section{background:#121217;border:1px dashed #41414a;border-radius:17px}
[data-testid="stFileUploaderDropzone"]{min-height:105px;border:1px dashed #41414a;border-radius:17px;background:#121217}.stFileUploader small{color:var(--muted)}
[data-testid="stTextArea"] textarea,[data-testid="stTextInput"] input,[data-testid="stSelectbox"] div[data-baseweb="select"]>div{background:#17171c!important;color:#f5f5f7!important;border:1px solid #2b2b32!important;border-radius:16px!important}label{color:#c9c9d0!important;font-size:12px!important;font-weight:600!important}
[data-testid="stTextArea"] textarea{min-height:120px}.stButton>button,.stDownloadButton>button{min-height:48px;border-radius:15px!important;background:#202027!important;color:#f5f5f7!important;border:1px solid #34343c!important;font-weight:700!important}.stButton>button[kind="primary"]{background:#fff!important;color:#111!important;border-color:#fff!important}
[data-testid="stImage"]{border-radius:16px;overflow:hidden;border:1px solid #292930}.stAlert{border-radius:15px}.stExpander{background:#15151a;border:1px solid #292930;border-radius:16px}
hr{border-color:#26262d!important;margin:22px 0!important}.cf-photo-card{background:#121217;border:1px solid #292930;border-radius:16px;padding:8px;height:100%}.cf-photo-name{font-size:10px;color:#aaaab3;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;padding:5px 2px 1px}
.cf-composer{position:fixed;left:50%;bottom:0;transform:translateX(-50%);width:min(760px,100%);padding:9px 14px 12px;background:linear-gradient(transparent,#0b0b0f 22%);z-index:15;pointer-events:none}.cf-composer>div{pointer-events:auto;background:#17171c;border:1px solid #34343c;border-radius:20px;padding:8px 12px;color:#8f8f98;font-size:11px;text-align:center}
@media(max-width:600px){.block-container{padding:0 12px 105px}.cf-topbar{margin:0 -12px}.cf-welcome{padding-top:28px}.cf-bubble{padding:13px}.cf-photo-card{padding:6px}}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="cf-topbar"><div><div class="cf-title">Creator Flow AI</div><div class="cf-subtitle">Image → Select → Video</div></div><div class="cf-menu">⋯</div></div>
<div class="cf-welcome"><div class="cf-logo">🎬</div><h1>Creator Flow AI</h1><p>Ubah foto produk menjadi konsep gambar dan video yang siap dipakai.</p></div>
<div class="cf-stepbar"><span class="cf-step active">① Foto</span><span class="cf-step">② Brief</span><span class="cf-step">③ Gambar</span><span class="cf-step">④ Pilih</span><span class="cf-step">⑤ Video</span></div>
""",
    unsafe_allow_html=True,
)

with st.expander("⚙️ Pengaturan AI", expanded=False):
    api_key = st.text_input("Google Gemini API Key", type="password", help="API key hanya digunakan untuk request dan tidak ditulis ke source code.")
    st.caption("🔒 API key tidak disimpan di source code aplikasi.")

st.markdown('<div class="cf-bubble"><div class="cf-label">📸 Foto Produk <span class="cf-count">maks. 7</span></div><div class="cf-muted">Tambahkan sampai 7 sudut foto produk. AI akan memakai semuanya sebagai referensi identitas produk.</div></div>', unsafe_allow_html=True)
product_files = st.file_uploader(
    "Tambahkan foto produk",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
    key="product_photos_uploader",
    help="Maksimal 7 foto. Pilih foto depan, belakang, samping, detail logo/tekstur, dan sudut lain yang penting.",
)
if product_files:
    save_product_photos(product_files)

if st.session_state.product_photos:
    st.caption(f"{len(st.session_state.product_photos)} / {MAX_PRODUCT_PHOTOS} foto produk dipilih")
    photo_cols = st.columns(2)
    for index, photo in enumerate(st.session_state.product_photos):
        with photo_cols[index % 2]:
            st.markdown('<div class="cf-photo-card">', unsafe_allow_html=True)
            st.image(photo["bytes"], use_container_width=True)
            st.markdown(f'<div class="cf-photo-name">{index + 1}. {photo["name"]}</div></div>', unsafe_allow_html=True)
    st.success("Semua foto siap menjadi referensi AI.")
else:
    st.info("📷 Tambahkan minimal 1 foto produk untuk memulai.")

st.markdown('<div class="cf-bubble"><div class="cf-label">📝 Brief</div><div class="cf-muted">Tulis tujuan konten seperti sedang memberi instruksi ke AI.</div></div>', unsafe_allow_html=True)
brief = st.text_area(
    "Brief konten",
    placeholder="Contoh: Buat iklan affiliate sepatu olahraga untuk TikTok. Pria muda memakai sepatu di taman, premium tetapi natural, hook kuat dan CTA cek keranjang kuning.",
    height=130,
    key="brief",
    label_visibility="collapsed",
)

col1, col2 = st.columns(2)
with col1:
    style = st.selectbox("Gaya visual", ["Photorealistic / Cinematic", "Natural UGC / TikTok", "Commercial Product Ad", "Luxury Product Ad", "Anime / Manga", "3D Animation"], key="style")
    aspect_ratio = st.selectbox("Aspect ratio", ["9:16 — TikTok / Reels / Shorts", "16:9 — YouTube", "1:1 — Square"], key="aspect_ratio")
with col2:
    camera = st.selectbox("Kamera", ["Natural handheld", "Cinematic wide shot", "Medium shot", "Close-up product", "POV", "Top-down / Bird-eye"], key="camera")
    lighting = st.selectbox("Lighting", ["Natural daylight", "Golden hour", "Soft studio light", "Moody cinematic", "Neon"], key="lighting")

st.markdown('<div class="cf-bubble"><div class="cf-label">🖼️ Buat Gambar</div><div class="cf-muted">AI akan menggabungkan brief dengan hingga 7 foto produk. Hasil gambar muncul langsung di aplikasi sebelum bisa diunduh.</div></div>', unsafe_allow_html=True)

if st.button("🖼️  BUAT GAMBAR DENGAN AI", type="primary", use_container_width=True, key="generate_image"):
    if not api_key.strip():
        st.error("Masukkan Google Gemini API Key terlebih dahulu.")
    elif not st.session_state.product_photos:
        st.warning("Upload minimal satu foto produk terlebih dahulu.")
    elif not brief.strip():
        st.warning("Brief belum diisi.")
    else:
        reference_count = len(st.session_state.product_photos)
        image_prompt = f"""
Create one polished commercial image using the supplied product reference photos as the source of truth.
There are {reference_count} reference photos of the SAME product. Cross-check all reference photos and
preserve the exact product identity: shape, proportions, colors, materials, texture, logo, label,
packaging and distinctive details. Never merge different products or invent missing product details.

BRIEF:
{brief}

STYLE: {style}
ASPECT RATIO: {aspect_ratio}
CAMERA: {camera}
LIGHTING: {lighting}

Create a believable advertising scene suitable for social media. Keep the product clearly visible,
with realistic shadows, anatomy and reflections. No watermark, random text, extra logos, duplicate product,
or distorted product details. The reference photos are product references, not instructions to reproduce their backgrounds.
"""
        try:
            with st.spinner("🤖 Gemini sedang membuat gambar dari foto produk..."):
                generated = generate_gemini_image(api_key, image_prompt, st.session_state.product_photos, aspect_ratio)
            st.session_state.generated_image_bytes = generated
            st.session_state.generated_image_type = "image/png"
            st.session_state.video_prompt_result = ""
            st.success("Gambar berhasil dibuat.")
        except Exception as exc:
            st.error(f"Gagal membuat gambar: {exc}")

if st.session_state.generated_image_bytes:
    st.markdown('<div class="cf-bubble"><div class="cf-label">✨ Hasil Gambar AI</div><div class="cf-muted">Periksa hasilnya dulu. Download hanya setelah hasil sesuai.</div></div>', unsafe_allow_html=True)
    st.image(st.session_state.generated_image_bytes, caption="Hasil gambar AI", use_container_width=True)
    a, b = st.columns(2)
    with a:
        st.download_button("📥 Simpan", data=st.session_state.generated_image_bytes, file_name="creator_flow_ai_image.png", mime="image/png", use_container_width=True, on_click="ignore")
    with b:
        if st.button("✅ Pilih untuk Video", use_container_width=True, key="select_generated"):
            use_generated_image_as_reference(st.session_state.generated_image_bytes, st.session_state.generated_image_type, "creator_flow_ai_image.png")
            st.success("Gambar dipilih untuk tahap video.")

st.markdown('<div class="cf-bubble"><div class="cf-label">📤 Pilih Gambar Final</div><div class="cf-muted">Jika gambar sudah dibuat di Google Flow, upload gambar final di sini untuk dijadikan referensi video.</div></div>', unsafe_allow_html=True)
flow_image = st.file_uploader("Upload gambar final dari Google Flow", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=False, key="flow_image_uploader", label_visibility="collapsed")
if flow_image is not None:
    st.session_state.selected_image_bytes = flow_image.getvalue()
    st.session_state.selected_image_name = flow_image.name
    st.session_state.selected_image_type = flow_image.type or "image/png"
    st.success("Gambar final sudah dipilih sebagai referensi video.")

st.markdown('<div class="cf-bubble"><div class="cf-label">🎬 Video</div><div class="cf-muted">Setelah gambar dipilih, AI menyusun prompt 3 scene untuk Google Flow. Durasi tetap ringkas: 8 atau 10 detik per scene.</div></div>', unsafe_allow_html=True)
if st.session_state.selected_image_bytes:
    st.image(st.session_state.selected_image_bytes, caption=st.session_state.selected_image_name or "Gambar terpilih", use_container_width=True)
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
"""
            try:
                with st.spinner("🤖 AI sedang menyusun 3 scene video..."):
                    st.session_state.video_prompt_result = generate_gemini_text(api_key, video_prompt, st.session_state.selected_image_bytes, st.session_state.selected_image_type)
                st.success("Prompt video siap digunakan di Google Flow.")
            except Exception as exc:
                st.error(f"Gagal menyusun video: {exc}")

    if st.session_state.video_prompt_result:
        st.markdown('<div class="cf-bubble"><div class="cf-label">🎬 Hasil Rencana Video</div><div class="cf-muted">Prompt siap disalin ke Google Flow.</div></div>', unsafe_allow_html=True)
        st.markdown(st.session_state.video_prompt_result)
        st.download_button("📥 Simpan Prompt Video", data=st.session_state.video_prompt_result, file_name="creator_flow_video_prompt.txt", mime="text/plain", use_container_width=True, on_click="ignore")
else:
    st.info("Pilih hasil gambar AI atau upload gambar final dari Google Flow untuk membuka tahap video.")

st.markdown('<div class="cf-composer"><div>Creator Flow AI • Foto Produk → Brief → Gambar → Pilih → Video</div></div>', unsafe_allow_html=True)
