from pydantic import BaseModel

# 1. ده القالب بتاع السؤال اللي اليوزر هيبعته
class QueryRequest(BaseModel):
    question: str

# 2. ده القالب بتاع الإجابة اللي الباك إند هيرجعها
class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    