from openai import OpenAI
from tavily import TavilyClient
import json
import os
from github import Github
import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.utils import embedding_functions

openai_api_key = os.environ.get('OPENAI_API_KEY')
tavily_api_key = os.environ.get('TAVILY_API_KEY')
moodle_token = os.environ.get('MOODLE_TOKEN')
git_token = os.environ.get('GIT_TOKEN')

client = OpenAI(api_key=openai_api_key)
tavily_client = TavilyClient(api_key=tavily_api_key)
g = Github(git_token)

chroma_client = chromadb.PersistentClient(path="BE/storage/chromadb")
default_ef = embedding_functions.DefaultEmbeddingFunction()
collection = chroma_client.get_or_create_collection(name="files", embedding_function=default_ef)

# Function to perform a Tavily search (sign up for an API key at https://app.tavily.com/home)
def tavily_search(query):
    search_result = tavily_client.get_search_context(query, search_depth="advanced", max_tokens=8000)
    return search_result


# Function for getting content of moodle course.
def get_moodle_course_content(courseid):
    """Get the content of a given moodle course"""
    moodle_call = 'https://moodle.htw-berlin.de/webservice/rest/server.php?wstoken=' + moodle_token + \
                  '&wsfunction=core_course_get_contents&moodlewsrestformat=json&courseid=' + courseid
    r = requests.get(moodle_call)
    return json.dumps(r.json())


# Function for getting all repo names from Github
def get_all_repo_name():
    result = []
    for repo in g.get_user().get_repos(visibility='public'):
        result.append(repo.name)
    return json.dumps(result)


# Function for getting content of all repo from Github
def get_content_all_repos():
    all_repos = g.get_user().get_repos(visibility='public')
    all_content = {}
    for repo in all_repos:
        repo_name = repo.full_name
        repo_content = get_content_given_repo(repo_name)
        all_content[repo_name] = repo_content
    return json.dumps(all_content, indent=4)



# Function for returning the content of a given repository
def get_content_given_repo(repo_name):
    repo = g.get_repo(f"{repo_name}")
    contents = repo.get_contents("")
    result = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            result.append(file_content)
    return json.dumps(f"{result}")



def get_content_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text_content = soup.get_text(separator=' ', strip=True)
    return text_content

def query_chromadb(input):
    results = collection.query(
        query_texts=[input],
        n_results=1
    )
    return json.dumps(f"{results}")


functions = [{
        "type": "function",
        "function": {
            "name": "tavily_search",
            "description": "Get information on from the web and given URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string",
                              "description": "The search query to use."},
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_moodle_course_content",
            "description": "Get the content of a given moodle course",
            "parameters": {
                "type": "object",
                "properties": {
                    "courseid": {
                        "type": "string",
                        "description": "The ID of a moodle course, e.g. 36301",
                    },
                },
                "required": ["courseid"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_repo_name",
            "description": "Get all repo names from Github",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_content_all_repos",
            "description": "Getting content of all repo from Github",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_content_given_repo",
            "description": "Get the content of a given repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_name": {
                        "type": "string",
                        "description": "The name of a repository, e.g. github-starter-course",
                    },
                },
                "required": ["repo_name"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_content_url",
            "description": "Get the content of a given url and answer the question from the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The url of a website",
                    },
                },
                "required": ["url"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_chromadb",
            "description": "Get the content of data from files stored in chromadb related to the user input ",
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "The user question want to ask about a certain information from files stored in chromadb",
                    },
                },
                "required": ["input"],
            },
        }
    }
]

function_lookup = {
    "tavily_search": tavily_search,
    "get_moodle_course_content": get_moodle_course_content,
    "get_all_repo_name": get_all_repo_name,
    "get_content_given_repo": get_content_given_repo,
    "get_content_url": get_content_url,
    "query_chromadb": query_chromadb,
    "get_content_all_repos": get_content_all_repos
}

"""
## Create an assistant
assistant = client.beta.assistants.create(
    name="JobMate Assistant",
    instructions="You are an assistant who has access to Moodle, GitHub, Web and files stored in Chroma database, and"
                 "also can browse web from a given URL. Help users in career consulting. Based on the information you have "
                 "from the Moodle account and GitHub repositories of the user, and also the resume uploaded in the beginning and "
                 "the URL of a job description can be provided, please optimize the resume so that it is most suitable for "
                 "the position. You can also help them in preparing questions for the interview related to the given position"
                 "Also based on information about their skills from GitHub, Moodle and resume, you can give recommendation on "
                 "what they can learn more to persue this career and links of related online courses for that",
    tools=functions,
    model="gpt-3.5-turbo-0125"
)
assistant = client.beta.assistants.create(
    name="JobMate Assistant",
    instructions="You are an assistant who has access to Moodle, GitHub, Web and files stored in Chroma database, and"
                 "also can browse web from a given URL. Help users in career consulting. Based on the information you have "
                 "from the Moodle account and GitHub repositories of the user, and also the resume uploaded in the beginning and "
                 "the URL of a job description can be provided, please optimize the resume so that it is most suitable for "
                 "the position. You can also help them in preparing questions for the interview related to the given position"
                 "Also based on information about their skills from GitHub, Moodle and resume, you can give recommendation on "
                 "what they can learn more to persue this career and links of related online courses for that",
    tools=functions,
    model="gpt-4-turbo"
)
"""


# Function to handle tool output submission
def submit_tool_outputs(thread_id, run_id, tools_to_call):
    tool_output_array = []
    for tool in tools_to_call:
        output = None
        tool_call_id = tool.id
        function_name = tool.function.name
        function_args = json.loads(tool.function.arguments)
        function_to_call = function_lookup[function_name]
        output = function_to_call(**function_args)
        if output:
            tool_output_array.append({"tool_call_id": tool_call_id, "output": output})

    return client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_output_array
    )

