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
    Remove ou substitui caracteres inválidos em nomes de arquivo.
    Mantém letras, números, espaços, hífens e underscores.
    Espaços múltiplos são convertidos em um único underscore.
    """
    filename = filename.replace(' ', '_')
    filename = re.sub(r'[\\/:*?"<>|,;()–]', '', filename)
    filename = re.sub(r'_+', '_', filename)
    filename = filename.strip('_')
    if len(filename) > 150:
        filename = filename[:150]
    return filename

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

    # --- ALTERAÇÃO AQUI: ADICIONANDO VALIDAÇÃO PARA OS CAMPOS DA IA ---
    # Se a IA não gerar conteúdo, um texto padrão será inserido.
    descricao_ia = gerar_texto_ia(dados_formulario, "descricao")
    dados_formulario["descricao"] = descricao_ia if descricao_ia else "Texto não gerado pela IA. Por favor, revise a 'Finalidade GERAL da demanda' para obter um resultado mais completo."
    
    justificativa_ia = gerar_texto_ia(dados_formulario, "justificativa")
    dados_formulario["justificativa"] = justificativa_ia if justificativa_ia else "Texto não gerado pela IA. Por favor, revise a 'Finalidade GERAL da demanda' para obter um resultado mais completo."
    # --- FIM DA ALTERAÇÃO ---

    dados_formulario["objetivo"] = gerar_texto_ia(dados_formulario, "objetivo")
    dados_formulario["planejamento"] = gerar_texto_ia(dados_formulario, "planejamento")
    dados_formulario["equipe"] = gerar_texto_ia(dados_formulario, "equipe") 

    etp_resultado = gerar_texto_ia(dados_formulario, "estudo_tecnico")
    plano_resultado = gerar_texto_ia(dados_formulario, "plano_contratacao")

    if etp_resultado and etp_resultado.strip().upper().startswith("SIM"):
        dados_formulario["estudo_tecnico_marcado"] = "(X) SIM\n( ) NÃO"
        dados_formulario["justificativa_etp"] = ""
    else:
        dados_formulario["estudo_tecnico_marcado"] = "( ) SIM\n(X) NÃO"
        dados_formulario["justificativa_etp"] = etp_resultado

    if plano_resultado and plano_resultado.strip().upper().startswith("SIM"):
        dados_formulario["plano_contratacao_marcado"] = "(X) SIM\n( ) NÃO"
        dados_formulario["justificativa_pca"] = ""
    else:
        dados_formulario["plano_contratacao_marcado"] = "( ) SIM\n(X) NÃO"
        dados_formulario["justificativa_pca"] = plano_resultado

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

    dados_formulario["objeto_opcoes"] = gerar_opcoes_marcadas(dados_formulario["tipo_objeto"], opcoes_objeto)
    dados_formulario["forma_contratacao_opcoes"] = gerar_opcoes_marcadas(dados_formulario["forma_contratacao"], opcoes_forma)

    dados_formulario["estudo_tecnico_fixo"] = "(X) NÃO\n( ) SIM" # Este parece ser um campo fixo, se for para mudar, precisamos de mais informações.
    dados_formulario["plano_contratacao_fixo"] = "(X) SIM\n( ) NÃO" # Este também parece fixo.

    dados_formulario["data"] = datetime.now().strftime("Cuiabá-MT, %d de %B de %Y")
    
    # --- NOVOS DADOS PARA O TEMPLATE ---
    dados_formulario["arp"] = dados_formulario.get("arp_seplag", "Não informado ou Não se aplica.")
    dados_formulario["data_pretendida"] = dados_formulario.get("data_pretendida", "Não informada.")
    dados_formulario["fiscal_nome"] = dados_formulario.get("fiscal_nome", "Não informado.")
    dados_formulario["fiscal_matricula"] = dados_formulario.get("fiscal_matricula", "Não informada.")

    # Dados do Item 6
    dados_formulario["programa"] = dados_formulario.get("programa", "")
    dados_formulario["subacao"] = dados_formulario.get("subacao", "")
    dados_formulario["elemento_despesa"] = dados_formulario.get("elemento_despesa", "")
    dados_formulario["projeto_atividade"] = dados_formulario.get("projeto_atividade", "")
    dados_formulario["etapa"] = dados_formulario.get("etapa", "")
    dados_formulario["fonte"] = dados_formulario.get("fonte", "")
    # --- FIM DOS NOVOS DADOS ---


    dados_para_template = {
        **dados_formulario,
        "lista_itens": lista_itens
    }

    output_dir = "static/arquivos_gerados"
    os.makedirs(output_dir, exist_ok=True)

    item_para_nome = "documento"
    if lista_itens and len(lista_itens) > 0:
        item_para_nome = lista_itens[0].get("descricao", "documento")

    nome_sanitizado = sanitize_filename(item_para_nome)

    nome_arquivo_base = f"DFD_{nome_sanitizado}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    nome_arquivo = os.path.join(output_dir, f"{nome_arquivo_base}.docx")

    doc.render(dados_para_template)
    doc.save(nome_arquivo)

    return nome_arquivo