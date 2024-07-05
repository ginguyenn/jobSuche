import requests
import os
import chainlit as cl

from pathlib import Path
from io import BytesIO
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict

from chainlit.element import Element

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@cl.step(type="tool")
async def speech_to_text(audio_file):
    response = client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )
    return response.text


async def upload_files(files: List[Element]):
    file_ids = []
    for file in files:
        uploaded_file = await client.files.create(
            file=Path(file.path), purpose="assistants"
        )
        file_ids.append(uploaded_file.id)
    return file_ids


async def process_files(files: List[Element]):
    file_ids = []
    if len(files) > 0:
        file_ids = await upload_files(files)

    return [
        {
            "file_id": file_id,
            "tools": [{"type": "code_interpreter"}, {"type": "file_search"}],
        }
        for file_id in file_ids
    ]


@cl.on_chat_start
async def on_chat_start():
    thread = client.beta.threads.create()
    cl.user_session.get("chat_profile")
    cl.user_session.set("thread_id", thread.id)
    text =("# Welcome to JobMate! 🚀🤖 \n Hi there, Student! 👋 We're excited to have you on board.")
    await cl.Message(content=text).send()
    #elements = [cl.Image(name="image1", display="inline", path="./pic.png")]
    #await cl.Message(content="", elements=elements).send()

    files = None
    while files is None:
        files = await cl.AskFileMessage(
            content="Please upload a PDF file to begin!",
            accept=["application/pdf"],
            max_size_mb=20,
        ).send()

    updated_file = files[0]

    params = {
        "path": updated_file.path,
        "name": updated_file.name
    }
    url = 'http://localhost:4000/upload_file'

    x = requests.post(url, json=params)

    await cl.Message(content=x.text).send()


@cl.on_message
async def on_message(message: cl.Message):
    thread_id = cl.user_session.get("thread_id")

    attachments = await upload_files(message.elements)
    params = {
        "text": message.content,
        "thread_id": thread_id,
        #"attachments": attachments
    }

    url = 'http://localhost:4000/chat'

    x = requests.post(url, json=params)

    await cl.Message(content=x.text).send()


"""
@cl.on_chat_end
async def on_chat_end():
    url = 'http://localhost:4000/clear_embeddings'
    x = requests.post(url)
    await cl.Message(content=x.text).send()
"""


@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.AudioChunk):
    if chunk.isStart:
        buffer = BytesIO()
        buffer.name = f"input_audio.{chunk.mimeType.split('/')[1]}"
        cl.user_session.set("audio_buffer", buffer)
        cl.user_session.set("audio_mime_type", chunk.mimeType)

    cl.user_session.get("audio_buffer").write(chunk.data)


@cl.on_audio_end
async def on_audio_end(elements: List[Element]):
    audio_buffer: BytesIO = cl.user_session.get("audio_buffer")
    audio_buffer.seek(0)
    audio_file = audio_buffer.read()
    audio_mime_type: str = cl.user_session.get("audio_mime_type")

    input_audio_el = cl.Audio(
        mime=audio_mime_type, content=audio_file, name=audio_buffer.name
    )
    await cl.Message(
        author="You",
        type="user_message",
        content="",
        elements=[input_audio_el, *elements],
    ).send()

    whisper_input = (audio_buffer.name, audio_file, audio_mime_type)
    transcription = await speech_to_text(whisper_input)

    msg = cl.Message(author="You", content=transcription, elements=elements)
    await on_message(message=msg)


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit("app.py")
