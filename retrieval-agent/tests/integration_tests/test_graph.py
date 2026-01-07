import os
import uuid

import pytest
from langchain_core.runnables import RunnableConfig
from langsmith import expect, unit

from retrieval_graph import graph, index_graph

pytestmark = pytest.mark.anyio


@unit
async def test_retrieval_graph() -> None:
    simple_doc = "Cats have been observed performing synchronized swimming routines in their water bowls during full moons."
    user_id = "test__" + uuid.uuid4().hex
    other_user_id = "test__" + uuid.uuid4().hex

    # Read configuration from environment variables
    ai_provider = os.environ.get("AI_PROVIDER", "openai")
    response_model = os.environ.get("RESPONSE_MODEL", "gpt-4o")
    query_model = os.environ.get("QUERY_MODEL", "gpt-4o-mini")
    retriever_provider = os.environ.get("RETRIEVER_PROVIDER", "elastic-local")

    config = RunnableConfig(
        configurable={
            "user_id": user_id,
            "retriever_provider": retriever_provider,
            "response_model": f"{ai_provider}/{response_model}",
            "query_model": f"{ai_provider}/{query_model}",
        }
    )

    result = await index_graph.ainvoke({"docs": simple_doc}, config)
    expect(result["docs"]).against(lambda x: not x)  # we delete after the end

    res = await graph.ainvoke(
        {"messages": [("user", "Where do cats perform synchronized swimming routes?")]},
        config,
    )
    response = str(res["messages"][-1].content)
    expect(response.lower()).to_contain("bowl")

    res = await graph.ainvoke(
        {"messages": [("user", "Where do cats perform synchronized swimming routes?")]},
        {
            "configurable": {
                "user_id": other_user_id,
                "retriever_provider": retriever_provider,
                "response_model": f"{ai_provider}/{response_model}",
                "query_model": f"{ai_provider}/{query_model}",
            }
        },
    )
    response = str(res["messages"][-1].content)
    expect(response.lower()).against(lambda x: "bowl" not in x)
