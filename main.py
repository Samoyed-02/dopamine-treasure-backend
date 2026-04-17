from fastapi import FastAPI
from routers import locations, treasures, admin
from database import engine, Base
import models.location
import models.attempt
import models.treasure


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(locations.router)
app.include_router(treasures.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "도파민 보물섬 API 작동 중!"}