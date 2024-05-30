import tiktoken
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone, FAISS
from langchain.embeddings import OpenAIEmbeddings
import pinecone
import os
from dotenv import load_dotenv

load_dotenv()

tokenizer = tiktoken.get_encoding("cl100k_base")


# create the length function
def tiktoken_len(text):
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)


loader = PyPDFDirectoryLoader("./docs")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=3000,
    chunk_overlap=500,
    length_function=tiktoken_len,
    separators=["\n\n", "\n", " ", ""],
)
docs = loader.load_and_split(text_splitter)

if __name__ == '__main__':
    type = input("Input vector store type: ")

    if type == "pinecone":
        index_name = "semiconduct-retrieval"
        pinecone.init(
            api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV")
        )
        print(pinecone.list_indexes())

        if index_name in pinecone.list_indexes():
            pinecone.delete_index(name=index_name)

        if index_name not in pinecone.list_indexes():
            # we create a new index
            pinecone.create_index(
                name=index_name,
                metric="cosine",
                dimension=1536,  # 1536 dim of text-embedding-ada-002
            )
            Pinecone.from_documents(docs, OpenAIEmbeddings(), index_name=index_name)
        else:
            Pinecone.add_documents(docs, OpenAIEmbeddings(), index_name=index_name)
    else:
        if os.path.exists("./vector/index.faiss"):
            db = FAISS.load_local("./vector", OpenAIEmbeddings())
            db.add_documents(docs)
        else:
            db = FAISS.from_documents(docs, OpenAIEmbeddings())
            db.save_local("./vector")