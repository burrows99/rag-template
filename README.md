# AI Agent Instructions for RAG Accelerator

## Project Overview

This is an **Azure AI Foundry + LangGraph RAG accelerator** combining a Python-based retrieval agent with a Next.js chat UI. The system features a unique **knowledge graph layer (Cognee)** on top of traditional vector search, providing semantic understanding beyond standard RAG implementations.

**Key Innovation**: Multi-backend architecture supporting 4 retriever types (Elasticsearch, Pinecone, MongoDB Atlas, Cognee) with user-scoped data isolation.

## Architecture

### Two-Service System

1. **`retrieval-agent/`** - Python LangGraph application with two graphs:
   - `indexer` (`index_graph.py`) - Ingests documents into vector stores
   - `retrieval_graph` (`graph.py`) - Handles conversational retrieval with chat history
   
2. **`agent-chat-ui/`** - Next.js frontend connecting to LangGraph servers via LangGraph SDK

### Critical Abstraction: User Isolation

**All retrievers enforce user-scoped filtering via `user_id`** in `configuration.py`. This enables multi-tenant deployments:
- Elasticsearch: `{"term": {"metadata.user_id": user_id}}`
- MongoDB: `{"user_id": {"$eq": user_id}}`
- Pinecone: `{"user_id": user_id}` in metadata filters
- Cognee: User-specific datasets

When adding new retrievers, **ALWAYS implement user_id filtering** in `retrieval.py`.

## Development Workflows

### Environment Setup

```bash
# Retrieval agent setup
cd retrieval-agent
cp .env.example ../.env.retrieval-agent
# Edit .env.retrieval-agent with:
# - OPENAI_API_KEY (required for embeddings)
# - Retriever credentials (ELASTICSEARCH_URL, PINECONE_API_KEY, etc.)

# Chat UI setup
cd agent-chat-ui
pnpm install
cp .env.example .env
# Set NEXT_PUBLIC_API_URL=http://localhost:2024
# Set NEXT_PUBLIC_ASSISTANT_ID=retrieval_graph
```

### Running the Stack

**Option 1: LangGraph Studio (Recommended)**
- Open `retrieval-agent/` folder in LangGraph Studio
- Studio auto-reads `langgraph.json` and `.env.retrieval-agent`
- Visual debugging of graph execution available

**Option 2: Docker Compose**
```bash
docker compose up cognee-api cognee-mcp  # Optional: elasticsearch
```

**Option 3: Local Development**
```bash
# Terminal 1: Start LangGraph server
cd retrieval-agent
langgraph dev --port 2024

# Terminal 2: Start UI
cd agent-chat-ui
pnpm dev  # Runs on http://localhost:3000
```

### Testing

```bash
cd retrieval-agent

# Unit tests (fast, no external dependencies)
make test

# Integration tests (requires vector store + OpenAI API)
export ELASTICSEARCH_URL=http://localhost:9200  # or your retriever
make integration_tests
```

**Test Pattern**: `tests/integration_tests/test_graph.py` demonstrates the full user journey:
1. Index documents for `user_id`
2. Query and verify retrieval
3. Verify isolation by querying with different `user_id`

### Code Quality

```bash
make lint        # Run ruff + mypy type checking
make format      # Auto-format with ruff
```

**Enforced Standards**:
- Strict mypy type checking (`--strict` flag in Makefile)
- Docstrings required (pydocstyle D rules in `pyproject.toml`)
- Import sorting (isort via ruff)

## Key Files to Understand

### Retrieval Agent Core

- **`src/retrieval_graph/configuration.py`** - Defines all configurable params including `user_id`, `retriever_provider`, and model selections. Uses `@dataclass` with metadata for LangGraph Studio integration.

- **`src/retrieval_graph/retrieval.py`** - Retriever factory pattern. Each `make_*_retriever()` function:
  1. Loads credentials from environment
  2. Initializes vector store with `make_text_encoder()`
  3. Applies user_id filtering
  4. Returns LangChain `VectorStoreRetriever`

- **`src/retrieval_graph/graph.py`** - Main conversational flow:
  1. `generate_query()` - First message uses input directly; subsequent uses LLM to refine based on history
  2. `retrieve()` - Fetches docs via configured retriever
  3. `generate()` - LLM generates response with retrieved context

- **`src/retrieval_graph/index_graph.py`** - Document ingestion. **Critical**: `ensure_docs_have_user_id()` stamps all docs with `user_id` metadata before indexing.

### Custom Cognee Integration

