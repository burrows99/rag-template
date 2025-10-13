from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
load_dotenv("rag_agent/.env")
import os
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")


embeddings = AzureOpenAIEmbeddings(
    model="text-embedding-3-small",
    # dimensions: Optional[int] = None, # Can specify dimensions with new text-embedding-3 models
    # azure_endpoint="https://<your-endpoint>.openai.azure.com/", If not provided, will read env variable AZURE_OPENAI_ENDPOINT
    # api_key=... # Can provide an API key directly. If missing read env variable AZURE_OPENAI_API_KEY
    # openai_api_version=..., # If not provided, will read env variable AZURE_OPENAI_API_VERSION
)

# # Create a vector store with a sample text
# from langchain_core.vectorstores import InMemoryVectorStore

# text = "LangChain is the framework for building context-aware reasoning applications"

# vectorstore = InMemoryVectorStore.from_texts(
#     [text],
#     embedding=embeddings,
# )

# # Use the vectorstore as a retriever
# retriever = vectorstore.as_retriever()

# # Retrieve the most similar text
# retrieved_documents = retriever.invoke("What is LangChain?")

# # show the retrieved document's content
# retrieved_documents[0].page_content

# text2 = (
#     "LangGraph is a library for building stateful, multi-actor applications with LLMs"
# )
# two_vectors = embeddings.embed_documents([text, text2])
# for vector in two_vectors:
#     print(str(vector)[:100])  # Show the first 100 characters of the vector



LLM_GPT_5_MINI = AzureChatOpenAI(
    azure_deployment="gpt-5-mini",

)

LLM_GPT_4_1 = AzureChatOpenAI(
    azure_deployment="gpt-4.1",

)

# messages = [
#     (
#         "system",
#         "You are a helpful assistant that translates English to French. Translate the user sentence.",
#     ),
#     ("human", "I love programming."),
# ]
# ai_msg = LLM_GPT_4_1.invoke(messages)
# print(ai_msg.content)

