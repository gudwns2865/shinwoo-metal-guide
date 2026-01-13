import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from openai import OpenAI

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI 클라이언트 설정 (환경 변수 사용)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 안내문 원본 텍스트 (AI 참고용)
GUIDE_CONTENT = """
[방화유리문(인정제품) 발주 및 시공 준수사항]

1. 주요 시공 준수 표준
- 방화문 손잡이(도어핸들) 설치 높이:
  * 일반 현장: 바닥면으로부터 800mm ~ 1,050mm (권장 900~950mm)
  * 장애인 현장: 바닥면으로부터 800mm ~ 900mm (BF인증 등)
  * 비고: 일자손잡이의 경우 손잡이 봉이 800~900mm 사이에 위치하면 적합
- 방화문 개폐 유효폭 확보:
  * 일반 현장: 유효폭 900mm 이상 권장
  * 장애인 현장: 반드시 유효폭 900mm 이상 확보 (문틀 사이즈 아님)
  * 측정 기준: 문을 90도 개방 시, 손잡이 등 돌출물을 제외한 순수 통과 폭(OPEN SIZE)
- 프레임 사면(4면) 구속 시공 조건:
  * 고정 조건: 프레임 4면(상·하·좌·우)을 인정받은 내화구조체에 견고하게 고정
  * 법령 참고: 건축물의 피난·방화구조 등의 기준에 관한 규칙 제3조(내화구조) 내용 참고
  * 주의: 별도 비차열창, 유리창 인접 부착 불가. 임의 인접창 설치 시 인정서 발급 불가.

2. 현장 시공 시 주의사항
- 하드웨어 임의 변경 금지: 신우에서 공급하는 인정 시 포함된 부속품(방화 성적서가 있는 하드웨어)만 사용 가능.
- 현장 가공 금지: 인정받은 제품 외 별도의 타공, 절단, 시트지 부착 불가.

3. 필수 제출 자료 (인정서 및 품질확인서 발급용)
- 안내: 아래 자료가 모두 확인되어야 인정서 및 품질확인서 발급이 가능합니다. (계산서 발행한 사업자 이름으로 발행됨)
- 필수 항목:
  * 품질확인 점검표: 당사 제공 양식에 따라 시공자가 항목별 점검 후 서명
  * 시공 사진: 내부·외부 전경 및 주요 고정 부위 사진 (프레임, 도어 세트 시공 후)
  * 전액 입금 확인: 발주 물량에 대한 입금 완료 후 서류 발송
- 주의: 인정서 발급 후 현장명, 현장주소 수정 불가.
"""

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        user_message = request.message
        system_prompt = f"""
        당신은 (주)신우금속의 방화문 시공 전문 AI 도우미입니다. 
        사용자의 질문에 대해 다음 지침을 엄격히 따르세요:
        1. **안내문 우선 답변**: 아래 제공된 [안내문 내용]에 해당 질문에 대한 답이 있다면, 반드시 이 내용을 바탕으로 먼저 답변하세요.
        2. **인터넷 검색 활용**: 만약 질문이 [안내문 내용]에 없거나, 더 광범위한 방화문 관련 법령, 최신 기술 기준에 대한 것이라면 당신의 지식과 실시간 검색 결과를 바탕으로 답변하세요.
        3. **가독성 극대화**: 답변은 전문적이고 친절하게 한국어로 작성합니다. 
           - 중요한 수치나 핵심 용어는 **볼드체**(**텍스트**)로 강조하세요.
           - 항목이 여러 개일 경우 글머리 기호( - 또는 1.)를 사용하여 명확히 구분하세요.
           - 문단 사이에는 적절한 줄바꿈을 사용하여 읽기 편하게 만드세요.
        4. **출처 명시**: 안내문 내용일 경우 "안내문에 따르면..."이라고 언급하고, 외부 정보일 경우 "실시간 검색 및 관련 법령에 따르면..."과 같은 문구를 포함하세요.

        [안내문 내용]
        {GUIDE_CONTENT}
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/logo.png")
async def get_logo():
    return FileResponse("new_logo.png")

if __name__ == "__main__":
    import uvicorn
    # Render.com에서 지정해주는 포트를 사용하도록 설정
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
