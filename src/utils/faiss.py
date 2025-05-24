from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_retriever():
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
    
    db = FAISS.load_local(
        "src/utils/vector", 
        embeddings=embedding,
        allow_dangerous_deserialization=True
    )
    
    return db.as_retriever(search_kwargs={"k":2})

def retrieve_top_k_documents(textbook_text: str):
    retriever = get_retriever()
    docs = retriever.get_relevant_documents(textbook_text)
    
    return [doc.page_content for doc in docs]