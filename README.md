# 🤖 ProjectFlow AI Pipeline

An autonomous 4-agent AI pipeline that handles B2B outbound sales end to end — from company research to personalized emails landing directly in Gmail drafts.

Built as a personal project to understand how agentic AI systems work under the hood.

---

## 🧠 How It Works

Four AI agents work sequentially, each passing context to the next:

| Agent | Role | Tools |
|-------|------|-------|
| Agent 1 — Researcher | Finds mid-size tech companies showing project management pain signals | Tavily Search |
| Agent 2 — Lead Finder | Identifies decision-maker contacts at each company | Tavily Search |
| Agent 3 — Copywriter | Writes personalized cold emails for each contact | Claude (reasoning) |
| Agent 4 — Gmail Drafter | Structures emails and pushes them to Gmail drafts | Gmail API |

---

## 🛠️ Tech Stack

- **[CrewAI](https://crewai.com)** — Agentic AI framework for orchestrating multi-agent pipelines
- **[Claude Sonnet (Anthropic)](https://anthropic.com)** — LLM powering all 4 agents
- **[Tavily](https://tavily.com)** — Real-time web search API built for AI agents
- **[Gmail API](https://developers.google.com/gmail/api)** — OAuth2 integration for creating Gmail drafts
- **Python** — Core language

---

## 📁 Project Structure

projectflow-ai-pipeline/
├── main.py                        # Main pipeline — all 4 agents
├── create_drafts.py               # Standalone Gmail draft creation
├── projectflow_pipeline.ipynb     # Jupyter notebook walkthrough
└── .gitignore                     # Excludes API keys and credentials

---

## ⚙️ Setup

**1. Clone the repo**
```bash
git clone https://github.com/yelsakkary1/projectflow-ai-pipeline.git
cd projectflow-ai-pipeline
```

**2. Create a virtual environment**
```bash
python3.13 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install crewai crewai-tools tavily-python anthropic google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv jupyter
```

**4. Add your API keys**

Create a `.env` file in the project root:

ANTHROPIC_API_KEY=your_anthropic_key_here
TAVILY_API_KEY=your_tavily_key_here

**5. Set up Gmail API**
- Go to [Google Cloud Console](https://console.cloud.google.com)
- Create a new project and enable the Gmail API
- Create OAuth 2.0 credentials (Desktop app)
- Download as `credentials.json` and place in the project root

**6. Run the pipeline**
```bash
python3 main.py
```

The first run will open a browser window to authorize Gmail access.

---

## 📤 Output

Each agent's output is saved to a local file:

- `research_output.txt` — Target companies with pain signals
- `leads_output.txt` — Decision-maker contacts
- `emails_output.txt` — Personalized email copy
- `gmail_output.txt` — Structured drafts ready for Gmail

Run `create_drafts.py` separately to push emails to Gmail without rerunning all agents.

---

## ⚠️ Important Notes

- Email addresses are formatted using standard conventions and should be verified with [Hunter.io](https://hunter.io) or [Apollo.io](https://apollo.io) before sending
- Never commit your `.env`, `credentials.json`, or `token.json` files
- This pipeline is industry-specific — swap Agent 1's keywords, Agent 2's target titles, and Agent 3's product description to target any market.

---

## 🗺️ Roadmap

- [ ] Hunter.io integration for email verification
- [ ] CSV export of leads and emails
- [ ] Inbox monitor agent (Agent 5) for reply classification
- [ ] Calendly integration for automated meeting scheduling

---

*Built with CrewAI · Claude Sonnet · Tavily · Gmail API*