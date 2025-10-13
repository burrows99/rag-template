# src/chat/orchestrator_agent.py
from typing import List, Dict, Any
from langgraph.graph import StateGraph
import asyncio
from concurrent.futures import ThreadPoolExecutor
from rag_agent.chat.memory_manager import MemoryManager
from langchain.prompts import (
    ChatPromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate
)


class OrchestratorAgentPrompt:
    @staticmethod
    def render(
        user_query: str,
        tools_description: str,
        tools_instruction: str,
        research_history: list[dict],
    ) -> str:
        chat_prompt = ChatPromptTemplate.from_messages([OrchestratorAgentPrompt.system_prompt()])
        chat_prompt_fmt = chat_prompt.format_messages(
            user_query=user_query,
            tools_description=tools_description,
            tools_instruction=tools_instruction,
            research_history=research_history,
        )
        return chat_prompt_fmt

    @staticmethod
    def tool_list_prompt_text() -> str:
        return """\
You have access to the following set of tools you can invoke to help you gather additional documents:
{tools_list}

The documents retrieved by the tools are referred to as "retrieved documents".

The tools include access to different information sources.
You may use the tools as many times as needed to gather information.

The information accessible by the tools will not be updated while you are researching the report.
So if you use them in the same way twice you will get the same results.
"""
    @staticmethod
    def tools_instruction_text():
        return """
If you want to use one of the tools, respond with the following schema:
```json
{
    "action": "use_tool",
    "reason": reason for the action, including which section, "data_needed" and "questions" you are trying to address,
    "tool_name": name of the tool,
    "tool_args": arguments to pass to the tool
}
```

For example, if you wanted to invoke a tool described by:
```json
{
    "tool_name": "adder_tool",
    "description": "Adds a value to the input.",
    "input_schema": {
        "value": {
            "title": "Value",
            "description": "The value to add the number to.",
            "type": "integer"
        }
    }
}
```

You would reply:
```json
{
    "action": "use_tool",
    "reason": why you are using it,
    "tool_name": "adder_tool",
    "tool_args": {
        "value": the value you want to add to
    }
}
```

"""
    @staticmethod
    def system_prompt_text():
        return """\
You are a research assistant, who is gathering a set of facts to be used in answering user question, referred to as the "user query".

{tools_description}

Your responses should be in the form of JSON dictionaries.
Always enclose your JSON response with "```json" and "```" as follows:
```json
{{
}}
```

Enclose JSON string values in double quotes. Be sure to properly escape any nested quotation marks.

This is the user query you are researching for:
{user_query}

If you want to insert new facts into the research history, respond with the following schema:
```json
{{
    "action": "assert",
    "reason": why you are doing it,
    "assertions": [
        {{
            "data": data received from the resource or tools which you find relevant to the user query (any form of data i.e. text, tables, json, markdown etc. copied verbatim from the resource),
            "resource_id" : identifier of supporting resource (copied verbatim from the resource),
            "resource_type": type of supporting resource (copied verbatim from the resource) (e.g. "index_search", "sql_search", "spreadsheet", "dataverse"),
        }},
        ...
    ]
}}
```

The text in a supporting source should be a contiguous block quoted verbatim from the resource.

You must specify at least one source. If you use incorrect sources, the assertion will be rejected.
All of the sources must be correct - if any one is incorrect, the assertion will be rejected.

{tools_instruction}

When you have gathered enough information to write a complete document of the specified form, respond with the following schema:
```json
{{
    "action": "end",
    "status": "success",
    "reason": why you think you succeeded
}}
```

If you think you are not able to complete this task, respond with the following schema:
```json
{{
    "action": "end",
    "status": "failure",
    "reason": why you think you are unable to finish
}}
```

Here is the history of your last few actions on the document (and possibly responses to your actions):
```json
{research_history}
```

Your previous assertions are accessible by looking at the document state.
Pay attention to errors resulting from your previous actions.
Try to learn from them and not repeat them when you select further actions.

Include as much directly relevant information as possible from the data you obtain. Try not to leave anything out.
"""
    @staticmethod
    def tool_list_prompt():
        return PromptTemplate.from_template(MemoBuilderPrompt.tool_list_prompt_text())

    @staticmethod
    def system_prompt():
        return SystemMessagePromptTemplate.from_template(MemoBuilderPrompt.system_prompt_text())

