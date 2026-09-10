"""
Camada de Acesso a Dados (Data Access Layer - DAL) em SQLite.

Este módulo é responsável por:
1. Gerenciar a conexão física com o arquivo de banco de dados 'database.db'.
2. Garantir a criação da estrutura do banco (Tabelas, Chaves Primárias e Estrangeiras).
3. Popular o banco com dados iniciais (Seed) caso ele esteja vazio.
4. Gerenciar inserção, atualização e consultas de pedidos com arredondamento em 2 casas decimais.
"""

import sqlite3
from datetime import datetime

# Nome do arquivo de banco de dados relacional SQLite que será criado no disco
DB_FILE = "database.db"


def get_connection():
    """
    Abre e configura uma conexão com o SQLite.
    
    Conceitos de Engenharia:
    - sqlite3.Row: Transforma o resultado de tuplas simples (ex: (1, 'Arroz')) 
      em objetos parecidos com dicionários (ex: linha['nome']).
    - PRAGMA foreign_keys = ON: Por padrão, o SQLite desabilita a verificação 
      de Chaves Estrangeiras. Executar esse PRAGMA garante a Integridade Referencial.
    """
    conexao = sqlite3.connect(DB_FILE)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def inicializar_banco():
    """
    Cria a estrutura de tabelas (DDL - Data Definition Language),
    aplica migrações de colunas, atualiza registros existentes e executa o povoamento inicial (Seed).
    """
    conexao = get_connection()
    cursor = conexao.cursor()

    # TABELA: usuarios
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

    # TABELA: produtos
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

    # TABELA: pedidos
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 1,
            valor_total REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'ativo',
            criado_em TEXT NOT NULL,
            atualizado_em TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
        """
    )

    # TABELA: pedidos_historico
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pedidos_historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            usuario_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER,
            valor_total REAL,
            acao TEXT NOT NULL,
            data_hora TEXT NOT NULL
        )
        """
    )

    # MIGRAÇÃO AUTOMÁTICA
    try:
        cursor.execute("ALTER TABLE pedidos ADD COLUMN valor_total REAL NOT NULL DEFAULT 0.0")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE pedidos_historico ADD COLUMN valor_total REAL")
    except sqlite3.OperationalError:
        pass

    # ATUALIZAÇÃO EM MASSA: Garante até 2 casas decimais nos registros antigos
    cursor.execute(
        """
        UPDATE pedidos
        SET valor_total = ROUND(quantidade * (
            SELECT preco 
            FROM produtos 
            WHERE produtos.id = pedidos.produto_id
        ), 2)
        WHERE valor_total = 0.0 OR valor_total IS NULL
        """
    )

    conexao.commit()
    _seed_produtos(cursor, conexao)
    conexao.close()


def _seed_produtos(cursor, conexao):
    """
    Povoamento Inicial (Seeding) de produtos.
    """
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
    """
    Retorna a data/hora atual no padrão ISO 8601.
    """
    return datetime.now().isoformat(timespec="seconds")


# ------------------------------------------------------------------
# Manipulação de Pedidos com Arredondamento
# ------------------------------------------------------------------

def adicionar_pedido(usuario_id: int, produto_id: int, quantidade: int):
    """
    Cria um novo pedido calculando o valor total arredondado para 2 casas decimais.
    """
    conexao = get_connection()
    cursor = conexao.cursor()
    
    cursor.execute("SELECT preco FROM produtos WHERE id = ?", (produto_id,))
    produto = cursor.fetchone()
    if not produto:
        conexao.close()
        raise ValueError("Produto não encontrado")
        
    valor_total = round(produto["preco"] * quantidade, 2)
    data_atual = agora()
    
    cursor.execute(
        """
        INSERT INTO pedidos (usuario_id, produto_id, quantidade, valor_total, status, criado_em, atualizado_em)
        VALUES (?, ?, ?, ?, 'ativo', ?, ?)
        """,
        (usuario_id, produto_id, quantidade, valor_total, data_atual, data_atual)
    )
    pedido_id = cursor.lastrowid
    
    cursor.execute(
        """
        INSERT INTO pedidos_historico (pedido_id, usuario_id, produto_id, quantidade, valor_total, acao, data_hora)
        VALUES (?, ?, ?, ?, ?, 'INSERIDO', ?)
        """,
        (pedido_id, usuario_id, produto_id, quantidade, valor_total, data_atual)
    )
    
    conexao.commit()
    conexao.close()
    return pedido_id


