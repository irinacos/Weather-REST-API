from flask import Flask
from countries import countries_bp
from cities import cities_bp
from temperatures import temp_bp

app = Flask(__name__)

# Folosirea blueprint-urilor pentru a organiza codul
app.register_blueprint(countries_bp)
app.register_blueprint(cities_bp)
app.register_blueprint(temp_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)