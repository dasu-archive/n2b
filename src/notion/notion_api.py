import requests
import os
from dotenv import load_dotenv
load_dotenv()
class notion_api:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("NOTION_API_KEY")
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2025-09-03",
            "Content-Type": "application/json",
            "accept": "application/json"
        }

    '''
    Notion Page API
    '''
    
    # 페이지 정보 가져오기
    def get_page(self, page_id: str):
        url = f"{self.base_url}/pages/{page_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    # 페이지 리스트 가져오기
    def get_pages(self, data_source_id = None, page_size:int = 15, filter: dict = None, sorts: dict = None):
        data_source_id = data_source_id or os.getenv("NOTION_DATA_SOURCE_ID")
        if data_source_id is None:
            raise ValueError("Database ID must be provided either as an argument or through the NOTION_DATABASE_ID environment variable.")
        
        url = f"{self.base_url}/data_sources/{data_source_id}/query"
        
        payload = {
            "page_size": page_size,
            "filter": filter or {},
            "sorts" : sorts or  [{
                "property": "시행날짜",
                "direction": "descending"
            }]
        }
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()
    
    def update_page_properties(self, page_id: str, properties: dict):
        url = f"{self.base_url}/pages/{page_id}"
        payload = {
            "properties": properties
        }
        response = requests.patch(url, headers=self._change_header_notion_version("2022-06-28"), json=payload)
        return response.json()
    
    def _change_header_notion_version(self, version: str):
        changed_header = self.headers.copy()
        changed_header["Notion-Version"] = version
        return changed_header
    '''
    Notion Database API
    '''
    
    # data source 정보 가져오기, 속성값, 데이터베이스 이름 등.
    def get_notion_data_sources(self,  data_source_id = None):
        data_source_id = data_source_id or os.getenv("NOTION_DATA_SOURCE_ID")
        if data_source_id is None:
            raise ValueError("Data source ID must be provided either as an argument or through the NOTION_DATA_SOURCE_ID environment variable.")
        url = f"{self.base_url}/data_sources/{data_source_id}"

        response = requests.get(url, headers=self.headers)
        return response.json()

    # 데이터베이스 정보 가져오기
    def get_database(self, database_id = None):
        database_id = database_id or os.getenv("NOTION_DATABASE_ID")
        if database_id is None:
            raise ValueError("Database ID must be provided either as an argument or through the NOTION_DATABASE_ID environment variable.")
        
        url = f"{self.base_url}/databases/{os.getenv('NOTION_DATABASE_ID')}"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
