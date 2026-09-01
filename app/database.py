import sqlite3
import hashlib

DATABASE_NAME = "refugio.db"

def obtener_password_hash_nativo(password: str) -> str:
    salt = "sena_salt_fixed"
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return key.hex()

def obtener_conexion():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_bd():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("CREATE TABLE IF NOT EXISTS roles (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, rol_id INTEGER NOT NULL, FOREIGN KEY (rol_id) REFERENCES roles (id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS especies (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE, descripcion TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS refugios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, direccion TEXT NOT NULL, telefono TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS animales (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, edad INTEGER, especie_id INTEGER NOT NULL, refugio_id INTEGER NOT NULL, estado TEXT DEFAULT 'Disponible', FOREIGN KEY (especie_id) REFERENCES especies (id) ON DELETE CASCADE, FOREIGN KEY (refugio_id) REFERENCES refugios (id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS historiales_medicos (id INTEGER PRIMARY KEY AUTOINCREMENT, animal_id INTEGER NOT NULL, descripcion TEXT NOT NULL, fecha TEXT NOT NULL, FOREIGN KEY (animal_id) REFERENCES animales (id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS solicitudes_adopcion (id INTEGER PRIMARY KEY AUTOINCREMENT, animal_id INTEGER NOT NULL, usuario_id INTEGER NOT NULL, estado TEXT DEFAULT 'Pendiente', fecha TEXT NOT NULL, FOREIGN KEY (animal_id) REFERENCES animales (id) ON DELETE CASCADE, FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS seguimientos (id INTEGER PRIMARY KEY AUTOINCREMENT, solicitud_id INTEGER NOT NULL, observaciones TEXT NOT NULL, fecha TEXT NOT NULL, FOREIGN KEY (solicitud_id) REFERENCES solicitudes_adopcion (id) ON DELETE CASCADE)")

    cursor.execute("INSERT OR IGNORE INTO roles (id, nombre) VALUES (1, 'Administrador')")
    cursor.execute("INSERT OR IGNORE INTO roles (id, nombre) VALUES (2, 'Voluntario')")

    admin_hash = obtener_password_hash_nativo("admin123")
    cursor.execute("INSERT OR IGNORE INTO usuarios (id, nombre, email, password_hash, rol_id) VALUES (1, 'Admin', 'admin@refugio.com', ?, 1)", (admin_hash,))
    cursor.execute("INSERT OR IGNORE INTO especies (id, nombre, descripcion) VALUES (1, 'Perro', 'Caninos')")
    cursor.execute("INSERT OR IGNORE INTO especies (id, nombre, descripcion) VALUES (2, 'Gato', 'Felinos')")

    conn.commit()
    conn.close()