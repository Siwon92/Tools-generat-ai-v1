import streamlit as st
from google import genai

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
        raise RuntimeError(
            "Gemini tidak mengembalikan teks. Coba lagi dengan input yang lebih jelas."
        )

    return generated_text


st.set_page_config(
    page_title="Creator Flow AI",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Creator Flow AI")
st.caption("Generator prompt gambar, video, storyboard & TikTok Affiliate")

if "image_prompts" not in st.session_state:
    st.session_state.image_prompts = ""
if "selected_image_prompt" not in st.session_state:
    st.session_state.selected_image_prompt = ""

# SIDEBAR
with st.sidebar:
    st.header("⚙️ Pengaturan")

    api_key = st.text_input(
        "Google Gemini API Key",
        type="password"
    )

    st.info("API Key digunakan untuk menjalankan generator.")

# INPUT PRODUK
st.subheader("1. Produk / Subjek")

subject = st.text_area(
    "Deskripsikan produk atau subjek",
    placeholder=(
        "Contoh: sepatu olahraga pria warna hitam, "
        "desain casual, nyaman digunakan untuk olahraga."
    ),
    height=100
)

# VISUAL
st.subheader("2. Gaya Visual")

col1, col2 = st.columns(2)

with col1:
    style = st.selectbox(
        "Style",
        [
            "Photorealistic / Cinematic",
            "Natural UGC / TikTok",
            "Commercial Product Ad",
            "Anime / Manga",
            "3D Animation",
            "Cyberpunk",
            "Vintage Film"
        ]
    )

    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        [
            "9:16 — TikTok / Reels / Shorts",
            "16:9 — YouTube",
            "1:1 — Square"
        ]
    )

with col2:
    camera = st.selectbox(
        "Camera",
        [
            "Natural handheld",
            "Cinematic wide shot",
            "Medium shot",
            "Close-up product",
            "POV",
            "Top-down / Bird-eye"
        ]
    )

    lighting = st.selectbox(
        "Lighting",
        [
            "Natural daylight",
            "Golden hour",
            "Soft studio light",
            "Moody cinematic",
            "Neon"
        ]
    )

# PIPELINE PRODUKSI
st.subheader("3. Pipeline Produksi")
production_mode = st.radio(
    "Pilih tahap yang ingin dikerjakan",
    [
        "🖼️ 1. Generate Prompt Gambar",
        "📝 2. Generate Konten / Prompt Video"
    ],
    horizontal=False
)

if production_mode.startswith("🖼️"):
    st.info(
        "Tahap 1 membuat prompt gambar siap ditempel ke Google Flow. "
        "Buat beberapa variasi, pilih satu gambar terbaik, lalu lanjutkan ke tahap video."
    )
else:
    st.success(
        "Gunakan tahap ini setelah gambar utama sudah dipilih. "
        "Prompt video akan mempertahankan identitas produk dan kontinuitas visual."
    )

# JENIS KONTEN
st.subheader("4. Jenis Konten")

content_type = st.selectbox(
    "Pilih yang ingin dibuat",
    [
        "TikTok Affiliate — 3 Scene",
        "Storyboard — 3 sampai 5 Scene",
        "Prompt Gambar",
        "Prompt Video",
        "Ide Konten + Hook"
    ]
)

story = st.text_area(
    "5. Ide / Informasi Produk / Alur",
    placeholder=(
        "Contoh: buat video affiliate sepatu. "
        "Tampilkan orang memakai sepatu, detail produk, "
        "kemudian ajak penonton cek keranjang kuning."
    ),
    height=120
)

if production_mode.startswith("🖼️"):
    st.subheader("6. Subjek Gambar")
    image_scene = st.text_area(
        "Adegan yang ingin dibuat",
        placeholder=(
            "Contoh: creator pria Indonesia sedang memakai sepatu di ruang tamu "
            "modern, memperlihatkan detail sepatu secara natural."
        ),
        height=100
    )
else:
    image_scene = ""

# PENGATURAN AFFILIATE
if content_type in [
    "TikTok Affiliate — 3 Scene",
    "Ide Konten + Hook"
]:
    st.subheader("7. Pengaturan Affiliate")

    col1, col2 = st.columns(2)

    with col1:
        duration = st.selectbox(
            "Durasi Scene",
            [
                "6 detik",
                "8 detik",
                "10 detik"
            ]
        )

    with col2:
        voice = st.selectbox(
            "Voice Over",
            [
                "Pria dewasa Indonesia, natural",
                "Wanita dewasa Indonesia, natural",
                "Tanpa voice over"
            ]
        )
else:
    duration = "8 detik"
    voice = "Natural"

