"""
Тестовий файл для перевірки AI Service
"""

import asyncio
import sys
import os

# Додаємо шлях до src
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ai_service import AIService


async def test_ai_service():
    """Тестування AI Service"""
    print("🧪 Тестування AI Service...")
    
    # Створюємо AI Service
    ai_service = AIService()
    
    # Тестові дані
    test_job = {
        "title": "Python Developer для веб-додатку",
        "description": "Потрібен досвідчений Python розробник для створення веб-додатку з використанням Django та React. Проект включає систему автентифікації, базу даних PostgreSQL, та REST API.",
        "budget": "$2000-5000",
        "skills": ["Python", "Django", "React", "PostgreSQL", "REST API"],
        "experience_level": "intermediate",
        "job_type": "fixed"
    }
    
    test_profile = {
        "skills": ["Python", "Django", "Flask", "JavaScript", "React", "PostgreSQL"],
        "experience": "3 роки розробки веб-додатків",
        "hourly_rate": "$35",
        "portfolio": "https://github.com/developer",
        "languages": ["Українська", "Англійська"]
    }
    
    test_jobs = [
        {
            "id": "1",
            "title": "Python Developer",
            "description": "Розробка веб-додатку",
            "budget": "$2000-5000",
            "skills": ["Python", "Django"]
        },
        {
            "id": "2", 
            "title": "React Developer",
            "description": "Створення UI компонентів",
            "budget": "$1500-3000",
            "skills": ["React", "JavaScript"]
        },
        {
            "id": "3",
            "title": "Full Stack Developer",
            "description": "Повноцінна розробка додатку",
            "budget": "$5000-10000",
            "skills": ["Python", "React", "PostgreSQL"]
        }
    ]
    
    print("\n1. 📊 Перевірка статусу сервісів...")
    status = ai_service.get_service_status()
    print(f"   OpenAI доступний: {status['openai_available']}")
    print(f"   Claude доступний: {status['claude_available']}")
    print(f"   Будь-який доступний: {status['any_available']}")
    
    if not status['any_available']:
        print("❌ Жоден AI сервіс не доступний. Перевірте API ключі.")
        return
    
    print("\n2. 🔍 Тестування аналізу вакансії...")
    try:
        analysis_result = await ai_service.analyze_job(test_job)
        if analysis_result["success"]:
            print("✅ Аналіз вакансії успішний")
            analysis = analysis_result["analysis"]
            print(f"   Складність: {analysis.get('complexity_score', 'N/A')}/10")
            print(f"   Бюджет: {analysis.get('budget_adequacy', 'N/A')}")
            print(f"   Ймовірність успіху: {analysis.get('success_probability', 'N/A')}")
        else:
            print(f"❌ Помилка аналізу: {analysis_result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Помилка аналізу: {e}")
    
    print("\n3. ✍️ Тестування генерації пропозиції...")
    try:
        proposal_result = await ai_service.generate_proposal(test_job, test_profile)
        if proposal_result["success"]:
            print("✅ Генерація пропозиції успішна")
            proposal = proposal_result["proposal"]
            print(f"   Модель: {proposal_result['model']}")
            print(f"   Текст довжиною: {len(proposal.get('proposal_text', ''))} символів")
            print(f"   Оцінка годин: {proposal.get('estimated_hours', 'N/A')}")
        else:
            print(f"❌ Помилка генерації: {proposal_result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Помилка генерації: {e}")
    
    print("\n4. 🔍 Тестування фільтрації вакансій...")
    try:
        filter_result = await ai_service.filter_jobs(test_jobs, test_profile)
        if filter_result["success"]:
            print("✅ Фільтрація вакансій успішна")
            filtered_jobs = filter_result["filtered_jobs"]
            print(f"   Відфільтровано: {len(filtered_jobs)} з {len(test_jobs)}")
            for job in filtered_jobs:
                print(f"   - {job.get('title', 'Unknown')} (AI score: {job.get('ai_score', 'N/A')})")
        else:
            print(f"❌ Помилка фільтрації: {filter_result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Помилка фільтрації: {e}")
    
    print("\n5. 🧪 Тестування з'єднання...")
    try:
        connection_result = await ai_service.test_connection()
        print("✅ Тест з'єднання завершено")
        print(f"   OpenAI тест: {connection_result.get('openai_test', {}).get('success', False)}")
        print(f"   Claude тест: {connection_result.get('claude_test', {}).get('success', False)}")
    except Exception as e:
        print(f"❌ Помилка тесту з'єднання: {e}")
    
    print("\n🎉 Тестування завершено!")


if __name__ == "__main__":
    asyncio.run(test_ai_service()) 