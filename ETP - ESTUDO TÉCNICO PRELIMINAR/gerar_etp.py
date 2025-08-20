# gerar_etp.py
from docxtpl import DocxTemplate
from datetime import datetime
from gerar_ia_etp import (
    gerar_justificativa_necessidade_ia,
    gerar_analise_mercado_ia,
    gerar_requisitos_tecnicos_ia,
    gerar_resultados_pretendidos_ia,
    gerar_impactos_ambientais_ia
)
import os

def gerar_etp_completo(dados_gerais, lista_de_itens):
    """
    Gera o Estudo Técnico Preliminar completo usando um modelo .docx e Jinja2.
    """
    # Usando o caminho do template fornecido pelo usuário
    caminho_template = r"C:\Users\pedrosilva\Desktop\PROJETO IA DETRAN\ETP - ESTUDO TÉCNICO PRELIMINAR\templates\template ETP.docx"

    try:
        doc = DocxTemplate(caminho_template)
    except Exception as e:
        print(f"Erro ao carregar o template '{caminho_template}': {e}")
        raise

    # Chama as funções de IA para gerar os textos complexos
    justificativa_necessidade_ia = gerar_justificativa_necessidade_ia(dados_gerais['finalidade_geral'])
    analise_mercado_ia = gerar_analise_mercado_ia(dados_gerais['solucoes_alternativas'], dados_gerais['solucao_escolhida'])
    requisitos_tecnicos_ia = gerar_requisitos_tecnicos_ia(dados_gerais['requisitos_tecnicos'])
    resultados_pretendidos_ia = gerar_resultados_pretendidos_ia(dados_gerais['finalidade_geral'])
    impactos_ambientais_ia = gerar_impactos_ambientais_ia(dados_gerais['impactos_ambientais'])
    
    # Usa o input do usuário diretamente, sem a IA, para a descrição da solução
    descricao_solucao_ia = dados_gerais['descricao_solucao']

    # Adiciona os valores unitários e totais para a tabela do ETP
    for item in lista_de_itens:
        try:
            valor_unitario = float(item.get('valor_unitario', '0').replace('R$ ', '').replace('.', '').replace(',', '.'))
            quantidade = int(item.get('qtd', '0').replace('.', ''))
            item['valor_unitario'] = f"R$ {valor_unitario:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
            item['valor_total'] = f"R$ {(valor_unitario * quantidade):,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
        except (ValueError, TypeError):
            item['valor_unitario'] = "N/A"
            item['valor_total'] = "N/A"

    # Cria o dicionário de contexto com todos os dados a serem substituídos
    context = {
        'etp_numero': dados_gerais['etp_numero'],
        'area_requisitante': dados_gerais['area_requisitante'],
        'responsavel': dados_gerais['responsavel'],
        'justificativa_necessidade_ia': justificativa_necessidade_ia,
        'subacao_input': dados_gerais['subacao'],
        'etapa_input': dados_gerais['etapa'],
        'natureza_despesa_input': dados_gerais['elemento_despesa'],
        'fonte_input': dados_gerais['fonte'],
        'requisitos_tecnicos_ia': requisitos_tecnicos_ia,
        'lista_de_itens': lista_de_itens,
        'analise_mercado_ia': analise_mercado_ia,
        'descricao_solucao_ia': descricao_solucao_ia,
        'justificativa_parcelamento_input': dados_gerais['justificativa_parcelamento'],
        'resultados_pretendidos_ia': resultados_pretendidos_ia,
        'providencias_input': dados_gerais['providencias'],
        'correlatas_input': dados_gerais['correlatas'],
        'impactos_ambientais_ia': impactos_ambientais_ia,
        'viabilidade': dados_gerais['viabilidade'],
        'data_final': dados_gerais['data_final'],
        'elaborador_nome': dados_gerais['elaborador_nome'],
        'elaborador_matricula': dados_gerais['elaborador_matricula'],
    }

    doc.render(context)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo = f"ETP_Gerado_{timestamp}.docx"
    
    doc.save(nome_arquivo)

    return nome_arquivo