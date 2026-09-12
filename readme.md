Aquí tienes la estructura completa y actualizada del `README.md`, combinando toda la información original del equipo con la sección de la bitácora de preparación para producción que trabajamos hoy:

```markdown
# API Rest de Adopción de Animales - SENA ADSO

## Integrantes
1. Liney Ricardo Medina
2. Steven Tobon Tobon
3. Thomas Isaza Chalarca
4. Durman Vanegas

API RESTful desarrollada para la gestión integral de un centro de adopción de mascotas. El proyecto implementa una arquitectura modular con **FastAPI** y **SQLite3 nativo**, aplicando control de acceso por roles (RBAC) e integridad referencial en cascada.

---

## Tecnologías Utilizadas

* **Lenguaje:** Python 3.10+
* **Framework:** FastAPI
* **Base de Datos:** SQLite3 (Motor relacional nativo con `row_factory = sqlite3.Row`)
* **Validación de Datos:** Pydantic v2
* **Seguridad:** Autenticación JWT y Hash de contraseñas con PBKDF2 (`hashlib`, `hmac` nativos)
* **Documentación:** Swagger UI (OpenAPI) integrando `HTTPBearer`

---

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

---

## Instalación y Ejecución Local

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/liney042-alt/adopcionAnimales.git](https://github.com/liney042-alt/adopcionAnimales.git)
   cd adopcionAnimales

```

2. **Crear y activar el entorno virtual:**
* **En Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

```


* **En Git Bash / Linux / macOS:**
```bash
source .venv/bin/activate

```


* **En CMD tradicional:**
```cmd
.\.venv\Scripts\activate.bat

```




3. **Instalar dependencias:**
```bash
pip install --upgrade pip
pip install -r requirements.txt

```


4. **Iniciar el servidor:**
* **Entorno de desarrollo:**
```bash
uvicorn app.main:app --reload

```


* **Ensayo de producción (local):**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000

```




*(Al ejecutar este comando por primera vez, la aplicación creará automáticamente la base de datos e insertará los datos semilla iniciales).*
**Credenciales de acceso iniciales:**
* **Correo:** `admin@refugio.com`
* **Contraseña:** `admin123`



---

## Documentación Interactiva

Accede a la consola de Swagger UI en tu navegador:

* Localhost: `http://127.0.0.1:8000/docs`
* Red Local: `http://<TU_IP_LOCAL>:8000/docs`

### Para probar endpoints protegidos:

1. Genera un token en `POST /token` o `POST /usuarios/login`.
2. Haz clic en el botón **Authorize** (arriba a la derecha).
3. Pega la cadena del `access_token` en la casilla **Value** y confirma.

---

## Preparación y Configuración para Producción (Render)

### Ajustes de Entorno y Seguridad

* **`CORSMiddleware`:** Configurado en `main.py` con orígenes permitidos `["*"]` justificados para pruebas de integración y clientes de prueba.
* **Health Check Endpoint:** Implementado la ruta `GET /health` (`{"estado": "ok"}`) para verificación de disponibilidad en Render.
* **Archivos de Control:**
* `.gitignore`: Exclusión de variables de entorno (`.env`), archivos `.db`, entornos virtuales (`.venv/`) y cachés.
* `.env.example`: Plantilla de variables sin credenciales expuestas.
* `.python-version`: Declaración de la versión del runtime para el despliegue.



### Pruebas de Integración y Calidad

* Suite de pruebas unitarias con `pytest` ejecutada y aprobada al 100% (**10/10 tests**), garantizando idempotencia en la base de datos.
* Corrección y sincronización de consultas en la tabla `solicitudes_adopcion`.

### Historial de Commits de Producción

1. `chore: configurar .gitignore, .env.example y .python-version para produccion`
2. `feat: agregar middleware CORS con justificacion y verificar endpoint /health`
3. `chore: regenerar requirements.txt actualizado`
4. `fix: corregir nombre de tabla solicitudes_adopcion y consultas de base de datos`



## Despliegue en Producción (Render)

El proyecto se encuentra desplegado y operativo en la nube a través de la plataforma Render.

* **URL Pública de la API:** [https://adopcionanimales.onrender.com](https://adopcionanimales.onrender.com)
* **Documentación Interactiva (Swagger UI):** [https://adopcionanimales.onrender.com/docs](https://adopcionanimales.onrender.com/docs)

###  Código QR de Acceso
Escanea el siguiente código QR desde tu dispositivo móvil para acceder a la documentación interactiva en producción:

![Código QR Swagger UI](./app/img/codigo.png)


## Limitaciones Conocidas del Entorno de Despliegue

Este proyecto se encuentra alojado en la infraestructura gratuita de **Render**, por lo que presenta las siguientes características de arquitectura:

1. **Suspensión por inactividad (Spin Down / Arranque en frío):**
   * **Comportamiento:** El servicio entra en estado de suspensión tras 15 minutos sin recibir peticiones HTTP.
   * **Causa:** Política de ahorro de recursos del plan *Free* de Render.
   * **Impacto:** La primera petición realizada después de un periodo de inactividad puede tardar entre 50 y 60 segundos mientras el contenedor se despierta.

2. **Sistema de archivos efímero (Persistencia de datos):**
   * **Comportamiento:** La base de datos SQLite (`refugio.db`) se reinicia a su estado inicial con los datos semilla en cada redespliegue o reinicio del servidor.
   * **Causa:** El almacenamiento en disco del plan gratuito es efímero y descarta archivos generados en tiempo de ejecución.
   * **Solución propuesta:** Para un entorno productivo empresarial, la persistencia se debe migrar a un motor gestionado externo como **PostgreSQL**.