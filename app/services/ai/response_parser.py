"""
AI World Engine - Response Parser.
Formats raw AI text output into a structured dict for page display.
Falls back gracefully to plain text if JSON parsing fails.
"""

import json
import re
from typing import Dict, Any, List, Optional


class ResponseParser:
    """Parses and formats AI response content."""

    @staticmethod
    def parse(raw_text: str) -> Dict[str, Any]:
        """
        Parse AI response text into a structured format.

        Returns:
            {
                "title": str,
                "summary": str,
                "sections": [
                    {"heading": str, "content": str}
                ],
                "raw_text": str
            }
        """
        if not raw_text:
            return {
                "title": "",
                "summary": "",
                "sections": [],
                "raw_text": "",
            }

        raw_text = raw_text.strip()

        # Try to extract the first line as title
        lines = raw_text.split("\n")
        title = lines[0].strip().lstrip("#").strip() if lines else ""
        if len(title) > 100:
            title = ""

        # Try to parse as JSON (some AI models output JSON)
        try:
            data = json.loads(raw_text)
            if isinstance(data, dict):
                return ResponseParser._from_json(data, raw_text)
        except (json.JSONDecodeError, ValueError):
            pass

        # Parse markdown-like sections (### or ==)
        sections = ResponseParser._extract_sections(raw_text)

        # Build summary: first non-heading paragraph
        summary = ResponseParser._extract_summary(raw_text, sections)

        return {
            "title": title,
            "summary": summary,
            "sections": sections,
            "raw_text": raw_text,
        }

    @staticmethod
    def _from_json(data: dict, raw_text: str) -> Dict[str, Any]:
        """Parse from a JSON <�数结构."""
        title = data.get("title", "")
        summary = data.get("summary", data.get("摘要", ""))

        sections: List[Dict[str, str]] = []
        # Handle sections array
        for s in data.get("sections", data.get("sections", [])):
            if isinstance(s, dict):
                heading = s.get("heading", s.get("title", ""))
                content = s.get("content", s.get("body", ""))
                sections.append({"heading": heading, "content": content})
            elif isinstance(s, str):
                sections.append({"heading": "", "content": s})

        # Try known top-level keys as sections
        if not sections:
            for key in ("问题列表", "关键事件", "涉及角色", "涉及势力", "影响范围", "潜在矛盾", "建议"):
                val = data.get(key)
                if val is not None:
                    if isinstance(val, list):
                        content = "\n".join(f"- {v}" for v in val)
                    else:
                        content = str(val)
                    sections.append({"heading": key, "content": content})

        return {
            "title": title,
            "summary": str(summary) if summary else "",
            "sections": sections,
            "raw_text": raw_text,
        }

    @staticmethod
    def _extract_sections(text: str) -> List[Dict[str, str]]:
        """Extract sections from markdown-style text."""
        sections: List[Dict[str, str]] = []

        # Split on ### or ## headings, or === or --- lines
        section_pattern = re.compile(
            r"^(?:#{1,3}\s+|=+\s*|—+\s*)(.*?)$", re.MULTILINE
        )
        matches = list(section_pattern.finditer(text))

        if not matches:
            # No headings found; return entire text as one section
            sections.append({"heading": "", "content": text})
            return sections

        for i, m in enumerate(matches):
            heading = m.group(1).strip().rstrip(":：").strip()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end].strip()
            if heading or content:
                sections.append({"heading": heading, "content": content})

        return sections

    @staticmethod
    def _extract_summary(raw_text: str, sections: List[Dict[str, str]]) -> str:
        """Extract a short summary paragraph from the text."""
        if not raw_text:
            return ""
        # Get the first non-heading paragraph
        for line in raw_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("#") or re.match(r"^=+|^—+|^---", line):
                continue
            return line[:200]
        return ""
