from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import query

# استدعاء دالة تحميل البيانات
from app.services.retrieval import load_vector_store

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up: Loading Vector Store and connecting to Ollama LLM...")
    # تحميل الـ Vector Store فعلياً هنا
    load_vector_store()
    yield 
    print("Shutting down...")

# باقي الكود زي ما هو ...

app = FastAPI(title="RAG Assistant API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تسجيل المسارات بتاعت query في التطبيق الأساسي
app.include_router(query.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running!"}