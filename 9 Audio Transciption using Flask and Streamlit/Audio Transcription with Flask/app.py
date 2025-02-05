from flask import Flask, render_template, request, jsonify
from groq import Groq
from deep_translator import GoogleTranslator

# Replace with your actual API key
api_key = ''

# Initialize the Groq client with the API key
client = Groq(api_key=api_key)

app = Flask(__name__)

# Available languages for translation
LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "es": "Spanish",
    "fr": "French",
    "de": "German"
}

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES)

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    
    file = request.files['audio_file']
    language = request.form.get('language', 'en')  # Default to English
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    temp_filename = "uploaded_audio.mp3"
    file.save(temp_filename)

    try:
        with open(temp_filename, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(temp_filename, audio_file.read()),
                model="whisper-large-v3",
                response_format="verbose_json"
            )
        
        transcribed_text = transcription.text
        translated_text = GoogleTranslator(source='auto', target=language).translate(transcribed_text)
        
        return jsonify({
            'transcription': transcribed_text,
            'translation': translated_text,
            'language': LANGUAGES.get(language, 'Unknown')
        })
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
