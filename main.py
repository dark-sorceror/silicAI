import os
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

PDF_PATH = "RM-MPU-9250A-00-v1.6.pdf"
MODEL_NAME = "phi3"

print(f"Loading {PDF_PATH}...")

loader = PyPDFLoader(PDF_PATH)
docs = loader.load()
print(f"Loaded {len(docs)} pages.")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000, 
    chunk_overlap = 200
)
splits = text_splitter.split_documents(docs)

print(len(splits))

# https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
embedding_function = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")

vectorstore = Chroma.from_documents(
    documents = splits, 
    embedding = embedding_function
)
retriever = vectorstore.as_retriever()

llm = ChatOllama(model = MODEL_NAME, temperature = 0)

while True:
    query = input("\nAsk a question about the datasheet: ")
    
    if query.lower() == "exit":
        break

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

    for chunk in llm.stream(full_prompt):
        print(chunk.content, end = "", flush = True)
        
    print(f"\n\n[Sources: Pages {', '.join(map(str, sources))}]")