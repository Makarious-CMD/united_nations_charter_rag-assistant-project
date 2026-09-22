import os
import ollama
from groq import Groq
from app.core.config import settings

# 1. تهيئة عميل Groq للقاضي (Judge) باستخدام مفتاح الـ API
groq_client = Groq(api_key=settings.groq_api_key)



SYSTEM_PROMPT = """
[ROLE / PERSONA]
You are a senior international law and international relations expert, acting as a legal and political analyst. Your tone is professional, objective, academic yet accessible (like an experienced law professor speaking to a university student).

[CORE OBJECTIVE]
Explain complex legal and political concepts clearly, step-by-step, focusing on the UN Charter, treaties, and international diplomacy.

[STRICT CONSTRAINTS & ANTI-HALLUCINATION RULES]
1. GROUNDING: Base your answer STRICTLY and EXCLUSIVELY on the provided context/retrieved sources. Do not rely on general knowledge if the answer requires context.
2. NO FABRICATION: Never invent, guess, or fabricate Article numbers, UN Charter provisions, quotes, treaties, historical events, or legal interpretations.
3. INSUFFICIENCY: If the provided context lacks enough information to answer the question reliably, you MUST explicitly state: "The provided sources do not contain sufficient information to answer this question." Do not attempt to fill gaps with hallucinated facts.
4. NEUTRALITY: Remain strictly neutral and analytical when discussing political issues. Present multiple perspectives without taking a political side.

[STRUCTURAL & FORMATTING INSTRUCTIONS]
1. STRUCTURE: Use clear headings, bullet points, and numbered steps.
2. TERMINOLOGY: Define complex legal or political terms simply before using them extensively.
3. DISTINCTION: Clearly distinguish between:
   - Facts explicitly stated in the source.
   - Reasonable inferences.
   - Analytical interpretations.
   - Illustrative examples (always label examples explicitly as illustrative, not as source facts).
4. RESPONSE FLOW (For complex concepts):
   - Direct Answer (Concise summary)
   - Legal/Factual Basis (Specific Articles/Provisions if available in context)
   - Step-by-Step Explanation
   - Illustrative Example (with a clear disclaimer that it is external/illustrative if not in the source)
"""



def generate_multiple_answers_with_ollama(question: str, context_chunks: list[str], num_generations: int = 3) -> list[str]:
    """
    توليد عدة إجابات محلياً باستخدام Ollama (Llama 3) مع تباين في درجة الإبداع (Temperature)
    """
    context_text = "\n\n".join(context_chunks)
    answers_list = []
    
    for i in range(num_generations):
        prompt = f"""Use the following context to answer the question accurately.
Context:
{context_text}

Question: {question}
Answer:"""

        try:
            # توليد الإجابة محلياً عبر Ollama
            response = ollama.chat(
    model=settings.llm_model,
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    options={
        "temperature": 0.1
    }
)
            answers_list.append(response['message']['content'])
        except Exception as e:
            answers_list.append(f"Error from Ollama generation {i+1}: {str(e)}")
            
    return answers_list


def evaluate_and_select_best_answer(question: str, answers: list[str]) -> str:
    """
    استخدام نموذج قسّم وقوي على Groq API ليعمل كـ "قاضي" (LLM-as-a-Judge)
    لمقارنة الإجابات الثلاثة واختيار الأفضل والأدق علمياً وقانونياً.
    """
    if not answers:
        return "No answers generated to evaluate."
    
    # تنسيق الإجابات لعرضها على القاضي
    formatted_answers = ""
    for idx, ans in enumerate(answers, 1):
        formatted_answers += f"\n--- Answer Option {idx} ---\n{ans}\n"

    judge_prompt = f"""You are an expert AI judge and evaluator. 
Your task is to review the following candidate answers generated for a specific question based on legal/official documents.
Select the absolute best, most accurate, and well-structured answer. 
Output ONLY the final selected best answer text directly, without any introductory or concluding remarks from yourself.

User Question: {question}

Candidate Answers:
{formatted_answers}

Best Answer:"""

    try:
        # إرسال المهمة لموديل قوي جداً على Groq (مثلا llama3-70b-8192)
        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a strict, objective, and expert AI judge."},
                {"role": "user", "content": judge_prompt}
            ],
            temperature=0.1,  # درجة حرارة منخفضة جداً للحيادية والدقة الصارمة
            max_tokens=1024
        )
        
        best_answer = completion.choices[0].message.content
        return best_answer
        
    except Exception as e:
        # في حال حدوث مشكلة في اتصال Groq، كخطوة أمان نرجع أول إجابة من Ollama مباشرة
        return answers[0] if answers else f"Judge Evaluation Error: {str(e)}"


# =====================================================
# الدالة الرئيسية (الميسترو) التي ينادي عليها ملف الـ Routes
# =====================================================
def generate_answer(question: str, context_chunks: list[str]) -> str:
    """
    1. توليد 3 إجابات بـ Ollama محلياً.
    2. تمريرهم لـ Groq API لاختيار الأفضل عبر تقنية LLM-as-a-Judge.
    3. إرجاع الإجابة الفائزة للمستخدم.
    """
    # الخطوة الأولى: توليد الإجابات المتعددة محلياً
    candidate_answers = generate_multiple_answers_with_ollama(question, context_chunks, num_generations=3)
    
    # الخطوة الثانية: اختيار الأفضل بواسطة القاضي الذكي على Groq
    final_best_answer = evaluate_and_select_best_answer(question, candidate_answers)
    
    return final_best_answer