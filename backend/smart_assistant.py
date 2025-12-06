# backend/server.py (добавьте к существующему коду)
import os
from dotenv import load_dotenv
from smart_assistant import UniversityAIAssistant
from pydantic import BaseModel

load_dotenv()

# Конфигурация БД из .env
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'datahub_kz'),
    'port': os.getenv('DB_PORT', 3306)
}

# Инициализируем ассистента
assistant = UniversityAIAssistant(db_config)

class AIRequest(BaseModel):
    question: str

# Эндпоинт для ИИ-ассистента
@app.post("/api/ai/ask")
async def ask_assistant(request: AIRequest):
    """
    Задайте вопрос ИИ-ассистенту
    Пример: {"question": "Какие IT-университеты есть в Алматы?"}
    """
    try:
        answer = assistant.ask(request.question)
        return {
            "success": True,
            "answer": answer,
            "question": request.question
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "answer": "Извините, произошла ошибка при обработке запроса."
        }

# Эндпоинт для сравнения университетов
@app.get("/api/ai/compare")
async def compare_universities(uni_ids: str):
    """
    Сравнить университеты по ID
    Пример: /api/ai/compare?uni_ids=1,2,3
    """
    try:
        ids = [int(id.strip()) for id in uni_ids.split(',')]
        
        # Получаем данные университетов
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        placeholders = ', '.join(['%s'] * len(ids))
        query = f"""
            SELECT u.*, GROUP_CONCAT(p.name SEPARATOR '; ') as programs
            FROM universities u
            LEFT JOIN programs p ON u.id = p.university_id
            WHERE u.id IN ({placeholders})
            GROUP BY u.id
        """
        
        cursor.execute(query, ids)
        universities = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Генерируем сравнение
        response = assistant.generate_comparison_table(universities)
        
        return {
            "success": True,
            "comparison": response,
            "universities": [{"id": u['id'], "name": u['name']} for u in universities]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}