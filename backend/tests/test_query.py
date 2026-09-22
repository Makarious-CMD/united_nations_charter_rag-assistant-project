from fastapi.testclient import TestClient
from app.main import app

# إنشاء عميل اختبار وهمي للسيرفر بتاعنا
client = TestClient(app)

def test_query_happy_path():
    """اختبار مسار ناجح: إرسال سؤال حقيقي وانتظار إجابة صحيحة (كود 200)"""
    response = client.post(
        "/query",
        json={"question": "ما هي أهداف الأمم المتحدة؟"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # التأكد إن الإجابة رجعت وفيها نص ومصادر
    assert "answer" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)

def test_query_invalid_input():
    """اختبار إدخال خاطئ: إرسال بيانات غير مكتملة وانتظار خطأ 422"""
    # هنبعت ريكويست من غير حقل question اللي الـ Schema بتطلبه
    response = client.post(
        "/query",
        json={"wrong_field": "أي كلام"}
    )
    
    # الدليل طالب إننا نتأكد من رجوع كود 422
    assert response.status_code == 422