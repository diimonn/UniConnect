import pymysql

try:
    conn = pymysql.connect(
        host='localhost',
        port=3310,  # ВАШ ПОРТ
        user='root',
        password='',  # ваш пароль если есть
        database='datahub_kz'
    )
    
    print("✅ Успешное подключение к MySQL!")
    
    with conn.cursor() as cursor:
        # Проверяем таблицы
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"Таблицы в базе: {tables}")
        
        # Проверяем университеты
        cursor.execute("SELECT COUNT(*) as count FROM universities")
        result = cursor.fetchone()
        print(f"Университетов в базе: {result['count']}")
        
        # Показываем университеты
        cursor.execute("SELECT short_name, city, rating FROM universities")
        unis = cursor.fetchall()
        print("\nСписок университетов:")
        for uni in unis:
            print(f"  - {uni['short_name']} ({uni['city']}), рейтинг: {uni['rating']}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    print("\nВозможные причины:")
    print("1. Неправильный порт (у вас 3310?)")
    print("2. База datahub_kz не существует")
    print("3. Неверный пароль MySQL")
    print("4. MySQL сервер не запущен")