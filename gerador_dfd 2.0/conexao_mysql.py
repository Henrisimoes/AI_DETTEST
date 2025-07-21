# conexao_mysql.py
import pymysql
from pymysql.cursors import DictCursor

def buscar_produto_por_nome(nome_item):
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="12345678@@",
        database="detran_ia",
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()

    query = """
        SELECT codigo, descricao
        FROM produtos
        WHERE descricao = %s
        LIMIT 1
    """
    cursor.execute(query, (nome_item,))
    resultado = cursor.fetchone()

    cursor.close()
    conn.close()
    return resultado

def listar_nomes_produtos():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="12345678@@",
        database="detran_ia"
    )
    cursor = conn.cursor()

    query = "SELECT DISTINCT descricao FROM produtos ORDER BY descricao"
    cursor.execute(query)
    resultados = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return resultados
