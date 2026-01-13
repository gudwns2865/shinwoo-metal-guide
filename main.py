import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini 설정 (환경 변수 확인 로직 강화)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("에러: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
else:
    genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')

# 안내문 원본 텍스트
GUIDE_CONTENT = """
[방화유리문(인정제품) 발주 및 시공 준수사항]
1. 주요 시공 준수 표준
- 방화문 손잡이 설치 높이: 일반 800~1,050mm, 장애인 800~900mm
- 방화문 개폐 유효폭: 일반 900mm 권장, 장애인 반드시 900mm 이상 확보
- 프레임 사면(4면) 구속: 4면을 내화구조체에 고정 (건축물 피난·방화구조 규칙 제3조 참고)
2. 주의사항: 하드웨어 임의 변경 금지, 현장 가공(타공, 절단) 금지
3. 필수 제출 자료: 품질확인 점검표, 시공 사진, 전액 입금 확인 (계산서 발행 사업자 명의로 발행)
"""

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not api_key:
        return {"response": "서버 설정 오류: API 키가 등록되지 않았습니다. Render 설정을 확인해 주세요."}
    
    try:
        prompt = f"""
        당신은 (주)신우금속의 방화문 시공 전문 AI 도우미입니다.
        지침:
        1. 아래 [안내문 내용]을 최우선으로 참고하여 답변하세요.
        2. 안내문에 없는 내용은 실시간 지식을 바탕으로 전문적으로 답변하세요.
        3. 한국어로 답변하고, 중요 수치는 볼드체(**)를 사용하세요.
        4. 줄바꿈을 적절히 사용하여 가독성을 높이세요.

        [안내문 내용]
        {GUIDE_CONTENT}

        사용자 질문: {request.message}
        """
        # 비동기 방식으로 호출하여 안정성 강화
        response = await model.generate_content_async(prompt)
        return {"response": response.text}
    except Exception as e:
        print(f"AI 호출 중 오류 발생: {str(e)}")
        return {"response": f"AI 서비스 연결 중 오류가 발생했습니다: {str(e)}"}

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/logo.png")
async def get_logo():
    return FileResponse("new_logo.png")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
