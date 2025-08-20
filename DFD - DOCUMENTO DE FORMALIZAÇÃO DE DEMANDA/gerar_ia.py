# gerar_ia.py
import requests

def gerar_texto_ia(dados, lista_itens, tipo):
    """
    Gera um texto usando o modelo de IA do Ollama com base no contexto do formulário e na lista de itens.
    """
    prompt = ""

    finalidade_geral = dados.get('finalidade', '')
    
    # Converte a lista de dicionários de itens em uma string formatada
    itens_formatados = "\n".join([
        f"- Descrição: {item['descricao']}\n  Quantidade: {item['qtd']}\n  Finalidade Específica: {item['finalidade_especifica']}"
        for item in lista_itens
    ])

    if tipo == "descricao":
        prompt = (
            f"Atue como um redator técnico especializado em documentos de contratação pública. "
            f"Escreva uma descrição curta, clara e precisa sobre a demanda de aquisição/contratação, "
            f"baseada na seguinte finalidade geral: '{finalidade_geral}'. "
            f"Itens detalhados:\n{itens_formatados}\n\n"
            f"Destaque a relevância da demanda para as operações do órgão. "
            f"Use linguagem formal, objetiva e sem redundâncias. "
            f"Limite a resposta a até 3 frases curtas."
        )

    elif tipo == "justificativa":
        prompt = (
            f"Você é um analista de compras responsável por redigir justificativas em documentos DFD. "
            f"Redija uma justificativa objetiva, convincente e sucinta "
            f"para a demanda de aquisição/contratação, considerando a seguinte finalidade geral: '{finalidade_geral}'. "
            f"Itens detalhados:\n{itens_formatados}\n\n"
            f"Foque na necessidade institucional, custo-benefício e benefícios diretos para o DETRAN-MT. "
            f"Considere que a demanda pode envolver múltiplos itens ou serviços. "
            f"Resuma em até 4-5 frases claras, se necessário."
        )

    elif tipo == "objetivo":
        prompt = (
            f"Redija de forma clara, concisa e institucional "
            f"o objetivo da demanda de aquisição/contratação. "
            f"Explique como essa aquisição atende a missão e as metas do DETRAN-MT, "
            f"considerando a finalidade geral: '{finalidade_geral}'. "
            f"Itens detalhados:\n{itens_formatados}\n\n"
            f"Evite termos vagos e prolongamentos desnecessários. "
            f"Limite a resposta a 2 ou 3 frases diretas."
        )

    elif tipo == "planejamento":
        prompt = (
            f"Explique em 2 ou 3 frases objetivas como a demanda de aquisição/contratação, "
            f"com finalidade '{finalidade_geral}', está alinhada ao planejamento estratégico do DETRAN-MT. "
            f"Itens detalhados:\n{itens_formatados}\n\n"
            f"Relacione a demanda a metas institucionais, melhoria de processos "
            f"ou eficiência administrativa. Use linguagem técnica, impessoal e sucinta. "
            f"Se o planejamento mais recente não for específico, mencione a busca por 'racionalização de recursos', 'otimização de serviços' ou 'modernização da infraestrutura'."
        )

    elif tipo == "equipe":
        return "NÃO SE APLICA."

    else:
        return "[CAMPO INDEFINIDO]"

    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3:8b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 150
            }
        })
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            print(f"Erro na resposta do modelo Ollama: {response.status_code} - {response.text}")
            return f"[FALHA NA RESPOSTA DO MODELO: {response.status_code}]"
    except requests.exceptions.ConnectionError:
        print("Erro de conexão com o Ollama. Certifique-se de que o servidor está rodando em http://localhost:11434")
        return "[ERRO DE CONEXÃO COM O MODELO IA]"
    except Exception as e:
        print(f"Erro ao consultar modelo: {e}")
        return "[FALHA AO GERAR]"