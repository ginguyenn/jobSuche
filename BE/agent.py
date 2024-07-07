import os
import pandas as pd
import requests
import json
import chromadb
from dotenv import load_dotenv

from openai import OpenAI
from tavily import TavilyClient
from github import Github
from bs4 import BeautifulSoup
from chromadb.utils import embedding_functions
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
tavily_client = TavilyClient(api_key=os.getenv('TAVILY_KEY'))
moodle_token = os.getenv('MOODLE_TOKEN')
github_token = os.getenv('GITHUB_TOKEN')

g = Github(github_token)
moodle_domain = 'https://moodle.htw-berlin.de/webservice/rest/server.php'

chroma_client = chromadb.PersistentClient(path="BE/storage/chromadb")
default_ef = embedding_functions.DefaultEmbeddingFunction()
collection = chroma_client.get_or_create_collection(name="files", embedding_function=default_ef)

# Function to perform a Tavily search
def tavily_search(query):
    search_result = tavily_client.get_search_context(query, search_depth="advanced", max_tokens=8000)
    return search_result


# Function for getting content of moodle course.
def get_moodle_course_content(courseid):
    moodle_call = f'{moodle_domain}?wstoken=' + moodle_token + \
                  '&wsfunction=core_course_get_contents&moodlewsrestformat=json&courseid=' + courseid
    response = requests.get(moodle_call).json()
    return json.dumps(response)


# Function for getting enrolled courses of actual user
def get_users_enrolled_courses():
    moodle_call = f'{moodle_domain}?wstoken=' + moodle_token + \
                  '&wsfunction=core_webservice_get_site_info&moodlewsrestformat=json'
    userid = requests.get(moodle_call).json()['userid']

    params = {
        'wstoken': moodle_token,
        'userid': userid,
        'wsfunction': 'core_enrol_get_users_courses',
        'moodlewsrestformat': 'json'
    }
    response = requests.get(moodle_domain, params=params).json()
    return json.dumps(f'{response}')


# Function for getting all repo names from Github
def get_all_repo_name():
    result = []
    for repo in g.get_user().get_repos(visibility='public'):
        result.append(repo.name)
    return json.dumps(result)


# Function for getting content of all repo from Github
def get_content_all_repos():
    all_repos = g.get_user().get_repos(visibility='public')
    all_content = []
    for repo in all_repos:
        repo_content = get_content_given_repo(repo.name)
        content = dict()
        content[repo.name] = repo_content
        all_content.append(content)
    return json.dumps(all_content, indent=4)



# Function for returning the content of a given repository
def get_content_given_repo(repo_name):
    for repo in g.get_user().get_repos(visibility='public'):
        if repo.name == str(repo_name):
            repo = g.get_repo(f"{repo.full_name}")
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

def scrape_careerjet(job_title, location):
    job_listings = []
    base_url = "https://www.careerjet.de/stellenangebote"

    for page in range(1):
        params = {
            's': job_title,
            'l': location,
            'nw': 7,
            'p': page + 1
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'de-DE,de;q=0.9,en-US,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'https://www.careerjet.com/'
        }

        response = requests.get(base_url, params=params, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        for job_card in soup.find_all('article', class_='job'):
            try:
                job_title = job_card.find('header').text.strip()
            except AttributeError:
                job_title = None
            try:
                company = job_card.find('p', class_='company').text.strip()
            except AttributeError:
                company = None
            try:
                location = job_card.find('ul', class_='location').text.strip()
            except AttributeError:
                location = None
            try:
                jd = job_card.find('div', class_='desc').text.strip()
            except AttributeError:
                jd = None

            job_listings.append({
                'Job Title': job_title,
                'Company': company,
                'Location': location,
                'Job Description': jd,
            })

    return pd.DataFrame(job_listings).to_html(index=False)


function_lookup = {
    "tavily_search": tavily_search,
    "get_moodle_course_content": get_moodle_course_content,
    "get_users_enrolled_courses": get_users_enrolled_courses,
    "get_all_repo_name": get_all_repo_name,
    "get_content_given_repo": get_content_given_repo,
    "get_content_url": get_content_url,
    "query_chromadb": query_chromadb,
    "get_content_all_repos": get_content_all_repos,
    #"scrape_careerjet": scrape_careerjet
}



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

