from typing import Dict

class MarkdownGeneratorTool:
    def generate(self, content: Dict) -> str:
        return f"# Generated Content\n\n{content['title']}\n{content['sections']}"