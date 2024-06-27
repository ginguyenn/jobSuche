import uvicorn
from fastapi import FastAPI
from openai import OpenAI
from agent import submit_tool_outputs
import fitz
import os
import time
from pydantic import BaseModel
import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime

openai_api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

#GPT 3.5
assistant_id = "asst_hiPrSu0i132e9CX6XMnSrGKw"

#GPT 4
#assistant_id = "asst_jp2GubaYiG6odVi2A2TNDdfv"

chroma_client = chromadb.PersistentClient(path="BE/storage/chromadb")
default_ef = embedding_functions.DefaultEmbeddingFunction()
collection = chroma_client.get_or_create_collection(name="files", embedding_function=default_ef)

app = FastAPI()

class MessageInput(BaseModel):
    text: str
    thread_id: str

class UploadedFile(BaseModel):
    path: str
    name: str


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
