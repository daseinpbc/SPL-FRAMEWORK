"""Prompt builders for the LangChain baseline."""

from __future__ import annotations

from typing import Dict, List

from common.email_schema import EmailRecord


def build_system_prompt(labels: List[Dict[str, str]]) -> str:
    """Construct a system prompt enumerating allowed labels."""
    labels_text = "\n".join([f'- "{item["name"]}": {item.get("description", "")}' for item in labels])
    return (
        "You classify emails into one of the provided labels. "
        "Respond only with JSON of the form {\"label\": \"<label>\"}.\n"
        "Labels:\n"
        f"{labels_text}"
    )


def build_user_prompt(email: EmailRecord) -> str:
    """Create the user prompt containing the email to classify."""
    return f"Subject: {email.subject}\n\nBody:\n{email.body}\n\nReturn JSON with the label only."
