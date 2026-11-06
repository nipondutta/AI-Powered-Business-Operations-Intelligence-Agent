# AI-Powered Business Operations & Intelligence Agent

An AI-powered business intelligence platform that helps e-commerce businesses make data-driven decisions by combining **Retrieval-Augmented Generation (RAG), Natural Language to SQL, Customer Feedback Analysis, and AI Agents** in one application.

The platform allows business users to ask questions about sales, products, customers, company policies, and customer complaints using natural language instead of manually exploring spreadsheets, databases, and documents.

Built with a local-first architecture using **FastAPI, LangGraph, Ollama, FAISS, BM25, Sentence Transformers, SQLite, and Streamlit**.

---

## 1. Business Problem

E-commerce businesses generate large amounts of information across multiple sources:

- Sales and order databases
- Product and customer records
- Customer support tickets
- Customer feedback and reviews
- Business policies and internal documentation

However, extracting useful insights from these sources often requires SQL knowledge, manual spreadsheet analysis, and searching through multiple documents.

This creates several challenges:

- Business teams spend time manually preparing reports.
- Non-technical employees struggle to retrieve database insights.
- Customer complaints are difficult to categorize at scale.
- Important business policies are scattered across documents.
- Decision-makers lack a unified interface for accessing business information.

### Our Solution

This project provides an AI-powered business assistant that connects structured and unstructured business data.

Users can ask questions in natural language, and the system intelligently routes each request to the appropriate capability:

| Business Requirement | Implemented Capability |
|---|---|
| Understand sales performance | Natural Language to SQL |
| Search business policies | Hybrid RAG |
| Analyze customer complaints | Customer Intelligence |
| Identify customer sentiment | Sentiment and feedback analysis |
| Route complex questions | LangGraph Agent |
| Access insights through an API | FastAPI |
| Interact through a dashboard | Streamlit |

---

## 2. Key Features

### 2.1 Natural Language to SQL

Ask business questions in plain English and retrieve insights from the business database.

**Example questions:**
- What is the total revenue this month?
- Which products generate the highest revenue?
- What are the top five selling products?
- Which customers have placed the most orders?
- What is the average order value?

**Implementation:**
- LLM-powered SQL generation
- SQLite database
- SQL query validation
- Read-only query execution
- Restricted SQL operations

The application validates generated queries before execution to reduce the risk of unsafe database operations.

### 2.2 Hybrid Retrieval-Augmented Generation (RAG)

Retrieve relevant information from business documents using a combination of keyword-based and semantic search.

**Supported document types:**
- PDF
- TXT
- Markdown
- CSV and Excel data through the structured-data workflow, where supported by the ingestion implementation

**Retrieval architecture:**

1. Load business documents.
2. Split documents into smaller chunks.
3. Generate embeddings using Sentence Transformers.
4. Store and retrieve dense vectors using FAISS.
5. Retrieve keyword matches using BM25.
6. Combine retrieval results.
7. Send relevant context to the local LLM.
8. Generate a grounded response.

**Example questions:**
- What is the company's return policy?
- How long does a customer have to return a product?
- What should the support team do when an order is delayed?
- What is the refund procedure?

### 2.3 Customer Intelligence

Analyze customer support tickets and feedback to identify common problems and customer satisfaction trends.

**Capabilities:**
- Sentiment classification
- Complaint categorization
- Identification of recurring issues
- Customer feedback summaries
- Business improvement suggestions

**Example questions:**
- What are the most common customer complaints?
- Why are customers requesting refunds?
- Which product-related issues appear frequently?
- Summarize negative customer feedback.

### 2.4 AI Agent with LangGraph

The application uses an agent workflow to determine which business capability should handle a user's question.

**Available workflows:**

- SQL Analytics Agent
- Business Knowledge Retrieval Agent
- Customer Intelligence Agent

The workflow selects an appropriate tool based on the user's query and returns the result through a unified interface.

### 2.5 Interactive Dashboard

The Streamlit interface provides a simple way to interact with the business intelligence platform.

Users can:
- Ask business questions.
- Retrieve business knowledge.
- Explore analytics.
- Analyze customer feedback.

---

## 3. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3.12 |
| Backend | FastAPI |
| Frontend | Streamlit |
| Agent Framework | LangGraph |
| LLM Runtime | Ollama |
| Language Model | Llama 3.2 |
| Embedding Model | all-MiniLM-L6-v2 |
| Vector Database | FAISS |
| Keyword Retrieval | BM25 |
| Database | SQLite |
| Data Processing | Pandas |
| Testing | Pytest |
| Code Quality | Ruff |
| Containerization | Docker |
| CI/CD | GitHub Actions |

---

## 4. System Architecture

```text
                   BUSINESS USER
                         |
                         v
                 STREAMLIT FRONTEND
                         |
                         v
                    FASTAPI
                         |
                         v
                 LANGGRAPH AGENT
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
         SQL Agent    RAG Agent   Customer
                                  Intelligence
             |           |           |
             v           v           v
          SQLite     FAISS +       Feedback
                     BM25           Analysis
             |           |           |
             +-----------+-----------+
                         |
                         v
                    OLLAMA LLM
                         |
                         v
                 BUSINESS INSIGHTS
```

---

## 5. Project Structure

```text
business-intelligence-ai/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── llm.py
│   ├── schemas.py
│   ├── main.py
│   ├── agent.py
│   ├── sql_analytics.py
│   ├── rag.py
│   ├── ingestion.py
│   └── customer_intelligence.py
│
├── frontend/
│   └── app.py
│
├── scripts/
│   ├── generate_sample_data.py
│   └── load_sample_data.py
│
├── sample_documents/
│   ├── return_policy.txt
│   └── customer_support_playbook.md
│
├── tests/
│   ├── test_sql_safety.py
│   └── test_rag_split.py
│
├── data/
│   └── .gitkeep
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 6. Installation and Setup

### Prerequisites

Install the following:

- Python 3.12
- Git
- Ollama
- VS Code (recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/business-intelligence-ai.git

cd business-intelligence-ai
```

