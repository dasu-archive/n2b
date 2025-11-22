
import asyncio
from n2b.notion.notion import NotionBot
from dotenv import load_dotenv
import json

from n2b.tistory.tistory import TistoryBot
load_dotenv()

# if __name__ == "__main__":
#     notion_bot  = NotionBot()
#     tistory_bot = TistoryBot()
#     # 1. attributes 업데이트. TODO: 카테고리 항목 env 로 관리하도록 변경 필요
#     notion_bot.update_attributes(["Category", "Group"])

#     # 2. 페이지 리스트 가져오기
#     pages = notion_bot.get_preprocessed_notion_pages_info(page_size=15)

#     for page in pages:

        # 3. 페이지의 매핑 확인
        # attribute_mapping = notion_bot.update_attribute_mappings_by_id(category_id=page["category_id"], group_id=page["group_id"])
        
        # # 4. tistory 에 카테고리 확인 및 생성 요청
        # if attribute_mapping.tistory_id is None | attribute_mapping.tistory_id == 0:
        #     tistory_bot.update_category(attribute_mapping)
        
        # # 5. 페이지 to markdown 변환 및 포스팅
        # markdown_content = notion_bot.get_page_to_markdown(page_id=page["id"])
        
        # Test. markdown 확인
        
        # # 6. tistory 에 md 업로드
        # tistory_bot.upload_markdown_post(attribute_mapping=attribute_mapping, page_info=page, content=markdown_content)
        
        # 7 notion 에 업로드 처리
        # notion_bot.update_publication_date(page["id"])
                

# Test 
if __name__ == "__main__":
    with TistoryBot() as bot:
        bot.do_login()
    
