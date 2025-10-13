import os

from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from rag_agent.LLM_Garden import embeddings
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")

index_name: str = "langchain-vector-demo"
AZURE_VECTOR_STORE: AzureSearch = AzureSearch(
    azure_search_endpoint=AZURE_SEARCH_ENDPOINT,
    azure_search_key=AZURE_SEARCH_KEY,
    index_name=index_name,
    embedding_function=embeddings.embed_query,
)

# # class  Variable(BaseSettings):
# #     key : str 
    


# # var = Variable
# # var.key()
# from langchain_community.document_loaders import TextLoader
# from langchain_text_splitters import CharacterTextSplitter

# loader = TextLoader("state_of_the_union.txt", encoding="utf-8")

# documents = loader.load()
# text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
# docs = text_splitter.split_documents(documents)

# AZURE_VECTOR_STORE.add_documents(documents=docs)

# # Perform a similarity search
# docs = AZURE_VECTOR_STORE.similarity_search(
#     query="What did the president say about Ketanji Brown Jackson",
#     k=3,
#     search_type="similarity",
# )
# print("similarity search")
# print(docs[0].page_content)

# # Perform a vector similarity search with relevance scores
# docs_and_scores = AZURE_VECTOR_STORE.similarity_search_with_relevance_scores(
#     query="What did the president say about Ketanji Brown Jackson",
#     k=4,
#     score_threshold=0.80,
# )
# from pprint import pprint
# print("similarity search with relevance scores")
# pprint(docs_and_scores)

# # Perform a hybrid search using the search_type parameter
# docs = AZURE_VECTOR_STORE.similarity_search(
#     query="What did the president say about Ketanji Brown Jackson",
#     k=3,
#     search_type="hybrid",
# )
# print("hybrid search ")
# print(docs[0].page_content)

# # Perform a hybrid search using the hybrid_search method
# docs = AZURE_VECTOR_STORE.hybrid_search(
#     query="What did the president say about Ketanji Brown Jackson", k=3
# )
# print("hybrid search 2")
# print(docs[0].page_content)

