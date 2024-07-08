# Results

### 1. Upload CV as a PDF file

#### Before uploading CV
We need to upload a PDF file to start the chat

<img alt="1.png" src="screenshot/1-UploadFile.png"/>

#### After uploading file
A message confirms that the PDF file has been uploaded. In the following screenshot, if you don't mention the CV is the uploaded file,
the AI can not process the PDF File
<img alt="2.png" src="screenshot/2-FileAsk.png"/>

### 2. Read PDF file/Extract details from CV + Optimization

#### Extract all infos in PDF File
<img alt="3.png" src="screenshot/3.0-ExtractCV.png"/>

#### Extract details about my background
**- Option 1:** 
<img alt="3.1.png" src="screenshot/3.1-ExtractCV.png"/>

**- Option 2:** 
<img alt="3.2.png" src="screenshot/3.2-ExtractCV.png"/>

#### Motivation Letter evaluate + optimize
The response sounds a little bit general, maybe we need to give it more context like prompt our request more detailed. 
<img alt="3.3.png" src="screenshot/3.3-OptimizeML.png"/>

### 3. GitHub Integration
By setting the GitHub Token as an environment variable, users can access their public repositories and retrieve content from any of their repositories.

#### List of all repository name
<img alt="3.1.png" src="screenshot/4.0-GitHubRepo.png"/>

#### Retrieve content of a given repo and ask about repo
<img alt="3.1.png" src="screenshot/4.1-GitHubRepo.png"/>

### 4. Moodle Courses
By setting the Moodle Token as an environment variable, users can retrieve name of their enrolled courses in Moodle

**Option 1**
<img alt="4.png" src="screenshot/5-MoodleCourses.png"/>

**Option 2**
<img alt="4.png" src="screenshot/5-MoodleCourses2.png"/>

### 5. Job Description Analysis
Based on your given URL, JobMate can analyze the job description and give advice for your skill development

#### Extract content of the job description from a given URL
<img alt="5.png" src="screenshot/6.0-JobDesc.png"/>

#### Evaluate your skills based on the job description
<img alt="5.1.png" src="screenshot/6.1-JobDesc.png"/>

#### Advice of JobMate for your skill development
<img alt="5.2.png" src="screenshot/6.2-SkillDev.png"/>

After uploading your CV file and telling AI about your enrolled Moodle course or GitHub repos,
you can request AI's advice for career orientation and AI will recommend you some suitable job positions based on your skills
#### Option 1: The AI's answer is not very right, maybe we need to give a specific context
<img alt="5.3.png" src="screenshot/6.3-CareerConsult.png"/>

#### Option 2: Better Answer based on request with more specific context
<img alt="5.4.png" src="screenshot/6.3-CareerConsult2.png"/>

### 6. Interview Preparation
Based on your uploaded resume and provided job description URL, 
JobMate will generate a list of potential interview questions

<img alt="6.png" src="screenshot/7-InterviewPrep.png"/>

### 7. Speech to Text Example
<img alt="7.png" src="screenshot/8-Audio.png"/>

# Insights

Overall, our AI is capable of performing all the desired functions, but there is significant room for future development.

Currently, the AI requires user requests to retrieve content from GitHub or Moodle before any queries can be made. It does not automatically access this content.

The response time is somewhat slow. Based on my research, this can be improved using streaming. However, we face challenges implementing this within our current structure and OpenAI Assistant. 
Most available solutions demonstrate streaming on the frontend, whereas our setup involves a separate backend connected to the frontend through Chainlit and FastAPI. 
This also complicates handling file attachments in messages, as locating the file path becomes problematic.

Additionally, due to the token limit that OpenAI can process, our AI occasionally encounters an "Internal Server Error" message. 
For example, functions such as `get_moodle_course_content` and `scrape_careerjet` face this error, although they can still run alone. 
We might address this by restructuring the return value in the methods to include only useful content and remove unnecessary information. 
We also tried saving all information related to enrolled courses in ChromaDB, but the query results were not concise, so we removed it. 
For the `scrape_careerjet` function, we faced similar issues: we could get job lists from the website but could not integrate them into our AI.

Moreover, we aimed to create different assistants for function callings based on user messages. 
However, implementing multiple assistants to process the same thread or runs proved difficult. 
Finally, we decided to implement all function callings in one assistant to ensure that our AI would work. 
This approach may lead to higher costs.

During our project, we switched between GPT-4 and GPT-3.5. The responses from GPT-4 were better and more logical, so we used it for our assistant. 
However, we used GPT-3.5 for implementing function callings to save costs and switched to GPT-4 after completing the code.

Despite the challenges, we have learned a lot from this project. 
In the future, we could explore implementing our AI models with other tools, such as open-source AI models, different databases, or alternative user interfaces instead of Chainlit. 
This project has been a valuable learning experience, and we are excited about the potential future improvements and innovations we can bring to our AI.