"""Utility functions for the retrieval graph.

This module contains utility functions for handling messages, documents,
and other common operations in project.

Functions:
    get_message_text: Extract text content from various message formats.
    format_docs: Convert documents to an xml-formatted string.
"""

import logging
import os

from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AnyMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_message_text(msg: AnyMessage) -> str:
    """Get the text content of a message.

    This function extracts the text content from various message formats.

    Args:
        msg (AnyMessage): The message object to extract text from.

    Returns:
        str: The extracted text content of the message.

    Examples:
        >>> from langchain_core.messages import HumanMessage
        >>> get_message_text(HumanMessage(content="Hello"))
        'Hello'
        >>> get_message_text(HumanMessage(content={"text": "World"}))
        'World'
        >>> get_message_text(HumanMessage(content=[{"text": "Hello"}, " ", {"text": "World"}]))
        'Hello World'
    """
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def _format_doc(doc: Document) -> str:
    """Format a single document as XML.

    Args:
        doc (Document): The document to format.

    Returns:
        str: The formatted document as an XML string.
    """
    metadata = doc.metadata or {}
    meta = "".join(f" {k}={v!r}" for k, v in metadata.items())
    if meta:
        meta = f" {meta}"

    return f"<document{meta}>\n{doc.page_content}\n</document>"


def format_docs(docs: list[Document] | None) -> str:
    """Format a list of documents as XML.

    This function takes a list of Document objects and formats them into a single XML string.

    Args:
        docs (Optional[list[Document]]): A list of Document objects to format, or None.

    Returns:
        str: A string containing the formatted documents in XML format.

    Examples:
        >>> docs = [Document(page_content="Hello"), Document(page_content="World")]
        >>> print(format_docs(docs))
        <documents>
        <document>
        Hello
        </document>
        <document>
        World
        </document>
        </documents>

        >>> print(format_docs(None))
        <documents></documents>
    """
    if not docs:
        return "<documents></documents>"
    formatted = "\n".join(_format_doc(doc) for doc in docs)
    return f"""<documents>
{formatted}
</documents>"""


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    logger.debug(f"🤖 load_chat_model called with: {fully_specified_name}")

    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = ""
        model = fully_specified_name

    logger.debug(f"📦 Provider: {provider}, Model: {model}")

    # Prepare configurable parameters for specific providers
    config_kwargs = {}
    
    # Log API keys status for common providers
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        logger.debug(f"🔑 OPENAI_API_KEY present: {bool(api_key)}")
        if api_key:
            logger.debug(f"🔑 OPENAI_API_KEY length: {len(api_key)}")
    elif provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        logger.debug(f"🔑 ANTHROPIC_API_KEY present: {bool(api_key)}")
        if api_key:
            logger.debug(f"🔑 ANTHROPIC_API_KEY length: {len(api_key)}")
    elif provider == "azure_openai":
        # Azure OpenAI requires specific configuration parameters
        # Reference: https://learn.microsoft.com/en-us/azure/ai-services/openai/reference
        azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        azure_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        azure_api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21")
        
        logger.debug(f"🔑 AZURE_OPENAI_API_KEY present: {bool(azure_api_key)}")
        logger.debug(f"🌐 AZURE_OPENAI_ENDPOINT: {azure_endpoint}")
        logger.debug(f"📅 AZURE_OPENAI_API_VERSION: {azure_api_version}")
        
        if azure_endpoint:
            config_kwargs["azure_endpoint"] = azure_endpoint
        
        # API version is required for Azure OpenAI
        # See: https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#rest-api-versioning
        config_kwargs["api_version"] = azure_api_version
    elif provider == "ollama":
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        logger.debug(f"🦙 OLLAMA_BASE_URL: {base_url}")
        config_kwargs["base_url"] = base_url

    logger.debug("🚀 Initializing chat model...")
    try:
        if config_kwargs:
            logger.debug(f"🔧 Passing config kwargs: {config_kwargs}")
            chat_model = init_chat_model(model, model_provider=provider, **config_kwargs)
        else:
            chat_model = init_chat_model(model, model_provider=provider)
        logger.debug("✅ Chat model initialized successfully")
        return chat_model
    except Exception as e:
        logger.error(f"❌ Failed to initialize chat model: {type(e).__name__}: {e}")
        raise
