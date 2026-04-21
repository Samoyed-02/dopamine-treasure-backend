from fastapi import FastAPI
from routers import locations, treasures, admin
from fastapi.staticfiles import StaticFiles
from database import engine, Base
import models.location
import models.attempt
import models.treasure
from fastapi.middleware.cors import CORSMiddleware



Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://0601sunny-spec.github.io",
        "http://127.0.0.1:5500",  
        "http://localhost:5500",
        "http://localhost:5173",   # ← Vite 로컬 개발 서버
        "http://127.0.0.1:5173", ],  # 개발 중엔 전체 허용, 배포 전에 프론트 주소로 교체
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")  # 추가

app.include_router(locations.router)
app.include_router(treasures.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "도파민 보물섬 API 작동 중!"}