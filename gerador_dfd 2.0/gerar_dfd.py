from docxtpl import DocxTemplate
from datetime import datetime
from gerar_ia import gerar_texto_ia
import locale

# Configura locale para português brasileiro para a data formatada
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')  # Pode variar conforme sistema operacional

def gerar_opcoes_marcadas(opcao_escolhida, opcoes_dict):
    linhas = []
    # Define largura fixa para alinhar "(X)" + label pela maior label
    max_label_len = max(len(label) for label in opcoes_dict)

    for label, chave in opcoes_dict.items():
        marcado = "(X)" if chave == opcao_escolhida else "( )"
        # Espaçamento: label alinhada à direita com padding para ficar visualmente organizado
        linha = f"{marcado} {label.ljust(max_label_len)}"
        linhas.append(linha)

    return "\n".join(linhas)


def gerar_dfd_completo(dados_formulario, lista_itens):
    doc = DocxTemplate("templates/modelo_dfd.docx")

    # Gera textos dinâmicos via IA para campos descritivos do formulário
    dados_formulario["descricao"] = gerar_texto_ia(dados_formulario, "descricao")
    dados_formulario["justificativa"] = gerar_texto_ia(dados_formulario, "justificativa")
    dados_formulario["objetivo"] = gerar_texto_ia(dados_formulario, "objetivo")
    dados_formulario["planejamento"] = gerar_texto_ia(dados_formulario, "planejamento")
    dados_formulario["equipe"] = gerar_texto_ia(dados_formulario, "equipe")

    # Gera respostas para campos SIM/NÃO com justificativa
    etp_resultado = gerar_texto_ia(dados_formulario, "estudo_tecnico")
    plano_resultado = gerar_texto_ia(dados_formulario, "plano_contratacao")

    # Marcações para estudo técnico preliminar
    if etp_resultado.strip().upper().startswith("SIM"):
        dados_formulario["estudo_tecnico"] = "(X) SIM\n( ) NÃO"
        dados_formulario["justificativa_etp"] = ""
    else:
        dados_formulario["estudo_tecnico"] = "( ) SIM\n(X) NÃO"
        dados_formulario["justificativa_etp"] = etp_resultado

    # Marcações para plano de contratação anual
    if plano_resultado.strip().upper().startswith("SIM"):
        dados_formulario["plano_contratacao"] = "(X) SIM\n( ) NÃO"
        dados_formulario["justificativa_pca"] = ""
    else:
        dados_formulario["plano_contratacao"] = "( ) SIM\n(X) NÃO"
        dados_formulario["justificativa_pca"] = plano_resultado

    # Mapas para opções marcadas em tópicos 1 e 3
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

    # Gera texto com opções marcadas para o documento
    dados_formulario["objeto_opcoes"] = gerar_opcoes_marcadas(dados_formulario["tipo_objeto"], opcoes_objeto)
    dados_formulario["forma_contratacao_opcoes"] = gerar_opcoes_marcadas(dados_formulario["forma_contratacao"], opcoes_forma)

    # Campos fixos SIM/NÃO para segurança (pode ajustar conforme necessidade)
    dados_formulario["estudo_tecnico"] = "(X) NÃO\n( ) SIM"
    dados_formulario["plano_contratacao"] = "(X) SIM\n( ) NÃO"

    # Formata data no padrão brasileiro, ex: "Cuiabá-MT, 04 de julho de 2025"
    dados_formulario["data"] = datetime.now().strftime("Cuiabá-MT, %d de %B de %Y")

    # Junta todos os dados e a lista de itens para o template
    dados = {
        **dados_formulario,
        "linha": lista_itens  # A lista de itens que será iterada no template docx
    }

    # Gera nome do arquivo com timestamp para evitar sobrescrever
    nome_arquivo = f"static/arquivos_gerados/DFD_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    doc.render(dados)
    doc.save(nome_arquivo)
    return nome_arquivo