def atualizar_pedido(pedido_id: int, nova_quantidade: int):
    """
    Atualiza a quantidade de um pedido recalculando o valor total para 2 casas decimais.
    """
    conexao = get_connection()
    cursor = conexao.cursor()
    
    cursor.execute(
        """
        SELECT p.usuario_id, p.produto_id, pr.preco 
        FROM pedidos p 
        JOIN produtos pr ON pr.id = p.produto_id 
        WHERE p.id = ?
        """,
        (pedido_id,)
    )
    pedido = cursor.fetchone()
    if not pedido:
        conexao.close()
        raise ValueError("Pedido não encontrado")
        
    valor_total = round(pedido["preco"] * nova_quantidade, 2)
    data_atual = agora()
    
    cursor.execute(
        """
        UPDATE pedidos 
        SET quantidade = ?, valor_total = ?, atualizado_em = ?
        WHERE id = ?
        """,
        (nova_quantidade, valor_total, data_atual, pedido_id)
    )
    
    cursor.execute(
        """
        INSERT INTO pedidos_historico (pedido_id, usuario_id, produto_id, quantidade, valor_total, acao, data_hora)
        VALUES (?, ?, ?, ?, ?, 'ALTERADO', ?)
        """,
        (pedido_id, pedido["usuario_id"], pedido["produto_id"], nova_quantidade, valor_total, data_atual)
    )
    
    conexao.commit()
    conexao.close()


def listar_pedidos_por_usuario(usuario_id: int):
    """
    Retorna pedidos ativos de um usuário especifico formatando o valor_total para 2 casas decimais.
    """
    conexao = get_connection()
    cursor = conexao.cursor()
    
    cursor.execute(
        """
        SELECT 
            p.id AS pedido_id,
            u.id AS usuario_id,
            u.nome AS usuario_nome,
            pr.nome AS produto_nome,
            pr.preco AS preco_unitario,
            p.quantidade,
            ROUND(p.valor_total, 2) AS valor_total,
            p.status,
            p.criado_em,
            p.atualizado_em
        FROM pedidos p
        JOIN usuarios u ON u.id = p.usuario_id
        JOIN produtos pr ON pr.id = p.produto_id
        WHERE p.usuario_id = ?
        ORDER BY p.criado_em DESC
        """,
        (usuario_id,)
    )
    
    pedidos = cursor.fetchall()
    conexao.close()
    return pedidos


def listar_historico_por_usuario(usuario_id: int):
    """
    Retorna o histórico de compras de um usuário formatando o valor_total para 2 casas decimais.
    """
    conexao = get_connection()
    cursor = conexao.cursor()
    
    cursor.execute(
        """
        SELECT 
            h.id AS historico_id,
            h.pedido_id,
            u.id AS usuario_id,
            u.nome AS usuario_nome,
            pr.nome AS produto_nome,
            h.quantidade,
            ROUND(h.valor_total, 2) AS valor_total,
            h.acao,
            h.data_hora
        FROM pedidos_historico h
        JOIN usuarios u ON u.id = h.usuario_id
        JOIN produtos pr ON pr.id = h.produto_id
        WHERE h.usuario_id = ?
        ORDER BY h.data_hora DESC
        """,
        (usuario_id,)
    )
    
    historico = cursor.fetchall()
    conexao.close()
    return historico