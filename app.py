import os
from glob import glob

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
base = os.path.join("static", "outputs", "bs_adn", "")
audio = glob(f"{base}*.wav")
transcripts = glob(f"{base.replace('outputs', 'text_outputs')}*.txt")
audio = [a for a in audio if a.replace('wav','txt').replace("outputs", "text_outputs") in transcripts]
print(len(audio), len(transcripts))
audio_data = [{"audio":a, "transcript":t} for a, t in zip(audio, transcripts)]


@app.route("/")
def index():

    total = len(audio_data)  # TO DO: calculate the total number of files
    if os.path.exists('last.txt'):
        with open('last.txt', 'r', encoding='utf-8') as f:
            last = int(f.read().strip())
    else:
        last = 0  # TO DO: calculate the last index
        with open('last.txt', 'w', encoding='utf-8') as f:
            f.write(str(last))
    print(total, last)
    return render_template("index.html", total=total, last=last, category="bs_adn")


@app.route("/load", methods=["POST"])
def load():
    data = request.get_json()
    print(data)
    ind = data.get('file_index')
    audio_path = audio_data[ind]['audio']
    transcript_path = audio_data[ind]['transcript']
    with open(transcript_path, "r", encoding='utf-8') as f:
        transcript = f.read()
    with open('last.txt', 'w', encoding='utf-8') as f:
        f.write(str(ind))
    return jsonify({"audio_path": audio_path, "transcript": transcript, "transcript_path": transcript_path, "next": ind+1 if ind+1 < len(audio_data) else None})


@app.route("/save", methods=["POST"])
def save():
    data = request.get_json()
    print(data)
    category = data.get("category")
    text = data.get("text")
    transcript_path = data.get("transcript_path")
    has_music = data.get("has_music")
    if transcript_path:
        transcript_path = transcript_path.replace("text_outputs", "cleaned_text")
        dirname = os.path.dirname(transcript_path)
        print(dirname)
        os.makedirs(dirname, exist_ok=True)
        if has_music == "1":
            text+="\n\nMUSIC"
        with open(transcript_path, "w", encoding='utf-8') as f:
            f.write(text)
        return jsonify({"message":"Text saved!"})
    else:
        return jsonify({"message":"Failed to save text. Missing transcript path."})
    

if __name__ == "__main__":
    app.run()