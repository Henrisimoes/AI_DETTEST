# gerar_ia.py
import requests

def gerar_texto_ia(dados, tipo):
    prompt = ""

    # Extrair a finalidade geral. Se não existir, usar uma string vazia para evitar erro.
    # O app.py já garante que 'finalidade_geral_dfd' está em dados_gerais como 'finalidade'.
    finalidade_geral = dados.get('finalidade', '')
    
    # Você também pode querer acessar a lista de itens se necessário para prompts mais complexos.
    # No entanto, a lista_itens_dfd é passada como um argumento separado para gerar_dfd_completo,
    # e não está em 'dados' (dados_formulario) aqui.
    # Se precisar dos itens individuais, eles teriam que ser passados para gerar_texto_ia ou
    # gerados de forma mais abstrata pela IA baseando-se na finalidade geral.

    if tipo == "descricao":
        # Descrição geral da demanda, não de um item específico
        prompt = (
            f"Atue como um redator técnico especializado em documentos de contratação pública. "
            f"Escreva uma descrição curta, clara e precisa sobre a demanda de aquisição/contratação, "
            f"baseada na seguinte finalidade geral: '{finalidade_geral}'. "
            f"Destaque a relevância da demanda para as operações do órgão. "
            f"Use linguagem formal, objetiva e sem redundâncias. "
            f"Limite a resposta a até 3 frases curtas."
        )

    elif tipo == "justificativa":
        # Justificativa para a demanda como um todo, não para um item único
        prompt = (
            f"Você é um analista de compras responsável por redigir justificativas em documentos DFD. "
            f"Redija uma justificativa objetiva, convincente e sucinta "
            f"para a demanda de aquisição/contratação, considerando a seguinte finalidade geral: '{finalidade_geral}'. "
            f"Foque na necessidade institucional, custo-benefício e benefícios diretos para o DETRAN-MT. "
            f"Considere que a demanda pode envolver múltiplos itens ou serviços. "
            f"Resuma em até 4-5 frases claras, se necessário." # Aumentei um pouco o limite
        )

    elif tipo == "objetivo":
        # Objetivo da contratação como um todo
        prompt = (
            f"Redija de forma clara, concisa e institucional "
            f"o objetivo da demanda de aquisição/contratação. "
            f"Explique como essa aquisição atende a missão e as metas do DETRAN-MT, "
            f"considerando a finalidade geral: '{finalidade_geral}'. "
            f"Evite termos vagos e prolongamentos desnecessários. "
            f"Limite a resposta a 2 ou 3 frases diretas."
        )

    elif tipo == "planejamento":
        # Alinhamento da demanda com o planejamento estratégico
        prompt = (
            f"Explique em 2 ou 3 frases objetivas como a demanda de aquisição/contratação, "
            f"com finalidade '{finalidade_geral}', está alinhada ao planejamento estratégico do DETRAN-MT. "
            f"Relacione a demanda a metas institucionais, melhoria de processos "
            f"ou eficiência administrativa. Use linguagem técnica, impessoal e sucinta. "
            f"Se o planejamento mais recente não for específico, mencione a busca por 'racionalização de recursos', 'otimização de serviços' ou 'modernização da infraestrutura'."
        )
        
    elif tipo == "estudo_tecnico":
        # Indicação de ETP para a demanda geral, considerando a finalidade
        prompt = (
            f"Com base na finalidade geral da demanda: '{finalidade_geral}', "
            f"indique se é necessária a elaboração do Estudo Técnico Preliminar (ETP) e análise de riscos "
            f"segundo a Lei 14.133/21. Responda apenas SIM ou NÃO. "
            f"Se for NÃO, forneça também uma justificativa curta e objetiva como 'Não se aplica'."
            f"Geralmente, para materiais de consumo ou itens de baixo valor/complexidade, a resposta é NÃO."
        )

    elif tipo == "plano_contratacao":
        # Indicação de PCA para a demanda geral, considerando a finalidade
        prompt = (
            f"Com base na finalidade geral da demanda: '{finalidade_geral}', "
            f"indique se os objetos a serem adquiridos/contratados estão previstos no Plano de Contratações Anual (PCA) do DETRAN-MT. "
            f"Responda apenas SIM ou NÃO. Se for NÃO, justifique de forma breve como 'Não previsto no PCA por ser demanda excepcional/emergencial' ou similar."
            f"Geralmente, a maioria das demandas regulares é SIM."
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
            "options": { # Adicione opções para controlar a saída do LLM
                "temperature": 0.3, # Menor temperatura para respostas mais diretas e menos criativas
                "top_p": 0.9,
                "max_tokens": 150 # Limite de tokens para controlar o tamanho da resposta
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