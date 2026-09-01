"""
Camada de acesso ao banco de dados (SQLite).

Este módulo concentra:
- a conexão com o arquivo de banco de dados (database.db);
- a criação das tabelas, caso ainda não existam;
- a carga inicial (seed) da tabela de produtos com pelo menos 15 itens.

Não há classes/ORM aqui de propósito: o projeto segue o mesmo estilo
procedural (dicionários/listas) do código original, apenas trocando o
armazenamento em JSON por um banco de dados relacional SQLite, conforme
apresentado no material de Introdução a Bancos de Dados.
"""

import sqlite3
from datetime import datetime

DB_FILE = "database.db"


def get_connection():
    """Abre uma conexão com o banco de dados SQLite.

    row_factory = sqlite3.Row permite acessar as colunas tanto por
    índice quanto por nome (ex: linha["nome"]), e facilita a conversão
    para dicionário com dict(linha).
    """
    conexao = sqlite3.connect(DB_FILE)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def inicializar_banco():
    """Cria as tabelas do banco (se não existirem) e popula os produtos."""
    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            idade INTEGER
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT,
            preco REAL NOT NULL
        )
        """
    )

    # Cada linha representa um item que está atualmente na lista de
    # compras de um usuário. O "status" indica se o item ainda está
    # ativo na lista ou se já foi removido (removido = soft delete).
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'ativo',
            criado_em TEXT NOT NULL,
            atualizado_em TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
        """
    )

    # Toda alteração feita em um pedido (criação, edição de quantidade
    # ou remoção) gera uma linha aqui, preservando o histórico mesmo
    # depois que o item é removido da lista atual.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pedidos_historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            usuario_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER,
            acao TEXT NOT NULL,
            data_hora TEXT NOT NULL
        )
        """
    )

    conexao.commit()
    _seed_produtos(cursor, conexao)
    conexao.close()


def _seed_produtos(cursor, conexao):
    """Insere uma lista inicial de produtos, apenas se a tabela estiver vazia."""
    cursor.execute("SELECT COUNT(*) AS total FROM produtos")
    total = cursor.fetchone()["total"]
    if total > 0:
        return

    produtos_iniciais = [
        ("Arroz 5kg", "Grãos", 24.90),
        ("Feijão 1kg", "Grãos", 8.50),
        ("Açúcar 1kg", "Mercearia", 4.90),
        ("Café 500g", "Mercearia", 14.90),
        ("Óleo de Soja 900ml", "Mercearia", 7.80),
        ("Macarrão 500g", "Massas", 5.30),
        ("Molho de Tomate 340g", "Mercearia", 3.90),
        ("Leite Integral 1L", "Laticínios", 5.20),
        ("Queijo Mussarela 400g", "Laticínios", 22.90),
        ("Manteiga 200g", "Laticínios", 9.50),
        ("Pão de Forma", "Padaria", 8.90),
        ("Ovos (dúzia)", "Hortifruti", 12.90),
        ("Banana (kg)", "Hortifruti", 6.50),
        ("Tomate (kg)", "Hortifruti", 7.90),
        ("Batata (kg)", "Hortifruti", 5.90),
        ("Frango (kg)", "Carnes", 16.90),
        ("Carne Moída (kg)", "Carnes", 28.90),
        ("Detergente 500ml", "Limpeza", 2.90),
        ("Sabão em Pó 1kg", "Limpeza", 12.50),
        ("Papel Higiênico (4un)", "Higiene", 9.90),
    ]

    cursor.executemany(
        "INSERT INTO produtos (nome, categoria, preco) VALUES (?, ?, ?)",
        produtos_iniciais,
    )
    conexao.commit()


def agora():
    """Retorna a data/hora atual como texto, no formato ISO 8601."""
    return datetime.now().isoformat(timespec="seconds")
