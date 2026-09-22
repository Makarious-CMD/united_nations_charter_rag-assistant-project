import os
import requests
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()

# قراءة عنوان الـ Backend من البيئة (مع وضع رابط افتراضي لو مش موجود)
API_BASE_URL = os.getenv("API_BASE_URL")

def get_answer_from_backend(question: str) -> dict:
    """
    إرسال السؤال إلى سيرفر الـ FastAPI واستقبال الإجابة والمصادر
    """
    endpoint = f"{API_BASE_URL}/query"   # تأكد إن دي نفس الـ route عندك في الـ backend
    
    payload = {
        "question": question
    }
    
    try:
        # إرسال طلب POST للباك إند
        response = requests.post(endpoint, json=payload, timeout=210)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": True,
                "message": f"خطأ من السيرفر: كود الاستجابة {response.status_code}"
            }
    except requests.exceptions.ConnectionError:
        return {
            "error": True,
            "message": "عذراً، مش قادر أربط بالـ Backend. تأكد إن سيرفر الـ FastAPI شغال على بورت 8000."
        }
    except Exception as e:
        return {
            "error": True,
            "message": f"حصل خطأ غير متوقع: {str(e)}"
        }