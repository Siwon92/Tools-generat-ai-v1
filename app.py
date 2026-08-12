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

# SIDEBAR
with st.sidebar:
    st.header("⚙️ Pengaturan")

    api_key = st.text_input(
        "Google Gemini API Key",
        type="password"
    )

    st.info(
        "API Key digunakan untuk menjalankan generator."
    )

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

# JENIS KONTEN
st.subheader("3. Jenis Konten")

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
    "4. Ide / Informasi Produk / Alur",
    placeholder=(
        "Contoh: buat video affiliate sepatu. "
        "Tampilkan orang memakai sepatu, detail produk, "
        "kemudian ajak penonton cek keranjang kuning."
    ),
    height=120
)

# PENGATURAN AFFILIATE
if content_type in [
    "TikTok Affiliate — 3 Scene",
    "Ide Konten + Hook"
]:

    st.subheader("5. Pengaturan Affiliate")

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


# GENERATE
if st.button(
    "🚀 GENERATE SEKARANG",
    type="primary",
    use_container_width=True
):

    if not api_key:
        st.error(
            "Masukkan Google Gemini API Key terlebih dahulu."
        )

    elif not subject.strip():
        st.warning(
            "Deskripsi produk belum diisi."
        )

    elif not story.strip():
        st.warning(
            "Ide atau alur cerita belum diisi."
        )

    else:

        try:

            prompt = f"""
Kamu adalah Creative Director,
Prompt Engineer dan TikTok Affiliate
Content Strategist profesional.

Tugas kamu adalah membuat konten AI
yang natural, realistis dan siap digunakan.

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


ATURAN PENTING:

1. Pertahankan identitas produk.
2. Jangan mengubah bentuk, warna,
   logo, label atau detail produk.
3. Jangan membuat klaim yang tidak
   diberikan oleh pengguna.
4. Prompt gambar dan video ditulis
   dalam Bahasa Inggris.
5. Penjelasan dan voice over
   menggunakan Bahasa Indonesia.
6. Hasil harus natural dan realistis.
7. Jangan membuat konten terasa seperti
   iklan yang terlalu agresif.


KHUSUS TIKTOK AFFILIATE:

Gunakan struktur:

HOOK
→ PROBLEM
→ PROOF
→ BENEFIT
→ CTA

Hook harus kuat dalam 1–3 detik pertama.

Gabungkan:

Visual action
+
Kalimat hook
+
Curiosity / payoff

Gunakan gaya creator TikTok
yang natural dan tidak kaku.


JIKA TIKTOK AFFILIATE — 3 SCENE:

Buat TEPAT 3 scene.

SCENE 1:
HOOK

SCENE 2:
PROBLEM + PROOF

SCENE 3:
BENEFIT + CTA


Untuk setiap scene berikan:

### Scene X

**Tujuan:**
...

**Aksi Visual:**
...

**Prompt Image:**
Prompt Bahasa Inggris.

**Prompt Video:**
Prompt Bahasa Inggris.

**Voice Over:**
Bahasa Indonesia.

**SFX / Audio:**
...


Pastikan ketiga scene:

- karakter konsisten
- produk konsisten
- lokasi konsisten
- pakaian konsisten
- pencahayaan konsisten
- alur menyambung


JIKA PROMPT GAMBAR:

Buat 3 variasi prompt
Bahasa Inggris yang detail.


JIKA PROMPT VIDEO:

Buat 3 prompt video Bahasa Inggris
dengan:

- camera movement
- subject movement
- natural physics
- realistic motion
- continuity
- ending frame


JIKA STORYBOARD:

Buat 3–5 scene yang saling menyambung.


JIKA IDE KONTEN + HOOK:

Buat 5 ide.

Setiap ide harus memiliki:

Hook
Problem
Proof
Benefit
CTA
Visual direction


Untuk konten affiliate,
CTA dapat menggunakan:

"Cek keranjang kuning."

Jangan memberikan pembukaan panjang.
Langsung berikan hasil.
"""

            with st.spinner(
                "🤖 Creator Flow AI sedang bekerja..."
            ):

                generated_text = generate_gemini_text(api_key, prompt)

            st.success(
                "✅ Berhasil dibuat!"
            )

            st.markdown(
                generated_text
            )

            st.download_button(
                "📥 Download Hasil TXT",
                data=generated_text,
                file_name="creator_flow_ai.txt",
                mime="text/plain",
                use_container_width=True
            )

        except Exception as e:

            st.error(
                f"Terjadi kesalahan: {e}"
            )


st.divider()

st.caption(
    "Creator Flow AI • V1"
          )
