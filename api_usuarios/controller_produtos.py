from fastapi import APIRouter, HTTPException
import service_produtos as service

# Configuração do grupo de rotas para produtos
# prefix="/produtos": define que todas as rotas neste arquivo iniciam com /produtos
# tags=["Produtos"]: categoriza as rotas na documentação automática (Swagger em /docs)
router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("")
def listar_produtos():
    """
    GET /produtos
    Retorna a lista completa de produtos cadastrados.
    A docstring entre aspas triplas vira a descrição oficial da API na documentação.
    """
    # Delega a busca para a camada service e retorna a lista convertida em JSON
    return service.listar_produtos()


@router.get("/{produto_id}")
def buscar_produto(produto_id: int):
    """
    GET /produtos/{produto_id}
    Busca um produto específico pelo seu identificador na URL (Exemplo: /produtos/17).
    """
    produto = service.buscar_produto(produto_id)
    
    # Validação de existência (Programação Defensiva)
    if produto is None:
        # HTTP 404 = Not Found (Indica ao cliente que o recurso solicitado não existe)
        raise HTTPException(status_code=404, detail="Produto não encontrado")
        
    return produto