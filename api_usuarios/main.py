from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Importa a função do módulo de banco de dados para criar a estrutura inicial (DDL/Seed)
from database import inicializar_banco

# Importa os controladores (roteadores) responsáveis pelas rotas de cada entidade
import controller_usuarios
import controller_produtos
import controller_pedidos

# Instância principal do FastAPI (Ponto de entrada da aplicação backend)
app = FastAPI(
    title="API de Usuários e Lista de Compras",
    version="2.0.0",
    description=(
        "API com cadastro de usuários, catálogo de produtos e lista de "
        "compras individual por usuário, persistidos em SQLite."
    ),
)

# Bootstrapping / Inicialização do Banco de Dados:
# Garante que o arquivo 'database.db', as tabelas e os produtos padrão existam 
# assim que o servidor web for iniciado.
inicializar_banco()

# Arquitetura Modular:
# Registra na aplicação principal os roteadores de cada módulo.
# Isso divide o sistema em arquivos menores e organizados (Princípio da Responsabilidade Única).
app.include_router(controller_usuarios.router)
app.include_router(controller_produtos.router)
app.include_router(controller_pedidos.router)

# Servidor de Arquivos Estáticos (Static Files):
# Mapeia a pasta física 'static' para a URL '/static'.
# Permite que o navegador baixe arquivos CSS (style.css), JS (app.js) e imagens.
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def landing_page():
    """
    Rota Raiz (GET /)
    """
    return FileResponse("static/index.html")