# Weather REST API


## Microserviciile utilizate (si combinate folosind utilitarul docker-compose)
- REST API (am folosit Flask pentru gestionarea de raspunsuri HTTP)
- Baza de date meteorologice (PostgreSQL)
- Utilitar de gestiune al bazei de date

## Rutele implementate
### Pentru tari:
1. POST /api/countries
2. GET /api/countries
3. PUT /api/countries/:id
4. DELETE /api/countries/:id
### Pentru orase:
1. POST /api/cities
2. GET /api/cities
3. GET /api/cities/:id_tara
4. PUT /api/cities/:id
5. DELETE /api/cities/:id
### Pentru temperaturi:
1. POST /api/temperatures
2. GET /api/temperatures?lat=Double&lon=Double&from=Date&until=Date
    - am construit o interogare initiala de baza, nefiltrata
    - in functie de parametrii de cerere, adaug la interogarea de baza
    - analog si pentru urmatoarele doua GET-uri 
3. GET /api/temperatures/cities/:id_oras?from=Date&until=Date
4. GET/api/temperatures/countries/:id_tara?from=Date&until=Date
5. PUT/api/temperatures/:id
6. DELETE/api/temperatures/:id

## Gestionarea erorilor
Am folosit libraria psycopg2.errors pentru a gestiona erorile/exceptiile 
intampinate la primirea cererilor HTTP. Astfel, trimit catre baza de date  
interogari PostgreSQL si verific prin blocuri try-except daca baza de date 
returneaza vreo exceptie.

Codurile HTTP folosite/returnate:
- 200 OK: Operatiune executata cu succes, fara a intampina probleme
- 201 CREATED: Adaugarea unei/unor linii in una dintre cele 3 tabele
- 400 BAD REQUEST: Utilizatorul a gresit cererea HTTP (parametrii lipsa)
- 404 NOT FOUND: 
    --- Parametrii invalizi, nu se regasesc in baza de date
    --- Cheie straina invalida (in cazul de fata, id-ul tarii atunci cand 
    ne uitam in tabela Orase sau id-ul orasului cand ne uitam in 
    tabela Temperaturi): exceptie psycopg2.errors.ForeignKeyViolation
- 409 CONFLICT: Nu se respecta constrangerile de unicitate ale entitatilor
    (exceptie psycopg2.errors.UniqueViolation)

De asemenea, am gestionat si cazurile in care un client ar putea omite 
parametrii necesari din URL (precum id-ul) pentru cererile GET, PUT si DELETE.

## Organizarea codului
Pentru a face codul mai lizibil, am folosit blueprint-urile din Flask,
fiecare entitate a bazei de date avand astfel propriul blueprint:
- countries_bp gestioneaza cererile legate de tari
- cities_bp gestioneaza cererile legate de orase
- temp_bp gestioneaza cererile legate de temperaturi

## Docker Compose
### Serviciile definite:
- db: container pentru baza de date PostgreSQL
- api: container pentru REST API
- admin: utilitar de gestionare a bazei de date
### Retele
- frontend: api
- backend: db, api, admin
### Persistenta
- Am folosit un volum in Docker pentru ca datele sa nu se piarda chiar
daca containerul este oprit/repornit.
- Am mapat un fisier SQL pentru a initializa baza de date cu entitatile 
necesare (Tari, Orase, Temperaturi)
- Am mapat un fisier JSON pentru a configura automat conexiunea catre 
serverul PostgreSQL pentru gestionarea bazei de date
### Variabile de mediu
Pentru configurarea serviciilor am folosit si variabile de mediu, precum 
POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB (baza de date) si
PGADMIN_DEFAULT_EMAIL, PGADMIN_DEFAULT_PASSWORD (server admin)
