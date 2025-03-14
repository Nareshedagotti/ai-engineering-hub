import os
from dotenv import load_dotenv
import fitz  # PyMuPDF
from PIL import Image
import io
import google.generativeai as genai
from langchain.vectorstores import FAISS
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, insert, text
import torch
from langchain.embeddings import HuggingFaceEmbeddings

# Load environment variables
load_dotenv()

# Check for GPU availability
device = "cuda" if torch.cuda.is_available() else "cpu"

# Database Setup
engine = create_engine('sqlite:///cities.db')
metadata = MetaData()

city_stats_table = Table(
    'city_stats', metadata,
    Column('id', Integer, primary_key=True),
    Column('city_name', String(50)),
    Column('population', Integer),
    Column('state', String(50))
)

def initialize_database():
    metadata.create_all(engine)
    
    # Populate initial data
    with engine.begin() as connection:
        connection.execute(city_stats_table.delete())
        
        rows = [{"city_name": "New York City", "population": 8336000, "state": "New York"},
                {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
                {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
                {"city_name": "Houston", "population": 2303000, "state": "Texas"},
                {"city_name": "Miami", "population": 449514, "state": "Florida"},
                {"city_name": "Seattle", "population": 749256, "state": "Washington"}]
        
        for row in rows:
            connection.execute(insert(city_stats_table).values(**row))

# Path to the document folder
DOCUMENT_FOLDER = "documents"

# PDF files in the document folder
pdf_files = [os.path.join(DOCUMENT_FOLDER, pdf) for pdf in [
    "newyork.pdf",
    "losangel.pdf",
    "chicago.pdf",
    "huston.pdf",
    "miami.pdf",
    "seattle.pdf"
]]
pdf_data = {}

def process_pdfs(chunk_size=2000):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    documents = []
    
    for pdf_file in pdf_files:
        try:
            doc = fitz.open(pdf_file)
            text = ""
            images = []
            
            for page in doc:
                text += page.get_text()
                # Store images for preview
                pix = page.get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes()))
                images.append(img)
            
            # Chunking with overlap
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size//2)]
            pdf_data[pdf_file] = {"chunks": chunks, "images": images, "full_text": text}
            
            documents.extend(chunks)
            
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
    
    return FAISS.from_texts(documents, embeddings) if documents else None

# Configure Gemini API
def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMENI_API_KEY not found in .env file.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash-latest')

model = configure_gemini()

def generate_sql(question: str) -> str:
    prompt = f"""Convert this question to SQL query for the city_stats table:
    Question: {question}
    
    Table columns: city_name (text), population (integer), state (text)
    
    Return ONLY the SQL query without any formatting or explanations."""
    
    response = model.generate_content(prompt)
    return response.text.strip().replace("```sql", "").replace("```", "")

vector_db = process_pdfs()

def retrieve_context(question: str) -> str:
    if not vector_db:
        return ""
    docs = vector_db.similarity_search(question, k=3)
    return "\n\n".join([doc.page_content for doc in docs])

def execute_query(query: str):
    try:
        with engine.connect() as conn:
            # Wrap the query in SQLAlchemy's text() function
            executable_query = text(query)
            result = conn.execute(executable_query)
            return {"data": result.fetchall(), "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}

def synthesize_response(question: str, sql_result: dict, context: str) -> str:
    prompt = f"""Analyze and combine these information sources:
    
    User Question: {question}
    
    Database Results: {sql_result['data'] or 'No results found'}
    
    Contextual Information: {context}
    
    Error Information: {sql_result['error'] or 'No errors'}
    
    Provide a comprehensive answer using both numerical data and contextual information.
    Structure your response with clear sections and bullet points where appropriate."""
    
    response = model.generate_content(prompt)
    return response.text