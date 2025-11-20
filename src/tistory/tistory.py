import requests
import os
from dotenv import load_dotenv

load_dotenv()

class TistoryBot:
    def __init__(self):
        self.base_url = os.getenv("TISTORY_API_BASE_URL")
        self.access_token = os.getenv("TISTORY_ACCESS_TOKEN")
        self.blog_name = os.getenv("TISTORY_BLOG_NAME")


    def update_category(self, modify_request_dto):
        url = f"{self.base_url}/manage/category.json"
        params = {
            "access_token": self.access_token,
            "blogName": self.blog_name,
            "append": [cat.dict() for cat in modify_request_dto.append],
            "delete": modify_request_dto.delete,
            "rootLabel": modify_request_dto.rootLabel,
            "update": [cat.dict() for cat in modify_request_dto.update]
        }
        response = requests.post(url, json=params)
        return response.json()