- **`src/langchain_cognee/retrievers.py`** - Custom `BaseRetriever` implementation communicating with Cognee HTTP API. Notable:
  - `add_documents()` - Accepts list of LangChain Documents
  - `process_data()` - Triggers knowledge graph construction (can take minutes)
  - `_get_relevant_documents()` - Queries via `/search` endpoint with `GRAPH_COMPLETION` search type

### Chat UI Integration Points

- **`src/app/api/[...path]/route.ts`** - Proxies all requests to LangGraph server using `langgraph-nextjs-api-passthrough`
- **`src/providers/Thread.tsx`** - Manages thread state, streaming, and LangGraph SDK client initialization
- **Environment variables override setup form** - Set `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_ASSISTANT_ID` to skip config screen

## Common Patterns

### Adding a New Retriever

1. Add provider option to `retriever_provider` Literal in `configuration.py`
2. Implement `make_<provider>_retriever()` in `retrieval.py`:
   ```python
   @contextmanager
   def make_custom_retriever(
       configuration: IndexConfiguration, embedding_model: Embeddings
   ) -> Generator[VectorStoreRetriever, None, None]:
       # 1. Load from env: os.environ["CUSTOM_API_KEY"]
       # 2. Initialize vector store with embedding_model
       # 3. CRITICAL: Apply user_id filter to search_kwargs
       search_kwargs = configuration.search_kwargs
       search_filter = search_kwargs.setdefault("filter", {})
       search_filter["user_id"] = configuration.user_id
       yield vstore.as_retriever(search_kwargs=search_kwargs)
   ```
3. Register in `get_retriever()` match statement
4. Update `.env.example` with required credentials
5. Add integration test in `test_graph.py` with new `retriever_provider` value

### Changing LLM Models

**For retrieval responses**:
```python
config = RunnableConfig(
    configurable={
        "response_model": "openai/gpt-4o",  # or "anthropic/claude-3-5-sonnet-20241022"
    }
)
```

**For query generation**:
```python
config = RunnableConfig(
    configurable={
        "query_model": "openai/gpt-4o-mini",
    }
)
```

Model format: `provider/model-name`. Supported providers in `utils.py`: `openai`, `anthropic`, `fireworks`.

### Modifying Prompts

System prompts are in `src/retrieval_graph/prompts.py`:
- `RESPONSE_SYSTEM_PROMPT` - Governs final LLM response generation
- `QUERY_SYSTEM_PROMPT` - Guides query refinement for multi-turn conversations

Override via configuration:
```python
Configuration(
    response_system_prompt="Custom instructions here...",
    query_system_prompt="Custom query refinement..."
)
```

## Debugging Tips

### Enable Debug Logging

```python
# Add to top of graph.py, retrieval.py, or any module
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Already set in key files
```

Logs include emoji prefixes: 🔧 (initialization), 🔍 (search), 💬 (messages), ✅ (success), ❌ (error)

### LangGraph Studio Visualization

- Time-travel debugging: Inspect state at each graph node
- View retrieved documents in `retrieve` node output
- Check token usage and latency per node
- Re-run from any checkpoint

### Common Issues

**"No documents returned"** - Check:
1. Documents indexed with correct `user_id`? (Run indexer graph)
2. Query embedding dimensions match store? (1536 for `text-embedding-3-small`)
3. User isolation filter applied? (Set `user_id` in config)

**"API key not found"** - Environment loading:
- LangGraph Studio: Uses `../.env.retrieval-agent` (relative to `retrieval-agent/` folder)
- Local `langgraph dev`: Uses `.env` in current directory
- Docker Compose: Pass via `environment:` in `compose.yaml`

## Documentation Structure

- **`REQUIREMENTS.md`** - Original project scope and deliverables
- **`PROJECT_SUMMARY.md`** - Current status vs. original scope (Cognee exceeded expectations)
- **`APPROACH.md`** - Research notes on Microsoft data connectors (SharePoint, Dataverse, Azure SQL)
- **`retrieval-agent/README.md`** - Detailed setup instructions for all 4 retriever backends
- **`agent-chat-ui/README.md`** - Frontend usage and customization guide

## What Makes This Codebase Unique

1. **Production-grade abstractions** - Not a tutorial, but a reusable accelerator with proper error handling, logging, and type safety
2. **Knowledge graph hybrid** - Cognee integration goes beyond vector similarity to understand entity relationships
3. **Multi-backend flexibility** - Switch retrievers via config, not code changes
4. **User isolation by default** - Multi-tenancy built into the architecture from day one
5. **LangGraph Studio compatible** - Visual debugging and development workflow

When extending this codebase, maintain these principles: user isolation, provider abstraction, and comprehensive logging.
