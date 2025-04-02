"""
The purpose of this simplistic flask server is for the 
front end (Javascript) to retrieve the audio generated from 
the conversation with ChatGPT.
"""

from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route("/audio")
def get_audio():
    wav_path = "audio/message.wav"
    mp3_path = "audio/message.mp3"

    if os.path.exists(wav_path):
        return send_file(wav_path, mimetype="audio/wav", as_attachment=True)
    elif os.path.exists(mp3_path):
        return send_file(mp3_path, mimetype="audio/mpeg", as_attachment=True)
    else:
        return "Аудиофайл не найден", 404

app.run(debug=True)