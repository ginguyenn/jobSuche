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
            }
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
            }
        },
    },

    {
        "type": "function",
        "function": {
            "name": "get_users_enrolled_courses",
            "description": "Get all enrolled courses of the actual user",
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
                        "description": "The ID of a moodle.py course, e.g. 36301",
                    },
                },
                "required": ["courseid"],
            }
        }
    }

]