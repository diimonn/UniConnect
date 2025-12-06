# backend/deepseek_assistant.py
import requests
import json
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

class DeepSeekAI:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "your_api_key_here")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'datahub_kz'),
            'port': int(os.getenv('DB_PORT', 3306))
        }
    
    def get_db_connection(self):
        """Подключение к MySQL"""
        return mysql.connector.connect(**self.db_config)
    
    def get_universities_data(self, filters=None):
        """Получает данные университетов из БД"""
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        sql = """
            SELECT 
                u.id, u.name, u.short_name, u.city, u.type,
                u.rating, u.ent_min_score, u.students_count,
                u.programs_count, u.description,
                u.mission, u.founded_year, u.international_partners,
                u.double_degree_info, u.website,
                GROUP_CONCAT(DISTINCT p.name SEPARATOR ' | ') as programs,
                GROUP_CONCAT(DISTINCT p.duration SEPARATOR ' | ') as durations,
                GROUP_CONCAT(DISTINCT p.language SEPARATOR ' | ') as languages
            FROM universities u
            LEFT JOIN programs p ON u.id = p.university_id
            WHERE 1=1
        """
        
        params = []
        
        # Применяем фильтры если есть
        if filters:
            if 'university_ids' in filters:
                placeholders = ', '.join(['%s'] * len(filters['university_ids']))
                sql += f" AND u.id IN ({placeholders})"
                params.extend(filters['university_ids'])
            
            if 'city' in filters:
                sql += " AND u.city = %s"
                params.append(filters['city'])
            
            if 'min_score' in filters:
                sql += " AND u.ent_min_score <= %s"
                params.append(filters['min_score'])
        
        sql += " GROUP BY u.id ORDER BY u.rating DESC LIMIT 15"
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return results
    
    def format_data_for_prompt(self, universities):
        """Форматирует данные для промпта"""
        if not universities:
            return "В базе данных пока нет информации об университетах."
        
        formatted = "БАЗА ДАННЫХ УНИВЕРСИТЕТОВ КАЗАХСТАНА:\n\n"
        formatted += "="*60 + "\n"
        
        for uni in universities:
            formatted += f"🎓 УНИВЕРСИТЕТ: {uni['name']} ({uni['short_name']})\n"
            formatted += f"📍 Город: {uni['city']}\n"
            formatted += f"🏛️ Тип: {uni['type']}\n"
            formatted += f"⭐ Рейтинг: {uni['rating']}/5\n"
            formatted += f"🎯 Мин. балл ЕНТ: {uni['ent_min_score']}\n"
            formatted += f"👨‍🎓 Студентов: {uni['students_count']}\n"
            formatted += f"📚 Программ: {uni['programs_count']}\n"
            
            if uni.get('description'):
                formatted += f"📝 Описание: {uni['description'][:200]}...\n"
            
            if uni.get('programs') and uni['programs'] != 'NULL':
                formatted += f"🎓 Программы: {uni['programs']}\n"
            
            if uni.get('international_partners'):
                formatted += f"🌍 Международные партнеры: {uni['international_partners']}\n"
            
            if uni.get('double_degree_info'):
                formatted += f"🎓 Двойные дипломы: {uni['double_degree_info']}\n"
            
            formatted += "="*60 + "\n"
        
        return formatted
    
    def analyze_question(self, question):
        """Анализирует вопрос пользователя"""
        question_lower = question.lower()
        
        analysis = {
            'type': 'general',
            'mentioned_universities': [],
            'filters': {},
            'needs_comparison': False
        }
        
        # Ищем университеты
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, short_name FROM universities")
        all_universities = cursor.fetchall()
        
        for uni in all_universities:
            # Проверяем полное название
            if uni['name'].lower() in question_lower:
                analysis['mentioned_universities'].append(uni['id'])
            # Проверяем короткое название
            elif uni['short_name'] and uni['short_name'].lower() in question_lower:
                analysis['mentioned_universities'].append(uni['id'])
        
        cursor.close()
        conn.close()
        
        # Определяем тип запроса
        if any(word in question_lower for word in ['сравни', 'сравнение', 'разница', 'лучше', 'хуже']):
            analysis['type'] = 'compare'
            analysis['needs_comparison'] = True
        
        elif any(word in question_lower for word in ['балл', 'ент', 'поступ', 'проходн']):
            analysis['type'] = 'admission'
            # Ищем цифры (баллы)
            import re
            numbers = re.findall(r'\d+', question)
            if numbers:
                analysis['filters']['min_score'] = int(numbers[0])
        
        elif any(word in question_lower for word in ['it', 'айти', 'компьютер', 'программир']):
            analysis['type'] = 'it'
        
        elif any(word in question_lower for word in ['алмат', 'астан']):
            if 'алмат' in question_lower:
                analysis['filters']['city'] = 'Алматы'
            elif 'астан' in question_lower:
                analysis['filters']['city'] = 'Астана'
        
        return analysis
    
    def ask(self, user_question):
        """Основной метод - задает вопрос DeepSeek с данными из БД"""
        
        # 1. Анализируем вопрос
        analysis = self.analyze_question(user_question)
        
        # 2. Получаем данные из БД
        filters = {}
        if analysis['mentioned_universities']:
            filters['university_ids'] = analysis['mentioned_universities']
        if 'city' in analysis['filters']:
            filters['city'] = analysis['filters']['city']
        if 'min_score' in analysis['filters']:
            filters['min_score'] = analysis['filters']['min_score']
        
        universities_data = self.get_universities_data(filters)
        
        # 3. Форматируем данные для промпта
        formatted_data = self.format_data_for_prompt(universities_data)
        
        # 4. Создаем промпт для DeepSeek
        system_prompt = f"""Ты - умный ассистент для абитуриентов Казахстана "DataHub ВУЗов РК".
Ты помогаешь выбирать университеты, сравнивать их, подбирать программы по баллам ЕНТ.

ИСПОЛЬЗУЙ ТОЛЬКО ЭТИ ДАННЫЕ ИЗ БАЗЫ:
{formatted_data}

ВАЖНЫЕ ПРАВИЛА:
1. Отвечай ТОЛЬКО на основе предоставленных данных выше
2. Если информации нет в данных - честно говори "В базе данных нет информации по этому вопросу"
3. Будь конкретным, полезным и дружелюбным
4. При сравнении университетов создавай четкие таблицы сравнения
5. При подборе по баллам ЕНТ - давай конкретные рекомендации
6. Отвечай на русском языке
7. Форматируй ответ с эмодзи и четкой структурой

Пример хорошего ответа:
"🎓 **МУИТ** - Международный Университет Информационных Технологий
📍 Алматы | ⭐ 4.6/5 | 🎯 ЕНТ от 105
💻 IT-программы: Информационные технологии, Кибербезопасность

⚖️ **Сравнение:**
| Параметр | МУИТ | КБТУ |
|----------|------|------|
| Рейтинг | 4.6 | 4.8 |
| Город | Алматы | Алматы |

💡 **Рекомендация:** Для IT выбирайте МУИТ, для инженерии - КБТУ"

Типы запросов которые ты обрабатываешь:
1. Сравнение университетов
2. Подбор по баллам ЕНТ
3. Информация о конкретном университете
4. IT-программы и направления
5. Международное сотрудничество
6. Рейтинги и топ университетов
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ]
        
        # 5. Отправляем запрос к DeepSeek API
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "max_tokens": 2000,
                    "temperature": 0.7,
                    "stream": False
                },
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
                
                # Добавляем информацию об источнике
                answer += f"\n\n---\n🤖 *Ответ сгенерирован DeepSeek AI на основе {len(universities_data)} университетов из базы данных*"
                
                return {
                    "success": True,
                    "answer": answer,
                    "universities_count": len(universities_data),
                    "query_type": analysis['type']
                }
            else:
                error_msg = f"Ошибка DeepSeek API: {response.status_code}"
                if response.text:
                    error_msg += f" - {response.text[:200]}"
                return {
                    "success": False,
                    "answer": "Извините, сервис ИИ временно недоступен. Попробуйте позже.",
                    "error": error_msg
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "answer": "⏳ ИИ долго думает... Попробуйте задать вопрос короче или переформулировать."
            }
        except Exception as e:
            return {
                "success": False,
                "answer": "🔧 Технические неполадки. Используйте упрощенный режим.",
                "error": str(e)
            }