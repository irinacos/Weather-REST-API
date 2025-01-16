from flask import Blueprint, request, jsonify
from database import get_db_connection
from psycopg2 import errors
from datetime import datetime

temp_bp = Blueprint('temperatures', __name__)

# Adaugarea unei temperaturi
@temp_bp.post('/api/temperatures')
def add_temperature():
    data = request.get_json()
    id_oras = data.get('idOras')
    temp = data.get('valoare')

    if not id_oras or not temp:
        return '', 400

    db = get_db_connection()
    cursor = db.cursor()
    # Generarea timestamp-ului actual
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

    try:
        cursor.execute(
            "INSERT INTO Temperaturi (valoare, timestamp, id_oras) VALUES (%s, %s, %s) RETURNING id;",
            (temp, timestamp, id_oras)
        )
        id = cursor.fetchone()[0]
        db.commit()

        return jsonify({"id": id}), 201
    # Gestioneaza exceptiile de unicitate (temperaturile au tuplul (id_oras, timestamp) unic)
    except errors.UniqueViolation:
        db.rollback()
        return '', 409
    # Gestioneaza exceptiile de cheie straina (id_oras trebuie sa existe in tabela Orase)
    except errors.ForeignKeyViolation:
        db.rollback()
        return '', 404
    except Exception as e:
        db.rollback()
        return '', 400
    finally:
        cursor.close()
        db.close()

# Obtinerea temperaturilor
@temp_bp.get('/api/temperatures')
def get_temps():
    args = request.args
    lat = args.get('lat')
    lon = args.get('lon')
    frm = args.get('from')
    til = args.get('until')

    params = []

    # Interogarea de baza
    query = "SELECT id, valoare, timestamp FROM Temperaturi WHERE TRUE"

    # Adaugarea conditiilor in functie de parametrii primiti
    if lat:
        query += " AND id_oras IN (SELECT id FROM Orase WHERE latitudine = %s)"
        params.append(lat)

    if lon:
        query += " AND id_oras IN (SELECT id FROM Orase WHERE longitudine = %s)"
        params.append(lon)

    if frm:
        query += " AND timestamp >= %s"
        params.append(frm)

    if til:
        query += " AND timestamp <= %s"
        params.append(til)

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(query, params)
    temps = cursor.fetchall()

    temp_list = [
        {"id": t[0], "valoare": t[1], "timestamp": t[2].strftime('%Y-%m-%d')}
        for t in temps
    ]

    cursor.close()
    db.close()

    return jsonify(temp_list), 200

# Obtinerea temperaturilor dintr-un oras (id_oras poate sa fie si null)
@temp_bp.get('/api/temperatures/cities/<int:id_oras>')
@temp_bp.get('/api/temperatures/cities/')
def get_temps_from_city(id_oras=None):
    if not id_oras or id_oras == 'null':
        return jsonify([]), 200
    
    args = request.args
    frm = args.get('from')
    til = args.get('until')

    params = [id_oras]
    query = "SELECT id, valoare, timestamp FROM Temperaturi WHERE id_oras = %s"

    if frm:
        query += " AND timestamp >= %s"
        params.append(frm)

    if til:
        query += " AND timestamp <= %s"
        params.append(til)

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(query, params)
    temps = cursor.fetchall()

    temp_list = [
        {"id": t[0], "valoare": t[1], "timestamp": t[2].strftime('%Y-%m-%d')}
        for t in temps
    ]

    cursor.close()
    db.close()

    return jsonify(temp_list), 200

# Obtinerea temperaturilor dintr-o tara (id_tara poate sa fie si null)
@temp_bp.get('/api/temperatures/countries/<int:id_tara>')
@temp_bp.get('/api/temperatures/countries/')
def get_temps_from_country(id_tara=None):
    if not id_tara or id_tara == 'null':
        return jsonify([]), 200
    
    args = request.args
    frm = args.get('from')
    til = args.get('until')

    params = [id_tara]

    query = "SELECT t.id, t.valoare, t.timestamp " \
            "FROM Temperaturi t " \
            "WHERE t.id_oras IN (SELECT o.id FROM Orase o WHERE o.id_tara = %s)"

    params = [id_tara]

    if frm:
        query += " AND timestamp >= %s"
        params.append(frm)
    if til:
        query += " AND timestamp <= %s"
        params.append(til)

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(query, params)
    temps = cursor.fetchall()

    temp_list = [
        {"id": t[0], "valoare": t[1], "timestamp": t[2].strftime('%Y-%m-%d')}
        for t in temps
    ]

    cursor.close()
    db.close()

    return jsonify(temp_list), 200

# Actualizarea unei temperaturi
@temp_bp.put('/api/temperatures/<int:id>')
@temp_bp.put('/api/temperatures/')
def update_temperature(id=None):
    if not id:
        return '', 400
    
    data = request.get_json()
    id_oras = data.get('idOras')
    valoare = data.get('valoare')

    if not id_oras or valoare is None:
        return '', 400

    db = get_db_connection()
    cursor = db.cursor()

    # Generarea timestamp-ului actual
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

    try:
        cursor.execute("SELECT 1 FROM Temperaturi WHERE id = %s;", (id,))
        if cursor.fetchone() is None:
            return '', 404

        cursor.execute(
            "UPDATE Temperaturi" \
            "SET id_oras = %s, valoare = %s, timestamp = %s" \
            "WHERE id = %s;",
            (id_oras, valoare, timestamp, id)
        )
        db.commit()

        return '', 200
    # Gestioneaza exceptiile de unicitate
    except errors.UniqueViolation:
        db.rollback()
        return '', 409
    # Gestioneaza exceptiile de cheie straina (id_oras)
    except errors.ForeignKeyViolation:
        db.rollback()
        return '', 404
    except Exception as e:
        db.rollback()
        return '', 400
    finally:
        cursor.close()
        db.close()

# Stergerea unei temperaturi
@temp_bp.delete('/api/temperatures/<int:id>')
@temp_bp.delete('/api/temperatures/')
def delete_temperature(id=None):
    if not id:
        return '', 400
    
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT 1 FROM Temperaturi WHERE id = %s;", (id,))
        if cursor.fetchone() is None:
            return '', 404

        cursor.execute("DELETE FROM Temperaturi WHERE id = %s;", (id,))
        db.commit()

        return '', 200
    except Exception as e:
        db.rollback()
        return '', 400
    finally:
        cursor.close()
        db.close()