# TAHAP 1: PROMPT GAMBAR
if production_mode.startswith("🖼️"):
    if st.button(
        "🖼️ GENERATE PROMPT GAMBAR",
        type="primary",
        use_container_width=True
    ):
        if not api_key:
            st.error("Masukkan Google Gemini API Key terlebih dahulu.")
        elif not subject.strip():
            st.warning("Deskripsi produk belum diisi.")
        elif not image_scene.strip():
            st.warning("Adegan gambar belum diisi.")
        else:
            image_prompt_request = f"""
Kamu adalah Visual Director dan Prompt Engineer profesional untuk Google Flow.
Buat prompt gambar yang siap dipakai untuk menghasilkan keyframe produk berkualitas tinggi.

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
1. Pertahankan identitas produk secara ketat.
2. Jangan mengubah bentuk, warna, logo, label, tekstur, material, atau detail produk.
3. Jika ada manusia, gunakan penampilan natural dan anatomi realistis.
4. Buat komposisi yang cocok untuk {aspect_ratio}.
5. Prioritaskan produk tetap terlihat jelas.
6. Hindari teks acak, watermark, logo tambahan, tangan/jari cacat, objek terdistorsi, dan artefak AI.
7. Gunakan Bahasa Inggris untuk prompt.
8. Buat TEPAT 3 variasi yang berbeda pada framing atau komposisi, tetapi produk dan identitas visual tetap sama.
9. Setiap prompt harus siap copy-paste ke Google Flow.
10. Jangan memberikan penjelasan panjang.

FORMAT:
### IMAGE PROMPT 1
[Prompt lengkap dalam Bahasa Inggris]

### IMAGE PROMPT 2
[Prompt lengkap dalam Bahasa Inggris]

### IMAGE PROMPT 3
[Prompt lengkap dalam Bahasa Inggris]
"""

            try:
                with st.spinner("🖼️ Gemini sedang menyusun prompt gambar..."):
                    st.session_state.image_prompts = generate_gemini_text(
                        api_key,
                        image_prompt_request
                    )
                st.session_state.selected_image_prompt = ""
                st.success("✅ 3 prompt gambar berhasil dibuat!")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

    if st.session_state.image_prompts:
        st.divider()
        st.subheader("🖼️ Hasil Prompt Gambar")
        st.markdown(st.session_state.image_prompts)

        st.session_state.selected_image_prompt = st.text_area(
            "Prompt gambar yang dipilih / hasil revisi",
            value=st.session_state.selected_image_prompt,
            placeholder="Tempel atau pilih prompt terbaik untuk dipakai di Google Flow...",
            height=180
        )

        if st.session_state.selected_image_prompt.strip():
            st.download_button(
                "📥 Download Prompt Gambar",
                data=st.session_state.selected_image_prompt,
                file_name="creator_flow_image_prompt.txt",
                mime="text/plain",
                use_container_width=True
            )

# TAHAP 2: KONTEN / VIDEO
else:
    if st.session_state.selected_image_prompt:
        st.text_area(
            "🖼️ Prompt Gambar Terpilih",
            value=st.session_state.selected_image_prompt,
            height=140,
            disabled=True
        )

    if st.button(
        "🚀 GENERATE KONTEN / PROMPT VIDEO",
        type="primary",
        use_container_width=True
    ):
        if not api_key:
            st.error("Masukkan Google Gemini API Key terlebih dahulu.")
        elif not subject.strip():
            st.warning("Deskripsi produk belum diisi.")
        elif not story.strip():
            st.warning("Ide atau alur cerita belum diisi.")
        else:
            prompt = f"""
Kamu adalah Creative Director, Prompt Engineer dan TikTok Affiliate Content Strategist profesional.

Tugas kamu adalah membuat konten AI yang natural, realistis dan siap digunakan.

INFORMASI:
Produk/Subjek:
{subject}

Style:
{style}

Aspect Ratio:
{aspect_ratio}

Camera:
{camera}

Lighting:
{lighting}

Jenis Konten:
{content_type}

Ide:
{story}

Durasi:
{duration}

Voice Over:
{voice}

Prompt Gambar Terpilih:
{st.session_state.selected_image_prompt}

ATURAN PENTING:
1. Pertahankan identitas produk.
2. Jangan mengubah bentuk, warna, logo, label atau detail produk.
3. Jangan membuat klaim yang tidak diberikan oleh pengguna.
4. Prompt gambar dan video ditulis dalam Bahasa Inggris.
5. Penjelasan dan voice over menggunakan Bahasa Indonesia.
6. Hasil harus natural dan realistis.
7. Jangan membuat konten terasa seperti iklan yang terlalu agresif.
8. Jika menggunakan prompt gambar terpilih, pertahankan karakter, produk, lokasi, pakaian, lighting, dan visual identity.

KHUSUS TIKTOK AFFILIATE:
Gunakan struktur HOOK → PROBLEM → PROOF → BENEFIT → CTA.
Hook harus kuat dalam 1–3 detik pertama.

JIKA TIKTOK AFFILIATE — 3 SCENE:
Buat TEPAT 3 scene.
SCENE 1: HOOK
SCENE 2: PROBLEM + PROOF
SCENE 3: BENEFIT + CTA

Untuk setiap scene berikan:
### Scene X
**Tujuan:** ...
**Aksi Visual:** ...
**Prompt Image:** Prompt Bahasa Inggris.
**Prompt Video:** Prompt Bahasa Inggris.
**Voice Over:** Bahasa Indonesia.
**SFX / Audio:** ...

Pastikan karakter, produk, lokasi, pakaian, pencahayaan, dan alur tetap konsisten.

JIKA PROMPT VIDEO:
Buat 3 prompt video Bahasa Inggris dengan camera movement, subject movement, natural physics, realistic motion, continuity, dan ending frame.

JIKA STORYBOARD:
Buat 3–5 scene yang saling menyambung.

JIKA IDE KONTEN + HOOK:
Buat 5 ide. Setiap ide memiliki Hook, Problem, Proof, Benefit, CTA, dan Visual direction.

Untuk konten affiliate, CTA dapat menggunakan: "Cek keranjang kuning."
Jangan memberikan pembukaan panjang. Langsung berikan hasil.
"""

            try:
                with st.spinner("🤖 Creator Flow AI sedang bekerja..."):
                    generated_text = generate_gemini_text(api_key, prompt)

                st.success("✅ Berhasil dibuat!")
                st.markdown(generated_text)
                st.download_button(
                    "📥 Download Hasil TXT",
                    data=generated_text,
                    file_name="creator_flow_ai.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

st.divider()
st.caption("Creator Flow AI • V1 — Image-first workflow")
