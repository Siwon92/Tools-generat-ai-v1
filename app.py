import streamlit as st
from google import genai

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Storyboard & Prompt AI Generator",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 AI Storyboard & Prompt Generator")
st.caption("Buat Prompt Gambar, Video, dan Storyboard Terstruktur Secara Otomatis")

# --- SIDEBAR: API KEY ---
with st.sidebar:
    st.header("⚙️ Pengaturan API")
    api_key = st.text_input("Masukkan Google Gemini API Key:", type="password")
    st.info("Dapatkan API Key di Google AI Studio.")

# --- FORM INPUT ---
st.subheader("1. Karakter & Subjek Utama")
character_desc = st.text_area(
    "Deskripsi Karakter/Objek Utama", 
    placeholder="Contoh: Pria Indonesia usia 30-an, memakai kemeja batik modern, berambut pendek rapi."
)

st.subheader("2. Konsep & Gaya Visual")
col1, col2 = st.columns(2)

with col1:
    style_option = st.selectbox(
        "Gaya Visual (Style)",
        ["Photorealistic / Cinematic", "Anime / Manga", "3D Animation (Pixar Style)", "Cyberpunk", "Vintage 90s Film"]
    )
    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        ["16:9 (Landscape / YouTube)", "9:16 (Portrait / TikTok & Reels)", "1:1 (Square)"]
    )

with col2:
    camera_shot = st.selectbox(
        "Sudut Kamera (Camera Shot)",
        ["Cinematic Wide Shot", "Close-up Portrait", "Medium Shot", "Drone/Bird-eye View", "POV (Point of View)"]
    )
    lighting = st.selectbox(
        "Pencahayaan (Lighting)",
        ["Golden Hour (Dramatic)", "Studio Soft Light", "Neon Cyberpunk", "Moody / Dark Cinematic", "Natural Daylight"]
    )

st.subheader("3. Cerita / Alur Skenario")
story_concept = st.text_area(
    "Jelaskan Alur Cerita / Konsep Video Singkat", 
    placeholder="Contoh: Karakter sedang berjalan di pasar tradisional di sore hari, membeli kopi, lalu tersenyum ke arah kamera."
)

output_type = st.radio(
    "Pilih Output yang Ingin Dihasilkan:",
    ["Storyboard Lengkap (Beberapa Scene)", "Prompt Gambar Tunggal (Midjourney/Leonardo)", "Prompt Video Motion (Runway/Luma/Sora)"]
)

# --- PROSES GENERATE ---
if st.button("🚀 Generate Prompt SEKARANG", type="primary"):
    if not api_key:
        st.error("Harap masukkan Gemini API Key di sidebar sebelah kiri terlebih dahulu!")
    elif not character_desc or not story_concept:
        st.warning("Harap lengkapi deskripsi karakter dan ide cerita!")
    else:
        try:
            client = genai.Client(api_key=api_key)

            with st.spinner("AI sedang merangkai prompt dan storyboard..."):
                prompt_system = (
                    "Kamu adalah seorang Expert AI Prompt Engineer dan Director Storyboard Profesional.\n"
                    "Tugasmu adalah membuat output prompt terstruktur berdasarkan input pengguna.\n\n"
                    f"INFORMASI INPUT:\n"
                    f"- Karakter Utama: {character_desc}\n"
                    f"- Style Visual: {style_option}\n"
                    f"- Aspect Ratio: {aspect_ratio}\n"
                    f"- Camera Shot: {camera_shot}\n"
                    f"- Lighting: {lighting}\n"
                    f"- Ide/Skenario: {story_concept}\n"
                    f"- Format Output yang Diminta: {output_type}\n\n"
                    "INSTRUKSI OUTPUT:\n"
                    "Berikan respon dalam Bahasa Indonesia yang rapi dengan format Markdown:\n"
                    "1. Jika output_type = 'Storyboard Lengkap', pecah ide cerita menjadi 3-5 urutan scene (Shot 1, Shot 2, dst). Untuk setiap scene sertakan:\n"
                    "   - Deskripsi Adegan (Bahasa Indonesia)\n"
                    "   - Prompt Gambar (Bahasa Inggris untuk Midjourney/Leonardo)\n"
                    "   - Prompt Motion Video (Bahasa Inggris untuk Runway/Luma)\n"
                    "2. Jika output_type = 'Prompt Gambar Tunggal', buatkan 3 variasi prompt bahasa Inggris tingkat tinggi (lengkap dengan parameter lighting, camera, style, dan aspect ratio).\n"
                    "3. Jika output_type = 'Prompt Video Motion', buatkan prompt bahasa Inggris fokus pada pergerakan kamera, pergerakan objek, dan transisi fisik adegan."
                )

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt_system,
                )
                
                st.success("✅ Berhasil Dihasilkan!")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
)

