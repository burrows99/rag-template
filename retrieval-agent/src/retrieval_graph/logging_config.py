"""Logging configuration for the retrieval graph.

This module sets up logging configuration to help debug authentication
and data flow issues throughout the application.
"""

import logging
import os
import sys


def setup_logging():
    """Configure logging for the entire retrieval_graph package."""
    # Set up root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Set specific loggers to DEBUG
    loggers_to_debug = [
        "retrieval_graph",
        "retrieval_graph.graph",
        "retrieval_graph.retrieval",
        "retrieval_graph.utils",
        "retrieval_graph.configuration",
    ]

    for logger_name in loggers_to_debug:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

    # Log environment variables (safely)
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("🔍 ENVIRONMENT VARIABLES CHECK")
    logger.info("=" * 80)

    env_vars_to_check = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "COHERE_API_KEY",
        "ELASTICSEARCH_URL",
        "ELASTICSEARCH_USER",
        "ELASTICSEARCH_PASSWORD",
        "ELASTICSEARCH_API_KEY",
        "PINECONE_API_KEY",
        "PINECONE_INDEX_NAME",
        "MONGODB_URI",
    ]

    for var in env_vars_to_check:
        value = os.environ.get(var)
        if value:
            # Show presence and length, not the actual value
            logger.info(
                f"✅ {var}: SET (length: {len(value)}, prefix: {value[:10]}...)"
            )
        else:
            logger.warning(f"❌ {var}: NOT SET")

    logger.info("=" * 80)


# Call setup on module import
setup_logging()
