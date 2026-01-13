# (주)신우금속 방화유리문 시공 안내 및 AI 도우미 배포 가이드

본 프로젝트는 방화유리문 시공 준수사항 안내와 실시간 검색 기반의 AI 챗봇 기능을 제공하는 웹 애플리케이션입니다.

## 📦 파일 구성
- `index.html`: 프론트엔드 웹페이지 (로고, 안내문, 챗봇 UI)
- `main.py`: 백엔드 API 서버 (FastAPI, OpenAI RAG 로직)
- `new_logo.png`: (주)신우금속 로고 이미지
- `requirements.txt`: 필요한 Python 라이브러리 목록

## 🚀 배포 방법 (Render.com 권장)

1. **GitHub 저장소 생성**: GitHub에 새로운 저장소를 만들고 모든 파일을 업로드합니다.
2. **Render.com 연동**: Render.com에서 'New Web Service'를 선택하고 GitHub 저장소를 연결합니다.
3. **설정 입력**:
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **환경 변수 설정**:
   - 'Environment' 탭에서 `OPENAI_API_KEY`를 추가하고 본인의 OpenAI API 키를 입력합니다.

## 🛠️ 로컬 실행 방법
1. Python 설치 확인
2. 라이브러리 설치: `pip install -r requirements.txt`
3. 환경 변수 설정: `export OPENAI_API_KEY='your_api_key_here'`
4. 서버 실행: `python main.py`
5. 브라우저 접속: `http://localhost:8080`

---
문의: (주)신우금속 (swst6253@naver.com)
