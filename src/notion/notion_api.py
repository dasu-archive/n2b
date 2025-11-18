import requests
import os
from dotenv import load_dotenv
load_dotenv()
class notion_api:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("NOTION_API_KEY")
        self.base_url = "https://api.notion.com/v1/"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2025-09-03",
            "Content-Type": "application/json"
        }


    def get_page(self, page_id):
        url = f"{self.base_url}pages/{page_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()
    def get_database(self, database_id):
        url = f"{self.base_url}data_sources/{database_id}/query"
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    def update_page(self, page_id, properties):
        url = f"{self.base_url}pages/{page_id}"
        data = {
            "properties": properties
        }
        response = requests.patch(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    def download_page_content(self, page_id):
        url = f"{self.base_url}blocks/{page_id}/children"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    

if __name__ == "__main__":
    notion_api = notion_api()
    notion_api.get_page("")