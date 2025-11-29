
import asyncio
import os
from n2b.notion.notion import NotionBot
from dotenv import load_dotenv
import json

from n2b.tistory.tistory import TistoryBot
load_dotenv()


# Tistory 로그인 및 포스팅 테스트
def test_tistory_login_and_upload():
    with TistoryBot() as bot:
        bot.do_login()
        bot.upload_post(
            title="테스트 업로드 제목",
            content="<p>테스트 업로드 내용<p>\n",
            category_id=1176809,
            tag=["테스트", "업로드"])
# Tistory 카테고리 업데이트 테스트
def test_tistory_category_update():
    notion_bot = NotionBot()
    with TistoryBot() as tistory_bot:
        # 1. 페이지 가져오기
        page = notion_bot.get_preprocessed_notion_page_info(page_id="")
        
        # 2. 페이지에 설정된 카테고리 그룹 매핑 업데이트 하기
        attribute_mapping = notion_bot.update_attribute_mappings_by_id(category_id=page["category_id"], group_id=page["group_id"])
        
        # 3. 티스토리 로그인
        tistory_bot.do_login()
        
        # 4. 카테고리 업데이트
        tistory_bot.update_category(attribute_mapping=attribute_mapping)

# 메인 기능 
def run():
    notion_bot  = NotionBot()
    tistory_bot = TistoryBot()
    # 1. attributes 업데이트. TODO: 카테고리 항목 env 로 관리하도록 변경 필요
    notion_bot.update_attributes(["Category", "Group"])

    # 2. 페이지 리스트 가져오기
    pages = notion_bot.get_preprocessed_notion_pages_info(page_size=15)

    for page in pages:

        # 3. 페이지의 매핑 확인
        attribute_mapping = notion_bot.update_attribute_mappings_by_id(category_id=page["category_id"], group_id=page["group_id"])
        
        # 4. tistory 에 카테고리 확인 및 생성 요청
        if attribute_mapping.tistory_id is None || attribute_mapping.tistory_id == 0:
            tistory_bot.update_category(attribute_mapping)
        
        # 5. 페이지 to markdown 변환 및 포스팅
        markdown_content = notion_bot.get_page_to_markdown(page_id=page["id"])
        
        '''
        TODO : markdown to content 를 하던가 to html 로 바로 하는 방법 찾기
        '''
        
        # 6. tistory 에 md 업로드
        tistory_bot.upload_post(title=page["title"], content=markdown_content, tag=page["tags"], category_id=attribute_mapping.tistory_id)
        
        # 7 notion 에 업로드 처리
        notion_bot.update_publication_date(page["id"])

if __name__ == "__main__":

    test_tistory_category_update()
        
    

