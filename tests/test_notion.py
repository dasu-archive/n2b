'''
Notion 테스트
'''
import os

from dotenv import load_dotenv
from notion.notion import NotionBot
from tistory.tistory import TistoryBot
load_dotenv()

notion_bot  = NotionBot()
tistory_bot = TistoryBot()

# 카테고리 mapping 까지 테스트
def test_notion_to_tistory_mapping():
    # 1. attributes 업데이트. TODO: 카테고리 항목 env 로 관리하도록 변경 필요
    notion_bot.update_attributes(["Category", "Group"])

    # 2. 페이지 리스트 가져오기
    pages = notion_bot.get_preprocessed_notion_pages_info(limit=15)
    
    for page in pages["results"]:
        # 3. 페이지의 매핑 확인
        attribute_mapping = notion_bot.update_attribute_mappings(category_id=page["category_id"], group_id=page["group_id"])
        