import sqlite3
from typing import Dict, Any, List, Optional
from langchain_core.tools import BaseTool
import pandas as pd
from sqlalchemy import create_engine, inspect
from rag_agent.LLM_Garden import LLM_GPT_5_MINI  
from io import StringIO

class SQLAgent:
    def __init__(self, sql_connection_string: Dict[str, Any]):
        """
        Example config:
        {
            "sql_connection_string": "sqlite:///path/to/database.db"
        }
        """
        self.connection_string = sql_connection_string
        self.db_path = self._extract_db_path(self.connection_string)
        self.llm_client = LLM_GPT_5_MINI
        self.schema_cache = self._introspect_schema()

    def _extract_db_path(self, conn_str: str) -> str:
        """Extract file path from sqlite connection string"""
        return conn_str.replace("sqlite:///", "").strip()

    async def retrieve(self, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """Convert natural language to SQL and execute"""
        nl_query = query_info["query"]
        sql_query = await self._nl_to_sql(nl_query)

        try:
            results = self._execute_sql(sql_query)
            return {
                "agent": "sql",
                "results": results,
                "query": sql_query,
                "success": True,
            }
        except Exception as e:
            return {
                "agent": "sql",
                "error": str(e),
                "success": False,
            }

    async def _nl_to_sql(self, nl_query: str) -> str:
        """Convert natural language to SQL using LLM"""
        prompt = f"""
        Convert this natural language query to SQL:
        Query: {nl_query}
        
        Available schema:
        {self.schema_cache}
        
        Return only the SQL query.
        """

        response = await self.llm_client.invoke(prompt)
        return self._sanitize_sql(response)

    def _introspect_schema(self) -> Dict[str, Any]:
        """Get database schema for context"""
        engine = create_engine(self.connection_string)
        inspector = inspect(engine)

        schema = {}
        for table_name in inspector.get_table_names():
            columns = []
            for column in inspector.get_columns(table_name):
                columns.append(
                    {
                        "name": column["name"],
                        "type": str(column["type"]),
                    }
                )
            schema[table_name] = columns

        return schema

    def _execute_sql(self, query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results as list of dicts"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn)
        return df.to_dict("records")

    def _sanitize_sql(self, sql_text: str) -> str:
        """Basic cleanup of SQL returned by LLM"""
        sql_text = sql_text.strip().strip("```").replace("sql", "", 1).strip()
        return sql_text

    def _format_markdown_table(self, df: pd.DataFrame) -> str:
        """Convert a pandas DataFrame to a Markdown table"""
        if df.empty:
            return "_No results found._"

        buf = StringIO()
        df.to_markdown(buf, index=False)
        return buf.getvalue()

    def _run(self, natural_language_query: str, limit: int = 10, table_name: Optional[str] = None) -> str:
        """Synchronously execute natural language query and return markdown table"""
        import asyncio
        loop = asyncio.get_event_loop()
        sql_query = loop.run_until_complete(self._nl_to_sql(natural_language_query))

        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(sql_query, conn)
                if limit:
                    df = df.head(limit)
            return self._format_markdown_table(df)
        except Exception as e:
            return f"**Error:** {str(e)}"

    async def _arun(self, natural_language_query: str, limit: int = 10, table_name: Optional[str] = None) -> str:
        """Asynchronously execute natural language query and return markdown table"""
        try:
            sql_query = await self._nl_to_sql(natural_language_query)
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(sql_query, conn)
                if limit:
                    df = df.head(limit)
            return self._format_markdown_table(df)
        except Exception as e:
            return f"**Error:** {str(e)}"
