import base64

import streamlit as st
from google import genai

GEMINI_TEXT_MODEL = "gemini-3.6-flash"
GEMINI_IMAGE_MODEL = "gemini-3.1-flash-image"
MAX_PRODUCT_PHOTOS = 7


def init_state():
    defaults = {
        "product_photos": [],
        "brief": "",
        "image_prompt_result": "",
        "generated_image_bytes": None,
        "selected_image_bytes": None,
        "selected_image_name": "",
        "selected_image_type": "image/png",
        "video_prompt_result": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_downstream():
    st.session_state.image_prompt_result = ""
    st.session_state.generated_image_bytes = None
    st.session_state.selected_image_bytes = None
    st.session_state.selected_image_name = ""
    st.session_state.selected_image_type = "image/png"
    st.session_state.video_prompt_result = ""


def save_product_photos(files):
    photos = []
    for uploaded in (files or [])[:MAX_PRODUCT_PHOTOS]:
        data = uploaded.getvalue()
        if data:
            photos.append(
                {
                    "bytes": data,
                    "name": uploaded.name,
                    "type": uploaded.type or "image/png",
                }
            )
    if photos != st.session_state.product_photos:
        st.session_state.product_photos = photos
        reset_downstream()


def make_client(api_key):
    key = (api_key or "").strip()
    if not key:
        raise ValueError("Google Gemini API Key belum diisi.")
    return genai.Client(api_key=key)


def get_ratio(label):
    return {
        "9:16 — TikTok / Reels / Shorts": "9:16",
        "16:9 — YouTube": "16:9",
        "1:1 — Square": "1:1",
    }.get(label, "9:16")


def gemini_text(api_key, prompt, photos=None):
    client = make_client(api_key)
    if photos:
        input_data = [{"type": "text", "text": prompt}]
        for photo in photos[:MAX_PRODUCT_PHOTOS]:
            input_data.append(
                {
                    "type": "image",
                    "data": base64.b64encode(photo["bytes"]).decode("utf-8"),
                    "mime_type": photo["type"] or "image/png",
                }
            )
    else:
        input_data = prompt

    interaction = client.interactions.create(
        model=GEMINI_TEXT_MODEL,
        input=input_data,
    )
    text = (interaction.output_text or "").strip()
    if not text:
        raise RuntimeError("Gemini tidak mengembalikan teks.")
    return text


def gemini_image(api_key, prompt, photos, aspect_ratio):
    if not photos:
        raise ValueError("Minimal satu foto produk diperlukan.")

    client = make_client(api_key)
    input_data = [{"type": "text", "text": prompt}]
    for photo in photos[:MAX_PRODUCT_PHOTOS]:
        input_data.append(
            {
                "type": "image",
                "data": base64.b64encode(photo["bytes"]).decode("utf-8"),
                "mime_type": photo["type"] or "image/png",
            }
        )

    interaction = client.interactions.create(
        model=GEMINI_IMAGE_MODEL,
        input=input_data,
        response_format={
            "type": "image",
            "aspect_ratio": get_ratio(aspect_ratio),
            "image_size": "1K",
        },
    )
    output_image = getattr(interaction, "output_image", None)
    data = getattr(output_image, "data", None) if output_image else None
    if not data:
        raise RuntimeError("Gemini tidak mengembalikan gambar.")
    return base64.b64decode(data) if isinstance(data, str) else data


def friendly_error(exc, stage):
    message = str(exc)
    lower = message.lower()
    if "429" in lower or "quota" in lower or "resource_exhausted" in lower:
        if stage == "image":
            return (
                "Quota Gemini untuk model gambar sedang tidak tersedia (error 429 / limit 0). "
                "Ini bukan kerusakan alur aplikasi. Gunakan mode Google Flow untuk membuat prompt gambar, "
                "lalu upload hasil Google Flow ke tahap berikutnya. Jika ingin gambar dibuat langsung di aplikasi, "
                "API project harus memiliki akses/quota untuk model image."
            )
        return "Quota Gemini sedang terbatas. Tunggu beberapa saat atau gunakan project/API key dengan quota yang tersedia."
    if "api key" in lower or "permission" in lower or "unauthenticated" in lower:
        return "API key tidak valid atau tidak memiliki izin untuk model yang dipilih. Periksa project Gemini API."
    return f"Gagal pada tahap {stage}: {message}"


st.set_page_config(
    page_title="Creator Flow AI",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed",
)
init_state()

st.markdown(
    """
<style>
:root{--bg:#0b0b0f;--surface:#17171c;--surface2:#121217;--border:#2b2b32;--text:#f5f5f7;--muted:#a7a7b0;--accent:#8b6cff}
html,body,[class*="css"]{font-family:Inter,system-ui,sans-serif}.stApp{background:var(--bg);color:var(--text)}
.block-container{max-width:760px;padding:0 14px 110px}.stApp>header{background:transparent}[data-testid="stToolbar"]{display:none}
.cf-top{position:sticky;top:0;z-index:20;margin:0 -14px;padding:12px 14px 10px;background:rgba(11,11,15,.94);backdrop-filter:blur(18px);border-bottom:1px solid #1c1c21}
.cf-title{font-size:17px;font-weight:700}.cf-sub{font-size:11px;color:var(--muted);margin-top:2px}.cf-hero{text-align:center;padding:24px 8px 16px}.cf-logo{width:46px;height:46px;margin:auto auto 10px;border-radius:15px;display:grid;place-items:center;background:#fff;color:#111;font-size:23px}.cf-hero h1{font-size:26px;margin:0 0 6px;letter-spacing:-.7px}.cf-hero p{font-size:13px;color:var(--muted);margin:0}
.cf-steps{display:flex;gap:7px;overflow-x:auto;padding:3px 0 12px;scrollbar-width:none}.cf-step{white-space:nowrap;padding:7px 10px;border:1px solid var(--border);border-radius:999px;background:#131318;color:#9e9ea7;font-size:11px}.cf-step.on{color:#fff;border-color:#6048a7;background:#211a34}
.cf-card{background:var(--surface);border:1px solid #24242a;border-radius:18px;padding:15px;margin:10px 0 14px}.cf-label{font-size:12px;font-weight:700;color:#d0d0d6;margin-bottom:7px}.cf-help{font-size:12px;line-height:1.5;color:var(--muted)}.cf-count{float:right;color:#aa96ff}
[data-testid="stFileUploaderDropzone"]{min-height:100px;border:1px dashed #41414a;border-radius:17px;background:var(--surface2)}
[data-testid="stTextArea"] textarea,[data-testid="stTextInput"] input,[data-testid="stSelectbox"] div[data-baseweb="select"]>div{background:var(--surface)!important;color:var(--text)!important;border:1px solid var(--border)!important;border-radius:15px!important}label{color:#c9c9d0!important;font-size:12px!important;font-weight:600!important}.stButton>button,.stDownloadButton>button{min-height:48px;border-radius:15px!important;background:#202027!important;color:#fff!important;border:1px solid #34343c!important;font-weight:700!important}.stButton>button[kind="primary"]{background:#fff!important;color:#111!important;border-color:#fff!important}
[data-testid="stImage"]{border-radius:16px;overflow:hidden;border:1px solid #292930}.stAlert,.stSuccess,.stWarning{border-radius:15px}.cf-photo{background:var(--surface2);border:1px solid #292930;border-radius:15px;padding:7px}.cf-name{font-size:10px;color:#aaaab3;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;padding:5px 2px 1px}.cf-code{background:#101015;border:1px solid #2d2d35;border-radius:14px;padding:12px;font-size:12px;line-height:1.55;white-space:pre-wrap}.cf-footer{position:fixed;left:50%;bottom:0;transform:translateX(-50%);width:min(760px,100%);padding:9px 14px 12px;background:linear-gradient(transparent,#0b0b0f 22%);z-index:15;pointer-events:none}.cf-footer div{background:#17171c;border:1px solid #34343c;border-radius:20px;padding:8px 12px;color:#8f8f98;font-size:11px;text-align:center}
@media(max-width:600px){.block-container{padding:0 12px 105px}.cf-top{margin:0 -12px}.cf-card{padding:13px}}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="cf-top"><div class="cf-title">Creator Flow AI</div><div class="cf-sub">Foto → Brief → Gambar → Pilih → Video</div></div>
<div class="cf-hero"><div class="cf-logo">🎬</div><h1>Creator Flow AI</h1><p>Alur sederhana untuk membuat aset iklan dan prompt Google Flow.</p></div>
<div class="cf-steps"><span class="cf-step on">① Foto</span><span class="cf-step">② Brief</span><span class="cf-step">③ Gambar</span><span class="cf-step">④ Pilih</span><span class="cf-step">⑤ Video</span></div>
""",
    unsafe_allow_html=True,
)

with st.expander("⚙️ Pengaturan AI", expanded=False):
    api_key = st.text_input("Google Gemini API Key", type="password")
    image_mode = st.radio(
        "Cara membuat gambar",
        ["Google Flow — prompt dulu (disarankan)", "Gemini Image API — gambar langsung di aplikasi"],
        index=0,
    )
    st.caption("Mode Google Flow tetap memakai Gemini untuk menyusun prompt; gambar final dibuat di Google Flow.")

st.markdown('<div class="cf-card"><div class="cf-label">📸 Foto Produk <span class="cf-count">maks. 7</span></div><div class="cf-help">Tambahkan sampai 7 sudut foto produk. AI memakai foto-foto ini sebagai referensi identitas produk.</div></div>', unsafe_allow_html=True)
files = st.file_uploader(
    "Tambahkan foto produk",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
    key="product_uploader",
    help="Maksimal 7 foto.",
)
if files:
    if len(files) > MAX_PRODUCT_PHOTOS:
        st.warning(f"Maksimal {MAX_PRODUCT_PHOTOS} foto. Foto setelah nomor {MAX_PRODUCT_PHOTOS} tidak digunakan.")
    save_product_photos(files)

if st.session_state.product_photos:
    st.caption(f"{len(st.session_state.product_photos)} / {MAX_PRODUCT_PHOTOS} foto produk")
    cols = st.columns(2)
    for i, photo in enumerate(st.session_state.product_photos):
        with cols[i % 2]:
            st.markdown('<div class="cf-photo">', unsafe_allow_html=True)
            st.image(photo["bytes"], use_container_width=True)
            st.markdown(f'<div class="cf-name">{i + 1}. {photo["name"]}</div></div>', unsafe_allow_html=True)
else:
    st.info("📷 Tambahkan minimal 1 foto produk untuk memulai.")

st.markdown('<div class="cf-card"><div class="cf-label">📝 Brief</div><div class="cf-help">Jelaskan adegan, target, gaya iklan, dan tujuan konten.</div></div>', unsafe_allow_html=True)
brief = st.text_area(
    "Brief konten",
    placeholder="Contoh: Iklan affiliate sepatu olahraga untuk TikTok. Pria muda memakai sepatu di taman, premium tetapi natural, hook kuat dan CTA cek keranjang kuning.",
    height=125,
    key="brief_input",
    label_visibility="collapsed",
)

c1, c2 = st.columns(2)
with c1:
    style = st.selectbox("Gaya visual", ["Photorealistic / Cinematic", "Natural UGC / TikTok", "Commercial Product Ad", "Luxury Product Ad", "Anime / Manga", "3D Animation"])
    aspect_ratio = st.selectbox("Aspect ratio", ["9:16 — TikTok / Reels / Shorts", "16:9 — YouTube", "1:1 — Square"])
with c2:
    camera = st.selectbox("Kamera", ["Natural handheld", "Cinematic wide shot", "Medium shot", "Close-up product", "POV", "Top-down / Bird-eye"])
    lighting = st.selectbox("Lighting", ["Natural daylight", "Golden hour", "Soft studio light", "Moody cinematic", "Neon"])

image_prompt = f"""
Create a production-ready image prompt for Google Flow / Gemini image generation.
Use the supplied product reference photos as the source of truth. They are different views of the SAME product.
Preserve exact product identity: shape, proportions, color, material, texture, logo, label, packaging and unique details.
Do not invent or merge products.

BRIEF:
{brief}
STYLE: {style}
ASPECT RATIO: {get_ratio(aspect_ratio)}
CAMERA: {camera}
LIGHTING: {lighting}

Write one complete English image-generation prompt for a polished social-media commercial.
Include subject, environment, composition, camera, lighting, product placement, realism, continuity and negative constraints.
No watermark, random text, extra logo, duplicate product, distorted anatomy or deformed product.
Return only the final prompt, with no introduction.
"""

st.markdown('<div class="cf-card"><div class="cf-label">🖼️ Tahap Gambar</div><div class="cf-help">Pilih Google Flow untuk alur aman tanpa error quota gambar. Jika project memiliki quota image, pilih mode Gemini untuk menampilkan gambar langsung di aplikasi.</div></div>', unsafe_allow_html=True)

button_text = "🖼️  BUAT PROMPT GAMBAR UNTUK GOOGLE FLOW" if image_mode.startswith("Google Flow") else "🖼️  BUAT GAMBAR DENGAN GEMINI"
if st.button(button_text, type="primary", use_container_width=True):
    if not api_key.strip():
        st.error("Masukkan Google Gemini API Key terlebih dahulu.")
    elif not st.session_state.product_photos:
        st.warning("Upload minimal satu foto produk terlebih dahulu.")
    elif not brief.strip():
        st.warning("Brief belum diisi.")
    else:
        try:
            if image_mode.startswith("Google Flow"):
                with st.spinner("🤖 Gemini sedang menyusun prompt gambar..."):
                    st.session_state.image_prompt_result = gemini_text(api_key, image_prompt, st.session_state.product_photos)
                st.success("Prompt gambar siap. Salin ke Google Flow, buat gambarnya, lalu upload hasil final di bawah.")
            else:
                with st.spinner("🤖 Gemini sedang membuat gambar..."):
                    st.session_state.generated_image_bytes = gemini_image(
                        api_key,
                        image_prompt,
                        st.session_state.product_photos,
                        aspect_ratio,
                    )
                st.session_state.image_prompt_result = ""
                st.success("Gambar berhasil dibuat dan tampil langsung di aplikasi.")
        except Exception as exc:
            st.error(friendly_error(exc, "gambar"))

if st.session_state.image_prompt_result:
    st.markdown('<div class="cf-card"><div class="cf-label">✨ Prompt Gambar Final</div><div class="cf-help">Gunakan prompt ini di Google Flow. Setelah gambar selesai, upload hasilnya pada tahap berikutnya.</div></div>', unsafe_allow_html=True)
    st.code(st.session_state.image_prompt_result, language="text")
    st.download_button(
        "📥 Simpan Prompt Gambar",
        data=st.session_state.image_prompt_result,
        file_name="creator_flow_image_prompt.txt",
        mime="text/plain",
        use_container_width=True,
    )

if st.session_state.generated_image_bytes:
    st.markdown('<div class="cf-card"><div class="cf-label">✨ Hasil Gambar AI</div><div class="cf-help">Periksa dulu. Jika sesuai, pilih untuk tahap video.</div></div>', unsafe_allow_html=True)
    st.image(st.session_state.generated_image_bytes, caption="Hasil gambar AI", use_container_width=True)
    a, b = st.columns(2)
    with a:
        st.download_button("📥 Simpan Gambar", data=st.session_state.generated_image_bytes, file_name="creator_flow_image.png", mime="image/png", use_container_width=True)
    with b:
        if st.button("✅ Pilih untuk Video", use_container_width=True):
            st.session_state.selected_image_bytes = st.session_state.generated_image_bytes
            st.session_state.selected_image_name = "creator_flow_image.png"
            st.session_state.selected_image_type = "image/png"
            st.session_state.video_prompt_result = ""
            st.success("Gambar dipilih untuk tahap video.")

st.markdown('<div class="cf-card"><div class="cf-label">📤 Pilih Gambar Final</div><div class="cf-help">Upload gambar final yang sudah dibuat di Google Flow. Setelah dipilih, tahap video otomatis terbuka.</div></div>', unsafe_allow_html=True)
final_file = st.file_uploader(
    "Upload gambar final",
    type=["png", "jpg", "jpeg", "webp"],
    key="final_image_uploader",
    label_visibility="collapsed",
)
if final_file is not None:
    data = final_file.getvalue()
    if data:
        changed = data != st.session_state.selected_image_bytes or final_file.name != st.session_state.selected_image_name
        if changed:
            st.session_state.selected_image_bytes = data
            st.session_state.selected_image_name = final_file.name
            st.session_state.selected_image_type = final_file.type or "image/png"
            st.session_state.video_prompt_result = ""
            st.success("Gambar final dipilih. Tahap video siap digunakan.")

if st.session_state.selected_image_bytes:
    st.markdown('<div class="cf-card"><div class="cf-label">🎬 Tahap Video</div><div class="cf-help">AI akan menyusun tepat 3 scene yang saling tersambung untuk Google Flow. Durasi setiap scene hanya 8 atau 10 detik.</div></div>', unsafe_allow_html=True)
    st.image(st.session_state.selected_image_bytes, caption=st.session_state.selected_image_name or "Gambar terpilih", use_container_width=True)
    d1, d2 = st.columns(2)
    with d1:
        duration = st.selectbox("Durasi per scene", ["8 detik", "10 detik"], key="video_duration")
    with d2:
        voice = st.selectbox("Voice Over", ["Pria dewasa Indonesia, natural", "Wanita dewasa Indonesia, natural", "Tanpa voice over"], key="video_voice")

    video_prompt = f"""
You are a senior commercial video director and Google Flow / Veo prompt engineer.
Use the selected reference image as the visual source of truth for the product.
Preserve product shape, proportions, colors, logo, label, materials, texture and distinctive details.

BRIEF:
{brief}
STYLE: {style}
ASPECT RATIO: {get_ratio(aspect_ratio)}
CAMERA: {camera}
LIGHTING: {lighting}
DURATION PER SCENE: {duration}
VOICE OVER: {voice}

Create EXACTLY 3 connected scenes for a social-media product video.
For each scene provide:
### Scene N — title
**Tujuan:** concise purpose
**Aksi Visual:** what happens
**Prompt Video:** complete English Google Flow / Veo-ready prompt including subject, action, camera movement, composition, lighting, continuity and realistic motion
**Voice Over:** Indonesian line if requested
**SFX / Audio:** concise sound direction

Continuity rules:
- The selected reference image is the source of truth.
- Never change or duplicate the product.
- Keep motion physically plausible.
- No watermark, random text, fake logo, or product deformation.
Return only the 3-scene production plan.
"""

    if st.button("🎬  SUSUN VIDEO UNTUK GOOGLE FLOW", type="primary", use_container_width=True):
        if not api_key.strip():
            st.error("Masukkan Google Gemini API Key terlebih dahulu.")
        elif not brief.strip():
            st.warning("Brief belum diisi.")
        else:
            try:
                with st.spinner("🤖 Gemini sedang menyusun 3 scene video..."):
                    st.session_state.video_prompt_result = gemini_text(
                        api_key,
                        video_prompt,
                        [
                            {
                                "bytes": st.session_state.selected_image_bytes,
                                "name": st.session_state.selected_image_name,
                                "type": st.session_state.selected_image_type,
                            }
                        ],
                    )
                st.success("3 scene video siap digunakan di Google Flow.")
            except Exception as exc:
                st.error(friendly_error(exc, "video"))

    if st.session_state.video_prompt_result:
        st.markdown('<div class="cf-card"><div class="cf-label">🎬 Hasil Prompt Video</div><div class="cf-help">Salin prompt ini ke Google Flow untuk membuat video final.</div></div>', unsafe_allow_html=True)
        st.code(st.session_state.video_prompt_result, language="markdown")
        st.download_button(
            "📥 Simpan Prompt Video",
            data=st.session_state.video_prompt_result,
            file_name="creator_flow_video_prompt.txt",
            mime="text/plain",
            use_container_width=True,
        )
else:
    st.info("Pilih hasil gambar AI atau upload gambar final dari Google Flow untuk membuka tahap video.")

st.markdown('<div class="cf-footer"><div>Creator Flow AI • Foto Produk → Brief → Gambar → Pilih → Video</div></div>', unsafe_allow_html=True)
