import os
import time
from datetime import datetime

from dotenv import load_dotenv
from typing import List, Optional

import chromadb
import fitz
import uvicorn
from chromadb.utils import embedding_functions
from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel

from agent import submit_tool_outputs

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

assistant_id = os.getenv('ASSISTANT_ID')

chroma_client = chromadb.PersistentClient(path="BE/storage/chromadb")
default_ef = embedding_functions.DefaultEmbeddingFunction()
collection = chroma_client.get_or_create_collection(name="files", embedding_function=default_ef)

app = FastAPI()

class UploadedFile(BaseModel):
    #file_id: str
    path: str
    name: str

class MessageInput(BaseModel):
    text: str
    thread_id: str


@app.post("/upload_file")
async def upload_file(uploaded_file: UploadedFile):
    doc = fitz.open(uploaded_file.path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()

    metadata = {
        "filename": uploaded_file.name,
        "upload_timestamp": datetime.now().isoformat(),
    }

    collection.add(
        documents=[text],
        metadatas=[metadata],
        ids=[uploaded_file.name]
    )

    return {"content": f"{uploaded_file.name} uploaded successfully! You can now ask questions."}


@app.post("/chat")
async def main(message_input: MessageInput):
    client.beta.threads.messages.create(
        thread_id=message_input.thread_id,
        role="user",
        content=message_input.text
    )
    run = client.beta.threads.runs.create(
        thread_id=message_input.thread_id,
        assistant_id=assistant_id
    )

    while run.status not in ['completed', 'failed']:
        print(run.status)
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=message_input.thread_id, run_id=run.id)
        if run.status == 'requires_action':
            run = submit_tool_outputs(message_input.thread_id, run.id, run.required_action.submit_tool_outputs.tool_calls)

    messages = client.beta.threads.messages.list(message_input.thread_id)
    return messages.data[0].content[0].text.value

@app.post("/clear_embeddings")
async def clear_embeddings():
    chroma_client.delete_collection(name="files")
    return {"status": "ChromaDB collection cleared."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=4000)
