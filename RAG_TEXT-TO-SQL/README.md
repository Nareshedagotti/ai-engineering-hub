# RAG + Text-to-SQL 

This project demonstrates a **Retrieval-Augmented Generation (RAG)** combined with **Text-to-SQL** to answer user queries about city data (e.g., population, state). The system uses **Gemini** for SQL generation and **FAISS** for document retrieval from PDFs. The user can query the database and receive contextual answers generated from both the database and PDF documents.

## Features

- **Text-to-SQL** conversion using **Gemini** to generate SQL queries from user input.
- **RAG Model** for document context retrieval using **FAISS** from processed PDF files.
- Combines **database results** and **retrieved PDF context** to synthesize a final answer.
- Streamlit-based interactive chat UI.

## Requirements

- Python 3.7 or later
- Streamlit
- PyMuPDF (fitz)
- Pillow
- google-generativeai
- FAISS
- SQLAlchemy
- Torch
- HuggingFaceEmbeddings

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Nareshedagotti/ai-engineering-hub.git
cd ai-engineering-hub
```

### 2. Install the dependencies

Create a virtual environment and activate it:

```bash
# Create a virtual environment (Optional but recommended)
python -m venv venv
source venv\Scripts\activate 

# Install the required libraries
pip install -r requirements.txt
```

### 3. Set up environment variables

You need to set up the **GEMINI_API_KEY** for **Gemini**. Create a `.env` file in the root directory of the project and add your API key:

```
GEMINI_API_KEY="your_gemini_api_key"
```

If you don't have a **Gemini API key**, you can obtain one from the official Gemini API service.

### 4. Database Setup

This project uses **SQLite** for storing city data. Upon the first run, the application will automatically create and populate the database with some initial city data. The cities included are:

- New York City
- Los Angeles
- Chicago
- Houston
- Miami
- Seattle

### 5. Running the App

To run the app, use the following command:

```bash
streamlit run app.py
```

### 6. Chat Interface

- Ask questions about the city data.
- The system will retrieve the relevant context from PDF documents using **FAISS**, convert the question into an **SQL query** using **Gemini**, and return a comprehensive answer combining both the database results and retrieved PDF context.

## File Structure

```
.
├── app.py                   # Main Streamlit app file
├── .env                     # Environment variables (API keys)
├── requirements.txt         # Python dependencies
├── utils.py                 # Helper functions for database, PDFs, and Gemini
└── documents/               # Folder containing PDF files for context retrieval
    ├── newyork.pdf
    ├── losangel.pdf
    ├── chicago.pdf
    ├── huston.pdf
    ├── miami.pdf
    └── seattle.pdf
```

## Tech Stack

- **Gemini API**: For generating SQL queries from natural language.
- **FAISS**: For retrieving relevant document context.
- **SQLAlchemy**: For executing SQL queries.
- **Streamlit**: For the interactive front-end UI.
- **PyMuPDF**: For processing and extracting text from PDF files.
- **Torch**: For checking GPU availability and other computations.

## Notes

- Ensure that your `.env` file is correctly configured with the **GEMINI_API_KEY** to interact with the **Gemini API**.
- The app works by first processing PDFs into embeddings and then retrieving context for user queries via FAISS. The system generates SQL queries using **Gemini** and executes them on an SQLite database to provide the user with answers.

