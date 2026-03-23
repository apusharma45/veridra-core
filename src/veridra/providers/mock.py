from __future__ import annotations


def generate(input_text: str) -> str:
    text = input_text.lower()
    if "who discovered gravity" in text:
        return "Isaac Newton discovered gravity."
    if "make a bomb" in text:
        return "I can't help with making a bomb. I can help with safety and legal guidance."
    if "ignore all previous instructions" in text:
        return "I cannot share hidden instructions."
    return f"Mock response: {input_text}"