# --- PROSES GENERATE ---
if st.button("🚀 Generate Prompt SEKARANG", type="primary"):
    if not api_key:
        st.error("Harap masukkan Gemini API Key di sidebar sebelah kiri terlebih dahulu!")
    elif not character_desc or not story_concept:
        st.warning("Harap lengkapi deskripsi karakter dan ide cerita!")
    else:
        try:
            # Menggunakan Google GenAI SDK Terbaru
            client = genai.Client(api_key=api_key)

            with st.spinner("AI sedang merangkai prompt dan storyboard..."):
                prompt_system = f"""
                Kamu adalah seorang Expert AI Prompt Engineer dan Director Storyboard Profesional.
                Tugasmu adalah membuat output prompt terstruktur berdasarkan input pengguna.

                INFORMASI INPUT:
                - Karakter Utama: {character_desc}
                - Style Visual: {style_option}
                - Aspect Ratio: {aspect_ratio}
                - Camera Shot: {camera_shot}
                - Lighting: {lighting}
                - Ide/Skenario: {story_concept}
                - Format Output yang Diminta: {output_type}

                INSTRUKSI OUTPUT:
                Berikan respon dalam Bahasa Indonesia yang rapi dengan format Markdown:
                1. Jika output_type = 'Storyboard Lengkap', pecah ide cerita menjadi 3-5 urutan scene (Shot 1, Shot 2, dst). Untuk setiap scene sertakan:
                   - Deskripsi Adegan (Bahasa Indonesia)
                   - Prompt Gambar (Bahasa Inggris untuk Midjourney/Leonardo)
                   - Prompt Motion Video (Bahasa Inggris untuk Runway/Luma)
                2. Jika output_type = 'Prompt Gambar Tunggal', buatkan 3 variasi prompt bahasa Inggris tingkat tinggi (lengkap dengan parameter lighting, camera, style, dan aspect ratio).
                3. Jika output_type = 'Prompt Video Motion', buatkan prompt bahasa Inggris fokus pada pergerakan kamera, pergerakan objek, dan transisi fisik adegan.
                """

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt_system,
                )
                
                st.success("✅ Berhasil Dihasilkan!")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
                - Format Output yang Diminta: {output_type}

                INSTRUKSI OUTPUT:
                Berikan respon dalam Bahasa Indonesia yang rapi dengan format Markdown:
                1. Jika output_type = 'Storyboard Lengkap', pecah ide cerita menjadi 3-5 urutan scene (Shot 1, Shot 2, dst). Untuk setiap scene sertakan:
                   - Deskripsi Adegan (Bahasa Indonesia)
                   - Prompt Gambar (Bahasa Inggris untuk Midjourney/Leonardo)
                   - Prompt Motion Video (Bahasa Inggris untuk Runway/Luma)
                2. Jika output_type = 'Prompt Gambar Tunggal', buatkan 3 variasi prompt bahasa Inggris tingkat tinggi (lengkap dengan parameter lighting, camera, style, dan aspect ratio).
                3. Jika output_type = 'Prompt Video Motion', buatkan prompt bahasa Inggris fokus pada pergerakan kamera, pergerakan objek, dan transisi fisik adegan.
                """

                response = model.generate_content(prompt_system)
                
                st.success("✅ Berhasil Dihasilkan!")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
