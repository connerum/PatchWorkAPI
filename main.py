from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.openapi.models import APIKey
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader
from moviepy.editor import concatenate_audioclips, AudioFileClip
from moviepy.editor import VideoFileClip
import asyncpraw
import openai
import requests
import json


app = FastAPI()

# Define API key header
API_KEY = "YOUR_API_KEY_HERE"
api_key_header = APIKeyHeader(name="Authorization")

openai.api_key = ("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")

# Create an instance of reddit class
user_agent = "TikTokSaaS"
reddit = asyncpraw.Reddit(username="Objective_Ad7158",
                     password="Ferbiscool2!",
                     client_id="oTWvTeP37ydTpslHTUDRZQ",
                     client_secret="0-8gGOzvYqiQylNjBKqPZf5Vio_7eg",
                     user_agent=user_agent
                     )


# Function to validate API key
async def validate_api_key(api_key_header: str = Header(None)) -> None:
    if api_key_header is None:
        raise HTTPException(status_code=400, detail="API key missing")
    elif api_key_header != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/")
async def root():
    return {"API STATUS": "Online!"}


@app.get("/generate_captions")
async def process_captions(category: str, quantity: int, api_key_header: APIKey = Depends(validate_api_key)):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Write me {quantity} TikTok captions for a story from the subreddit {category}. Make these captions as if they are reacting to the story itself, and do not use first-person speech. Keep the captions original, but do not present any bias. Do not include hashtags.",
            max_tokens=500,
            temperature=0.6
        )
        captions = response["choices"][0]["text"]
        captions_list = captions.split("\n")
        captions_list = [caption.replace("\\", "").replace("\"", "") for caption in captions_list if caption != ""]
        return {"captions": captions_list}
    except Exception as e:
        # add error handling and logging
        return {"error": str(e)}


@app.get("/generate_headlines")
async def process_headlines(category: str, quantity: int, api_key_header: APIKey = Depends(validate_api_key)):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Write me {quantity} TikTok thumbnail hooks for a story from the subreddit {category}. Make these hooks related to the nature of the subreddit and a way to draw in engagement. Do not make the hooks too detailed, as you do not know the specifics of the story. In other words, make the hooks broad. Do not use vulgar language. Keep them short as well as to fit across a phone screen.",
            max_tokens=500,
            temperature=0.6
        )
        headlines = response["choices"][0]["text"]
        headlines_list = headlines.split("\n")
        headlines_list = [headline.replace("\\", "").replace("\"", "") for headline in headlines_list if headline != ""]
        return {"headlines": headlines_list}
    except Exception as e:
        # add error handling and logging
        return {"error": str(e)}


@app.get("/creation_video")
async def create_reddit(story: str, video: str, option: int, api_key_header: APIKey = Depends(validate_api_key)):
    if option == 0:
        makeVideo(story, video)
    elif option == 1:
        story = storyGrabber(story)
        makeVideo(story, video)
    return FileResponse("created.mp4")


def storyGrabber(urlInput):
    submission = reddit.submission(
        url=urlInput)
    text = submission.selftext
    return text


def makeVideo(story, video):
    vidPath = getVideo(video)

    audioUrls = murfAPI(story)
    audio_clip_paths = download_audio_files(audioUrls)
    if len(audio_clip_paths) >= 2:
        concatenate_audio_moviepy(audio_clip_paths, "conc.mp3")
        audPath = "conc.mp3"
    else:
        audPath = audio_clip_paths[0]
    videoclip = VideoFileClip(vidPath)
    new_clip = videoclip.without_audio()
    audio = AudioFileClip(audPath)
    video_with_new_audio = new_clip.set_audio(audio)
    video_with_new_audio = video_with_new_audio.loop(duration=audio.duration)
    video_with_new_audio.write_videofile("created.mp4", fps=30, audio_codec="aac", audio_bitrate="160k")
    video_with_new_audio.close()
    return "created.mp4"


def getVideo(video):
    videoUrl = video
    vidFile = requests.get(videoUrl).content
    with open('video.mp4', 'wb') as f:
        f.write(vidFile)
    return "video.mp4"


def murfAPI(userText):
    userTextList = split_string(userText)

    url = "https://api.murf.ai/v1/speech/generate-with-key"
    headers = {
        'Content-Type': 'application/json',
        'api-key': 'api_211b0400-4594-484a-a5f5-8111bb85b0e8',
        'Accept': 'application/json'
    }

    urlList = []
    for chapter in userTextList:
        payload = json.dumps({
            "voiceId": "en-US-wayne",
            "style": "null",
            "text": chapter,
            "rate": 15,
            "pitch": 0,
            "sampleRate": 24000,
            "format": "MP3",
            "channelType": "STEREO",
            "pronunciationDictionary": {},
            "encodeAsBase64": False
        })

        response = requests.request("POST", url, headers=headers, data=payload)
        urlList.append(response.json()['audioFile'])
    return urlList


def split_string(text):
    length = len(text)
    max_length = 1000
    num_parts = (length + max_length - 1) // max_length
    part_size = (length + num_parts - 1) // num_parts
    parts = [text[i:i + part_size] for i in range(0, length, part_size)]
    return parts


def download_audio_files(urlList):
    pathList = []
    i = 0
    for audLink in urlList:
        url = audLink
        response = requests.get(url)

        with open(str(i) + ".mp3", "wb") as f:
            f.write(response.content)
            pathList.append(f.name)
        i += 1
    return pathList


def concatenate_audio_moviepy(audio_clip_paths, output_path):
    clips = [AudioFileClip(c) for c in audio_clip_paths]
    final_clip = concatenate_audioclips(clips)
    final_clip.write_audiofile(output_path)