"""
Regras de negócio e acesso a dados dos usuários (tabela `usuarios`).
"""

from database import get_connection


def criar_usuario(usuario):
    conexao = get_connection()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email, idade) VALUES (?, ?, ?)",
        (usuario["nome"], usuario["email"], usuario.get("idade")),
    )
    conexao.commit()
    novo_id = cursor.lastrowid
    conexao.close()
    return buscar_usuario(novo_id)


def listar_usuarios():
    conexao = get_connection()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM usuarios ORDER BY id")
    usuarios = [dict(linha) for linha in cursor.fetchall()]
    conexao.close()
    return usuarios


def buscar_usuario(usuario_id):
    conexao = get_connection()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    linha = cursor.fetchone()
    conexao.close()
    return dict(linha) if linha else None


def atualizar_usuario(usuario_id, dados):
    usuario_atual = buscar_usuario(usuario_id)
    if usuario_atual is None:
        return None

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
    return buscar_usuario(usuario_id)


def excluir_usuario(usuario_id):
    usuario_atual = buscar_usuario(usuario_id)
    if usuario_atual is None:
        return False

    conexao = get_connection()
    cursor = conexao.cursor()
    # Os pedidos do usuário são apagados em cascata (ON DELETE CASCADE),
    # mas o histórico de pedidos é preservado para fins de auditoria.
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conexao.commit()
    conexao.close()
    return True
