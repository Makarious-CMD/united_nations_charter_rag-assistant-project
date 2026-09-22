from fastapi import APIRouter, HTTPException
from app.schemas.query import QueryRequest, QueryResponse
# استدعاء الدالة الجديدة الصحيحة
from app.services.retrieval import process_and_retrieve 
from app.services.generation import generate_answer

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    user_question = request.question
    
    try:
        # استخدام دالة البحث والـ Reranking الجديدة
        retrieved_chunks, sources = process_and_retrieve(user_question)
        
        if not retrieved_chunks:
            return QueryResponse(
                answer="I'm sorry, but I couldn't find any relevant information to answer your question.",
                sources=[]
            )
            
        # توليد الإجابة باستخدام الموديل
        generated_answer = generate_answer(user_question, retrieved_chunks)
        
        return QueryResponse(answer=generated_answer, sources=sources)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))