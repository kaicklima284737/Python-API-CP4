from fastapi import APIRouter, HTTPException
# Importa a camada de serviço responsável pelas regras de negócio e acesso ao banco.
# Mantedes-se o padrão de arquitetura: a rota gerencia a requisição e o serviço trata os dados.
import service_usuarios as service

# Configura o agrupador de rotas para usuários
# prefix="/usuarios": define a URL base
# tags=["Usuários"]: organiza os endpoints na documentação automática (/docs)
router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("")
def criar_usuario(usuario: dict):
    """
    POST: Cria um novo usuário (Operação 'Create' do CRUD).
    Recebe um dicionário JSON no corpo da requisição.
    """
    #verifica se os campos obrigatórios foram preenchidos
    if not usuario.get("nome") or not usuario.get("email"):
        # HTTP 400 = Bad Request (O cliente esqueceu de enviar dados essenciais)
        raise HTTPException(status_code=400, detail="Informe nome e email")
    
    # Repassa a criação para a camada service
    return service.criar_usuario(usuario)


@router.put("/{usuario_id}")
def atualizar_usuario(usuario_id: int, usuario: dict):
    """
    PUT: Atualiza os dados de um usuário existente (Operação 'Update' do CRUD).
    Recebe o id na URL e os novos dados no corpo em formato JSON.
    """
    resultado = service.atualizar_usuario(usuario_id, usuario)
    
    # Tratamento de erro: se o usuário não existir no banco de dados
    if resultado is None:
        # HTTP 404 = Not Found
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    return resultado


@router.get("")
def listar_usuarios():
    """
    GET: Retorna a lista completa de usuários (Operação 'Read' do CRUD).
    """
    return service.listar_usuarios()


@router.get("/{usuario_id}")
def buscar_usuario(usuario_id: int):
    """
    GET: Busca um único usuário pelo ID especificado na URL.
    """
    usuario = service.buscar_usuario(usuario_id)
    
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    return usuario


@router.delete("/{usuario_id}")
def excluir_usuario(usuario_id: int):
    """
    DELETE: Remove um usuário do sistema (Operação 'Delete' do CRUD).
    """
    resultado = service.excluir_usuario(usuario_id)
    
    if not resultado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    return {"mensagem": "Usuário excluído com sucesso"}