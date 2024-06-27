import chainlit as cl
import requests
from openai import OpenAI
import os

openai_api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

@cl.on_chat_start
async def on_chat_start():
    thread = client.beta.threads.create()
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
    params = {
        "text": message.content,
        "thread_id": thread_id
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

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit("app.py")


