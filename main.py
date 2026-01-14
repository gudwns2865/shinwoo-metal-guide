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

# 1. Gemini 설정 및 모델 자동 선택 로직
api_key = os.environ.get("GEMINI_API_KEY")
model = None

if not api_key:
    print("❌ 에러: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
else:
    genai.configure(api_key=api_key)
    try:
        # 사용 가능한 모델 목록 가져오기
        available_models = [
            m.name for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
        
        if available_models:
            # 우선순위: gemini-1.5-flash -> gemini-1.5-pro -> 리스트의 첫 번째 모델
            selected_model_name = None
            for target in ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-pro']:
                if target in available_models:
                    selected_model_name = target
                    break
            
            if not selected_model_name:
                selected_model_name = available_models[0]
            
            model = genai.GenerativeModel(selected_model_name)
            print(f"✅ AI 모델 연결 성공: {selected_model_name}")
        else:
            print("❌ 에러: 사용 가능한 Gemini 모델이 없습니다.")
    except Exception as e:
        print(f"❌ 모델 초기화 중 오류 발생: {e}")

# 안내문 원본 텍스트
GUIDE_CONTENT = """
[방화유리문(인정제품) 발주 및 시공 준수사항]
1. 주요 시공 준수 표준
- 방화문 손잡이 설치 높이: 일반 800~1,050mm, 장애인 800~900mm
- 방화문 개폐 유효폭: 일반 900mm 권장, 장애인 반드시 900mm 이상 확보
- 프레임 사면(4면) 구속: 4면을 내화구조체에 고정 (건축물 피난·방화구조 규칙 제3조 참고)
2. 주의사항: 하드웨어 임의 변경 금지, 현장 가공(타공, 절단) 금지
3. 인정서 요청 필수 제출 자료: 품질확인 점검표, 시공 사진, 전액 입금 확인 (계산서 발행 사업자 명의로 발행)
"""

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    # 2. 예외 처리 강화
    if not api_key:
        return {"response": "서버 설정 오류: API 키가 등록되지 않았습니다."}
    if not model:
        return {"response": "AI 모델을 초기화할 수 없습니다. API 키 권한을 확인하세요."}
    
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
        
        # 비동기 호출
        response = await model.generate_content_async(prompt)
        return {"response": response.text}
        
    except Exception as e:
        print(f"AI 호출 중 오류 발생: {str(e)}")
        # 에러 메시지가 너무 길 경우를 대비해 요약된 메시지 반환
        return {"response": f"AI 서비스 연결 중 오류가 발생했습니다. (사유: {str(e)[:100]})"}

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/logo.png")
async def get_logo():
    # 파일명 오타 방지를 위해 실제 존재하는 파일명으로 확인 필요 (new_logo.png vs logo.png)
    # 기존 코드에서 new_logo.png를 반환하도록 되어 있어 유지합니다.
    return FileResponse("new_logo.png")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
