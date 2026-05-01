# AI-Driven Student Management System (Student Agent)

An intelligent, API-first Student Management System built with **FastAPI** and **PostgreSQL**, integrated with a powerful AI Agent using **LangGraph** and the **Model Context Protocol (MCP)**. This system not only provides standard CRUD operations for university management but also features an advanced agentic interface (Text-to-SQL capabilities) to query and interact with academic data naturally.

## 🚀 Features

* **Comprehensive Academic Management:** * Manage Students (`sinh_vien`), Lecturers (`giang_vien`), Faculties (`khoa`), and Majors (`nganh`).
    * Handle Courses (`mon_hoc`), Classes (`lop_hoc`), and Course Registrations (`dang_ky_mon`).
    * Track Academic Records and Grades (`fact_diem`).
* **Agentic AI Integration (LangGraph & MCP):**
    * Embedded AI agent capable of translating natural language queries into SQL (Text-to-SQL).
    * Utilizes LangGraph for complex reasoning and workflow orchestration.
    * Model Context Protocol (MCP) server integration for standardized tool usage.
* **Robust Security:** Built-in authentication and authorization (`auth_service`).
* **Data Processing:** Bulk import features (`import_router`) and automated ID generation.

## 🛠️ Tech Stack

* **Backend Framework:** FastAPI (Python 3.10+)
* **Database:** PostgreSQL (with SQLAlchemy ORM)
* **AI & LLM Frameworks:** LangChain, LangGraph
* **Protocol:** Model Context Protocol (MCP)

## 📂 Project Structure

```text
student_agent/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database connection & session management
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic models for validation
│   ├── routers/                # API Endpoints (auth, students, grades, ai_agent, etc.)
│   ├── services/               # Business logic, Agent tools, and MCP services
│   ├── repositories/           # Data access layer (CRUD operations)
│   └── prompts/                # System prompts for the AI agent
├── mcp_server/                 # Standalone MCP Server implementation
├── requirements.txt            # Python dependencies
├── create_admin.py             # Script to initialize admin user
├── create_users.py             # Script to seed initial users
└── test_connection.py          # Database and API connection testing utility

⚙️ Installation & Setup
Clone the repository:

Bash
git clone <your-repository-url>
cd student_agent
Create and activate a virtual environment:

Bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
Install dependencies:

Bash
pip install -r requirements.txt
Configure Environment Variables:
Create a .env file in the root directory and add your configurations (e.g., Database URL, LLM API Keys):

Đoạn mã
DATABASE_URL=postgresql://user:password@localhost:5432/student_db
OPENAI_API_KEY=your_api_key_here # Or your preferred LLM provider
Initialize the Database:
Run the setup scripts to create tables and seed initial admin/user accounts:

Bash
python create_admin.py
python create_users.py
🏃‍♂️ Running the Application
1. Start the FastAPI Web Server:

Bash
uvicorn app.main:app --reload
The API documentation (Swagger UI) will be available at: http://localhost:8000/docs

2. Start the MCP Server (Optional/If run separately):

Bash
python mcp_server/server.py
