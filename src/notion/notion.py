from notion_client import Client
from notion_to_md import NotionToMarkdown

import os

from database.mysql_conf import SessionLocal
from database.models import Attributes, AttributesMapping, init_tables
from notion.notion_api import notion_api
from database.repository.attribute_repository import get_mappings_by_notion_id, get_attribute_by_notion_attribute_id


class NotionBot:
    def __init__(self):
        self.n2m = NotionToMarkdown(Client(auth=os.getenv("NOTION_API_KEY")))
        self.notion_api = notion_api()
        init_tables()
        self.db = SessionLocal()

    '''
    Notion 페이지 관련 기능
    '''
    # Notion 페이지 정보 불러오기
    # return: dict
    def get_notion_page_info(self, page_id: str):
        return self.notion_api.get_page(page_id)
    
    # Notion 정제된 페이지 정보 불러오기
    # return dict
    def get_preprocessed_notion_page_info(self, page_id: str):
        return self._preprocess_notion_page(self.get_notion_page_info(page_id=page_id))
    
    # Notion 정제된 페이지 리스트 불러오기
    # return: list
    def get_preprocessed_notion_pages_info(self, database_id: str = None, page_size: int = 15, csutom_filter: dict = None ):
        notion_pages = self.get_notion_pages_info(database_id, page_size, csutom_filter)
        preprocessed_notion_pages = []
        for page in notion_pages["results"]:
            preprocessed_notion_pages.append(self._preprocess_notion_page(page))
        return preprocessed_notion_pages
        
    def _preprocess_notion_page(self, page: dict):
        # 비어있을 수 있으므로
        tags_data = page["properties"]["태그"]["multi_select"]
        return {
            "id": page["id"],
            "title": page["properties"]["이름"]["title"][0]["plain_text"],
            "type": page["properties"]["Type"]["select"]["name"],
            "category_id": page["properties"]["Category"]["select"]["id"],
            "category": page["properties"]["Category"]["select"]["name"],
            "group_id": page["properties"]["Group"]["select"]["id"],
            "group": page["properties"]["Group"]["select"]["name"],
            "tags": [value["name"] for value in tags_data] if tags_data else []
        }
        
    # Notion 페이지 리스트 불러오기
    def get_notion_pages_info(self, database_id: str = None, page_size: int = 15, csutom_filter: dict = None   ):
        filter = csutom_filter or {
            "and": [
                {
                    "property": "Status",
                    "status": { "equals": "완료" }
                },
                {
                    "or": [
                        {
                            "property": "Type",
                            "select": { "equals": "DeveloperGoal" }
                        },
                        {
                            "property": "Type",
                            "select": { "equals": "CodingTest" }
                        },
                        {
                            "property": "Type",
                            "select": { "equals": "Project" }
                        }
                    ]
                },
                {
                    "property": "발행날짜",
                    "date": {
                        "is_empty": True
                    }
                    
                }
            ]
        }
        return self.notion_api.get_pages(filter=filter)
    


    # Notion 페이지를 마크다운으로 변환
    def get_page_to_markdown(self, page_id: str):
        return self.n2m.to_markdown_string(self.n2m.page_to_markdown(page_id)).get("parent")
    
    def save_markdown_to_file(self, page_id: str, filename: str):
        """마크다운 문자열을 파일로 저장"""
        
        # 1. 마크다운 내용 가져오기
        markdown_content = self.get_page_to_markdown(page_id)
        
        # 2. 파일 저장 경로 및 이름 설정
        output_dir = "output_md"
        # 디렉토리가 없으면 생성
        os.makedirs(output_dir, exist_ok=True) 
        
        file_path = os.path.join(output_dir, filename)
        
        # 3. 파일 쓰기 (UTF-8 인코딩 사용 권장)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"✅ 마크다운 파일이 성공적으로 저장되었습니다: {file_path}")
        except Exception as e:
            print(f"❌ 파일 저장 중 오류 발생: {e}")
            
            
            
            
    def update_publication_date(self, page_id: str):
        from datetime import datetime
        self.notion_api.update_page_properties(
            page_id,
            {
                "발행날짜": {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                }
            }
        )
        return True
    '''
    Notion 속성 관련 기능
    '''
    # 속성 전체 불러오기
    # return: Dict[category:str, List[Attribute]]
    def get_attributes(self):
        attributes = self.db.query(Attributes).all()
        attributes_seperated = {"Category": [], "Group": []}
        for attr in attributes:
            attributes_seperated[attr.attribute_kind].append(attr)
        return attributes_seperated
    
    # 해당 카테고리 불러오기
    # return: List[Attribute]
    def get_attributes(self, category: str):
        return self.db.query(Attributes).filter_by(attribute_kind=category).all()
    
    # 해당 카테고리 및 이름으로 속성 불러오기
    # return: Attribute
    def get_attribute_by_name(self, category: str, name: str):
        return self.db.query(Attributes).filter_by(
            attribute_kind=category,
            notion_attribute_name=name
        ).first()
    
    # Notion에서 속성 불러와서 데이터베이스에 업데이트
    # return: bool
    def update_attributes(self, categories =  ["Category", "Group"]):
        data_sources = self.notion_api.get_notion_data_sources()

        for category in categories:
           attribute_value_list =  data_sources["properties"][category]["select"]["options"]
           self.update_attribute_in_database(attribute_value_list, category)

        return True
    
    # List 데이터 정제 및 데이터베이스 업데이트
    # return: bool
    def update_attribute_in_database(self, attribute_value_list, category):
        for value in attribute_value_list:
            # UPSERT 구현: MySQL에서는 ON DUPLICATE KEY 가능, SQLAlchemy는 merge 사용
            attr = self.db.query(Attributes).filter_by(notion_attribute_id=value["id"]).first()
            if attr:
                attr.notion_attribute_name = value["name"]
                attr.attribute_kind = category
            else:
                attr = Attributes(
                    notion_attribute_id=value["id"],
                    notion_attribute_name=value["name"],
                    attribute_kind=category
                )
                self.db.add(attr)
        self.db.commit()
        return True

    # 속성 매핑 업데이트
    # return: AttributesMapping

    
    def update_attribute_mappings_by_id(self, category_id: str, group_id: str, tistory_id: int = 0)->AttributesMapping:
        attribute_mapping = get_mappings_by_notion_id(session=self.db, category_id=category_id, group_id=group_id)
        
        if not attribute_mapping:
            parent = get_attribute_by_notion_attribute_id(session=self.db,attribute_id=category_id, kind="Category")
            child = get_attribute_by_notion_attribute_id(session=self.db,attribute_id=group_id, kind="Group")
            attribute_mapping = self.update_attribute_mappings_by_attributes(
                parent=parent,
                child=child,
                tistory_id=tistory_id
            )   

        return attribute_mapping
        
        
    def update_attribute_mappings_by_attributes(self, parent: Attributes, child: Attributes, tistory_id: int = 0)->AttributesMapping:
        attribute_mapping = self.db.query(AttributesMapping).filter_by(
            category_id=parent.id,
            group_id=child.id
        ).first()
        
        if not attribute_mapping:
            attribute_mapping = AttributesMapping(
                category_id=parent.id,
                group_id=child.id,
                tistory_id=tistory_id or 0
            )
            self.db.add(attribute_mapping)
            self.db.commit()
            self.db.refresh(attribute_mapping)
        else:
            pass
        return attribute_mapping
    