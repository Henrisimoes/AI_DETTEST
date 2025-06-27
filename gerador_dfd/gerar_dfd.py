# gerar_dfd.py
from docxtpl import DocxTemplate
from datetime import datetime
from gerar_ia import gerar_texto_ia

def gerar_opcoes_marcadas(opcao_escolhida, opcoes_dict):
    linhas = []
    for label, chave in opcoes_dict.items():
        marcado = "(X)" if chave == opcao_escolhida else "( )"
        linhas.append(f"{marcado} {label}")
    return "\n".join(linhas)

def gerar_dfd_completo(dados_formulario, lista_itens):
    doc = DocxTemplate("templates/modelo_dfd.docx")

    # IA para os campos descritivos
    dados_formulario["descricao"] = gerar_texto_ia(dados_formulario, "descricao")
    dados_formulario["justificativa"] = gerar_texto_ia(dados_formulario, "justificativa")
    dados_formulario["objetivo"] = gerar_texto_ia(dados_formulario, "objetivo")
    dados_formulario["planejamento"] = gerar_texto_ia(dados_formulario, "planejamento")
    dados_formulario["equipe"] = gerar_texto_ia(dados_formulario, "equipe")

    # Marcações dinâmicas nos tópicos 1 e 3
    opcoes_objeto = {
        "Material de consumo": "consumo",
        "Material permanente": "permanente",
        "Equipamento de TI": "ti",
        "Serviço não continuado": "servico_nao",
        "Serviço sem dedicação exclusiva de mão de obra": "servico_sem_exclusiva",
        "Serviço com dedicação exclusiva de mão de obra": "servico_com_exclusiva"
    }

    opcoes_forma = {
        "Modalidades da Lei nº 14.133/21": "lei14133",
        "Utilização à ARP - Órgão Participante": "arp",
        "Adesão à ARP de outro Órgão": "adesao",
        "Dispensa/Inexigibilidade": "dispensa"
    }

    dados_formulario["objeto_opcoes"] = gerar_opcoes_marcadas(dados_formulario["tipo_objeto"], opcoes_objeto)
    dados_formulario["forma_contratacao_opcoes"] = gerar_opcoes_marcadas(dados_formulario["forma_contratacao"], opcoes_forma)

    # Campos fixos de sim/não
    dados_formulario["estudo_tecnico"] = "(X) NÃO\n( ) SIM"
    dados_formulario["plano_contratacao"] = "(X) SIM\n( ) NÃO"

    # Data formatada
    dados_formulario["data"] = datetime.now().strftime("Cuiabá-MT, %d de %B de %Y")

    dados = {
        **dados_formulario,
        "linha": lista_itens
    }

    nome_arquivo = f"static/arquivos_gerados/DFD_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    doc.render(dados)
    doc.save(nome_arquivo)
    return nome_arquivo
