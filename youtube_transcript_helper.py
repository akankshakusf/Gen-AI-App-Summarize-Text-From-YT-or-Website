import pytube
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(video_url):
    """
    Extracts the video ID from a YouTube URL.
    Handles both standard (youtube.com) and shortened (youtu.be) URL formats.
    """
    try:
        if "youtube.com" in video_url:
            return video_url.split("v=")[-1].split("&")[0]  # Extract from standard URL
        elif "youtu.be" in video_url:
            return video_url.split("/")[-1].split("?")[0]  # Extract from shortened URL
        else:
            return None
    except:
        return None

def get_youtube_transcript(video_url):
    """
    Fetches the transcript for a given YouTube video.
    Returns the transcript as a single text string.
    """
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            return "Error: Invalid YouTube URL"

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript])  # Join transcript into a single string

    except Exception as e:
        return f"Error fetching transcript: {e}"
