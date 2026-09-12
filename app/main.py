from fastapi import FastAPI
from app.database import inicializar_bd
from app.routers import usuarios, especies, refugios, animales, historiales, solicitudes, seguimientos

# DDL e insercion automatica de datos al iniciar
inicializar_bd()

app = FastAPI(
    title="Sistema Adopción Animales",
    description="API v1.0.1 - Desplegada con CI/CD",
    version="1.0.1"
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