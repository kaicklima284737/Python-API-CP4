"""
Camada de Serviço (Service Layer) de Produtos.

Responsável exclusivamente por executar as consultas SQL relacionadas
ao catálogo global de produtos disponíveis.
"""

from database import get_connection


def listar_produtos():
    """
    Retorna todos os produtos do catálogo ordenados por categoria e nome.
    """
    # 1. Abre a conexão com o banco de dados SQLite
    conexao = get_connection()
    cursor = conexao.cursor()

    # 2. Executa a consulta SQL ordenando primeiro por categoria e depois por nome (ordem alfabética)
    cursor.execute("SELECT * FROM produtos ORDER BY categoria, nome")

    # 3. List Comprehension: Transforma cada registro sqlite3.Row em um dicionário Python (dict).
    produtos = [dict(linha) for linha in cursor.fetchall()]

    # 4. Libera a conexão do banco para economizar recursos do sistema
    conexao.close()

    return produtos


def buscar_produto(produto_id):
    """
    Busca um único produto no banco de dados pelo seu ID.
    Retorna o dicionário do produto ou None caso não seja encontrado.
    """
    conexao = get_connection()
    cursor = conexao.cursor()

    # Segurança (Prevenção contra SQL Injection):
    # O '?' é um parâmetro posicional. O valor de 'produto_id' é enviado em uma tupla (produto_id,)
    # para que o driver do SQLite trate a entrada estritamente como dado seguro.
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))

    # .fetchone() recupera apenas o primeiro registro correspondente
    linha = cursor.fetchone()

    conexao.close()

    # Operador Ternário: Se 'linha' contiver dados, converte para dicionário; caso contrário, retorna None.
    return dict(linha) if linha else None