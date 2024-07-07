import os

from dotenv import load_dotenv
from openai import OpenAI
from tool_descriptions import functions

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt ="""You are an assistant who has access to Moodle, GitHub, Web and files stored in Chroma database, and also can browse web from a given URL. Help users in career consulting.

Based on the information you have from the Moodle, GitHub repositories of the user, and also the resume uploaded in the beginning and the URL of a provided job description, please optimize the resume so that it is most suitable for the position.

You can also help them in preparing questions for the interview related to the given position and the URL of a provided job description as well as give feedback for user's answer to interview question.

Also based on information about their skills from GitHub, Moodle and resume, you can give recommendation on what they can learn more to pursue this career and links of related online courses for that.
"""

assistant = openai_client.beta.assistants.create(
    name="JobMate Assistant",
    instructions=prompt,
    tools=functions,
    model="gpt-4"
)
print(assistant.id)
