from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import inicializar_bd
from app.routers import usuarios, especies, refugios, animales, historiales, solicitudes, seguimientos

# DDL e inserción automática de datos al iniciar
inicializar_bd()

app = FastAPI(
    title="Sistema Refugio de Animales - SQLite3 Nativo",
    version="1.0.0"
)

# Configuración del Middleware de CORS
# Permitimos todos los orígenes (*) para facilitar el acceso de clientes y pruebas durante el despliegue de la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(especies.router)
app.include_router(refugios.router)
app.include_router(animales.router)
app.include_router(historiales.router)
app.include_router(solicitudes.router)
app.include_router(seguimientos.router)

@app.get("/")
def root():
    return {"mensaje": "API Operativa - SQLite3 Nativo sin ORM"}

# Endpoint de salud para verificación de Render (Health Check)
@app.get("/health")
def health_check():
    return {"estado": "ok"}