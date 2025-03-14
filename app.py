# from flask import Flask, request, jsonify, render_template, url_for, redirect, session, Response
# import yt_dlp
# import json
# import time
# import os
# from pathlib import Path

# app = Flask(__name__, template_folder="templates")
# # DOWNLOAD_FOLDER = "downloads"
# # os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# # Get the default Downloads folder for the current user
# if os.name == 'nt':  # Windows OS
#     DOWNLOAD_FOLDER = str(Path(os.getenv('USERPROFILE')) / 'Downloads')
# else:  # For Unix-like systems (Linux/macOS), you can adjust the path accordingly
#     DOWNLOAD_FOLDER = str(Path.home() / 'Downloads')
# # Make sure the folder exists (Windows downloads folder should already exist)
# os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


# download_progress = {"progress": "0%", "speed": "0 KB/s", "eta": "N/A", "status": "Waiting"}

# def progress_hook(d):
#     """Handles download progress updates."""
#     global download_progress

#     if d["status"] == "downloading":
#         downloaded = d.get("downloaded_bytes", 0)
#         total = d.get("total_bytes", 1)  # Prevent division by zero
#         percentage = (downloaded / total) * 100 if total > 0 else 0

#         speed = d.get("_speed_str", "Unknown")
#         eta = d.get("_eta_str", "N/A")

#         download_progress.update({
#             "progress": f"{round(percentage, 2)}%",
#             "speed": speed,
#             "eta": eta,
#             "status": "Downloading..."
#         })

#     elif d["status"] == "finished":
#         download_progress.update({
#             "progress": "100%",
#             "status": "Download Complete",
#             "speed": "Done",
#             "eta": "0s"
#         })

# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/facebook")
# def facebook():
#     return render_template("facebook.html")

# @app.route("/instagram")
# def instagram():
#     return render_template("instagram.html")

# @app.route("/twitter")
# def twitter():
#     return render_template("twitter.html")

# @app.route("/tiktok")
# def tiktok():
#     return render_template("tiktok.html")


# @app.route("/progress")
# def progress():
#     """Streams live download progress."""
#     def event_stream():
#         while True:
#             time.sleep(1)  # Update every second
#             yield f"data: {json.dumps(download_progress)}\n\n"

#     return Response(event_stream(), mimetype="text/event-stream")

# @app.route("/download", methods=["POST"])
# def download_video():
#     data = request.json
#     url = data.get("url")
#     format_option = data.get("format", "video")

#     if not url:
#         return jsonify({"success": False, "error": "Invalid request: URL missing"}), 400

#     download_progress.update({
#         "progress": "0%",
#         "status": "Starting...",
#         "speed": "0 KB/s",
#         "eta": "N/A"
#     })

#     ydl_opts = {
#         "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
#         "progress_hooks": [progress_hook]
#     }

#     try:
#         with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
#             info = ydl.extract_info(url, download=False)
#             available_formats = {fmt["height"] for fmt in info.get("formats", []) if fmt.get("height")}
#             # Get the video thumbnail URL
#             thumbnail_url = info.get("thumbnail", None)
#         format_map = {
#             "4k": (2160, "bestvideo[height=2160]+bestaudio/best"),
#             "2k": (1440, "bestvideo[height=1440]+bestaudio/best"),
#             "1080p": (1080, "bestvideo[height=1080]+bestaudio/best"),
#             "720p": (720, "bestvideo[height=720]+bestaudio/best"),
#             "480p": (480, "bestvideo[height=480]+bestaudio/best"),
#             "video": (None, "bestvideo+bestaudio/best"),
#             "audio": (None, "bestaudio")
#         }

#         if format_option in format_map:
#             res, fmt = format_map[format_option]
#             if res and res not in available_formats:
#                 return jsonify({"success": False, "error": f"{format_option} resolution is not available"}), 400
#             ydl_opts["format"] = fmt

#         if format_option == "audio":
#             ydl_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}]

#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info_dict = ydl.extract_info(url, download=True)
#             filename = ydl.prepare_filename(info_dict)

#         return jsonify({"success": True, "filename": filename, "thumbnail_url": thumbnail_url})

#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)}), 500


# @app.route('/get-video-info', methods=['POST'])
# def get_video_info():
#     data = request.get_json()
#     video_url = data.get("url")

#     if not video_url:
#         return jsonify({"error": "No URL provided"}), 400

#     try:
#         ydl_opts = {"quiet": True}
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(video_url, download=False)
#             thumbnail_url = info.get("thumbnail", "")
#             formats = info.get("formats", [])
            
#             # Extract available video quality options
#             quality_options = []
#             for f in formats:
#                 if f.get("vcodec") != "none":  # Ignore audio-only formats
#                     quality_options.append(f"{f.get('height')}p")

#             return jsonify({
#                 "thumbnail_url": thumbnail_url,
#                 "qualities": list(set(quality_options))  # Remove duplicates
#             })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
    
# if __name__ == "__main__":
#     app.run(debug=True, threaded=True)


from flask import Flask, request, jsonify, render_template, Response
import yt_dlp
import json
import time
import os
from pathlib import Path

app = Flask(__name__, template_folder="templates")

# Get the default Downloads folder for the current user
if os.name == 'nt':  # Windows OS
    DOWNLOAD_FOLDER = str(Path(os.getenv('USERPROFILE')) / 'Downloads')
else:  # For Unix-like systems (Linux/macOS), you can adjust the path accordingly
    DOWNLOAD_FOLDER = str(Path.home() / 'Downloads')

# Make sure the folder exists (Windows downloads folder should already exist)
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

@app.route("/progress")
def progress():
    """Streams live download progress."""
    def event_stream():
        while True:
            time.sleep(1)  # Update every second
            yield f"data: {json.dumps(download_progress)}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")

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
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",  # Save to the browser's download folder
        "progress_hooks": [progress_hook]
    }

    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            available_formats = {fmt["height"] for fmt in info.get("formats", []) if fmt.get("height")}
            # Get the video thumbnail URL
            thumbnail_url = info.get("thumbnail", None)

        format_map = {
            "4k": (2160, "bestvideo[height=2160]+bestaudio/best"),
            "2k": (1440, "bestvideo[height=1440]+bestaudio/best"),
            "1080p": (1080, "bestvideo[height=1080]+bestaudio/best"),
            "720p": (720, "bestvideo[height=720]+bestaudio/best"),
            "480p": (480, "bestvideo[height=480]+bestaudio/best"),
            "video": (None, "bestvideo+bestaudio/best"),
            "audio": (None, "bestaudio")
        }

        if format_option in format_map:
            res, fmt = format_map[format_option]
            if res and res not in available_formats:
                return jsonify({"success": False, "error": f"{format_option} resolution is not available"}), 400
            ydl_opts["format"] = fmt

        if format_option == "audio":
            ydl_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)

        return jsonify({"success": True, "filename": filename, "thumbnail_url": thumbnail_url})

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
