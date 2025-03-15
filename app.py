from flask import Flask, request, jsonify, render_template, url_for, redirect, send_file, session, Response
import yt_dlp
import json
import time
import os
from pathlib import Path

app = Flask(__name__, template_folder="templates")
# DOWNLOAD_FOLDER = "downloads"
# os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Get the default Downloads folder for the current user
DOWNLOAD_FOLDER = "/tmp/downloads"  # Store files temporarily on Ubuntu
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


download_progress = {"progress": "0%", "speed": "0 KB/s", "eta": "N/A", "status": "Waiting"}

def progress_hook(d):
    """Handles download progress updates."""
    global download_progress

    if d["status"] == "downloading":
        downloaded = d.get("downloaded_bytes", 0)
        total = d.get("total_bytes", 1)  # Prevent division by zero
        percentage = (downloaded / total) * 100 if total > 0 else 0

        speed = d.get("_speed_str", "Unknown")
        eta = d.get("_eta_str", "N/A")

        download_progress.update({
            "progress": f"{round(percentage, 2)}%",
            "speed": speed,
            "eta": eta,
            "status": "Downloading..."
        })

    elif d["status"] == "finished":
        download_progress.update({
            "progress": "100%",
            "status": "Download Complete",
            "speed": "Done",
            "eta": "0s"
        })

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/facebook")
def facebook():
    return render_template("facebook.html")

@app.route("/instagram")
def instagram():
    return render_template("instagram.html")

@app.route("/twitter")
def twitter():
    return render_template("twitter.html")

@app.route("/tiktok")
def tiktok():
    return render_template("tiktok.html")


@app.route("/progress")
def progress():
    """Streams live download progress."""
    def event_stream():
        while True:
            time.sleep(1)  # Update every second
            yield f"data: {json.dumps(download_progress)}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")

    
@app.route('/download-file/<filename>')
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    return send_file(file_path, as_attachment=True)
    
@app.route("/download", methods=["POST"])
def download_video():
    data = request.json
    url = data.get("url")
    format_option = data.get("format", "video")

    if not url:
        return jsonify({"success": False, "error": "Invalid request: URL missing"}), 400

    download_progress.update({
        "progress": "0%",
        "status": "Starting...",
        "speed": "0 KB/s",
        "eta": "N/A"
    })

    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
        "progress_hooks": [progress_hook],
        "quiet": False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = info.get("requested_downloads", [{}])[0].get("filename", None)

            if not filename:
                filename = f"{info.get('title', 'video')}.mp4"

            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            print(f"File downloaded to: {file_path}")  # Debug print

            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True, download_name=filename, mimetype="video/mp4")
            else:
                return jsonify({"success": False, "error": "File not found"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/get-video-info', methods=['POST'])
def get_video_info():
    data = request.get_json()
    video_url = data.get("url")

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            thumbnail_url = info.get("thumbnail", "")
            formats = info.get("formats", [])
            
            # Extract available video quality options
            quality_options = []
            for f in formats:
                if f.get("vcodec") != "none":  # Ignore audio-only formats
                    quality_options.append(f"{f.get('height')}p")

            return jsonify({
                "thumbnail_url": thumbnail_url,
                "qualities": list(set(quality_options))  # Remove duplicates
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


    
if __name__ == "__main__":
    app.run(debug=True, threaded=True)
