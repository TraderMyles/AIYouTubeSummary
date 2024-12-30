import os
import logging
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename="app.log", filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    video_id = data.get('video_id')

    if not video_id:
        logging.error("No video ID provided in the request.")
        return jsonify({"error": "No video ID provided!"}), 400

    try:
        # Fetch transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([segment["text"] for segment in transcript])
    except TranscriptsDisabled:
        logging.warning(f"Transcripts are disabled for video ID: {video_id}")
        return jsonify({"error": "Subtitles are disabled for this video."}), 400
    except NoTranscriptFound:
        logging.warning(f"No transcript found for video ID: {video_id}")
        return jsonify({"error": "No transcript found for this video."}), 404
    except Exception as e:
        logging.error(f"Error fetching transcript for video ID {video_id}: {e}")
        return jsonify({"error": f"Error fetching transcript: {e}"}), 500

    # Return fake summary for now (to isolate transcript issues)
    return jsonify({"summary": f"Transcript successfully fetched for video {video_id}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
