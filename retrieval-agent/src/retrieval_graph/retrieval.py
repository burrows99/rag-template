"""Manage the configuration of various retrievers.

This module provides functionality to create and manage retrievers for different
vector store backends, specifically Elasticsearch, Pinecone, and MongoDB.

The retrievers support filtering results by user_id to ensure data isolation between users.
"""

import logging
import os
from contextlib import contextmanager
from typing import Generator

from langchain_core.embeddings import Embeddings
from langchain_core.runnables import RunnableConfig
from langchain_core.vectorstores import VectorStoreRetriever

from retrieval_graph.configuration import Configuration, IndexConfiguration

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

## Encoder constructors


def make_text_encoder(model: str) -> Embeddings:
    """Connect to the configured text encoder."""
    logger.debug(f"🔧 make_text_encoder called with model: {model}")
    provider, model = model.split("/", maxsplit=1)
    logger.debug(f"📦 Provider: {provider}, Model: {model}")

    match provider:
        case "openai":
            from langchain_openai import OpenAIEmbeddings

            # Check for API key
            api_key = os.environ.get("OPENAI_API_KEY")
            logger.debug(f"🔑 OPENAI_API_KEY present: {bool(api_key)}")
            if api_key:
                logger.debug(f"🔑 OPENAI_API_KEY length: {len(api_key)}")
                logger.debug(f"🔑 OPENAI_API_KEY prefix: {api_key[:10]}...")

            logger.debug(f"🚀 Initializing OpenAIEmbeddings with model: {model}")
            try:
                embeddings = OpenAIEmbeddings(model=model)
                logger.debug("✅ OpenAIEmbeddings initialized successfully")
                return embeddings
            except Exception as e:
                logger.error(
                    f"❌ Failed to initialize OpenAIEmbeddings: {type(e).__name__}: {e}"
                )
                raise

        case "cohere":
            from langchain_cohere import CohereEmbeddings

            logger.debug(f"🚀 Initializing CohereEmbeddings with model: {model}")
            return CohereEmbeddings(model=model)  # type: ignore

        case _:
            raise ValueError(f"Unsupported embedding provider: {provider}")


## Retriever constructors


@contextmanager
def make_elastic_retriever(
    configuration: IndexConfiguration, embedding_model: Embeddings
) -> Generator[VectorStoreRetriever, None, None]:
    """Configure this agent to connect to a specific elastic index."""
    from langchain_elasticsearch import ElasticsearchStore

    connection_options = {}
    if configuration.retriever_provider == "elastic-local":
        connection_options = {
            "es_user": os.environ["ELASTICSEARCH_USER"],
            "es_password": os.environ["ELASTICSEARCH_PASSWORD"],
        }

    else:
        connection_options = {"es_api_key": os.environ["ELASTICSEARCH_API_KEY"]}

    vstore = ElasticsearchStore(
        **connection_options,  # type: ignore
        es_url=os.environ["ELASTICSEARCH_URL"],
        index_name="langchain_index_1536",
        embedding=embedding_model,
    )

    search_kwargs = configuration.search_kwargs

    search_filter = search_kwargs.setdefault("filter", [])
    search_filter.append({"term": {"metadata.user_id": configuration.user_id}})
    yield vstore.as_retriever(search_kwargs=search_kwargs)


@contextmanager
def make_pinecone_retriever(
    configuration: IndexConfiguration, embedding_model: Embeddings
) -> Generator[VectorStoreRetriever, None, None]:
    """Configure this agent to connect to a specific pinecone index."""
    from langchain_pinecone import PineconeVectorStore

    search_kwargs = configuration.search_kwargs

    search_filter = search_kwargs.setdefault("filter", {})
    search_filter.update({"user_id": configuration.user_id})
    vstore = PineconeVectorStore.from_existing_index(
        os.environ["PINECONE_INDEX_NAME"], embedding=embedding_model
    )
    yield vstore.as_retriever(search_kwargs=search_kwargs)


@contextmanager
def make_mongodb_retriever(
    configuration: IndexConfiguration, embedding_model: Embeddings
) -> Generator[VectorStoreRetriever, None, None]:
    """Configure this agent to connect to a specific MongoDB Atlas index & namespaces."""
    from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch

    vstore = MongoDBAtlasVectorSearch.from_connection_string(
        os.environ["MONGODB_URI"],
        namespace="langgraph_retrieval_agent.default",
        embedding=embedding_model,
    )
    search_kwargs = configuration.search_kwargs
    pre_filter = search_kwargs.setdefault("pre_filter", {})
    pre_filter["user_id"] = {"$eq": configuration.user_id}
    yield vstore.as_retriever(search_kwargs=search_kwargs)


@contextmanager
def make_cognee_retriever(
    configuration: IndexConfiguration, embedding_model: Embeddings
) -> Generator[VectorStoreRetriever, None, None]:
    """Configure this agent to connect to Cognee knowledge graph retriever."""
    from langchain_cognee.retrievers import CogneeRetriever

    # Get OpenAI API key from environment
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is required for Cognee retriever"
        )

    # Get API URL from environment
    api_url = os.environ.get("COGNEE_API_URL", "http://localhost:8000")

    # Get k value from search_kwargs or use default
    k = configuration.search_kwargs.get("k", 3)

    # Get dataset_name from configuration
    dataset_name = getattr(configuration, "dataset_name", "main_dataset")

    logger.debug(
        f"🧠 Initializing Cognee retriever with dataset: {dataset_name}, k={k}, api_url={api_url}"
    )

    retriever = CogneeRetriever(
        llm_api_key=openai_api_key,
        dataset_name=dataset_name,
        k=k,
        api_url=api_url,
    )

    logger.debug("✅ Cognee retriever initialized successfully")
    yield retriever


@contextmanager
def make_retriever(
    config: RunnableConfig,
) -> Generator[VectorStoreRetriever, None, None]:
    """Create a retriever for the agent, based on the current configuration."""
    logger.debug("🔍 make_retriever called")
    logger.debug(f"📋 Config: {config}")

    configuration = IndexConfiguration.from_runnable_config(config)
    logger.debug("⚙️ Configuration loaded:")
    logger.debug(f"  - user_id: {configuration.user_id}")
    logger.debug(f"  - embedding_model: {configuration.embedding_model}")
    logger.debug(f"  - retriever_provider: {configuration.retriever_provider}")
    logger.debug(f"  - search_kwargs: {configuration.search_kwargs}")

    embedding_model = make_text_encoder(configuration.embedding_model)
    # user_id = configuration.user_id
    # if not user_id:
    #     raise ValueError("Please provide a valid user_id in the configuration.")
    match configuration.retriever_provider:
        case "elastic" | "elastic-local":
            with make_elastic_retriever(configuration, embedding_model) as retriever:
                yield retriever

        case "pinecone":
            with make_pinecone_retriever(configuration, embedding_model) as retriever:
                yield retriever

        case "mongodb":
            with make_mongodb_retriever(configuration, embedding_model) as retriever:
                yield retriever

        case "cognee":
            with make_cognee_retriever(configuration, embedding_model) as retriever:
                yield retriever

        case _:
            raise ValueError(
                "Unrecognized retriever_provider in configuration. "
                f"Expected one of: {', '.join(Configuration.__annotations__['retriever_provider'].__args__)}\n"
                f"Got: {configuration.retriever_provider}"
            )
