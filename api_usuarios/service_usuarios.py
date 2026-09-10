"""
Camada de Serviço (Service Layer) de Usuários.

Concentra as regras de negócio e operações de acesso a dados (CRUD)
para a entidade 'Usuários' na tabela `usuarios`.
"""

from database import get_connection


def criar_usuario(usuario):
    """
    Insere um novo usuário no banco de dados e retorna o registro criado.
    """
    conexao = get_connection()
    cursor = conexao.cursor()

    # Executa o INSERT utilizando parâmetros com '?' para prevenção de SQL Injection.
    # usuario.get("idade") evita erro (KeyError) se a propriedade idade não for informada.
    cursor.execute(
        "INSERT INTO usuarios (nome, email, idade) VALUES (?, ?, ?)",
        (usuario["nome"], usuario["email"], usuario.get("idade")),
    )

    # Persiste as alterações no banco de dados
    conexao.commit()

    # Recupera a chave primária (id) gerada automaticamente pelo AUTOINCREMENT
    novo_id = cursor.lastrowid

    conexao.close()

    # Reaproveita a função de busca para retornar o usuário recém-criado em formato de dicionário
    return buscar_usuario(novo_id)


def listar_usuarios():
    """
    Retorna todos os usuários cadastrados ordenados pelo ID.
    """
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM usuarios ORDER BY id")

    # List Comprehension: Converte a lista de linhas sqlite3.Row em uma lista de dicionários Python
    usuarios = [dict(linha) for linha in cursor.fetchall()]

    conexao.close()
    return usuarios


def buscar_usuario(usuario_id):
    """
    Busca um único usuário pelo seu ID (Chave Primária).
    Retorna um dicionário com os dados do usuário ou None se não encontrado.
    """
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    linha = cursor.fetchone()

    conexao.close()

    # Operador Ternário: Converte a linha para dicionário se ela existir; senão retorna None
    return dict(linha) if linha else None


def atualizar_usuario(usuario_id, dados):
    """
    Atualiza os dados de um usuário existente no banco de dados.
    Suporta atualização parcial: campos omitidos no envio mantêm seus valores atuais.
    """
    # 1. Validação de existência
    usuario_atual = buscar_usuario(usuario_id)
    if usuario_atual is None:
        return None

    # 2. Técnica de Fallback (Valor de Contingência):
    # O método .get("chave", valor_padrao) usa o dado enviado caso exista; 
    # se não enviado, preserva o dado atual armazenado no banco.
    nome = dados.get("nome", usuario_atual["nome"])
    email = dados.get("email", usuario_atual["email"])
    idade = dados.get("idade", usuario_atual["idade"])

    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "UPDATE usuarios SET nome = ?, email = ?, idade = ? WHERE id = ?",
        (nome, email, idade, usuario_id),
    )

    conexao.commit()
    conexao.close()

    # Retorna o registro devidamente atualizado
    return buscar_usuario(usuario_id)


def excluir_usuario(usuario_id):
    """
    Remove fisicamente um usuário do banco de dados (Hard Delete).
    """
    # Checa se o usuário realmente existe antes de tentar a remoção
    usuario_atual = buscar_usuario(usuario_id)
    if usuario_atual is None:
        return False

    conexao = get_connection()
    cursor = conexao.cursor()

    # Executa o DELETE. Devido à regra 'ON DELETE CASCADE' configurada na tabela 'pedidos',
    # as compras ativas deste usuário serão removidas automaticamente, enquanto o
    # histórico na tabela 'pedidos_historico' é preservado.
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))

    conexao.commit()
    conexao.close()

    return True