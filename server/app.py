from flask import Flask, request, jsonify
import yt_dlp
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = ["GET, POST, OPTIONS"]
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

def get_video_info(video_url):
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio[ext=m4a]/bestaudio/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        # 'postprocessors': [{
        #     'key': 'FFmpegVideoConvertor',
        #     'preferedformat': 'mp4'
        # }]
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        video_info = {
            "title": info.get("title"),
            "description": info.get("description"),
            "thumbnail": info.get("thumbnail"),
            "video_links": [{
                "format": fmt["format_id"],
                "quality": fmt.get("height"),
                "url": fmt["url"]
            } for fmt in info.get("formats", []) if fmt.get("vcodec") != "none"],
            "audio_link": {
                "format": audio_fmt["format_id"],
                "bitrate": audio_fmt.get("abr"),
                "extension": audio_fmt.get("ext"),
                "url": audio_fmt["url"],
            } if (audio_fmt := next((fmt for fmt in info.get("formats", []) if fmt.get("acodec") != "none"), None)) else None
        }
        return video_info

@app.route('/process', methods=['POST'])
def process_url():
    data = request.json
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({"error": "URL not provided"}), 400
    if "youtube.com" not in video_url and "youtu.be" not in video_url:
        return jsonify({"error": "Invalid YouTube URL"}), 400
    
    try:
        video_info = get_video_info(video_url)
        print("URL received: ", video_url)
        print("video info:", video_info)
        return jsonify(video_info)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