Replace `YOUR_USERNAME` with your GitHub username.

### Step 2: Create a Virtual Environment

**Windows:**

```bash
python -m venv .venv

.venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv .venv

source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
python -m pip install --upgrade pip

pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Copy the example environment file:

**Windows:**

```bash
copy .env.example .env
```

**Linux/macOS:**

```bash
cp .env.example .env
```

Review `.env` and configure the values required by the application.

### Step 5: Install and Start Ollama

Download Ollama:

https://ollama.com/

Pull the recommended model:

```bash
ollama pull llama3.2:3b
```

Start the Ollama service:

```bash
ollama serve
```

If Ollama is already running in the background, you do not need to start it again.

### Step 6: Generate Sample Business Data

```bash
python scripts/generate_sample_data.py
```

### Step 7: Load Sample Data

```bash
python scripts/load_sample_data.py
```

This prepares the sample e-commerce database for analytics.

### Step 8: Start the FastAPI Backend

```bash
uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Step 9: Start the Streamlit Frontend

Open another terminal, activate the virtual environment, and execute:

```bash
streamlit run frontend/app.py
```

The dashboard will be available at:

```text
http://localhost:8501
```

---

## 7. Example Business Questions

Try these questions after setting up the application.

### Sales Analytics

```text
What is the total revenue generated by the business?
```

```text
Which five products generate the highest revenue?
```

```text
What is the average order value?
```

### Business Knowledge

```text
What is the company's return policy?
```

```text
How should the support team handle delayed orders?
```

### Customer Intelligence

```text
What are the most common customer complaints?
```

```text
Summarize the negative customer feedback.
```

```text
What improvements should the business prioritize?
```

The exact supported questions depend on the database schema, sample data, and implemented agent workflows.

---

## 8. API Endpoints

The FastAPI application provides the backend interface.

Explore the available endpoints through:

```text
http://127.0.0.1:8000/docs
```

The API is designed to expose business analytics, document ingestion, and agent interactions.

Refer to the actual FastAPI route definitions in `app/main.py` for the current endpoint names and request formats.

---

## 9. Testing

Run the test suite:

```bash
pytest -v
```

Run code-quality checks:

```bash
ruff check .
```

These checks help identify SQL safety issues, document-processing problems, and code-quality issues.

---

## 10. Docker Setup

Build and run the application using Docker Compose:

```bash
docker compose up --build
```

Stop the containers:

```bash
docker compose down
```

**Note:** Ollama must be accessible from the application container. Configure the Ollama host appropriately for your operating system and Docker environment.

---

## 11. Security and Reliability Considerations

The project incorporates several important engineering practices:

- Restricting SQL execution to read-only operations.
- Validating generated SQL before execution.
- Keeping environment-specific configuration outside source code.
- Using a modular backend architecture.
- Testing important application components.
- Running the language model locally to avoid sending business data to an external LLM provider by default.

This is a learning and portfolio project, not a production-certified system. Production deployment would require additional authentication, authorization, rate limiting, audit logging, robust query controls, monitoring, and data governance.

---

## 12. Future Improvements

Potential enhancements include:

- PostgreSQL support for larger business datasets.
- Advanced hybrid retrieval with Reciprocal Rank Fusion (RRF).
- Cross-encoder reranking.
- More robust document ingestion and incremental indexing.
- LangGraph state persistence and human-in-the-loop approval.
- Advanced customer segmentation.
- Sales forecasting using machine learning.
- Churn prediction.
- Automated business report generation.
- Evaluation using retrieval metrics and answer-quality datasets.
- Observability and tracing for agent workflows.
- Authentication and role-based access control.
- Cloud deployment.

---

## 13. What I Learned

Through this project, I aim to demonstrate practical experience in:

- Building production-style REST APIs using FastAPI.
- Implementing Retrieval-Augmented Generation systems.
- Combining BM25 and dense vector retrieval.
- Working with FAISS and Sentence Transformers.
- Building AI workflows using LangGraph.
- Connecting LLMs with structured SQL databases.
- Designing safer Text-to-SQL execution.
- Processing and analyzing customer feedback.
- Building interactive applications with Streamlit.
- Writing automated tests with Pytest.
- Containerizing applications using Docker.
- Implementing CI workflows using GitHub Actions.

---

**AI-Powered Business Operations & Intelligence Agent | Python, FastAPI, LangGraph, RAG, FAISS, BM25, Ollama, SQL**

- Developed an AI-powered business intelligence assistant integrating hybrid RAG, natural-language SQL analytics, and customer feedback intelligence to simplify business decision-making.
- Implemented hybrid retrieval using BM25 and FAISS with Sentence Transformers to retrieve relevant information from unstructured business documents.
- Built an LLM-powered Text-to-SQL workflow with query validation and read-only execution to enable natural-language access to business data.
- Designed agent workflows using LangGraph to route user queries across analytics, knowledge retrieval, and customer intelligence capabilities.
- Developed REST APIs using FastAPI and an interactive Streamlit interface, with automated tests and Docker-based deployment support.

*Keep these bullets aligned with the features you have actually implemented and tested before adding the project to your CV.*

---

## 14. Author

**Nipon Kumar Dutta**

---

## License

This project is intended for educational and portfolio purposes. Add a license file if you plan to distribute or reuse the project under specific terms.