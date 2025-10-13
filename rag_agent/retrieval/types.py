# Import necessary libraries
import os
import json
import hashlib
import logging
import sys
import traceback
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, ValidationError


class SearchResult(BaseModel):
    content: str 
    url: Optional[List[Union[str, int]]] = None
    score: float
    metadata: Dict[str, Any] = {}


class SearchRequest(BaseModel):
    query: str
    limit: int = 5
    urls: Optional[List[Union[str, int]]] = None

