import pymysql

def buscar_produto_por_nome(nome_item):
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="12345678@@",
        database="detran_ia"
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    query = """
        SELECT catmat, descricao, unidade
        FROM produtos
        WHERE descricao = %s
        LIMIT 1
    """
    cursor.execute(query, (nome_item,))
    resultado = cursor.fetchone()

    cursor.close()
    conn.close()
    return resultado
