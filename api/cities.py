from flask import Blueprint, request, jsonify
from database import get_db_connection
from psycopg2 import errors

cities_bp = Blueprint('cities', __name__)

# Adaugarea unui oras
@cities_bp.post('/api/cities')
def add_city():
    data = request.get_json()
    id_tara = data.get('idTara')
    nume = data.get('nume')
    lat = data.get('lat')
    lon = data.get('lon')

    if not id_tara or not nume or not lat or not lon:
        return '', 400

    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO Orase (nume_oras, latitudine, longitudine, id_tara) VALUES (%s, %s, %s, %s) RETURNING id;",
            (nume, lat, lon, id_tara)
        )
        id = cursor.fetchone()[0]
        db.commit()

        return jsonify({"id": id}), 201
    # Gestioneaza exceptiile de unicitate (orasele au tuplul (id_tara, nume_oras) unic)
    except errors.UniqueViolation:
        db.rollback()
        return '', 409
    # Gestioneaza exceptiile de cheie straina (id_tara trebuie sa existe in tabela Tari)
    except errors.ForeignKeyViolation:
        db.rollback()
        return '', 404
    except Exception as e:
        db.rollback()
        return '', 400
    finally:
        cursor.close()
        db.close()

# Obtinerea oraselor
@cities_bp.get('/api/cities')
def get_cities():
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Orase;")
    cities = cursor.fetchall()

    cities_list = [
        {"id": c[0], "idTara": c[1], "nume": c[2], "lat": c[3], "lon": c[4]}
        for c in cities
    ]

    cursor.close()
    db.close()
    return jsonify(cities_list), 200

# Obtinerea oraselor dintr-o tara (id_tara poate sa fie si null)
@cities_bp.get('/api/cities/country/<id_tara>')
@cities_bp.get('/api/cities/country/')
def get_cities_from_country(id_tara=None):
    if not id_tara or id_tara == 'null':
        return jsonify([]), 200

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT id, nume_oras, latitudine, longitudine FROM Orase WHERE id_tara = %s;", (id_tara,))
    cities = cursor.fetchall()

    cities_list = [
        {"id": c[0], "nume": c[1], "lat": c[2], "lon": c[3]}
        for c in cities
    ]

    cursor.close()
    db.close()
    return jsonify(cities_list), 200

# Obtinerea unui oras (id poate sa fie si null)
@cities_bp.put('/api/cities/<int:id>')
@cities_bp.put('/api/cities/')
def update_city(id=None):
    if not id:
        return '', 400
    
    data = request.get_json()
    id_tara = data.get('idTara')
    nume = data.get('nume')
    lat = data.get('lat')
    lon = data.get('lon')

    if not id_tara or not nume or not lat or not lon:
        return '', 400

    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT 1 FROM Orase WHERE id = %s;", (id,))
        if cursor.fetchone() is None:
            return '', 404

        cursor.execute(
            "UPDATE Orase SET id_tara = %s, nume_oras = %s, latitudine = %s, longitudine = %s WHERE id = %s;",
            (id_tara, nume, lat, lon, id)
        )
        db.commit()

        return '', 200
    except errors.UniqueViolation:
        db.rollback()
        return '', 409
    except Exception as e:
        db.rollback()
        return '', 400
    finally:
        cursor.close()
        db.close()

# Stergerea unui oras (id poate sa fie si null)
@cities_bp.delete('/api/cities/<int:id>')
@cities_bp.delete('/api/cities/')
def delete_city(id=None):
    if not id:
        return '', 400
    
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM Orase WHERE id = %s;", (id,))
        db.commit()

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