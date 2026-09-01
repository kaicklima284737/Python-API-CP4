from fastapi import APIRouter, HTTPException
import service_pedidos as service

router = APIRouter(prefix="/pedidos", tags=["Pedidos (lista de compras)"])


@router.post("")
def adicionar_item(pedido: dict):
    """Adiciona um produto à lista de compras de um usuário.

    Corpo esperado: {"usuario_id": 1, "produto_id": 3, "quantidade": 2}
    """
    usuario_id = pedido.get("usuario_id")
    produto_id = pedido.get("produto_id")
    quantidade = pedido.get("quantidade", 1)

    if usuario_id is None or produto_id is None:
        raise HTTPException(status_code=400, detail="Informe usuario_id e produto_id")
    if not isinstance(quantidade, int) or quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser um inteiro maior que zero")

    resultado = service.adicionar_item(usuario_id, produto_id, quantidade)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Usuário ou produto não encontrado")
    return resultado


@router.get("/usuario/{usuario_id}")
def listar_itens_usuario(usuario_id: int, incluir_removidos: bool = False):
    """Lista os itens da lista de compras de um usuário."""
    itens = service.listar_itens_usuario(usuario_id, incluir_removidos)
    if itens is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return itens


@router.get("/usuario/{usuario_id}/historico")
def listar_historico_usuario(usuario_id: int):
    """Retorna o histórico completo de alterações da lista de um usuário."""
    historico = service.listar_historico_usuario(usuario_id)
    if historico is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return historico


@router.put("/{pedido_id}")
def atualizar_item(pedido_id: int, dados: dict):
    """Atualiza a quantidade de um item já presente na lista de um usuário."""
    quantidade = dados.get("quantidade")
    if not isinstance(quantidade, int) or quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser um inteiro maior que zero")

    resultado = service.atualizar_item(pedido_id, quantidade)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Item não encontrado na lista")
    return resultado


@router.delete("/{pedido_id}")
def remover_item(pedido_id: int):
    """Remove um item da lista de compras do usuário (mantém histórico)."""
    resultado = service.remover_item(pedido_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Item não encontrado na lista")
    return {"mensagem": "Item removido da lista de compras"}
