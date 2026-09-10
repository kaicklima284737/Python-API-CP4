"""
Camada de Serviço (Service / Business Logic Layer) de Pedidos/Carrinho.

Concentra a regra de negócio da lista de compras individual do usuário e 
o histórico imutável de audit trail (auditoria).
"""

from database import get_connection, agora
from service_usuarios import buscar_usuario
from service_produtos import buscar_produto

def _registrar_historico(cursor, pedido_id, usuario_id, produto_id, quantidade, acao):
    """
    Função Privada (indicada pelo underline '_'):
    Grava uma linha de histórico para cada alteração no carrinho.
    
    Reaproveita a mesma transação (cursor) aberta pela função chamadora 
    para garantir atomicidade (ambas as operações acontecem ou nenhuma acontece).
    """
    cursor.execute(
        """
        INSERT INTO pedidos_historico
            (pedido_id, usuario_id, produto_id, quantidade, acao, data_hora)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (pedido_id, usuario_id, produto_id, quantidade, acao, agora()),
    )


def _linha_para_dict(linha):
    """
    Função Auxiliar / DTO (Data Transfer Object) manual:
    Converte o resultado bruto do banco (sqlite3.Row) proveniente de um JOIN
    em um dicionário limpo para a resposta da API.
    """
    return {
        "pedido_id": linha["id"],
        "usuario_id": linha["usuario_id"],
        "produto_id": linha["produto_id"],
        "produto_nome": linha["produto_nome"],
        "produto_categoria": linha["produto_categoria"],
        "produto_preco": linha["produto_preco"],
        "quantidade": linha["quantidade"],
        "status": linha["status"],
        "criado_em": linha["criado_em"],
        "atualizado_em": linha["atualizado_em"],
    }


def adicionar_item(usuario_id, produto_id, quantidade):
    """
    Adiciona um produto à lista ou incrementa a quantidade se já existir.
    Regra de Negócio: Impede a criação de registros duplicados do mesmo item ativo.
    """
    # Validação de Dependências: Garante que Usuário e Produto existem antes de prosseguir
    if buscar_usuario(usuario_id) is None:
        return None
    if buscar_produto(produto_id) is None:
        return None

    conexao = get_connection()
    cursor = conexao.cursor()

    # Verifica se o produto já está presente no carrinho ativo do usuário
    cursor.execute(
        """
        SELECT * FROM pedidos
        WHERE usuario_id = ? AND produto_id = ? AND status = 'ativo'
        """,
        (usuario_id, produto_id),
    )
    existente = cursor.fetchone()

    if existente:
        # Lógica de Atualização: Soma a nova quantidade à existente
        nova_quantidade = existente["quantidade"] + quantidade
        cursor.execute(
            "UPDATE pedidos SET quantidade = ?, atualizado_em = ? WHERE id = ?",
            (nova_quantidade, agora(), existente["id"]),
        )
        pedido_id = existente["id"]
        _registrar_historico(
            cursor, pedido_id, usuario_id, produto_id, nova_quantidade, "atualizado"
        )
    else:
        # Lógica de Inserção: Cria um novo item na lista
        agora_str = agora()
        cursor.execute(
            """
            INSERT INTO pedidos
                (usuario_id, produto_id, quantidade, status, criado_em, atualizado_em)
            VALUES (?, ?, ?, 'ativo', ?, ?)
            """,
            (usuario_id, produto_id, quantidade, agora_str, agora_str),
        )
        pedido_id = cursor.lastrowid  # Recupera o ID gerado pelo AUTOINCREMENT
        _registrar_historico(
            cursor, pedido_id, usuario_id, produto_id, quantidade, "adicionado"
        )

    conexao.commit()
    conexao.close()
    return buscar_item(pedido_id)


def listar_itens_usuario(usuario_id, incluir_removidos=False):
    """
    Retorna os itens da lista do usuário utilizando JOIN relacional.
    - JOIN: Combina colunas da tabela 'pedidos' com a tabela 'produtos'.
    """
    if buscar_usuario(usuario_id) is None:
        return None

    conexao = get_connection()
    cursor = conexao.cursor()

    # Construção condicional da query para tratar o Soft Delete
    filtro_status = "" if incluir_removidos else "AND p.status = 'ativo'"
    cursor.execute(
        f"""
        SELECT p.id, p.usuario_id, p.produto_id, p.quantidade, p.status,
               p.criado_em, p.atualizado_em,
               pr.nome AS produto_nome, pr.categoria AS produto_categoria,
               pr.preco AS produto_preco
        FROM pedidos p
        JOIN produtos pr ON pr.id = p.produto_id
        WHERE p.usuario_id = ? {filtro_status}
        ORDER BY p.criado_em
        """,
        (usuario_id,),
    )
    # List Comprehension: Transforma cada linha do banco em dicionário formatado
    itens = [_linha_para_dict(linha) for linha in cursor.fetchall()]
    conexao.close()
    return itens


def buscar_item(pedido_id):
    """
    Busca os detalhes completos de um item específico da lista pelo seu ID.
    """
    conexao = get_connection()
    cursor = conexao.cursor()
    cursor.execute(
        """
        SELECT p.id, p.usuario_id, p.produto_id, p.quantidade, p.status,
               p.criado_em, p.atualizado_em,
               pr.nome AS produto_nome, pr.categoria AS produto_categoria,
               pr.preco AS produto_preco
        FROM pedidos p
        JOIN produtos pr ON pr.id = p.produto_id
        WHERE p.id = ?
        """,
        (pedido_id,),
    )
    linha = cursor.fetchone()
    conexao.close()
    return _linha_para_dict(linha) if linha else None


def atualizar_item(pedido_id, quantidade):
    """
    Atualiza a quantidade de um item mantendo a rastreabilidade no histórico.
    """
    item_atual = buscar_item(pedido_id)
    # Garante que só é possível alterar itens existentes e que estejam com status 'ativo'
    if item_atual is None or item_atual["status"] != "ativo":
        return None

    conexao = get_connection()
    cursor = conexao.cursor()
    cursor.execute(
        "UPDATE pedidos SET quantidade = ?, atualizado_em = ? WHERE id = ?",
        (quantidade, agora(), pedido_id),
    )
    _registrar_historico(
        cursor,
        pedido_id,
        item_atual["usuario_id"],
        item_atual["produto_id"],
        quantidade,
        "atualizado",
    )
    conexao.commit()
    conexao.close()
    return buscar_item(pedido_id)


def remover_item(pedido_id):
    """
    Executa o Soft Delete: altera o status para 'removido' sem excluir o registro do banco.
    """
    item_atual = buscar_item(pedido_id)
    if item_atual is None or item_atual["status"] != "ativo":
        return False

    conexao = get_connection()
    cursor = conexao.cursor()
    cursor.execute(
        "UPDATE pedidos SET status = 'removido', atualizado_em = ? WHERE id = ?",
        (agora(), pedido_id),
    )
    _registrar_historico(
        cursor,
        pedido_id,
        item_atual["usuario_id"],
        item_atual["produto_id"],
        item_atual["quantidade"],
        "removido",
    )
    conexao.commit()
    conexao.close()
    return True


def listar_historico_usuario(usuario_id):
    """
    Consulta a tabela de auditoria 'pedidos_historico' ordenada da alteração 
    mais recente para a mais antiga (DESC).
    """
    if buscar_usuario(usuario_id) is None:
        return None

    conexao = get_connection()
    cursor = conexao.cursor()
    cursor.execute(
        """
        SELECT h.id, h.pedido_id, h.usuario_id, h.produto_id, h.quantidade,
               h.acao, h.data_hora, pr.nome AS produto_nome
        FROM pedidos_historico h
        JOIN produtos pr ON pr.id = h.produto_id
        WHERE h.usuario_id = ?
        ORDER BY h.data_hora DESC
        """,
        (usuario_id,),
    )
    historico = [dict(linha) for linha in cursor.fetchall()]
    conexao.close()
    return historico