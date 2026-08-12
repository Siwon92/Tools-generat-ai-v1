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


def generate_gemini_text(api_key: str, prompt: str) -> str:
    """Generate text with the Google Gen AI SDK and a user-provided API key."""
    client = genai.Client(api_key=api_key.strip())
    interaction = client.interactions.create(
        model=GEMINI_MODEL,
        input=prompt,
    )
    generated_text = (interaction.output_text or "").strip()
    if not generated_text:
        raise RuntimeError("Gemini tidak mengembalikan teks. Coba lagi dengan input yang lebih jelas.")
    return generated_text


def save_prompt_callback() -> None:
    save_image_prompt()


def select_image_callback() -> None:
    save_selected_image(st.session_state.image_uploader)


def reset_image_callback() -> None:
    clear_selected_image()


def go_video_callback() -> None:
    if not continue_to_video():
        st.session_state.video_stage = "locked"


st.set_page_config(page_title="Creator Flow AI", page_icon="🎬", layout="centered")
initialize_image_video_state()

st.title("🎬 Creator Flow AI")
st.caption("Generator prompt gambar, gambar utama, video, storyboard & TikTok Affiliate")

with st.sidebar:
    st.header("⚙️ Pengaturan")
    api_key = st.text_input("Google Gemini API Key", type="password")
    st.info("API Key digunakan untuk menjalankan generator dan tidak disimpan di source code.")

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
    ["🖼️ 1. Buat Prompt Gambar", "🖼️ 2. Pilih Gambar Utama", "🎬 3. Buat Prompt Video"],
    key="production_mode",
)

st.subheader("4. Jenis Konten")
content_type = st.selectbox(
    "Pilih yang ingin dibuat",
    ["TikTok Affiliate — 3 Scene", "Storyboard — 3 sampai 5 Scene", "Prompt Gambar", "Prompt Video", "Ide Konten + Hook"],
    key="content_type",
)

story = st.text_area(
    "5. Ide / Informasi Produk / Alur",
    placeholder="Contoh: buat video affiliate sepatu. Tampilkan orang memakai sepatu, detail produk, kemudian ajak penonton cek keranjang kuning.",
    height=120,
    key="story",
)

