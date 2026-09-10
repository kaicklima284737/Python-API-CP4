"""
Camada de Acesso a Dados (Data Access Layer - DAL) em SQLite.

Este módulo é responsável por:
1. Gerenciar a conexão física com o arquivo de banco de dados 'database.db'.
2. Garantir a criação da estrutura do banco (Tabelas, Chaves Primárias e Estrangeiras).
3. Popular o banco com dados iniciais (Seed) caso ele esteja vazio.
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
    Cria a estrutura de tabelas (DDL - Data Definition Language) 
    e executa o povoamento inicial (Seed) de dados.
    """
    conexao = get_connection()
    cursor = conexao.cursor()

    # TABELA: usuarios
    # Armazena dados cadastrais dos clientes.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- Chave Primária Autoincrementada
            nome TEXT NOT NULL,                  -- Campo obrigatório
            email TEXT NOT NULL UNIQUE,           -- Unicidade: não permite e-mails duplicados
            idade INTEGER
        )
        """
    )

    # TABELA: produtos
    # Catálogo global de produtos disponíveis para compra.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT,
            preco REAL NOT NULL                  -- Tipo REAL usado para valores decimais (floats)
        )
        """
    )

    # TABELA: pedidos
    # Representa os itens presentes no carrinho/lista de compras de um usuário.
    # Implementa 'Soft Delete' através da coluna status ('ativo' / 'removido').
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
            -- Integridade Referencial:
            -- Se o usuário for excluído, todos os seus pedidos vinculados também são removidos (CASCADE).
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
        """
    )

    # TABELA: pedidos_historico
    # Tabela de Auditoria (Audit Log): Mantém o registro histórico imutável de todas 
    # as ações (inserções, alterações de quantidade e remoções) realizadas pelos usuários.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pedidos_historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            usuario_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER,
            acao TEXT NOT NULL,                  -- Ex: 'INSERIDO', 'ALTERADO', 'REMOVIDO'
            data_hora TEXT NOT NULL
        )
        """
    )

    # Confirma a execução dos comandos DDL
    conexao.commit()
    
    # Executa a carga inicial de dados
    _seed_produtos(cursor, conexao)
    
    # Fecha a conexão para liberar memória e evitar locks no banco
    conexao.close()


def _seed_produtos(cursor, conexao):
    """
    Povoamento Inicial (Seeding):
    Insere produtos padrão apenas se a tabela estiver completamente vazia.
    O underline '_' no início do nome da função indica que ela é de uso privado/interno deste módulo.
    """
    cursor.execute("SELECT COUNT(*) AS total FROM produtos")
    total = cursor.fetchone()["total"]
    
    # Se já existir qualquer produto cadastrado, interrompe a execução para não duplicar
    if total > 0:
        return

    # Lista de tuplas com a massa de dados inicial
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

    # executemany: Insere múltiplos registros em um único lote (Bulk Insert) de forma performática
    cursor.executemany(
        "INSERT INTO produtos (nome, categoria, preco) VALUES (?, ?, ?)",
        produtos_iniciais,
    )
    conexao.commit()


def agora():
    """
    Função utilitária para padronização de datas.
    Retorna a data/hora atual formatada em texto no padrão internacional ISO 8601 (YYYY-MM-DDTHH:MM:SS).
    """
    return datetime.now().isoformat(timespec="seconds")