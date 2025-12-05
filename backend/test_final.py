import pymysql

try:
    conn = pymysql.connect(
        host='localhost',
        port=3310,
        user='uniconnect',
        password='',
        database='datahub_kz',
        cursorclass=pymysql.cursors.DictCursor  # <-- ДОБАВЬТЕ ЭТО
    )
    
    print("✅ Подключение успешно!")
    
    with conn.cursor() as cursor:
        # Проверяем таблицы
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"📊 Таблицы: {[list(t.values())[0] for t in tables]}")
        
        # Считаем университеты
        cursor.execute("SELECT COUNT(*) as count FROM universities")
        result = cursor.fetchone()
        print(f"🏛 Университетов: {result['count']}")
        
        # Показываем их
        cursor.execute("SELECT short_name, city, rating FROM universities")
        unis = cursor.fetchall()
        print("📋 Список университетов:")
        for uni in unis:
            print(f"   • {uni['short_name']} - {uni['city']} (⭐ {uni['rating']})")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Ошибка: {e}")