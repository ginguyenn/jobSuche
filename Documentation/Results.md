# Results

### 1. Upload CV as a PDF file**

#### Before uploading CV
We need to upload a PDF file to start the chat

<img alt="1.png" src="screenshot/1-UploadFile.png"/>

#### After uploading file
A message confirms that the PDF file has been uploaded. In the following screenshot

<img alt="2.png" src="screenshot/2-FileAsk.png"/>

### 2. Read PDF file/Extract details from CV

#### Extract all infos in PDF File
<img alt="3.png" src="screenshot/3.0-ExtractCV.png"/>

#### Extract details about my background
**- Option 1:** 
<img alt="3.1.png" src="screenshot/3.1-ExtractCV.png"/>

**- Option 2:** 
<img alt="3.2.png" src="screenshot/3.2-ExtractCV.png"/>

### 3. GitHub Integration
By setting the GitHub Token as an environment variable, users can access their public repositories and retrieve content from any of their repositories.

#### List of all repository name
<img alt="3.1.png" src="screenshot/4.0-GitHubRepo.png"/>

#### Retrieve content of a given repo and ask about repo
<img alt="3.1.png" src="screenshot/4.1-GitHubRepo.png"/>

### 4. Moodle Courses
By setting the Moodle Token as an environment variable, users can retrieve name of their enrolled courses in Moodle
<img alt="4.png" src="screenshot/5-MoodleCourses.png"/>

### 5. Job Description Analysis
Based on your given URL, JobMate can analyze the job description and give advice for your skill development

#### Extract content of the job description from a given URL
<img alt="5.png" src="screenshot/6.0-JobDesc.png"/>

#### Evaluate your skills based on the job description
<img alt="5.1.png" src="screenshot/6.1-JobDesc.png"/>

#### Advice of JobMate for your skill development
<img alt="5.2.png" src="screenshot/6.2-SkillDev.png"/>

#### Advice for career orientation, but the AI's answer is not very right, maybe we need to give a specific context
<img alt="5.3.png" src="screenshot/6.3-CareerConsult.png"/>


### 6. Interview Preparation
Based on your uploaded resume and provided job description URL, 
JobMate will generate a list of potential interview questions

<img alt="6.png" src="screenshot/7-InterviewPrep.png"/>


# Insights

Overall, our AI is capable of performing all the desired functions, but there is significant room for future development.

Currently, the AI requires user requests to retrieve content from GitHub or Moodle 
before any queries can be made to ask about this content. It does not automatically access the content on its own.

The response time is somewhat slow. Based on my research, this can be improved using streaming. 
However, we face challenges implementing this within our current structure and OpenAI Assistant. 
Most available solutions demonstrate streaming on the frontend, whereas our setup involves a separate backend connected to the frontend through Chainlit and FastAPI. 
This disparity also complicates handling file attachments in messages, as locating the file path becomes problematic.

Additionally, due to the token limit that OpenAI can process, our AI occasionally encounters an "Internal Server Error" message. 
For example, our functions such as "get_moodle_course_content" and "scrape_careerjet" face this error, although it can still run alone.