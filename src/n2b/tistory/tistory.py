import requests
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

class TistoryBot:
    def __init__(self):
        self.base_url = os.getenv("TISTORY_API_BASE_URL")
        self.access_token = os.getenv("TISTORY_ACCESS_TOKEN")
        self.blog_name = os.getenv("TISTORY_BLOG_NAME")
    
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
            page.wait_for_timeout(100000)
            
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
        
    def _get_cookies(self): 
        return  self.page.context.cookies()
        
    def _is_kakako_login_page(self):
        return self.page.locator("text=카카오계정 로그인").is_visible()
        
    def update_category_mappings(self, modify_request_dto):
        url = f"{self.base_url}/manage/category.json"
        headers = {
            "Authorization":