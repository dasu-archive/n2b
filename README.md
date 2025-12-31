# n2b

간단한 노션(Notion) → 티스토리(Tistory) 전송 도구입니다. 노션에서 글을 읽어와 필요한 변환을 거친 뒤 티스토리에 업로드하고, 일부 데이터를 로컬 MySQL에 관리합니다. 

---

## 주요 기능 ✅

- Notion에서 콘텐츠를 읽어오기 (`src/n2b/notion/`)
- Notion 콘텐츠 변환 (예: HTML 변환, 필터링)
- 티스토리 API로 글 업로드 (`src/n2b/tistory/`)
- MySQL에 일부 메타데이터/설정 저장 (`src/n2b/database/`)

---

## 설치 및 실행 💡

1. 저장소 클론

   git clone <repo-url>

2. 의존성 설치 (Poetry 권장)

   poetry install

3. 환경 변수 설정

   - Notion, Tistory API 키 및 MySQL 접속 정보 설정 필요
   - 프로젝트 루트 또는 실행 환경에 환경 변수로 추가

4. 실행

   - Poetry 사용: `poetry run n2b`
   - 또는: `python -m src.n2b.main`

---

## 프로젝트 구조 🔍

- `src/n2b/`
  - `notion/` — Notion API, 변환 로직
  - `tistory/` — 티스토리 API 래퍼 및 업로드 로직
  - `database/` — 모델 및 저장소(repository)
  - `main.py` — 실행 진입점


