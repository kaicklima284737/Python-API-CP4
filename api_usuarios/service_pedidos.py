"""
Lista de compras individual de cada usuário (tabela `pedidos`) e o
histórico de alterações (tabela `pedidos_historico`).

Cada linha de `pedidos` é um produto (da tabela `produtos`) que o
usuário colocou na própria lista, com uma quantidade. O item pode ser
editado (quantidade) ou removido; nos dois casos, e também na criação,
uma linha é gravada em `pedidos_historico`, preservando o registro
mesmo depois de o item ser removido da lista atual.
"""

from database import get_connection, agora
from service_usuarios import buscar_usuario
from service_produtos import buscar_produto


def _registrar_historico(cursor, pedido_id, usuario_id, produto_id, quantidade, acao):
    cursor.execute(
        """
        INSERT INTO pedidos_historico
            (pedido_id, usuario_id, produto_id, quantidade, acao, data_hora)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (pedido_id, usuario_id, produto_id, quantidade, acao, agora()),
    )


def _linha_para_dict(linha):
    """Converte uma linha da consulta (com join) em um dicionário amigável."""
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
    """Adiciona um produto à lista de compras de um usuário.

    Retorna None se o usuário ou o produto não existirem.
    Se o produto já estiver ativo na lista do usuário, soma a
    quantidade informada em vez de criar uma linha duplicada.
    """
    if buscar_usuario(usuario_id) is None:
        return None
    if buscar_produto(produto_id) is None:
        return None

    conexao = get_connection()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT * FROM pedidos
        WHERE usuario_id = ? AND produto_id = ? AND status = 'ativo'
        """,
        (usuario_id, produto_id),
    )
    existente = cursor.fetchone()

    if existente:
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
        agora_str = agora()
        cursor.execute(
            """
            INSERT INTO pedidos
                (usuario_id, produto_id, quantidade, status, criado_em, atualizado_em)
            VALUES (?, ?, ?, 'ativo', ?, ?)
            """,
            (usuario_id, produto_id, quantidade, agora_str, agora_str),
        )
        pedido_id = cursor.lastrowid
        _registrar_historico(
            cursor, pedido_id, usuario_id, produto_id, quantidade, "adicionado"
        )

    conexao.commit()
    conexao.close()
    return buscar_item(pedido_id)


def listar_itens_usuario(usuario_id, incluir_removidos=False):
    if buscar_usuario(usuario_id) is None:
        return None

    conexao = get_connection()
    cursor = conexao.cursor()

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
    itens = [_linha_para_dict(linha) for linha in cursor.fetchall()]
    conexao.close()
    return itens


def buscar_item(pedido_id):
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
    """Atualiza a quantidade de um item ativo na lista de um usuário."""
    item_atual = buscar_item(pedido_id)
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
    """Remove (soft delete) um item da lista de compras do usuário."""
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
