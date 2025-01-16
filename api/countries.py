from flask import Blueprint, request, jsonify
from database import get_db_connection
from psycopg2 import errors

countries_bp = Blueprint('countries', __name__)

# Adaugarea unei tari
@countries_bp.post('/api/countries')
def add_country():
    data = request.get_json()
    nume = data.get('nume')
    lat = data.get('lat')
    lon = data.get('lon')

    if not nume or not lat or not lon:
        return '', 400

    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO Tari (nume_tara, latitudine, longitudine) VALUES (%s, %s, %s) RETURNING id;",
            (nume, lat, lon)
        )
        id = cursor.fetchone()[0]
        db.commit()

        return jsonify({"id": id}), 201
    # Gestionarea exceptiilor de unicitate (tara are nume unic)
    except errors.UniqueViolation:
        db.rollback()
        return '', 409
    # Gestionarea erorilor cauzate de parametrii gresiti
    except Exception as e:
        db.rollback()
        return '', 400

    finally:
        cursor.close()
        db.close()

# Obtinerea tarilor
@countries_bp.get('/api/countries')
def get_countries():
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Tari;")
    countries = cursor.fetchall()

    countries_list = [
        {"id": c[0], "nume": c[1], "lat": c[2], "lon": c[3]}
        for c in countries
    ]

    cursor.close()
    db.close()
    return jsonify(countries_list), 200

# Obtinerea unei tari dupa id
@countries_bp.put('/api/countries/<int:id>')
@countries_bp.put('/api/countries/')
def update_country(id=None):
    if not id:
        return '', 400
    
    data = request.get_json()
    nume = data.get('nume')
    lat = data.get('lat')
    lon = data.get('lon')

    if not nume or not lat or not lon:
        return '', 400

    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "UPDATE Tari SET nume_tara = %s, latitudine = %s, longitudine = %s WHERE id = %s;",
            (nume, lat, lon, id)
        )
        if cursor.rowcount == 0:
            return '', 404

        db.commit()
        return '', 200
    except Exception as e:
        db.rollback()
        return '', 400
    finally:
        cursor.close()
        db.close()

# Stergerea unei tari dupa id
@countries_bp.delete('/api/countries/<int:id>')
@countries_bp.delete('/api/countries/')
def delete_country(id=None):
    if not id:
        return '', 400
    
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT 1 FROM Tari WHERE id = %s;", (id,))
        country = cursor.fetchone()
        
        if not country:
            return '', 404
        
        cursor.execute("DELETE FROM Tari WHERE id = %s;", (id,))
        db.commit()

        return '', 200
    except Exception as e:
        db.rollback()
        return '', 400
    finally:
        cursor.close()
        db.close()