from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from db_connection import Database  # Импорт из нового файла
import os

app = Flask(__name__, static_folder='../frontend')
CORS(app)

db = Database()

@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

@app.route('/api/universities')
def get_universities():
    universities = db.get_all_universities()
    return jsonify(universities)

@app.route('/api/university/<int:univ_id>')
def get_university(univ_id):
    university = db.get_university_by_id(univ_id)
    
    if not university:
        return jsonify({'error': 'University not found'}), 404
    
    programs = db.get_programs_by_university(univ_id)
    university['programs'] = programs
    
    return jsonify(university)

@app.route('/api/universities/search')
def search_universities():
    city = request.args.get('city', '')
    uni_type = request.args.get('type', '')
    
    with db.connection.cursor() as cursor:
        sql = """
            SELECT id, name, short_name, city, type, 
                   students_count, rating, programs_count
            FROM universities 
            WHERE 1=1
        """
        params = []
        
        if city and city != 'Все':
            sql += " AND city = %s"
            params.append(city)
        
        if uni_type and uni_type != 'Все':
            sql += " AND type = %s"
            params.append(uni_type)
        
        sql += " ORDER BY rating DESC"
        cursor.execute(sql, params)
        results = cursor.fetchall()
    
    return jsonify(results)

@app.route('/api/university/<int:univ_id>/programs')
def get_university_programs(univ_id):
    programs = db.get_programs_by_university(univ_id)
    return jsonify(programs)

if __name__ == '__main__':
    print("🚀 Server started!")
    print("🌐 Main page: http://localhost:5000")
    print("📡 API universities: http://localhost:5000/api/universities")
    print("📡 API university details: http://localhost:5000/api/university/1")
    app.run(debug=True, port=5000)