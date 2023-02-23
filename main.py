import re

from fastapi import FastAPI
from fastapi.responses import FileResponse
import openai
import requests
import json

app = FastAPI()

openai.api_key = ("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")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/generate_audio")
async def process_video(story: str, voice: str):
    audFile = getAudio(story)
    with open('audio.mp3', 'wb') as f:
        f.write(audFile)
    return FileResponse('audio.mp3')


@app.get("/generate_captions")
async def process_captions(category: str, quantity: int):
    captions = chatGPTResponse(0, quantity, category)
    captions_list = captions.split("\n")
    captions_list = [caption.replace("\\", "").replace("\"", "") for caption in captions_list if caption != ""]
    return {"captions": captions_list}


@app.get("/generate_headlines")
async def process_headlines(category: str, quantity: int):
    headlines = chatGPTResponse(1, quantity, category)
    headlines_list = headlines.split("\n")
    headlines_list = [headline.replace("\\", "").replace("\"", "") for headline in headlines_list if headline != ""]
    return {"headlines": headlines_list}


def getAudio(story):
    downloadUrl = "https://support.readaloud.app/ttstool/getParts?q="
    saveAs = "&saveAs=narration.mp3"
    audioId = getId(story)

    combinedUrl = downloadUrl + audioId + saveAs
    audFile = requests.get(combinedUrl)

    return audFile.content


def getId(story):
    idUrl = "https://support.readaloud.app/ttstool/createParts"

    payload = json.dumps([
        {
            "voiceId": "Amazon US English (Joey)",
            "ssml": "<speak version=\"1.0\" xml:lang=\"en-US\"><prosody volume='default' rate='medium' pitch='default'>" + story + "</prosody></speak>"
        }
    ])

    idHeaders = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", idUrl, headers=idHeaders, data=payload)
    audioId = response.text
    idText = audioId[2:-2]
    return idText


def chatGPTResponse(option, quantity, category):
    if option == 0:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Write me " + str(quantity) + " TikTok captions for a story from the subreddit " + category + ". Make these captions as if they are reacting to the story itself, and do not use first-person speech. Keep the captions original, but do not present any bias. Do not include hashtags.",
            max_tokens=500,
            temperature=0.6
        )
        return response["choices"][0]["text"]
    elif option == 1:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Write me " + str(quantity) + " TikTok thumbnail hooks for a story from the subreddit " + category + ". Make these hooks related to the nature of the subreddit and a way to draw in engagement. Do not make the hooks too detailed, as you do not know the specifics of the story. In other words, make the hooks broad. Do not use vulgar language. Keep them short as well as to fit across a phone screen.",
            max_tokens=500,
            temperature=0.6
        )
        return response["choices"][0]["text"]