from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
import os
from groq import Groq

app = Flask(__name__)

# Ensure the GROQ_API_KEY is set in environment variables
if not os.environ.get("GROQ_API_KEY"):
    raise EnvironmentError("GROQ_API_KEY environment variable is not set.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    video_id = data.get('video_id')

    if not video_id:
        return jsonify({"error": "No video ID provided!"}), 400

    try:
        # Fetch the transcript of the specified YouTube video
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([segment["text"] for segment in transcript])  # Combine all segments
    except Exception as e:
        return jsonify({"error": f"Error fetching transcript: {str(e)}"}), 500

    # Initialize Groq API client
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    try:
        # Create a chat completion request to summarize the transcript
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that summarizes YouTube video transcripts into step-by-step instructions or a list of key points."
                },
                {
                    "role": "user",
                    "content": f"Please summarize the following transcript: {transcript_text}"
                }
            ],
            model="llama3-8b-8192",  # Use the appropriate model
        )

        # Extract the summary from the response
        summary_text = chat_completion.choices[0].message.content
        return jsonify({"summary": summary_text}), 200
    except Exception as e:
        return jsonify({"error": f"Error processing the summarization: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if PORT isn't set
    app.run(host="0.0.0.0", port=port)

