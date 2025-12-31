import json
import requests
import os
from dotenv import load_dotenv

from n2b.database.models import AttributesMapping
from n2b.database.mysql_conf import SessionLocal
from n2b.database.repository.attribute_repository import count_mappings_by_parent_id, update_attributes_mapping_tistory_id
from n2b.tistory.api.tistory_api import TistoryApi

load_dotenv()

class TistoryBot:
    def __init__(self):
        self.base_url = os.getenv("TISTORY_API_BASE_URL")
        self.access_token = os.getenv("TISTORY_ACCESS_TOKEN")
        self.blog_name = os.getenv("TISTORY_BLOG_NAME")
        self.db = SessionLocal()
        self.api = TistoryApi()
    

    
    # 게시글 업로드
    def upload_post(self, title, content, category_id=None, tag=None):

        data = {"id":"0",
            "title": title, # String 
            "content": content, # String "<p>32432324</p>\n<h2>2323211</h2>\n
            "slogan":title,
            "visibility":20,
            "category": category_id, # integer
            "tag": ",".join(tag), # String  "111 222 333"
            "published":1,
            "password":"test1234",
            "uselessMarginForEntry":1,
            "daumLike":"401",
            "cclCommercial":0,
            "cclDerive":0,
            "type":"post",
            "attachments":[],
            "recaptchaValue":"",
            "draftSequence":None
        }
        
        response = self.api.post_post_request(data=data)
    
    # 카테고리 업로드
    def update_category(self, attribute_mapping:AttributesMapping, tistory_categories:json):
        # 카테고리를 넣은후 -> 받은 카테고리 번호를 가져와 -> 내꺼 db에 업데이트 시키기
        parent_mapping = attribute_mapping.parent
        self._check_and_update_category(parent_mapping,tistory_categories, is_child=False)
        self._check_and_update_category(attribute_mapping, tistory_categories, is_child=True)

            
    # 카테고리 업데이트
    # parent = 카테고리 업로드
    def _check_and_update_category(self, attribute_mapping:AttributesMapping, tistory_categories:json, is_child:bool=True):
        if attribute_mapping.tistory_id is None or attribute_mapping.tistory_id == 0:
            # 카테고리 tistory_id 업데이트
            label = attribute_mapping.category.notion_attribute_name + (("/" + attribute_mapping.group.notion_attribute_name) if is_child  else "")
            tistory_id = self._find_existing_category_in_now_tistory(label=label, tistory_categories=tistory_categories, is_child=is_child)
            # 현재 카테고리가 tistory 에 없을때 생성 후 업데이트 
            if  tistory_id is None:
                # body 생성
                data = self._create_tistoy_category_body(attribute_mapping)
                # 카테고리 생성 요청
                response = self.api.put_category_request(data=data)
                # 카테고리 tistory_id 업데이트
                self._update_attributes_mapping_tistory_id(attribute_mapping, response, label)    
                
            # 현재 카테고리에 적혀있진 않은데 tistory 에 카테고리가 있을 경우 id 만 업데이트 
            else:
                update_attributes_mapping_tistory_id(session=self.db, attributes_mapping=attribute_mapping, tistory_id=tistory_id)
                
            
    # 기존 티스토리 카테고리에서 존재하는지 찾기
    # parent = 카테고리 업데이트
    def _find_existing_category_in_now_tistory(self, label:str, tistory_categories:json, is_child:bool=True):
        find_category = label.split("/")[0]
        for category in tistory_categories:
            if category["label"] == find_category:
                if is_child:
                    # 자식 카테고리 확인
                    for child in category.get("children", []):
                        if child["label"] == label:
                            return child["id"]
                return category["id"]
        return None
    
    
    # 카테고리 생성용 body 생성
    # parent = 카테고리 업데이트
    def _create_tistoy_category_body(self, attribute_mapping:AttributesMapping):
        
        # 1. priority ( 순서 명확해야 함 )
        # 2. parent 
        # 3. depth
        # 4. Category Lable
        # 5. name
        # 6. tistory_id
        is_parent = attribute_mapping.parent_id == None 
  
        # Category 
        if is_parent:
            # tistory_id  어차피 0 
            parent_tistory_id = 0
            
            depth = 1
            # categoryLabel : [Category]
            categoryLabel = attribute_mapping.category.notion_attribute_name
            # priority : category 개수
            priority = count_mappings_by_parent_id(session=self.db)
            # name
            name = attribute_mapping.category.notion_attribute_name
            
        # Group 
        else:
            # parent : parent의 tistory id , default = 0 
            parent_tistory_id =  attribute_mapping.parent.tistory_id
            depth = 2
            # categoryLabel : [Category]/[Group]
            categoryLabel = attribute_mapping.category.notion_attribute_name + "/" + attribute_mapping.group.notion_attribute_name
            # priority : group 개수 
            priority = count_mappings_by_parent_id(session=self.db, parent_id=attribute_mapping.parent_id)
            # name
            name = attribute_mapping.group.notion_attribute_name
            

            
        data =  {
                    "rootLabel": "분류 전체보기",
                    "delete": [],
                    "append": [
                        {
                            "id": -1,
                            "name": name,
                            "children": [],
                            "depth": depth,
                            "opened": True,
                            "priority": priority,
                            "visibility": 20,
                            "parent": parent_tistory_id, # 없을 시 0
                            "viewChannel": "401", # IT,인터넷 고정
                            "entries": 0,
                            "categoryInfo": {},
                            "isNew": True,
                            "updatedData": True,
                            "label": categoryLabel # [Category]/[Group] 형식 
                        }
                    ],
                    "update": [
                        {
                            "id": -1,
                            "name": name,
                            "children": [],
                            "depth": depth,
                            "opened": True,
                            "priority": priority,
                            "visibility": 20,
                            "parent": parent_tistory_id, # 없을 시 0
                            "viewChannel": "401", # IT,인터넷 고정
                            "entries": 0,
                            "categoryInfo": {},
                            "isNew": True,
                            "updatedData": True,
                            "label": categoryLabel # [Category]/[Group] 형식 
                        }
                    ]
                }
            
        return data
                    
    # tistory_id 업데이트
    # parent = 카테고리 업데이트
    def _update_attributes_mapping_tistory_id(self,attribute_mapping:AttributesMapping, response, label:str):
        try:
            data = json.loads(response.text)
        except:
            data = response.text
        tistory_id = self._find_id_by_label(data=data, label=label)
        update_attributes_mapping_tistory_id(session=self.db, attributes_mapping=attribute_mapping, tistory_id=tistory_id)
    


        
    # Label 찾기
    # parent = tistory_id 업데이트
    def _find_id_by_label(self, data, label:str):
        
        # categoryTree를 재귀 탐색
        def search_tree(tree_list):
            for node in tree_list:
                if node.get("label") == label:
                    return node.get("id")
                # children가 있으면 재귀 탐색
                children = node.get("children", [])
                if children:
                    result = search_tree(children)
                    if result is not None:
                        return result
            return None

        # 우선 categoryTree에서 검색
        result = search_tree(data.get("categoryTree", []))
        if result is not None:
            return result
        
        
    # 카테고리 가져오기
    def get_tistory_category_list(self):
        response = self.api.get_category_list()
        data = json.loads(response.text)
        return data["categories"]
        
