\# 🤖 AI Email Automation Agent



An AI-powered email automation system built with Python that can fetch emails, analyze them with Gemini, classify intent and priority, retrieve relevant company policies using RAG, generate reply drafts, and manage human-approved responses.



\## 🚀 Features



\- 📧 Gmail API integration with OAuth2

\- 🤖 AI-powered email classification using Google Gemini

\- 🏷️ Automatic category detection

\- 🚨 Priority detection: LOW, MEDIUM, HIGH, URGENT

\- 📝 Email summaries and intent extraction

\- 💬 AI-generated reply drafts

\- 👤 Human approval before sending replies

\- 📚 RAG-based knowledge retrieval

\- 📎 Attachment handling

\- 📄 PDF text extraction

\- 🔁 Follow-up tracking

\- 🛡️ Duplicate email protection

\- 🛡️ Duplicate reply-send protection

\- 🔄 Retry handling for temporary AI/API failures

\- 📊 Streamlit dashboard

\- 🗃️ SQLite database

\- 🧪 Automated pytest test suite

\- 📝 Rotating application logs



\## 🏗️ Architecture


Incoming Email

&#x20;     ↓

&#x20;  Gmail API

&#x20;     ↓

&#x20;   Python

&#x20;     ↓

&#x20; AI Analysis

&#x20;     ↓

Category / Priority / Intent / Summary

&#x20;     ↓

&#x20;  RAG Search

&#x20;     ↓

Knowledge Base

&#x20;     ↓

&#x20; Reply Draft

&#x20;     ↓

Human Approval

&#x20;     ↓

&#x20;  Gmail Send

&#x20;     ↓

Follow-up Tracking

&#x20;     ↓

Database + Logs + Dashboard

````



\## 🧰 Tech Stack



\* Python

\* FastAPI

\* Pydantic

\* SQLAlchemy

\* SQLite

\* Gmail API

\* Google Gemini API

\* Scikit-learn

\* Streamlit

\* PyMuPDF

\* pandas

\* pytest

\* APScheduler



\## 📁 Project Structure


ai-email-automation/

│

├── app/

│   ├── ai/

│   │   ├── analyzer.py

│   │   ├── gemini\_client.py

│   │   ├── reply\_generator.py

│   │   └── schemas.py

│   │

│   ├── dashboard/

│   │   └── dashboard.py

│   │

│   ├── database/

│   │   ├── database.py

│   │   ├── init\_db.py

│   │   └── models.py

│   │

│   ├── gmail/

│   │   ├── auth.py

│   │   ├── client.py

│   │   ├── fetch\_emails.py

│   │   └── send\_email.py

│   │

│   ├── rag/

│   │   ├── knowledge\_base.json

│   │   └── retriever.py

│   │

│   ├── services/

│   │   ├── ai\_email\_service.py

│   │   ├── email\_pipeline.py

│   │   ├── email\_storage.py

│   │   ├── follow\_up\_service.py

│   │   ├── reply\_approval\_service.py

│   │   ├── reply\_draft\_service.py

│   │   ├── scheduler.py

│   │   └── send\_reply\_service.py

│   │

│   ├── core/

│   │   ├── config.py

│   │   └── logging.py

│   │

│   └── main.py

│

├── tests/

│   ├── test\_app.py

│   ├── test\_ai\_schemas.py

│   ├── test\_analyzer.py

│   ├── test\_integration.py

│   └── test\_retriever.py

│

├── .env.example

├── .gitignore

├── pytest.ini

├── requirements.txt

└── README.md

```



\## ⚙️ Setup



\### 1. Clone the repository



```bash

git clone https://github.com/heyitssuzain/ai-email-automation.git

cd ai-email-automation

```



\### 2. Create a virtual environment



Windows:



```powershell

python -m venv .venv

.venv\\Scripts\\Activate.ps1

```



\### 3. Install dependencies



```powershell

pip install -r requirements.txt

```



\### 4. Configure environment variables



Create a `.env` file:



```env

APP\_NAME=AI Email Automation Agent

APP\_ENV=development

DATABASE\_URL=sqlite:///./email\_agent.db

LOG\_LEVEL=INFO



GEMINI\_API\_KEY=your\_gemini\_api\_key

```



\### 5. Gmail OAuth



Place your Google OAuth desktop credentials in:


credentials.json

```



The application will generate:


token.json

```



These files are intentionally excluded from Git.



\## ▶️ Running the Application



\### Start FastAPI



```powershell

uvicorn app.main:app --reload

```



\### Start the dashboard



```powershell

python -m streamlit run app/dashboard/dashboard.py

```



\## 🧪 Testing



Run the complete automated test suite:



```powershell

python -m pytest -v

```



Current test suite:



20 tests passing

```



The suite covers:



\* API health/root endpoints

\* AI schema validation

\* JSON response cleaning

\* RAG retrieval

\* RAG scoring

\* Top-K filtering

\* AI + RAG integration flow



\## 🔐 Security



Sensitive credentials are intentionally excluded from version control.



Ignored files include:


.env

credentials.json

token.json

\*.key

\*.pem

```



Never commit API keys, OAuth credentials, access tokens, or refresh tokens.



\## 🧠 AI Workflow



The AI analyzes incoming emails and produces structured information:



Category

Priority

Intent

Summary

Requires Reply

```



Supported categories:



Customer Support

Sales

Complaint

Job Inquiry

Invoice

General

Spam

```



\## 📚 RAG Knowledge Base



The system uses a local knowledge base containing company policies such as:



\* Refund policy

\* Customer support information

\* Invoice information

\* Shipping policy

\* Complaint handling

\* Job inquiry information



Relevant documents are retrieved using TF-IDF and cosine similarity before generating grounded replies.



\## 🛡️ Reliability



The application includes:



\* Duplicate email detection

\* Duplicate reply-send protection

\* Retry handling for transient AI/API failures

\* Analysis attempt tracking

\* Follow-up tracking

\* Rotating application logs

\* Human approval before automated replies



\## 📊 Dashboard



The Streamlit dashboard provides visibility into:



\* Email statistics

\* AI analysis

\* Reply drafts

\* Follow-ups

\* Analytics

\* Gmail connection status

\* Gemini status

\* Scheduler status



\## 🎯 Project Goal



This project demonstrates how modern AI systems can be combined with traditional backend engineering to build a practical email automation workflow.



It focuses on:



\* AI integration

\* API integration

\* Backend development

\* Database design

\* RAG

\* Automation

\* Reliability

\* Security

\* Testing

\* Observability



\## 📌 Status



🚧 Portfolio project — actively developed.



Core email processing, AI analysis, RAG, reply generation, approval workflow, follow-ups, dashboard, logging, security, and automated testing are implemented.



````

````





