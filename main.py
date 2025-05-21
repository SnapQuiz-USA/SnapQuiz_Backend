from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.interfaces.api.routes.question_routes import router as question_router

app = FastAPI(
    title="USA API",
    description="문제 생성 및 답변 검증 API",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 특정 도메인만 허용하도록 수정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(question_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)