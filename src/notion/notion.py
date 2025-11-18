from notion_client import Client
from notion_to_md import NotionToMarkdown
import os

notion = Client(auth=os.getenv("NOTION_API_KEY"))

class notion_bot:
    def __init__(self):
        self.n2m = NotionToMarkdown(notion)

    def download_page_as_markdown(self, page_id: str) -> str:
        markdown = self.n2m.page_to_markdown(page_id)
        md_content = self.n2m.to_markdown_string(markdown)
        return md_content
    
    def get_page_to_databases(self, database_id: str):
        results = notion.databases.query(database_id=database_id).get("results")
        return results
    
    def get_new_pages_from_database(self, database_id: str, last_checked_time: str):
        results = notion.databases.query(
            database_id=database_id,
            filter={
                "property": "Last Edited Time",
                "last_edited_time": {
                    "after": last_checked_time
                }
            }
        ).get("results")
        return results
    

    def update_attribute(self, page_id: str, properties: dict):
        notion.pages.update(
            page_id=page_id,
            properties=properties
        )
        