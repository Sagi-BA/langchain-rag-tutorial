import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class DataQuery:
    CHROMA_PATH = "chroma"
    PROMPT_TEMPLATE = """
    Answer the question based only on the following context:

    {context}

    ---

    Answer the question based on the above context: {question}
    """

    def __init__(self):
        load_dotenv()
        self.embedding_function = OpenAIEmbeddings(openai_api_key=os.environ['OPENAI_API_KEY'])
        self.db = None
        self.model = ChatOpenAI()

    def prepare_db(self):
        print("Creating Chroma vector store...")
        self.db = Chroma(persist_directory=self.CHROMA_PATH, embedding_function=self.embedding_function)
        print("Chroma vector store created.")

    def query(self, query_text):
        if not self.db:
            self.prepare_db()

        print(f"Querying the vector store for: {query_text}")
        results = self.db.similarity_search_with_relevance_scores(query_text, k=3)
        print(f"Results found: {results}")

        print(results[0][1] < 0.7)
        if len(results) == 0 or results[0][1] < 0.7:
            print(f"Unable to find matching results.")
            return None

        for i, (doc, score) in enumerate(results):
            print(f"Result {i+1} - Score: {score}, Content: {doc.page_content[:500]}")  # Print first 500 chars of each result

        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(self.PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)
        # print(f"Generated prompt: {prompt}")

        response_text = self.model.predict(prompt)
        # print(f"Response: {response_text}")

        sources = [doc.metadata.get("source", None) for doc, _score in results]
        formatted_response = f"Response: {response_text}\nSources: {sources}"
        print(formatted_response)

        # return formatted_response
        return response_text

# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    
    myquery = DataQuery()
    result = myquery.query(args.query_text)
    print(result)
