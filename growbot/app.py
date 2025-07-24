import streamlit as st
import google.generativeai as genai
import os

# --- Konfigurasi Halaman Streamlit ---
st.set_page_config(
    page_title="Micro-Challenge Chatbot",
    page_icon="🤖"
)

# --- Judul Aplikasi ---
st.title("🤖 Micro-Challenge Chatbot")
st.write("Dapatkan tantangan harian kecil untuk membuat harimu lebih produktif!")

# ==============================================================================
# PENGATURAN API KEY DAN MODEL (PENTING! UBAH SESUAI KEBUTUHAN ANDA)
# ==============================================================================

# Ambil API Key dari Streamlit Secrets atau variabel lingkungan
# PASTIKAN API KEY ANDA TERSIMPAN DI FILE .streamlit/secrets.toml (lokal)
# ATAU DI PENGATURAN REPO STREAMLIT CLOUD SEBAGAI "GEMINI_API_KEY"
try:
    API_KEY = os.environ.get("GEMINI_API_KEY") or st.secrets["GEMINI_API_KEY"]
except (KeyError, AttributeError):
    st.error("🚨 GEMINI_API_KEY tidak ditemukan!")
    st.warning("Pastikan Anda telah mengatur API Key Gemini di Streamlit Secrets atau variabel lingkungan.")
    st.stop() # Hentikan eksekusi jika API Key tidak ada

# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

# Definisikan peran chatbot Anda di sini.
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Kamu adalah Pemberi Tantangan Harian. Berikan satu 'micro-challenge' yang bisa dilakukan hari ini (misal: 'Belajar 5 kata baru', 'Senyum pada 3 orang asing'). Tolak permintaan selain 'tantangan'."]
    },
    {
        "role": "model",
        "parts": ["Siap untuk tantangan hari ini? Ketik 'tantangan' untuk mendapatkan 'micro-challenge' Anda!"]
    }
]

# ==============================================================================
# FUNGSI UTAMA CHATBOT (HINDARI MENGUBAH BAGIAN INI JIKA TIDAK YAKIN)
# ==============================================================================

# Inisialisasi Gemini API
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"Kesalahan saat mengkonfigurasi API Key Gemini: {e}")
    st.stop()

# Inisialisasi model (gunakan cache agar tidak membuat ulang setiap rerun)
@st.cache_resource
def get_gemini_model():
    return genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )

model = get_gemini_model()

# --- Inisialisasi Riwayat Chat di Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = INITIAL_CHATBOT_CONTEXT

# --- Tampilkan Riwayat Chat ---
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["parts"][0])
    elif message["role"] == "model":
        with st.chat_message("assistant"):
            st.write(message["parts"][0])

# --- Input Pengguna ---
user_input = st.chat_input("Ketik 'tantangan' atau 'exit'...")

if user_input:
    # Tampilkan input pengguna di chat
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "parts": [user_input]})

    if user_input.lower() == 'exit':
        with st.chat_message("assistant"):
            st.write("Sampai jumpa!")
        st.session_state.messages.append({"role": "model", "parts": ["Sampai jumpa!"]})
        st.stop() # Hentikan aplikasi jika 'exit'

    # Kirim input ke Gemini dan dapatkan respons
    with st.spinner("Chatbot sedang berpikir..."):
        try:
            # Re-inisialisasi sesi chat dengan riwayat saat ini
            chat_session = model.start_chat(history=st.session_state.messages)
            response = chat_session.send_message(user_input.lower(), request_options={"timeout": 60})

            if response and response.text:
                ai_response = response.text
            else:
                ai_response = "Maaf, saya tidak bisa memberikan balasan. Respons API kosong atau tidak valid."

        except Exception as e:
            ai_response = f"Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini: {e}\n\n" \
                          "Kemungkinan penyebab:\n" \
                          " - Masalah koneksi internet atau timeout.\n" \
                          " - API Key mungkin dibatasi, tidak valid, atau melebihi kuota.\n" \
                          " - Masalah internal di server Gemini."

    # Tampilkan respons chatbot dan tambahkan ke riwayat
    with st.chat_message("assistant"):
        st.write(ai_response)
    st.session_state.messages.append({"role": "model", "parts": [ai_response]})