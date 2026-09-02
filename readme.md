# API Rest de Adopción de Animales - SENA ADSO

## Integrantes 
1. Liney Ricardo  Medina 
2. Steven tobon tobon 
3. Thomas Izasa Chalarca 
4. Durman Vanegas 

API RESTful desarrollada para la gestión integral de un centro de adopción de mascotas. El proyecto implementa una arquitectura modular con **FastAPI** y **SQLite3 nativo**, aplicando control de acceso por roles (RBAC) e integridad referencial en cascada.

##  Tecnologías Utilizadas

* **Lenguaje:** Python 3.10+
* **Framework:** FastAPI
* **Base de Datos:** SQLite3 (Motor relacional nativo con `row_factory = sqlite3.Row`)
* **Validación de Datos:** Pydantic v2
* **Seguridad:** Autenticación JWT y Hash de contraseñas con PBKDF2 (`hashlib`, `hmac` nativos)
* **Documentación:** Swagger UI (OpenAPI) integrando `HTTPBearer`


## Modelo de Base de Datos y Entidades

El sistema gestiona 8 entidades relacionadas mediante claves foráneas con eliminación en cascada (`ON DELETE CASCADE`):

1. **Roles:** Administrador / Cliente
2. **Usuarios:** Datos de autenticación y perfil
3. **Especies:** Clasificación de animales
4. **Refugios:** Sedes físicas de acogida
5. **Animales:** Ficha de mascotas
6. **Historiales Médicos:** Registro clínico del animal
7. **Solicitudes de Adopción:** Peticiones realizadas por los usuarios
8. **Seguimientos:** Observaciones post-adopción


##  Instalación y Ejecución Local

1. Clonar el repositorio:
   
   git clone (https://github.com/liney042-alt/adopcionAnimales.git)
   cd adopcionAnimales

2. Crear y activar el entorno virtual:

### En Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

### En Windows (Git Bash / Command Prompt) o Linux/macOS:

### Git Bash / Linux / macOS
source venv/bin/activate

### CMD tradicional
.\venv\Scripts\activate.bat
Instalar dependencias:

3. Instalar dependencias:

Bash
pip install --upgrade pip
pip install -r requirements.txt

4. Iniciar el servidor de desarrollo:

Bash
python -m uvicorn app.main:app --reload
(Al ejecutar este comando por primera vez, la aplicación creará automáticamente el archivo de base de datos refugio.db e insertará los datos iniciales)

Correo: admin@refugio.com
Contraseña: admin123

## Documentación Interactiva
Accede a la consola de Swagger UI en tu navegador:
http://127.0.0.1:8000/docs

### Para probar endpoints protegidos:

1. Genera un token en POST /token o POST /usuarios/login.
2. Haz clic en el botón Authorize arriba a la derecha.
3. Pega la cadena del access_token en la casilla Value y confirma.