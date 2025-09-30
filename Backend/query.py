import argparse
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings  # Updated embeddings import
from langchain_community.llms import HuggingFacePipeline  # Updated LLM import
from langchain.chains import RetrievalQA
from transformers import pipeline, GPT2Tokenizer, GPT2LMHeadModel

# Path to your Chroma database
CHROMA_PATH = "chroma"

# Prompt template to give context to the LLM
PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Question: {question}
Answer:
"""

def main():
    # --- CLI setup ---
    parser = argparse.ArgumentParser(description="Query your PDF or documents via Chroma embeddings.")
    parser.add_argument("query_text", type=str, help="The question you want to ask.")
    args = parser.parse_args()
    query_text = args.query_text

    # --- Load embeddings and Chroma DB ---
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # free, fast embeddings
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # --- Create HuggingFace LLM pipeline ---
    hf_pipeline = pipeline(
        "text-generation",
        model="gpt2", #much smaller model(faster), "tiiuae/falcon-7b-instruct" (larger model) or any HuggingFace model you want
        device=-1,  # Force CPU to avoid MPS/BFloat16 issues
        tokenizer=GPT2Tokenizer.from_pretrained("gpt2"),  # ensure proper tokenizer
        max_new_tokens=150,  # controls output length safely, prevent index out of range / too long sequences
    )
    llm = HuggingFacePipeline(pipeline=hf_pipeline)

    # --- Create Retrieval QA chain ---
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=db.as_retriever(search_kwargs={"k": 3}),  # top 3 docs
        return_source_documents=True
    )

    # --- Run query ---
    result = qa_chain.invoke({"query": query_text})

    answer = result["result"]
    sources = [doc.metadata.get("source", "Unknown") for doc in result["source_documents"]]

    # --- Print nicely ---
    print(f"\nQuery: {query_text}\n")
    print("Answer:\n", answer, "\n")
    print("Sources:")
    for src in sources:
        print("-", src)

if __name__ == "__main__":
    main()
