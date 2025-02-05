'''
   Author  : Emon Hasan
   Email   : iconicemon01@gmail.com
   GitHub  : https://github.com/Md-Emon-Hasan
   LinkedIn: https://www.linkedin.com/in/emon-hasan/
   Date    : 01/29/2025
   Time    : 00:11
   Project : Multilingual audio transcription and translation using Groq api and whisper-large-v3 model
'''

# Import required libraries
import streamlit as st
from groq import Groq
from deep_translator import GoogleTranslator

# Groq API key (replace with your actual API key)
api_key = ''

# Initialize the Groq client with the API key
client = Groq(api_key=api_key)

# Supported languages for translation
LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Bangla": "bn",
    "Spanish": "es",
    "French": "fr",
    "German": "de"
}

def transcribe_audio(file):
    """
    Transcribe the uploaded audio file using the Groq Whisper-large-v3 model.
    :param file: The uploaded audio file
    :return: Transcribed text from the audio file
    """
    temp_filename = "uploaded_audio.mp3"
    with open(temp_filename, "wb") as f:
        f.write(file.getbuffer())

    with open(temp_filename, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=(temp_filename, audio_file.read()),
            model="whisper-large-v3",
            response_format="verbose_json",
        )
    
    return transcription.text

def translate_text(text, target_lang):
    """
    Translate the given text to the selected language.
    :param text: The text to translate
    :param target_lang: The target language code
    :return: Translated text
    """
    translator = GoogleTranslator(source='auto', target=target_lang)
    return translator.translate(text)

def main():
    st.title("Multilingual Audio Transcription & Translation")
    st.write("Upload an audio file (MP3, WAV, etc.) to transcribe and translate it into your preferred language.")

    # Language selection
    selected_lang = st.selectbox("Select Translation Language", options=list(LANGUAGES.keys()))
    
    # File uploader
    uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "m4a"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/mp3")
        
        with st.spinner("Transcribing... Please wait."):
            try:
                transcription_text = transcribe_audio(uploaded_file)
                st.subheader("Transcription Result:")
                st.text_area("Transcribed Text", transcription_text, height=200)
                
                # Translate the transcription
                target_lang_code = LANGUAGES[selected_lang]
                translated_text = translate_text(transcription_text, target_lang_code)
                
                st.subheader(f"Translated Text ({selected_lang}):")
                st.text_area("Translation", translated_text, height=200)
            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
