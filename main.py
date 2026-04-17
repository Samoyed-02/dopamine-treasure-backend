from fastapi import FastAPI
from routers import locations, treasures, admin
from database import engine, Base
import models.location
import models.attempt
import models.treasure
from fastapi.middleware.cors import CORSMiddleware



Base.metadata.create_all(bind=engine)

app = FastAPI()

#allow_origins=[
#    "http://localhost:3000",   # 박주원님 로컬 개발용
#    "http://localhost:5173",   # Vite 쓰면 이 포트일 수도 있음
#    "https://프론트배포주소.com"  # 나중에 추가
#],

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중엔 전체 허용, 배포 전에 프론트 주소로 교체
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(locations.router)
app.include_router(treasures.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "도파민 보물섬 API 작동 중!"}