"""
Acesso à lista de produtos disponíveis para compra (tabela `produtos`).

A lista é cadastrada uma única vez (seed em database.py) e fica
disponível para ser consultada a qualquer momento por qualquer usuário,
servindo de base para a lista de compras individual de cada um.
"""

from database import get_connection


def listar_produtos():
    conexao = get_connection()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM produtos ORDER BY categoria, nome")
    produtos = [dict(linha) for linha in cursor.fetchall()]
    conexao.close()
    return produtos


def buscar_produto(produto_id):
    conexao = get_connection()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    linha = cursor.fetchone()
    conexao.close()
    return dict(linha) if linha else None
