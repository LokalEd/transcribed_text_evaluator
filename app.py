import os
from glob import glob

import aiofiles
from quart import Quart, jsonify, render_template, request

app = Quart(__name__)

audio_data = []


@app.before_serving
async def setup_data():
    global audio_data
    base = os.path.join("static", "outputs", "bs_adn", "")
    print(base)
    audio = sorted(glob(f"{base}*.wav"))
    transcripts = sorted(glob(f"{base.replace('outputs', 'text_outputs')}*.txt"))
    audio = [
        a
        for a in audio
        if a.replace("wav", "txt").replace("outputs", "text_outputs") in transcripts
    ]
    transcripts = [
        t
        for t in transcripts
        if t.replace("txt", "wav").replace("text_outputs", "outputs") in audio
    ]
    print(len(audio), len(transcripts))
    audio_data = [{"audio": a, "transcript": t} for a, t in zip(audio, transcripts)]


@app.before_request
async def check_last_txt():
    if not os.path.exists("last.txt"):
        async with aiofiles.open("last.txt", "w", encoding="utf-8") as f:
            await f.write("0")


@app.route("/")
async def index():
    total = len(audio_data)
    async with aiofiles.open("last.txt", "r", encoding="utf-8") as f:
        last = int((await f.read()).strip() or 0)
    print(total, last)
    return await render_template(
        "index.html", total=total, last=last, category="bs_adn"
    )


@app.route("/load", methods=["POST"])
async def load():
    data = await request.get_json()
    print(data)
    ind = data.get("file_index")
    audio_path = audio_data[ind]["audio"]
    transcript_path = audio_data[ind]["transcript"]
    async with aiofiles.open(transcript_path, "r", encoding="utf-8") as f:
        transcript = await f.read()
    async with aiofiles.open("last.txt", "w", encoding="utf-8") as f:
        await f.write(str(ind))
    response = {
        "audio_path": audio_path,
        "transcript": transcript,
        "transcript_path": transcript_path,
        "next": ind + 1 if ind + 1 < len(audio_data) else None,
        "filename": os.path.basename(audio_path),
    }
    print(response)
    return jsonify(response)


@app.route("/save", methods=["POST"])
async def save():
    data = await request.get_json()
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
            text += "\n\nMUSIC"
        async with aiofiles.open(transcript_path, "w", encoding="utf-8") as f:
            await f.write(text)
        return jsonify({"message": "Text saved!"})
    else:
        return jsonify({"message": "Failed to save text. Missing transcript path."})


@app.errorhandler(404)
async def page_not_found(e):
    return jsonify(error=str(e)), 404


@app.errorhandler(500)
async def internal_server_error(e):
    return jsonify(error=str(e)), 500


if __name__ == "__main__":
    app.run()
