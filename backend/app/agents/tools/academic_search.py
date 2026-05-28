from typing import List, Dict

class AcademicSearchTool:
    def search(self, query: str) -> List[Dict[str, str]]:
        return [
            {"title": f"{query} Research", "url": f"https://example.com/{query}", "year": "2024"}
        ]