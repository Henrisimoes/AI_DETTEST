# gerar_ia_etp.py
import requests
import json

def _chamar_ollama(prompt_texto, modelo="llama3:8b", max_tokens=500):
    """Função para gerar texto com o modelo local Ollama."""
    if not prompt_texto or prompt_texto.strip() == "":
        return "Texto gerado pela IA."
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": modelo,
            "prompt": prompt_texto,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": max_tokens
            }
        }, timeout=120)  # Aumenta o timeout para 120 segundos
        
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            print(f"Erro na resposta do modelo Ollama: {response.status_code} - {response.text}")
            return f"[FALHA NA RESPOSTA DO MODELO: {response.status_code}]"
    except requests.exceptions.ConnectionError:
        print("Erro de conexão com o Ollama. Certifique-se de que o servidor está rodando em http://localhost:11434.")
        return "[ERRO DE CONEXÃO COM O MODELO IA]"
    except requests.exceptions.Timeout:
        print("A solicitação ao Ollama excedeu o tempo limite. Tente novamente.")
        return "[ERRO DE TEMPO LIMITE DA IA]"
    except Exception as e:
        print(f"Erro ao consultar modelo Ollama: {e}")
        return "[FALHA AO GERAR TEXTO COM IA]"

def gerar_justificativa_necessidade_ia(finalidade_geral):
    """Gera o texto para o item 3 do ETP."""
    prompt = f"""
    Com base na seguinte finalidade geral para a contratação: '{finalidade_geral}',
    elabore um texto detalhado para a seção 'Descrição da Necessidade da Contratação'
    de um ETP (Estudo Técnico Preliminar). O texto deve ser formal, técnico e
    justificar a contratação em termos de eficiência e interesse público.
    """
    return _chamar_ollama(prompt)

def gerar_requisitos_tecnicos_ia(requisitos_base):
    """Gera o texto para o item 5 do ETP."""
    prompt = f"""
    Com base nos requisitos técnicos e de sustentabilidade fornecidos: '{requisitos_base}',
    elabore um texto formal e completo para a seção 'Descrição dos Requisitos da Contratação',
    incluindo critérios de qualidade, garantia e sustentabilidade.
    """
    return _chamar_ollama(prompt)

def gerar_analise_mercado_ia(solucoes_alternativas, solucao_escolhida):
    """Gera o texto para o item 7 do ETP."""
    prompt = f"""
    A solução escolhida para um ETP é: '{solucao_escolhida}'.
    As soluções alternativas consideradas no mercado foram: '{solucoes_alternativas}'.
    
    Gere um texto para a seção 'Análise das soluções alternativas de mercado',
    apresentando as opções consideradas, suas vantagens e desvantagens, e
    justificando tecnicamente a escolha da solução selecionada.
    """
    return _chamar_ollama(prompt)

def gerar_resultados_pretendidos_ia(finalidade_geral):
    """Gera o texto para o item 11 do ETP."""
    prompt = f"""
    Com base na finalidade geral: '{finalidade_geral}', descreva os resultados
    pretendidos para o ETP, em termos de economicidade e de melhor aproveitamento
    dos recursos humanos, materiais e financeiros disponíveis.
    """
    return _chamar_ollama(prompt)

def gerar_impactos_ambientais_ia(impactos_base):
    """Gera o texto para o item 14 do ETP."""
    prompt = f"""
    Com base nas informações sobre impactos ambientais: '{impactos_base}', gere um texto
    para a seção 'Descrição de Possíveis Impactos Ambientais' do ETP, incluindo
    medidas mitigadoras, requisitos de baixo consumo e logística reversa.
    """
    return _chamar_ollama(prompt)

def gerar_descricao_solucao_ia(descricao_base):
    """Gera o texto para o item 9 do ETP."""
    prompt = f"""
    Com base na descrição da solução fornecida: '{descricao_base}', elabore um texto formal e completo para a seção 'Descrição da Solução como um todo', incluindo exigências relacionadas à garantia, manutenção e assistência técnica.
    """
    return _chamar_ollama(prompt)