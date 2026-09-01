from fastapi import APIRouter, HTTPException
import service_usuarios as service

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("")
def criar_usuario(usuario: dict):
    if not usuario.get("nome") or not usuario.get("email"):
        raise HTTPException(status_code=400, detail="Informe nome e email")
    return service.criar_usuario(usuario)


@router.put("/{usuario_id}")
def atualizar_usuario(usuario_id: int, usuario: dict):
    resultado = service.atualizar_usuario(usuario_id, usuario)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return resultado


@router.get("")
def listar_usuarios():
    return service.listar_usuarios()


@router.get("/{usuario_id}")
def buscar_usuario(usuario_id: int):
    usuario = service.buscar_usuario(usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.delete("/{usuario_id}")
def excluir_usuario(usuario_id: int):
    resultado = service.excluir_usuario(usuario_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"mensagem": "Usuário excluído com sucesso"}
