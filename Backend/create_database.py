from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
import shutil

# Path where ChromaDB will store the vector database
CHROMA_PATH = "chroma"

def main():
    store_data()

def store_data():
    # Load the document(s)
    document = load_document()
    # Split into smaller chunks
    chunks = split_text(document)
    # Save chunks as embeddings in ChromaDB
    save_to_chroma(chunks)

def load_document():
    """
    Load documents from the current folder.
    Here we load a single file 'BackendKnowledge.pdf'.
    """
    # loader = TextLoader("alice_in_wonderland.md")
    loader = PyPDFLoader("/Users/prakarsha/Desktop/courseGPT/Backend_Knowledge.pdf")
    my_document = loader.load()
    return my_document

def split_text(documents: list[Document]):
    """
    Split documents into smaller chunks with overlap
    for better embedding + retrieval.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,   # each chunk is ~1000 characters
        chunk_overlap=500, # overlap between chunks
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} document(s) into {len(chunks)} chunks.")

    # Print a sample chunk to verify
    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks

def save_to_chroma(chunks: list[Document]):
    """
    Save the text chunks into ChromaDB using Hugging Face embeddings.
    This runs locally, no API key required.
    """
    # Clear out old database if it exists
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Initialize local embeddings model: hugging face api is the free trained AI model
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Store chunks in Chroma vector DB
    db = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_PATH)
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

if __name__ == "__main__":
    main()
