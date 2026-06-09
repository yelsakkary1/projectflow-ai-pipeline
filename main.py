import os
import os.path
import base64
import re
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai_tools import TavilySearchTool

# Gmail authentication and draft creation
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def create_draft(service, to, subject, body):
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft = service.users().drafts().create(userId='me', body={'message': {'raw': raw}}).execute()
    print(f"Draft created for {to}: {subject}")
    return draft

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = "sk-placeholder"

# Initialize Claude as the LLM
claude = LLM(
    model="anthropic/claude-sonnet-4-6",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Initialize Tavily search tool
search_tool = TavilySearchTool()

# Agent 1 - Researcher
researcher = Agent(
    role="Tech Industry Researcher",
    goal="Find mid-size tech companies struggling with project management, missed deadlines, failed product launches, or rapid team growth",
    backstory="""You are an expert tech industry researcher. 
    You know how to find companies that are publicly signaling project 
    management pain through news, job postings, Glassdoor reviews, 
    LinkedIn posts, and press releases.""",
    tools=[search_tool],
    llm=claude,
    verbose=True
)

research_task = Task(
    description="""Search for mid-size tech companies (50-1000 employees) in the US 
    that are dealing with project management challenges such as missed deadlines, 
    failed product launches, rapid team growth, or remote team coordination issues.
    Look for recent news, job postings, Glassdoor reviews, and press coverage.
    Return a list of at least 5 companies with a brief note on why each is a good lead.""",
    expected_output="A list of 5 tech companies with company name, location, size, and reason they are a good lead",
    agent=researcher
)

# Agent 2 - Lead Finder
lead_finder = Agent(
    role="Tech Company Lead Finder",
    goal="Find the right decision-maker contacts at each tech company identified by the researcher",
    backstory="""You are an expert at finding the right people to contact 
    at tech companies. You know how to identify CTOs, VPs of Engineering, 
    Heads of Product, Directors of Operations, and CEOs at mid-size tech 
    companies using public information and web searches.""",
    tools=[search_tool],
    llm=claude,
    verbose=True
)

lead_task = Task(
    description="""Using ONLY the specific companies identified by the researcher in the previous task,
    do not search for new companies. For each company already identified, find:
    - Full name and title of the CEO or Chief Executive Officer
    - Full name and title of the CTO or Chief Technology Officer
    - Full name and title of the VP of Engineering
    - Full name and title of the Head of Product or CPO
    - Full name and title of the Director of Operations
    - LinkedIn URL or professional email if publicly available""",
    expected_output="A list of contacts for each company from the researcher's list",
    agent=lead_finder,
    context=[research_task]
)

# Agent 3 - Copywriter
copywriter = Agent(
    role="B2B SaaS Copywriter",
    goal="Write personalized outreach emails to tech company decision-makers that speak directly to their project management pain",
    backstory="""You are an expert B2B SaaS copywriter. 
    You know how to write concise, personalized cold emails that resonate with 
    tech executives. You reference specific pain points unique to each company 
    and position ProjectFlow as directly relevant to their situation. 
    You never sound generic or salesy.""",
    tools=[],
    llm=claude,
    verbose=True
)

copy_task = Task(
    description="""Using ONLY the companies from the researcher and ONLY the contacts 
    from the lead finder, write personalized cold outreach emails.
    
    Do not invent new companies or contacts. Use exactly what was provided by the 
    previous two agents.
    
    For each company and its contacts write an email that:
    - Has a compelling subject line
    - Opens by referencing a specific pain point or news item about THAT company
    - Briefly introduces ProjectFlow: a project management platform that gives 
      engineering and product teams real-time visibility into sprint progress, 
      resource allocation, and delivery timelines
    - Includes a soft call to action (15 minute call)
    - Is under 150 words
    - Sounds human, not robotic or salesy""",
    expected_output="Personalized emails for each company using only the companies and contacts identified by the previous agents, organized by company name and contact",
    agent=copywriter,
    context=[research_task, lead_task]
)

# Agent 4 - Gmail Drafter
gmail_drafter = Agent(
    role="Gmail Draft Creator",
    goal="Take the personalized emails written by the copywriter and create Gmail drafts for each one",
    backstory="""You are an expert at organizing and preparing email outreach. 
    You take finalized email copy and prepare it for sending by creating 
    Gmail drafts. You are precise and ensure every email is correctly 
    formatted with the right recipient, subject line, and body.""",
    tools=[],
    llm=claude,
    verbose=True
)

gmail_task = Task(
    description="""Take the emails written by the copywriter and create Gmail drafts.
    For each email extract:
    - The recipient contact name and email address
    - The subject line
    - The email body
    
    Then format them ready for Gmail draft creation.
    Return a structured list of all emails with recipient, subject, and body clearly separated.""",
    expected_output="A structured list of emails with recipient, subject line, and body clearly labeled for each contact",
    agent=gmail_drafter,
    context=[copy_task]
)

crew = Crew(
    agents=[researcher, lead_finder, copywriter, gmail_drafter],
    tasks=[research_task, lead_task, copy_task, gmail_task],
    verbose=True
)

result = crew.kickoff()

# Save agent outputs to files
try:
    with open("research_output.txt", "w") as f:
        f.write(research_task.output.raw)
    print("Research output saved")
except Exception as e:
    print(f"Could not save research output: {e}")

try:
    with open("leads_output.txt", "w") as f:
        f.write(lead_task.output.raw)
    print("Leads output saved")
except Exception as e:
    print(f"Could not save leads output: {e}")

try:
    with open("emails_output.txt", "w") as f:
        f.write(copy_task.output.raw)
    print("Emails output saved")
except Exception as e:
    print(f"Could not save emails output: {e}")

try:
    with open("gmail_output.txt", "w") as f:
        f.write(gmail_task.output.raw)
    print("Gmail output saved")
except Exception as e:
    print(f"Could not save gmail output: {e}")

# Create Gmail drafts
gmail_service = get_gmail_service()

email_blocks = re.split(r'---\s*\n## EMAIL \d+', gmail_task.output.raw)

drafts_created = 0
for block in email_blocks:
    try:
        subject_match = re.search(r'\*\*Subject Line:\*\*\s*(.+)', block)
        body_match = re.search(r'\*\*Email Body:\*\*\s*\n(.*?)(?=---|\Z)', block, re.DOTALL)
        email_match = re.search(r'\*\*Email Address:\*\*\s*(.+)', block)

        if subject_match and body_match and email_match:
            subject = subject_match.group(1).strip()
            body = body_match.group(1).strip()
            to = email_match.group(1).strip()

            create_draft(gmail_service, to, subject, body)
            drafts_created += 1
    except Exception as e:
        print(f"Could not create draft: {e}")

print(f"\n{drafts_created} Gmail drafts created successfully")

print("\n\n=== FINAL RESULT ===")
print(result)