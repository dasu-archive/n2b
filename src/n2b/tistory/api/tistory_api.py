import os
from dotenv import load_dotenv
import requests
from playwright.sync_api import sync_playwright

load_dotenv()

class TistoryApi:
    
    def __init__(self):
        self.base_url = os.getenv("TISTORY_API_BASE_URL")
        self.blog_name = os.getenv("TISTORY_BLOG_NAME")
        
        self.do_login()
    
    # 로그인 로직 ( Cookie 얻기 )
    def do_login(self):
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 0. 첫 페이지 이동
        page.goto("https://tistory.com")
        page.wait_for_timeout(1000)  

        # 1. 첫 버튼 클릭
        btn1 = page.locator('xpath=//*[@id="mArticle"]/div/div[2]/div/div[1]/a')
        if btn1.is_visible():
            btn1.click()
            page.wait_for_timeout(1000)  
            
        # 2. 두번째 버튼 클릭
        btn2 = page.locator('xpath=/html/body/div[5]/div/div/a[2]')
        if btn2.is_visible():
            btn2.click()
            page.wait_for_timeout(1000) 
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
        
        self.cookies = page.context.cookies()
        self._get_cookies_for_requests()
        
        if browser:
            browser.close()
        if playwright:
            playwright.stop()
    # 필요한 쿠키 필터링 헤더 목록 
    def _get_cookie_headers_for_requests(self):
        return ["__gads","__eoi", "IS_TC","TSSESSION","__T_","__T_SECURE","TSMT","_T_ANO"]
    # 필요한 쿠기 값들만 추출
    def _get_cookies_for_requests(self):
       
        cookies = self.cookies
        filtered_cookie_headers = self._get_cookie_headers_for_requests()
        cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies if cookie['name'] in filtered_cookie_headers])
        cookie_str += "; TSMT=0"
        return cookie_str    
    # header 생성
    def _get_headers(self, referer: str):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": referer,
            "Origin": f"{self.base_url}",
            "Content-Type": "application/json",
            "Cookie": self._get_cookies_for_requests()
        }
        return headers

    # 게시글 업로드
    def post_post_request(self, data):
    
        url = f"{self.base_url}/manage/post.json"
        cookies = self._get_cookies_for_requests()
        headers = self._get_headers(f"{self.base_url}/manage/newpost")
        response = requests.post(url, headers=headers, json=data)
        return response
        
    # 카테고리 넣기
    def put_category_request(self, data):
        url = f"{self.base_url}/manage/category.json"
        headers = self._get_headers(f"{self.base_url}/manage/category")
        response = requests.put(url, headers=headers, json=data)
        return response
        
    # 카테고리 가져오기
    def get_category_list(self):
        
        # 카테고리 업로드 url 
        url = f"{self.base_url}/manage/category.json"
        # 공통 헤더 설정
        headers = self._get_headers(f"{self.base_url}/manage/category") 
        response = requests.get(url, headers=headers)
        return response