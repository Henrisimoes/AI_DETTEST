# gerar_ia.py
import requests

def gerar_texto_ia(dados, tipo):
    prompt = ""

    if tipo == "descricao":
        prompt = f"Descreva tecnicamente o item '{dados['item']}' para ser usado em {dados['finalidade']}."
    elif tipo == "justificativa":
        prompt = f"Justifique de forma objetiva a aquisição de {dados['quantidade']} unidades do item '{dados['item']}', considerando o uso para {dados['finalidade']}."
    elif tipo == "objetivo":
        prompt = f"Descreva o objetivo institucional da contratação do item '{dados['item']}'."
    elif tipo == "planejamento":
        prompt = f"Explique como o item '{dados['item']}' está alinhado ao planejamento estratégico do DETRAN-MT."
    elif tipo == "equipe":
        return "NÃO SE APLICA."
    else:
        return "[CAMPO INDEFINIDO]"

    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3:8b",
            "prompt": prompt,
            "stream": False
        })
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except Exception as e:
        print(f"Erro ao consultar modelo: {e}")

    return "[FALHA AO GERAR]"
