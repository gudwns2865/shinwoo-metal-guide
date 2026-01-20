import os
import time
import asyncio
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Gemini 설정 및 모델 자동 선택
api_key = os.environ.get("GEMINI_API_KEY")
model = None

def setup_model():
    global model
    if not api_key:
        print("❌ 에러: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        return
    
    genai.configure(api_key=api_key)
    try:
        available_models = [
            m.name for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
        
        if available_models:
            # 무료 티어에서 가장 쿼터가 넉넉한 1.5-flash를 1순위로 고정
            selected_model_name = 'models/gemini-1.5-flash' 
            if selected_model_name not in available_models:
                selected_model_name = available_models[0]
            
            model = genai.GenerativeModel(selected_model_name)
            print(f"✅ AI 모델 연결 성공: {selected_model_name}")
        else:
            print("❌ 에러: 사용 가능한 Gemini 모델이 없습니다.")
    except Exception as e:
        print(f"❌ 모델 초기화 중 오류 발생: {e}")

setup_model()

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
    if not api_key:
        return {"response": "서버 설정 오류: API 키가 등록되지 않았습니다."}
    if not model:
        setup_model() # 모델이 없으면 재시도
        if not model: return {"response": "AI 모델을 초기화할 수 없습니다."}
    
    prompt = f"""당신은 (주)신우금속의 방화문 시공 전문 AI 도우미입니다.
    다음 안내문을 참고하여 질문에 답하세요: {GUIDE_CONTENT}
    질문: {request.message}"""
    
    # --- 할당량 초과(429) 대응 로직 ---
    max_retries = 2  # 최대 2번 재시도
    for i in range(max_retries + 1):
        try:
            response = await model.generate_content_async(prompt)
            return {"response": response.text}
        
        except Exception as e:
            error_msg = str(e)
            # 할당량 초과(429) 에러인 경우
            if "429" in error_msg:
                if i < max_retries:
                    await asyncio.sleep(3) # 3초 대기 후 재시도
                    continue
                else:
                    return {"response": "⚠️ 현재 사용자가 많아 응답이 지연되고 있습니다. **10초만 기다렸다가** 다시 질문해 주시겠어요?"}
            
            # 기타 에러
            print(f"AI 호출 오류: {error_msg}")
            return {"response": f"AI 서비스 연결 중 오류가 발생했습니다. (잠시 후 다시 시도해 주세요)"}

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/logo.png")
async def get_logo():
    return FileResponse("logo.png")

@app.get("/model1.jpg")
async def get_model1():
    return FileResponse("model1.jpg")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
