CREATE TABLE Tari (
    id SERIAL PRIMARY KEY,
    nume_tara VARCHAR(255) UNIQUE NOT NULL,
    latitudine DOUBLE PRECISION NOT NULL,
    longitudine DOUBLE PRECISION NOT NULL
);

CREATE TABLE Orase (
    id SERIAL PRIMARY KEY,
    id_tara INT REFERENCES Tari(id) ON DELETE CASCADE,
    nume_oras VARCHAR(255) NOT NULL,
    latitudine DOUBLE PRECISION NOT NULL,
    longitudine DOUBLE PRECISION NOT NULL,
    UNIQUE (id_tara, nume_oras)
);

CREATE TABLE Temperaturi (
    id SERIAL PRIMARY KEY,
    valoare DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_oras INT REFERENCES Orase(id) ON DELETE CASCADE,
    UNIQUE (id_oras, timestamp)
);
