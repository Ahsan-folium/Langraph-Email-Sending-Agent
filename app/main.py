from fastapi import FastAPI
from app.routes import api_file_router


app = FastAPI(
    title="Practice Project",
    version="0.1.0",
    description="This project is being built to revise langgraph , implement tools and human in the loop",
)
app.include_router(api_file_router)


@app.get("/")
async def root():
    return {"message": "Langraph API", "docs": "/docs", "health": "/health"}
