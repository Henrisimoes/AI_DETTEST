# gerar_dfd.py
from docxtpl import DocxTemplate
from datetime import datetime
from gerar_ia import gerar_texto_ia
import locale
import os
import re

# Configura locale para português brasileiro para a data formatada
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, '') # Fallback para o padrão do sistema

def sanitize_filename(filename):
    """
    Remove ou substitui caracteres inválidos em nomes de arquivo e garante um tamanho razoável.
    """
    filename = re.sub(r'[\\/:*?"<>|]', '', filename)
    filename = re.sub(r'\s+', '_', filename)
    filename = re.sub(r'_+', '_', filename)
    if len(filename) > 80:
        filename = filename[:80]
    return filename.strip('_')

def gerar_opcoes_marcadas(opcao_escolhida, opcoes_dict):
    linhas = []
    max_label_len = 0
    if opcoes_dict:
        max_label_len = max(len(label) for label in opcoes_dict)

    for label, chave in opcoes_dict.items():
        marcado = "(X)" if chave == opcao_escolhida else "( )"
        linha = f"{marcado} {label.ljust(max_label_len)}"
        linhas.append(linha)

    return "\n".join(linhas)

def gerar_dfd_completo(dados_formulario, lista_itens):
    template_path = os.path.join(os.path.dirname(__file__), "templates", "modelo_dfd.docx")
    doc = DocxTemplate(template_path)

    # Dicionário de contexto para o template, incluindo todos os dados do formulário
    contexto = dados_formulario.copy()

    # --- CORREÇÃO APLICADA AQUI: PASSANDO A LISTA DE ITENS PARA A IA ---
    
    # Frase a ser removida do texto gerado pela IA
    frase_a_remover = "Aqui está uma justificativa objetiva, convincente e sucinta para a demanda de aquisição/contratação:"

    # Geração dos textos com a IA. Note que `lista_itens` foi adicionado como segundo argumento.
    justificativa_ia = gerar_texto_ia(dados_formulario, lista_itens, "justificativa")
    if justificativa_ia:
        justificativa_limpa = justificativa_ia.replace(frase_a_remover, "").strip()
        contexto["justificativa"] = justificativa_limpa
    else:
        contexto["justificativa"] = dados_formulario.get("justificativa", "")

    # As outras chamadas para a IA também foram corrigidas
    contexto["descricao"] = gerar_texto_ia(dados_formulario, lista_itens, "descricao") or dados_formulario.get("descricao")
    contexto["objetivo"] = gerar_texto_ia(dados_formulario, lista_itens, "objetivo") or dados_formulario.get("objetivo")
    contexto["planejamento"] = gerar_texto_ia(dados_formulario, lista_itens, "planejamento") or dados_formulario.get("planejamento")
    contexto["equipe"] = gerar_texto_ia(dados_formulario, lista_itens, "equipe") or dados_formulario.get("equipe")
    
    # --- FIM DA CORREÇÃO ---

    # -------------------------------------------------------------------
    # Lógica para os novos campos ETP e PCA (Tópicos 4 e 5)
    # -------------------------------------------------------------------
    contexto['necessidade_etp_bool'] = dados_formulario.get('necessidade_etp')
    contexto['previsao_pca_bool'] = dados_formulario.get('previsao_pca')

    if contexto['necessidade_etp_bool'] == 'NÃO':
        contexto['justificativa_etp'] = dados_formulario.get('justificativa_etp', "Não se aplica.")
    else:
        contexto['justificativa_etp'] = "A necessidade de Estudos Técnicos Preliminares (ETP) é verificada para esta contratação, por se tratar de objeto de maior complexidade."
    
    if contexto['previsao_pca_bool'] == 'NÃO':
        contexto['justificativa_pca'] = dados_formulario.get('justificativa_pca', "")
    else:
        contexto['justificativa_pca'] = "Os objetos a serem adquiridos/contratados estão previstos no Plano de Contratações Anual."
    # -------------------------------------------------------------------
    
    # Lógica para as opções de objeto e forma de contratação
    opcoes_objeto = {
        "Material de consumo": "Material de consumo",
        "Material permanente": "Material permanente",
        "Equipamento de TI": "Equipamento de TI",
        "Serviço não continuado": "Serviço não continuado",
        "Serviço sem dedicação exclusiva de mão de obra": "Serviço sem dedicação exclusiva de mão de obra",
        "Serviço com dedicação exclusiva de mão de obra": "Serviço com dedicação exclusiva de mão de obra"
    }
    opcoes_forma = {
        "Modalidades da Lei nº 14.133/21": "Modalidades da Lei nº 14.133/21",
        "Utilização à ARP - Órgão Participante": "Utilização à ARP - Órgão Participante",
        "Adesão à ARP de outro Órgão": "Adesão à ARP de outro Órgão",
        "Dispensa/Inexigibilidade": "Dispensa/Inexigibilidade"
    }
    contexto["objeto_opcoes"] = gerar_opcoes_marcadas(contexto.get("tipo_objeto"), opcoes_objeto)
    contexto["forma_contratacao_opcoes"] = gerar_opcoes_marcadas(contexto.get("forma_contratacao"), opcoes_forma)
    
    # Adiciona a lista de itens
    contexto["lista_itens"] = lista_itens
    
    # Mapeamento do item 6 (Dotação Orçamentária)
    contexto["programa"] = dados_formulario.get("programa", "")
    contexto["subacao"] = dados_formulario.get("subacao", "")
    contexto["elemento_despesa"] = dados_formulario.get("elemento_despesa", "")
    contexto["projeto_atividade"] = dados_formulario.get("projeto_atividade", "")
    contexto["etapa"] = dados_formulario.get("etapa", "")
    contexto["fonte"] = dados_formulario.get("fonte", "")

    # Mapeamento do item 9 (ARP)
    contexto["arp"] = dados_formulario.get("arp_seplag", "")
    
    # Mapeamento do item 11 (Data Pretendida)
    contexto["data_pretendida"] = dados_formulario.get("data_pretendida", "")

    # Mapeamento do item 13 (Fiscal)
    contexto["fiscal_nome"] = dados_formulario.get("fiscal_nome", "")
    contexto["fiscal_matricula"] = dados_formulario.get("fiscal_matricula", "")

    # Renderiza o documento com o contexto completo
    doc.render(contexto)
    
    output_dir = os.path.join(os.path.dirname(__file__), "static", "arquivos_gerados")
    os.makedirs(output_dir, exist_ok=True)
    
    item_para_nome = "documento"
    if lista_itens and len(lista_itens) > 0:
        item_para_nome = lista_itens[0].get("descricao", "documento")
    
    nome_sanitizado = sanitize_filename(item_para_nome)
    nome_arquivo_base = f"DFD_{nome_sanitizado}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if len(nome_arquivo_base) > 100:
        nome_arquivo_base = nome_arquivo_base[:100]
    
    nome_arquivo = os.path.join(output_dir, f"{nome_arquivo_base}.docx")
    doc.save(nome_arquivo)

    return nome_arquivo