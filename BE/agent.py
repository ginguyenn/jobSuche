import time

from fastapi import APIRouter, Request
from BE.utils import utils
from pydantic import BaseModel


router = APIRouter(prefix="/agent")

assistant_id = ""

class ChatRequest(BaseModel):
    thread_id: str
    text: str


@router.post("/chat")
async def chat(internal:Request, request: ChatRequest):
    client = internal.app.state.openai_client

    message = client.beta.threads.messages.create(
        thread_id=request.thread_id,
        role="user",
        content=request.message,
    )

    run = client.beta.threads.runs.create(
        thread_id=request.thread_id,
        assistant_id=assistant_id
    )

    while run.status not in ["completed", "failed"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=request.thread_id,run_id=run.id)
        if run.status == "requires_action":
            tool_output_array = utils.submit_tool_outputs(
                thread_id=request.thread_id,
                run_id=run.id,
                tool_outputs = tool_output_array
            )

    messages = client.beta.threads.messages.list(thread_id=request.thread_id)

    return messages.data[0].content[0].text.value
