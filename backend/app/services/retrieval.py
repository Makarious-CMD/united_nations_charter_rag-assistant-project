import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer, CrossEncoder
from app.core.config import settings
# 1. تعريف موديلات الـ Embedding والـ Re-ranker (بتتحمل مرة واحدة أول ما السيرفر يشتغل)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

vector_collection = None

def load_vector_store():
    """تحميل قاعدة البيانات وربطها بدالة التضمين"""
    global vector_collection
    client = chromadb.PersistentClient(path=settings.vector_store_path)
    vector_collection = client.get_collection(
        name="un_charter_collection",
        embedding_function = sentence_transformer_ef
        )
    print("Vector store loaded successfully!")


# =====================================================
# 2. جلب كل البيانات من قاعدة المتجهات
# =====================================================
def fetch_all_data():
    """تسحب كل النصوص والميتاداتا والمتجهات من ChromaDB"""
    if vector_collection is None:
        raise ValueError("Vector store is not loaded.")
    
    data = vector_collection.get(include=["documents", "metadatas", "embeddings"])
    return data["documents"], data["metadatas"], data["embeddings"]


# =====================================================
# 3. تحويل السؤال لـ Vector
# =====================================================
def embed_query(query: str):
    """تحويل السؤال لأرقام باستخدام sentence_transformer_ef"""
    query_embedding = sentence_transformer_ef([query])[0]
    return np.array(query_embedding)
# =====================================================
# 4. دالة البحث الهجين (Hybrid Search)
# =====================================================
def get_retrieval_results(
    query, query_embedding, document_embeddings, documents, metadatas, k=5, threshold=0.70
):
    """البحث الدقيق بالـ Regex أو التشابه الرياضي Cosine Similarity مع دمج النص والميتا داتا"""
    
    results = []

    # أ. البحث عن رقم مادة (Article)
    article_match = re.search(r'\barticle\s+(\d+)\b', query, re.IGNORECASE)
    if article_match:
        article_number = article_match.group(1)
        target_article = f"Article {article_number}"
        for idx, metadata in enumerate(metadatas):
            if metadata.get("article", "").lower() == target_article.lower():
                doc_text = documents[idx]
                chapter_name = metadata.get("chapter", "Unknown Chapter")
                page_num = metadata.get("page", "Unknown")
                
                # دمج العنوان والميتا داتا مع النص الفعلي للمادة
                formatted_text = f"[{chapter_name} - {target_article} (Page {page_num})]\n{doc_text}"
                
                results.append({
                    "text": formatted_text, 
                    "metadata": metadata, 
                    "similarity": "Article-Exact"
                })
        if results:
            return results

    # ب. البحث عن فصل (Chapter)
    chapter_match = re.search(r'\bchapter\s+([IVXLCDM]+|\d+)\b', query, re.IGNORECASE)
    if chapter_match:
        chapter_number = chapter_match.group(1).upper()
        for idx, metadata in enumerate(metadatas):
            stored_chapter = metadata.get("chapter", "")
            stored_match = re.search(r'\bchapter\s+([IVXLCDM]+|\d+)\b', stored_chapter, re.IGNORECASE)
            if stored_match:
                stored_chapter_number = stored_match.group(1).upper()
                if stored_chapter_number == chapter_number:
                    doc_text = documents[idx]
                    article_name = metadata.get("article", "Unknown Article")
                    page_num = metadata.get("page", "Unknown")
                    
                    # دمج الفصل والمادة والنص الفعلي
                    formatted_text = f"[{stored_chapter} - {article_name} (Page {page_num})]\n{doc_text}"
                    
                    results.append({
                        "text": formatted_text, 
                        "metadata": metadata, 
                        "similarity": "Chapter-Exact"
                    })
        if results:
            return results
    # ج. البحث العادي بالتشابه
    similarities = cosine_similarity(query_embedding.reshape(1, -1), document_embeddings)[0]
    valid_indices = np.where(similarities >= threshold)[0]
    sorted_indices = valid_indices[np.argsort(similarities[valid_indices])[::-1]]
    top_indices = sorted_indices[:k]
    
    results = []
    for idx in top_indices:
        results.append({
            "text": documents[idx],
            "metadata": metadatas[idx],
            "similarity": float(similarities[idx])
        })
    return results


