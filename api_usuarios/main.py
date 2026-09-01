from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import inicializar_banco
import controller_usuarios
import controller_produtos
import controller_pedidos

app = FastAPI(
    title="API de Usuários e Lista de Compras",
    version="2.0.0",
    description=(
        "API com cadastro de usuários, catálogo de produtos e lista de "
        "compras individual por usuário, persistidos em SQLite."
    ),
)

# Cria as tabelas (se necessário) e popula o catálogo de produtos
# assim que a aplicação sobe.
inicializar_banco()

app.include_router(controller_usuarios.router)
app.include_router(controller_produtos.router)
app.include_router(controller_pedidos.router)

# Landing page (HTML/CSS/JS puro) que consome a API acima.
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def landing_page():
    return FileResponse("static/index.html")
