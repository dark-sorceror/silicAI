from pathlib import Path
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

PDF_PATH = Path("../media/RM-MPU-9250A-00-v1.6.pdf")

loader = PyPDFLoader(PDF_PATH)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000, 
    chunk_overlap = 200
)
splits = text_splitter.split_documents(docs)

# https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
embedding_function = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")

vectorstore = Chroma.from_documents(
    documents = splits, 
    embedding = embedding_function
)
retriever = vectorstore.as_retriever()

llm = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash",
    temperature = 0,
)

def gemini_chat(query: str) -> None:
    relevant_docs = retriever.invoke(query)

    context_text = ""
    sources = set()
    
    for d in relevant_docs:
        context_text += d.page_content + "\n\n"
        sources.add(d.metadata['page'] + 1)

    system_prompt = f"""
    You are an expert embedded software engineer assistant.
    Use the provided datasheet context to answer the user's question accurately.
    If the answer is found in a table, format it clearly.
    If you don't know, say "I can't find that in the document."

    Context:
    {context_text}
    """

    full_prompt = f"{system_prompt}\n\nQuestion: {query}"
    
    response = llm.invoke(full_prompt).content
    
    return [response, sources]