# =====================================================
# 5. دالة إعادة الترتيب (Re-ranker) اللي إنت طلبتها
# =====================================================
def rerank_results(query, results):
    """
    إعادة ترتيب النتائج المسترجعة باستخدام Cross-Encoder 
    واعطاء دقة أعلى لاختيار أفضل فقرة.
    """
    if not results:
        return []

    # صناعة أزواج من (السؤال وكل نص تم استرجاعهن)
    pairs = [
        [query, result["text"]]
        for result in results
    ]

    # حساب درجات الـ Re-ranker
    scores = reranker.predict(pairs)

    # إضافة درجة الـ reranker لكل نتيجة
    for result, score in zip(results, scores):
        result["reranker_score"] = float(score)

    # ترتيب النتائج تنازلياً حسب دقة الـ reranker
    sorted_results = sorted(
        results,
        key=lambda x: x["reranker_score"],
        reverse=True
    )

    # هنا رجعنا النتائج مرتبة بالكامل (عشان لو حبنا ناخد أفضل نتيجة أو أفضل كذا نتيجة)
    return sorted_results


# =====================================================
# 6. المايسترو الرئيسي (Process & Retrieve)
# =====================================================
# =====================================================
# 6. المايسترو الرئيسي (Process & Retrieve) المعدل
# =====================================================
def process_and_retrieve(question: str, k=5, threshold=0.70):
    """
    بتربط كل الخطوات (Embedding -> Fetch -> Hybrid Search -> Reranker)
    وترجع النتائج والمصادر حسب نوع السؤال (Chapter, Article, Semantic).
    """
    # 1. تشفير السؤال
    query_emb = embed_query(question)
    
    # 2. سحب البيانات من قاعدة البيانات
    docs, metas, embs = fetch_all_data()
    
    # 3. البحث الهجين
    results = get_retrieval_results(
        query=question,
        query_embedding=query_emb,
        document_embeddings=embs,
        documents=docs,
        metadatas=metas,
        k=k,
        threshold=threshold
    )
    
    # لو مفيش أي نتائج مطابقة
    if not results:
        return [], []

    retrieved_chunks = []
    sources = []

    similarity_type = str(results[0]["similarity"]).lower()

    # 4. الحالة الأولى: لو السؤال عن فصل (Chapter) - (بيجيب كل الأجزاء الخاصة بالفصل)
    if "chapter" in similarity_type:
        retrieved_chunks = [res["text"] for res in results]
        sources = [str(res["metadata"]) for res in results]

    # 5. الحالة الثانية: لو السؤال عن مادة معينة (Article) - (بيجيب المادة المحددة بدقة)
    elif "article" in similarity_type:
        retrieved_chunks = [res["text"] for res in results] # جبنا كل الأجزاء المطابقة للمادة لو فيه أكتر من جزء
        sources = [str(res["metadata"]) for res in results]
    # 6. الحالة الثالثة: بحث دلالي عادي (Semantic) - (نستخدم الـ Reranker لتحديد الأفضل)
    else:
        # لو رجع أكتر من نتيجة، بندخلها على الـ Reranker
        if len(results) > 1:
            reranked_results = rerank_results(query=question, results=results)
            # ممكن ناخد أفضل نتيجة أو أفضل 3 نتائج مرتبة بالـ Reranker
            top_results = reranked_results[:1] 
        else:
            top_results = results

        retrieved_chunks = [res["text"] for res in top_results]
        sources = [str(res["metadata"]) for res in top_results]

    return retrieved_chunks, sources