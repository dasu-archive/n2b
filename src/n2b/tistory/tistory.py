import json
import requests
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from n2b.database.models import AttributesMapping
from n2b.database.mysql_conf import SessionLocal
from n2b.database.repository.attribute_repository import count_mappings_by_parent_id, update_attributes_mapping_tistory_id

load_dotenv()

class TistoryBot:
    def __init__(self):
        self.base_url = os.getenv("TISTORY_API_BASE_URL")
        self.access_token = os.getenv("TISTORY_ACCESS_TOKEN")
        self.blog_name = os.getenv("TISTORY_BLOG_NAME")
        self.db = SessionLocal()
    
    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        return self
    
    def __exit__(self, exc_type, exc, tb):
        # 리소스 정리
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
            
            
    def do_login(self):
        page = self.page
        
        # 0. 첫 페이지 이동
        page.goto("https://tistory.com")
        page.wait_for_timeout(1000)  # 🔥 4초 대기

        # 1. 첫 버튼 클릭
        btn1 = page.locator('xpath=//*[@id="mArticle"]/div/div[2]/div/div[1]/a')
        if btn1.is_visible():
            btn1.click()
            page.wait_for_timeout(1000)  # 🔥 4초 대기
            
        # 2. 두번째 버튼 클릭
        btn2 = page.locator('xpath=/html/body/div[5]/div/div/a[2]')
        if btn2.is_visible():
            btn2.click()
            page.wait_for_timeout(1000)  # 🔥 4초 대기
        # 3. 현재 URL 확인 → 로그인 필요 여부 판단
        page.wait_for_load_state("networkidle")
        if "https://accounts.kakao.com/login" in page.url:
            print("로그인 필요 → 로그인 화면 감지")
            page.wait_for_timeout(1000)

            # 3-1. ID 입력
            page.fill('xpath=//*[@id="loginId--1"]', os.getenv("TISTORY_ID"))
            page.wait_for_timeout(1000)

            # 3-2. PW 입력
            page.fill('xpath=//*[@id="password--2"]', os.getenv("TISTORY_PASSWORD"))
            page.wait_for_timeout(1000)

            # 3-3. 로그인 버튼 클릭
            page.click('xpath=//*[@id="mainContent"]/div/div/form/div[4]/button[1]')
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)
            
            # 4. 2단 인증 처리가 필요할 시, 이메일 인증 입력 사용자한테 받게 하기
            # TODO 조건문 True 없애기. 
            # if True:
            #     print("2단계 인증 필요 → 이메일 인증 처리")

            #     # 4-1. 이메일 인증 버튼 클릭
            #     page.locator("xpath=//*[@id='mainContent']/div/div/div[1]/div/ul/li[2]/a]").click()
            #     page.wait_for_timeout(1000)

            #     # 4-2. 이메일 선택 후 다음 버튼 클릭
            #     page.locator("xpath=//*[@id='mainContent']/div/div/form/div[2]/button").click()
            #     page.wait_for_timeout(1000)

            #     # 4-3. 사용자에게 인증번호 입력 받기
            #     code = input("📧 이메일로 받은 인증번호를 입력하세요: ")
            #     page.fill("xpath=//*[@id='passcode--6']", code)
            #     page.wait_for_timeout(1000)

            #     # 4-4. 확인 버튼 클릭
            #     page.locator("xpath=//*[@id='mainContent']/div/div/form/div[3]/button").click()
            #     page.wait_for_load_state("networkidle")
            #     page.wait_for_timeout(4000)
            #     print("2단계 인증 완료")
            print("로그인 완료")
        else:
            print("이미 로그인되어 있음")
            page.wait_for_timeout(1000)
        
        page.goto(f"{self.base_url}/manage/category")
        
        self.cookies = self._get_cookies()
        self._get_cookies_for_requests()
        
    def _get_cookies(self): 
        return  self.page.context.cookies()
    
    def _get_cookie_headers_for_requests(self):
        return ["__gads","__eoi", "IS_TC","TSSESSION","__T_","__T_SECURE","TSMT","_T_ANO"]
    
    def _get_cookies_for_requests(self):
       
        cookies = self.cookies
        filtered_cookie_headers = self._get_cookie_headers_for_requests()
        cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies if cookie['name'] in filtered_cookie_headers])
        cookie_str += "; TSMT=0"
        return cookie_str    
     
    def _is_kakako_login_page(self):
        return self.page.locator("text=카카오계정 로그인").is_visible()
        
    def upload_post(self, title, content, category_id=None, tag=None):
        url = f"{self.base_url}/manage/post.json"

        cookies = self._get_cookies_for_requests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": f"{self.base_url}/manage/newpost",
            "Origin": f"{self.base_url}",
            "Content-Type": "application/json",
            "Cookie": cookies
        }
        data = {"id":"0",
            "title": title, # String 
            "content": content, # String "<p>32432324</p>\n<h2>2323211</h2>\n
            "slogan":title,
            "visibility":20,
            "category": category_id, # integer
            "tag": " ".join(tag), # String  "111 222 333"
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
        
        response = requests.post(url, headers=headers, json=data)
        print("Tistory Post Upload Response:", response.status_code, response.text)
    
    
    # 카테고리를 넣은후 -> 받은 카테고리 번호를 가져와 -> 내꺼 db에 업데이트 시키기
    # AttributesMapping의 parent 부터 확인
    def update_category(self, attribute_mapping:AttributesMapping):
        
        # 카테고리 업로드 url 
        url = f"{self.base_url}/manage/category.json"
        # 공통 헤더 설정
        headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Referer": f"{self.base_url}/manage/category",
                "Origin": f"{self.base_url}",
                "Content-Type": "application/json",
                "Cookie": self._get_cookies_for_requests()
        }
        
        parent_mapping = attribute_mapping.parent
        if parent_mapping.tistory_id is None or parent_mapping.tistory_id == 0:
            data = self._create_tistoy_category_body(parent_mapping)
            response = requests.put(url, headers=headers, json=data)
            label = attribute_mapping.category.notion_attribute_name
            self._update_attributes_mapping_tistory_id(attribute_mapping.parent, response, label)
            print("[create] Tistory Category", response.status_code)
            
        if attribute_mapping.tistory_id is None or attribute_mapping.tistory_id == 0:
            data = self._create_tistoy_category_body(attribute_mapping)
            response = requests.put(url, headers=headers, json=data)
            label = attribute_mapping.category.notion_attribute_name + "/" + attribute_mapping.group.notion_attribute_name
            self._update_attributes_mapping_tistory_id(attribute_mapping, response, label)
            print("[create] Tistory Category", response.status_code)
            
            
    # Response 를 받아 text 로 json 반환
    def _update_attributes_mapping_tistory_id(self,attribute_mapping:AttributesMapping, response, label:str):
        try:
            data = json.loads(response.text)
        except:
            data = response.text
        tistory_id = self._find_id_by_label(data=data, label=label)
        update_attributes_mapping_tistory_id(session=self.db, attributes_mapping=attribute_mapping, tistory_id=tistory_id)
        
        
    # Label 찾기
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
        
        
    # 카테고리 체크 항목
    # 1. priority ( 순서 명확해야 함 )
    # 2. parent 
    # 3. depth
    # 4. Category Lable
    # 5. name
    # 6. tistory_id
    def _create_tistoy_category_body(self, attribute_mapping:AttributesMapping):
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
            
                