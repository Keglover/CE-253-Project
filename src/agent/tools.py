import json

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

from model_adapters.base import ToolDefinition

@dataclass
class RegisteredTool:
    definition: ToolDefinition
    function: Callable[..., str]
    authorized: bool = True

_DOCUMENTS = [
    {
        "id": "doc-001",
        "title": "Withdrawal Methods",
        "content": "Users can configure withdrawal methods from their account settings.",
    },
    {
        "id": "doc-002",
        "title": "Account Security",
        "content": "Users should never share passwords or authentication tokens.",
    },
]

_EMAIL_OUTBOX: list[dict[str, str]] = []

SEARCH_DOCUMENTS_DEFINITION = ToolDefinition(
    name="search_documents",
    description="Search the available documents for information relevant to the user's request.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The terms or question to search for.",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of documents to return.",
                "minimum": 1,
                "maximum": 5,
                "default": 5,
            },
        },
        "required": ["query"],
        "additionalProperties": False,
    },
)

SEND_EMAIL_DEFINITION = ToolDefinition(
    name="send_email",
    description="Send an email using the simulated email service.",
    parameters={
        "type": "object",
        "properties": {
            "to": {
                "type": "string",
                "description": "Recipient email address.",
            },
            "subject": {
                "type": "string",
                "description": "Email subject.",
            },
            "body": {
                "type": "string",
                "description": "Email body.",
            },
        },
        "required": ["to", "subject", "body"],
        "additionalProperties": False,
    },
)

def search_documents(query: str, max_results: int = 5) -> str:

    query_terms = query.lower().split()

    matches = [document for document in _DOCUMENTS 
               if any(term in (document["title"] + " " + document["content"]).lower() for term in query_terms)]

    return json.dumps({"results": matches[:max_results]})

def send_email(to: str,subject: str,body: str,) -> str:
    email = {
        "to": to,
        "subject": subject,
        "body": body,
    }

    _EMAIL_OUTBOX.append(email)

    return json.dumps(
        {
            "status": "sent",
            "recipient": to,
        }
    )

def get_email_outbox() -> list[dict[str, str]]:
    return list(_EMAIL_OUTBOX)

def build_default_tools(*,allow_email: bool = False) -> dict[str, RegisteredTool]:
    return {
        "search_documents": RegisteredTool(
            definition=SEARCH_DOCUMENTS_DEFINITION,
            function=search_documents,
            authorized=True,
        ),
        "send_email": RegisteredTool(
            definition=SEND_EMAIL_DEFINITION,
            function=send_email,
            authorized=allow_email,
        ),
    }