if production_mode == "🖼️ 1. Buat Prompt Gambar":
    st.info("Buat 3 variasi prompt, pilih/edit satu prompt, lalu simpan sebelum lanjut ke gambar di Google Flow.")
    image_scene = st.text_area(
        "Adegan yang ingin dibuat",
        placeholder="Contoh: creator pria Indonesia sedang memakai sepatu di ruang tamu modern, memperlihatkan detail sepatu secara natural.",
        height=100,
        key="image_scene",
    )

    st.subheader("Pengaturan Affiliate")
    duration = st.selectbox("Durasi Scene", ["6 detik", "8 detik", "10 detik"], key="duration_image")
    voice = st.selectbox("Voice Over", ["Pria dewasa Indonesia, natural", "Wanita dewasa Indonesia, natural", "Tanpa voice over"], key="voice_image")

    if st.button("🖼️ GENERATE 3 PROMPT GAMBAR", type="primary", use_container_width=True):
        if not api_key:
            st.error("Masukkan Google Gemini API Key terlebih dahulu.")
        elif not subject.strip():
            st.warning("Deskripsi produk belum diisi.")
        elif not image_scene.strip():
            st.warning("Adegan gambar belum diisi.")
        else:
            request = f"""
Kamu adalah Visual Director dan Prompt Engineer profesional untuk Google Flow.
Buat TEPAT 3 prompt gambar siap copy-paste.

PRODUK/SUBJEK:
{subject}
ADEGAN:
{image_scene}
STYLE:
{style}
ASPECT RATIO:
{aspect_ratio}
CAMERA:
{camera}
LIGHTING:
{lighting}
IDE KONTEN:
{story}

ATURAN:
- Pertahankan identitas produk secara ketat: bentuk, warna, logo, label, tekstur, material, dan detail.
- Jika ada manusia, gunakan penampilan natural dan anatomi realistis.
- Produk harus jelas dan menjadi fokus.
- Hindari watermark, teks acak, logo tambahan, tangan/jari cacat, distorsi dan artefak AI.
- Gunakan Bahasa Inggris.
- Tiga variasi boleh berbeda pada framing/komposisi, tetapi identitas visual harus konsisten.

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
                st.session_state.image_stage = "prompt"
                st.success("✅ 3 prompt gambar berhasil dibuat.")
            except Exception as exc:
                st.error(f"Terjadi kesalahan: {exc}")

    if st.session_state.image_prompts:
        st.divider()
        st.subheader("🖼️ Hasil Prompt Gambar")
        st.markdown(st.session_state.image_prompts)
        st.text_area(
            "Prompt gambar terpilih / hasil revisi",
            key="image_prompt_editor",
            placeholder="Salin prompt terbaik dari 3 hasil di atas, lalu edit jika diperlukan.",
            height=200,
        )
        st.button("💾 SIMPAN PROMPT TERPILIH", on_click=save_prompt_callback, use_container_width=True)
        if st.session_state.selected_image_prompt:
            st.success("Prompt tersimpan. Sekarang buka tahap 2 dan buat gambar tersebut di Google Flow.")
            st.download_button(
                "📥 Download Prompt Gambar",
                data=st.session_state.selected_image_prompt,
                file_name="creator_flow_image_prompt.txt",
                mime="text/plain",
                use_container_width=True,
            )

elif production_mode == "🖼️ 2. Pilih Gambar Utama":
    st.info("Setelah membuat gambar di Google Flow, upload hasilnya di sini. Gambar akan disimpan di Session State agar tetap tersedia saat aplikasi melakukan rerun.")

    if not st.session_state.selected_image_prompt:
        st.warning("Simpan prompt gambar terlebih dahulu pada tahap 1.")
    else:
        st.text_area("📝 Prompt Gambar Terpilih", value=st.session_state.selected_image_prompt, height=160, disabled=True)

        uploaded = st.file_uploader(
            "Upload gambar hasil Google Flow",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=False,
            key="image_uploader",
            help="Upload satu gambar utama/keyframe yang akan menjadi referensi kontinuitas video.",
        )

        if uploaded is not None:
            st.image(uploaded, caption="Preview gambar yang dipilih", use_container_width=True)
            st.button("⭐ JADIKAN GAMBAR UTAMA", on_click=select_image_callback, use_container_width=True)

        if st.session_state.selected_image_bytes:
            st.divider()
            st.subheader("⭐ Gambar Utama")
            st.image(
                st.session_state.selected_image_bytes,
                caption=st.session_state.selected_image_name,
                use_container_width=True,
            )
            st.success("Gambar utama tersimpan di sesi ini.")
            c1, c2 = st.columns(2)
            with c1:
                st.button("🔄 Ganti Gambar Utama", on_click=reset_image_callback, use_container_width=True)
            with c2:
                if st.button("➡️ LANJUT KE VIDEO", on_click=go_video_callback, type="primary", use_container_width=True):
                    pass

        if st.session_state.video_stage == "ready":
            st.success("✅ Gambar utama siap digunakan untuk tahap Prompt Video. Buka tahap 3.")

else:
    st.info("Tahap video hanya bisa digunakan setelah prompt gambar disimpan dan gambar utama hasil Google Flow dipilih.")

    if not st.session_state.selected_image_prompt:
        st.warning("Belum ada prompt gambar terpilih. Kembali ke tahap 1.")
    elif not st.session_state.selected_image_bytes:
        st.warning("Belum ada gambar utama. Kembali ke tahap 2 dan upload hasil Google Flow.")
    else:
        st.subheader("⭐ Referensi Gambar Utama")
        st.image(st.session_state.selected_image_bytes, caption=st.session_state.selected_image_name, use_container_width=True)
        st.text_area("📝 Prompt Gambar sebagai sumber kontinuitas", value=st.session_state.selected_image_prompt, height=150, disabled=True)

        duration = st.selectbox("Durasi per Scene", ["6 detik", "8 detik", "10 detik"], key="duration_video")
        voice = st.selectbox("Voice Over", ["Pria dewasa Indonesia, natural", "Wanita dewasa Indonesia, natural", "Tanpa voice over"], key="voice_video")

        if st.button("🎬 GENERATE PROMPT VIDEO", type="primary", use_container_width=True):
            prompt = f"""
Kamu adalah Creative Director dan Prompt Engineer untuk video generatif.
Buat prompt video yang menjaga kontinuitas dari gambar utama yang dipilih.

PRODUK/SUBJEK:
{subject}

PROMPT GAMBAR UTAMA:
{st.session_state.selected_image_prompt}

JENIS KONTEN:
{content_type}
IDE/ALUR:
{story}
STYLE:
{style}
ASPECT RATIO:
{aspect_ratio}
CAMERA:
{camera}
LIGHTING:
{lighting}
DURASI:
{duration}
VOICE OVER:
{voice}

ATURAN KONTINUITAS:
1. Pertahankan produk, karakter, wajah, pakaian, lokasi, warna, material, lighting, dan visual identity dari gambar utama.
2. Jangan menambahkan produk berbeda atau mengubah bentuk/warna/logo.
3. Gerakan harus natural, realistis, dan mengikuti fisika.
4. Camera movement harus jelas dan tidak berlebihan.
5. Prompt video ditulis dalam Bahasa Inggris.
6. Voice over ditulis dalam Bahasa Indonesia.
7. Jika TikTok Affiliate — 3 Scene, buat TEPAT 3 scene: HOOK → PROBLEM/PROOF → BENEFIT/CTA.
8. Setiap scene harus menyebut continuity dari keyframe dan ending frame yang cocok untuk scene berikutnya.

FORMAT:
### Scene 1
**Tujuan:** ...
**Aksi Visual:** ...
**Prompt Video:** [complete English prompt]
**Voice Over:** ...
**SFX / Audio:** ...

### Scene 2
...

### Scene 3
...
"""
            try:
                with st.spinner("🎬 Gemini sedang menyusun prompt video..."):
                    generated_video_prompt = generate_gemini_text(api_key, prompt)
                st.session_state.video_prompt_result = generated_video_prompt
                st.success("✅ Prompt video siap digunakan di Google Flow.")
            except Exception as exc:
                st.error(f"Terjadi kesalahan: {exc}")

        if st.session_state.get("video_prompt_result"):
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
st.caption("Creator Flow AI • Image → Select → Video workflow")
