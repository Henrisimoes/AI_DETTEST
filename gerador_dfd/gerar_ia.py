# gerar_ia.py
import requests

def gerar_texto_ia(dados, tipo):
    prompt = ""

    if tipo == "descricao":
        prompt = (
            f"Atue como um redator técnico especializado. "
            f"Escreva uma descrição curta, clara e precisa sobre o item '{dados['item']}', "
            f"explicando suas principais características técnicas e destacando "
            f"sua relevância para ser utilizado em {dados['finalidade']}. "
            f"Use linguagem formal, objetiva e sem redundâncias. "
            f"Limite a resposta a até 3 frases curtas."
        )

    elif tipo == "justificativa":
        prompt = (
            f"Você é um analista de compras. "
            f"Redija uma justificativa objetiva, convincente e sucinta "
            f"para a aquisição de {dados['quantidade']} unidades do item '{dados['item']}', "
            f"considerando sua aplicação prática para {dados['finalidade']}. "
            f"Foque na necessidade institucional, custo-benefício e benefícios diretos. "
            f"Resuma em até 3 frases claras."
        )

    elif tipo == "objetivo":
        prompt = (
            f"Redija de forma clara, concisa e institucional "
            f"o objetivo da contratação do item '{dados['item']}'. "
            f"Explique como essa aquisição atende a missão e as metas do órgão público, "
            f"evitando termos vagos e prolongamentos desnecessários. "
            f"Limite a resposta a 2 ou 3 frases diretas."
        )

    elif tipo == "planejamento":
        prompt = (
            f"Explique em 2 ou 3 frases objetivas como a aquisição do item '{dados['item']}' "
            f"está alinhada ao planejamento estratégico do DETRAN-MT. "
            f"Relacione o item a metas institucionais, melhoria de processos "
            f"ou eficiência administrativa. Use linguagem técnica, impessoal e sucinta."
        )
        
    elif tipo == "estudo_tecnico":
        prompt = (
            f"Com base no item '{dados['item']}' e na finalidade '{dados['finalidade']}', "
            f"indique se é necessária a elaboração do Estudo Técnico Preliminar (ETP) e análise de riscos "
            f"segundo a Lei 14.133/21. Responda apenas SIM ou NÃO. "
            f"Se for NÃO, forneça também uma justificativa curta e objetiva."
        )

    elif tipo == "plano_contratacao":
        prompt = (
            f"Com base no item '{dados['item']}' e na finalidade '{dados['finalidade']}', "
            f"indique se os objetos a serem adquiridos/contratados estão previstos no Plano de Contratações Anual (PCA). "
            f"Responda apenas SIM ou NÃO. Se for NÃO, justifique de forma breve."
        )

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
