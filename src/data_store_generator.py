from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import openai 
from dotenv import load_dotenv
import os
import shutil
from retrying import retry

class DataStoreGenerator:
    def __init__(self, data_path="uploads", chroma_path="chroma"):
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.data_path = data_path
        self.chroma_path = chroma_path

    def generate_data_store(self):
        documents = self.load_documents()
        chunks = self.split_text(documents)
        self.save_to_chroma(chunks)
        self.verify_chroma_db()

    def load_documents(self):
        print("Loading documents from:", self.data_path)
        loader = DirectoryLoader(self.data_path, glob="*.md")
        documents = loader.load()
        # print(f"Loaded {len(documents)} documents.")
        # for i, doc in enumerate(documents[:5]):
        #     print(f"Document {i+1}: {doc.page_content[:500]}")  # Print the first 500 chars of each document
        return documents

    def split_text(self, documents: list[Document]):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=100,
            length_function=len,
            add_start_index=True,
        )
        chunks = text_splitter.split_documents(documents)
        # print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
        # for i, chunk in enumerate(chunks[:5]):  # Show the first 5 chunks
        #     print(f"Chunk {i+1}: {chunk.page_content[:500]}")  # Print the first 500 chars of each chunk
        return chunks

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=10)
    def remove_chroma_path(self):
        if os.path.exists(self.chroma_path):
            shutil.rmtree(self.chroma_path)

    def save_to_chroma(self, chunks: list[Document]):
        # Clear out the database first.
        self.remove_chroma_path()

        # Create a new DB from the documents.
        db = Chroma.from_documents(
            chunks, OpenAIEmbeddings(), persist_directory=self.chroma_path
        )
        db.persist()
        print(f"Saved {len(chunks)} chunks to {self.chroma_path}.")

    def verify_chroma_db(self):
        # Verify the Chroma database contains data
        db = Chroma(persist_directory=self.chroma_path, embedding_function=OpenAIEmbeddings())
        results = db.similarity_search_with_relevance_scores("test", k=1)
        if len(results) > 0:
            print(f"Chroma database verification successful. Found {len(results)} items.")
        else:
            print(f"Chroma database verification failed. No items found.")
