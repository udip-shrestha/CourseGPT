# This script creates a Chroma vector database from the PDF file.
# Run this once to build the database.
# Requirements: pip install langchain langchain-community chromadb pypdf sentence-transformers langchain-huggingface torch

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Path to your PDF file
pdf_path = "/Users/prakarsha/Desktop/courseGPT/sdmay26-37/Backend/Data/Backend_Knowledge.pdf"

# Load the PDF
loader = PyPDFLoader(pdf_path)
documents = loader.load()

# Split the documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = text_splitter.split_documents(documents)

# Use HuggingFace embeddings (compatible with macOS ARM64 via PyTorch)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Create and persist the Chroma database in the "Data" folder
persist_directory = "./Data/chroma_db"
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory=persist_directory
)

print(f"Database created and saved to {persist_directory}")