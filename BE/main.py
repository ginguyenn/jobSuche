import uvicorn
from fastapi import FastAPI
from openai import OpenAI
from setup.agent import submit_tool_outputs
import chardet
import os
import time
from pydantic import BaseModel


openai_api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

assistant_id = "asst_Fgpcx9WLGYEp4QI1tfyffuFp"

app = FastAPI()

class MessageInput(BaseModel):
    text: str
    thread_id: str

class UploadedFile(BaseModel):
    path: str
    name: str


@app.post("/upload_file")
async def upload_file(uploaded_file: UploadedFile):
    with open(uploaded_file.path, "rb") as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    with open(uploaded_file.path, "r", encoding=encoding, errors="replace") as f:
        text = f.read()

    return {"content": f"{uploaded_file.name} uploaded successfully!"}


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

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=4000)
