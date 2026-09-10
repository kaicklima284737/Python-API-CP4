from fastapi import APIRouter, HTTPException
# A camada 'service' isola a regra de negócio (banco de dados/lógica), permitindo que esta camada (rotas) cuide apenas de requisições e respostas HTTP.
import service_pedidos as service

# Agrupador de rotas.
# prefix="/pedidos": todas as URLs deste arquivo começam com /pedidos
# tags: organiza a documentação automática do Swagger (/docs)
router = APIRouter(prefix="/pedidos", tags=["Pedidos (lista de compras)"])


@router.post("")
def adicionar_item(pedido: dict):
    """
    POST: Utilizado para CRIAR um novo registro.
    Recebe um dicionário JSON no corpo da requisição.
    """
    # 1. Extração segura de dados usando .get() para evitar erros de chave inexistente
    usuario_id = pedido.get("usuario_id")
    produto_id = pedido.get("produto_id")
    quantidade = pedido.get("quantidade", 1) 
    # Valor padrão é 1 caso não informado

    if usuario_id is None or produto_id is None:
        # HTTP 400 = Bad Request (Dados enviados pelo cliente estão incompletos ou errados)
        raise HTTPException(status_code=400, detail="Informe usuario_id e produto_id")
    
    if not isinstance(quantidade, int) or quantidade <= 0:
        #isinstance verifica se a variável é do tipo especificado (int, str, list, etc)
        raise HTTPException(status_code=400, detail="Quantidade deve ser um inteiro maior que zero")

    resultado = service.adicionar_item(usuario_id, produto_id, quantidade)
    
    if resultado is None:
        # HTTP 404 = Not Found (O recurso solicitado não existe no banco de dados)
        raise HTTPException(status_code=404, detail="Usuário ou produto não encontrado")
        
    return resultado


@router.get("/usuario/{usuario_id}")
def listar_itens_usuario(usuario_id: int, incluir_removidos: bool = False):
    """
    GET: Utilizado para LEITURA/CONSULTA de dados.
    - usuario_id: Parâmetro de rota.
    """
    itens = service.listar_itens_usuario(usuario_id, incluir_removidos)
    
    if itens is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    return itens


@router.get("/usuario/{usuario_id}/historico")
def listar_historico_usuario(usuario_id: int):
    """
    GET: Consulta o histórico de auditoria ou alterações do usuário.
    """
    historico = service.listar_historico_usuario(usuario_id)
    
    if historico is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    return historico


@router.put("/{pedido_id}")
def atualizar_item(pedido_id: int, dados: dict):
    """
    PUT: Utilizado para ATUALIZAR/ALTERAR um recurso existente.
    """
    quantidade = dados.get("quantidade")
    
    if not isinstance(quantidade, int) or quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser um inteiro maior que zero")

    resultado = service.atualizar_item(pedido_id, quantidade)
    
    if resultado is None:
        raise HTTPException(status_code=404, detail="Item não encontrado na lista")
        
    return resultado


@router.delete("/{pedido_id}")
def remover_item(pedido_id: int):
    """
    DELETE: Utilizado para REMOVER um recurso.
    Aqui faz-se um 'Soft Delete' (deleção lógica), mantendo o histórico no banco.
    """
    resultado = service.remover_item(pedido_id)
    
    if not resultado:
        raise HTTPException(status_code=404, detail="Item não encontrado na lista")
        
    return {"mensagem": "Item removido da lista de compras"}