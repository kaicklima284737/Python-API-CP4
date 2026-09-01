from fastapi import APIRouter, HTTPException
import service_produtos as service

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("")
def listar_produtos():
    """Lista de itens de compra disponíveis, cadastrada uma única vez
    e utilizável por qualquer usuário a qualquer momento."""
    return service.listar_produtos()


@router.get("/{produto_id}")
def buscar_produto(produto_id: int):
    produto = service.buscar_produto(produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto
