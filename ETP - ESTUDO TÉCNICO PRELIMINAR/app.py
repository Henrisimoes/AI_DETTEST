# app.py
import streamlit as st
from gerar_etp import gerar_etp_completo
from datetime import datetime
import os
from docx import Document
import pandas as pd
import io
import time
from pathlib import Path

# ========= ESTILO VISUAL (com a adição da classe para texto branco) =========
st.set_page_config(layout="wide", page_title="Gerador de ETP - DETRAN-MT")

st.markdown("""
    <style>
        /* Estilo para a cor de fundo do aplicativo */
        .stApp {
            background-color: #0a2540 !important;
        }
        /* Estilos para forçar o fundo azul nos principais controle pccontêineres do Streamlit */
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewBlockContainer"],
        .main,
        section.main {
            background-color: #0a2540 !important;
        }

        .title-container {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 10px 10px 20px 10px;
        }
        .title-text {
            color: white;
            font-size: 28px;
            font-weight: bold;
        }
        
        /* Classe para texto branco */
        .white-text {
            color: white !important;
        }

        div[data-testid="stForm"] {
            background-color: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 0 10px rgba(0,0,0,0);
            margin-bottom: 20px;
        }
        
        .caixa-branca {
            background-color: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 0 10px rgba(0,0,0,0);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)


# ========= TÍTULO COM LOGO E MENSAGEM DE BOAS-VINDAS (AGORA COM COR BRANCA) =========
st.markdown("<h1 class='white-text'>Bem-vindo(a) ao Gerador de Documentos DETRAN-MT</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='white-text'>Insira os dados para a geração do seu ETP (Estudo Técnico Preliminar)</h3>", unsafe_allow_html=True)
st.markdown("---")


# ====================================================================
# --- FUNÇÃO PARA LER O DOCUMENTO DFD E EXTRAIR A TABELA (CORRIGIDA) ---
# ====================================================================

def extract_items_from_dfd(doc_file_content):
    try:
        doc = Document(io.BytesIO(doc_file_content))
        
        for table in doc.tables:
            header_row_index = -1
            
            # Encontra o índice da linha de cabeçalho
            for i, row in enumerate(table.rows):
                row_text = " ".join([cell.text.strip().upper() for cell in row.cells])
                if "SIAGO/TCE" in row_text and "UN." in row_text and "QTDE" in row_text and "ESPECIFICAÇÃO DO PRODUTO" in row_text:
                    header_row_index = i
                    break
            
            if header_row_index != -1:
                header_row = table.rows[header_row_index]
                header_texts = [cell.text.strip().upper() for cell in header_row.cells]
                
                catmat_idx = -1
                desc_idx = -1
                un_idx = -1
                qtd_idx = -1
                
                for i, text in enumerate(header_texts):
                    if "SIAGO/TCE" in text:
                        catmat_idx = i
                    elif "ESPECIFICAÇÃO" in text or "PRODUTO" in text:
                        desc_idx = i
                    elif "UN." in text:
                        un_idx = i
                    elif "QTDE" in text:
                        qtd_idx = i

                if desc_idx != -1 and un_idx != -1 and qtd_idx != -1:
                    items_list = []
                    
                    # Itera sobre as linhas de dados a partir da linha seguinte ao cabeçalho
                    for row in table.rows[header_row_index + 1:]:
                        cells = row.cells
                        if len(cells) > max(catmat_idx, desc_idx, un_idx, qtd_idx):
                            item_data = {
                                "catmat": cells[catmat_idx].text.strip() if catmat_idx != -1 else "",
                                "descricao": cells[desc_idx].text.strip(),
                                "unidade": cells[un_idx].text.strip(),
                                "qtd": cells[qtd_idx].text.strip(),
                                "valor_unitario": ""
                            }
                            # Adiciona o item somente se a descrição não estiver vazia
                            if item_data["descricao"].strip():
                                items_list.append(item_data)
                    return items_list
        return []
    except Exception as e:
        # Se houver um erro, exibe a mensagem detalhada e retorna None para tratamento na interface
        st.error(f"❌ Erro ao ler o documento: '{e}'")
        return None


# ====================================================================
# --- ESTADO DA SESSÃO PARA PERSISTÊNCIA DE DADOS ---
# ====================================================================
if 'lista_de_itens_etp' not in st.session_state:
    st.session_state.lista_de_itens_etp = []
if 'item_etp_descricao' not in st.session_state:
    st.session_state.item_etp_descricao = ""
if 'item_etp_catmat' not in st.session_state:
    st.session_state.item_etp_catmat = ""
if 'item_etp_unidade' not in st.session_state:
    st.session_state.item_etp_unidade = "UN"
if 'item_etp_quantidade' not in st.session_state:
    st.session_state.item_etp_quantidade = ""
if 'item_etp_valor_unitario' not in st.session_state:
    st.session_state.item_etp_valor_unitario = ""

# ========= INTERFACE DE SELEÇÃO DE ARQUIVOS DFD ---------
st.markdown("---")
# Usando st.markdown para os títulos com a classe white-text
st.markdown("<h3 class='white-text'>Importar Itens do DFD</h3>", unsafe_allow_html=True)
st.markdown("<p class='white-text'>Selecione um documento DFD (.docx) para importar a lista de itens.</p>", unsafe_allow_html=True)

# Define o caminho para a pasta de arquivos do DFD
DFD_FOLDER = Path(r"C:\Users\pedrosilva\Desktop\PROJETO IA DETRAN\DFD - DOCUMENTO DE FORMALIZAÇÃO DE DEMANDA\static\arquivos_gerados")
DFD_FILE_LIST = [f.name for f in DFD_FOLDER.glob("*.docx")] if DFD_FOLDER.exists() else []

if DFD_FILE_LIST:
    selected_file = st.selectbox(
        "Selecione um arquivo DFD:", 
        DFD_FILE_LIST,
        index=0,
        key="selected_dfd_file"
    )

    if st.button("✅ Carregar itens do DFD"):
        file_path = DFD_FOLDER / selected_file
        try:
            with open(file_path, "rb") as f:
                imported_items = extract_items_from_dfd(f.read())
            
            if imported_items:
                st.session_state.lista_de_itens_etp = imported_items
                st.success(f"✅ {len(imported_items)} itens importados com sucesso do DFD!")
                st.rerun()
            else:
                st.warning("Não foi possível encontrar a tabela de itens no documento DFD selecionado.")
        except Exception as e:
            st.error(f"❌ Erro ao ler o arquivo: {e}")
            
else:
    st.warning("Nenhum arquivo DFD (.docx) encontrado na pasta de origem.")


# ========= FORMULÁRIO PRINCIPAL PARA O ETP ---------
with st.form("form_etp", clear_on_submit=False):
    st.subheader("1. Informações Gerais do ETP")
    col1, col2 = st.columns(2)
    with col1:
        etp_numero = st.text_input("Número do ETP", value="003/2025")
        area_requisitante = st.text_input("Área Requisitante", value="COORDENADORIA DE TECNOLOGIA DA INFORMAÇÃO")
    with col2:
        responsavel = st.text_input("Responsável pela Área", value="Danilo Vieira da Cruz")
        
    st.subheader("2. Finalidade Geral e Justificativas")
    finalidade_geral = st.text_area(
        "Finalidade GERAL da Contratação (Base para a IA)", 
        help="Descreva o problema a ser resolvido e a necessidade de forma clara.",
        value="Aquisição de materiais de consumo (itens de informática) para atender às demandas do Departamento Estadual de Trânsito de Mato Grosso."
    )
    
    st.subheader("3. Detalhes de Planejamento e Orçamento")
    col3, col4, col5, col6 = st.columns(4)
    with col3:
        subacao = st.text_input("Sub ação", value="xx")
    with col4:
        etapa = st.text_input("Etapa", value="xx")
    with col5:
        natureza_despesa = st.text_input("Natureza da Despesa", value="xxxx-xxxx")
    with col6:
        fonte = st.text_input("Fonte", value="xxx")

    st.subheader("4. Requisitos e Itens da Contratação")
    requisitos_tecnicos = st.text_area(
        "Requisitos Técnicos da Solução",
        help="Descreva os requisitos técnicos e de sustentabilidade necessários. A IA irá refinar este texto."
    )

    # Lógica para adicionar itens à tabela (agora com verificação)
    st.markdown("---")
    st.markdown("##### Adicionar Item à Tabela")
    
    if st.session_state.lista_de_itens_etp:
        st.info("Itens importados do DFD. Para adicionar manualmente, reinicie o aplicativo ou limpe a lista.")
    else:
        col_item1, col_item2, col_item3, col_item4, col_item5 = st.columns([1, 2, 1, 1, 1])
        with col_item1:
            item_etp_catmat = st.text_input("SIAG/TCE", value=st.session_state.item_etp_catmat)
        with col_item2:
            item_etp_descricao = st.text_input("Descrição do Item", value=st.session_state.item_etp_descricao)
        with col_item3:
            item_etp_unidade = st.text_input("UN", value=st.session_state.item_etp_unidade)
        with col_item4:
            item_etp_quantidade = st.text_input("QTD", value=st.session_state.item_etp_quantidade)
        with col_item5:
            item_etp_valor_unitario = st.text_input("V. Unitário", value=st.session_state.item_etp_valor_unitario)
        
        adicionar_item_button = st.form_submit_button("➕ Adicionar Item")
        if adicionar_item_button and item_etp_descricao:
            st.session_state.lista_de_itens_etp.append({
                "catmat": item_etp_catmat,
                "descricao": item_etp_descricao,
                "unidade": item_etp_unidade,
                "qtd": item_etp_quantidade,
                "valor_unitario": item_etp_valor_unitario
            })
            st.session_state.item_etp_catmat = ""
            st.session_state.item_etp_descricao = ""
            st.session_state.item_etp_unidade = "UN"
            st.session_state.item_etp_quantidade = ""
            st.session_state.item_etp_valor_unitario = ""
            st.rerun()

    if st.session_state.lista_de_itens_etp:
        st.dataframe(st.session_state.lista_de_itens_etp, use_container_width=True)

    st.subheader("5. Levantamento de Mercado e Solução")
    solucoes_alternativas = st.text_area(
        "Soluções Alternativas (lista separada por vírgula)",
        help="Ex: 'Contrato de manutenção, aquisição via ata de registro de preços, compra direta'. A IA irá usar isso para a análise."
    )
    solucao_escolhida = st.text_input(
        "Solução Escolhida",
        help="Descreva a solução que foi selecionada para a contratação."
    )

    st.subheader("6. Justificativas e Outras Informações")
    descricao_solucao = st.text_area("Descrição da Solução como um todo")
    justificativa_parcelamento = st.text_area("Justificativa para o parcelamento")
    providencias = st.text_area("Providências a serem adotadas pela Administração")
    correlatas = st.text_area("Contratações correlatas e/ou interdependentes")
    impactos_ambientais = st.text_area("Descrição de possíveis impactos ambientais")
    
    st.subheader("7. Conclusão e Responsabilidade")
    viabilidade = st.radio(
        "Posicionamento Conclusivo",
        ('É VIÁVEL a presente contratação.', 'NÃO É VIÁVEL a presente contratação.'),
        index=0
    )
    elaborador_nome = st.text_input("Elaborado por (Nome)", value="XXXXXXXXX")
    elaborador_matricula = st.text_input("Matrícula do Elaborador", value="XXXXXX")
    data_final = st.date_input("Data de Término", value=datetime.now().date())
    
    gerar_etp_button = st.form_submit_button("📥 Gerar ETP Completo", type="primary")


# ====== PROCESSAMENTO E GERAÇÃO DO ETP (COM DIAGNÓSTICO) ========
if gerar_etp_button:
    dados_gerais = {
        'etp_numero': etp_numero,
        'area_requisitante': area_requisitante,
        'responsavel': responsavel,
        'finalidade_geral': finalidade_geral,
        'subacao': subacao,
        'etapa': etapa,
        'elemento_despesa': natureza_despesa,
        'fonte': fonte,
        'requisitos_tecnicos': requisitos_tecnicos,
        'solucoes_alternativas': solucoes_alternativas,
        'solucao_escolhida': solucao_escolhida,
        'descricao_solucao': descricao_solucao,
        'justificativa_parcelamento': justificativa_parcelamento,
        'providencias': providencias,
        'correlatas': correlatas,
        'impactos_ambientais': impactos_ambientais,
        'viabilidade': viabilidade,
        'elaborador_nome': elaborador_nome,
        'elaborador_matricula': elaborador_matricula,
        'data_final': data_final.strftime("%d de %B de %Y")
    }

    if not st.session_state.lista_de_itens_etp:
        st.error("❌ Por favor, adicione ao menos um item à tabela do ETP.")
        st.stop()
        
    with st.spinner("Gerando documento com apoio da IA..."):
        try:
            # Tenta gerar o ETP
            caminho_arquivo = gerar_etp_completo(dados_gerais, st.session_state.lista_de_itens_etp)
            
            # Adicionei esta verificação para confirmar que o arquivo existe
            if caminho_arquivo and os.path.exists(caminho_arquivo):
                st.success("✅ Documento gerado com sucesso!")
                with open(caminho_arquivo, "rb") as f:
                    st.download_button(
                        "📥 Baixar ETP Gerado",
                        f,
                        file_name=os.path.basename(caminho_arquivo),
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            else:
                st.error("❌ O arquivo não foi gerado ou o caminho retornado é inválido.")
                if not caminho_arquivo:
                    st.write("O caminho do arquivo retornado por 'gerar_etp_completo' é nulo ou vazio.")
                else:
                    st.write(f"O caminho do arquivo retornado é: '{caminho_arquivo}'")

        except Exception as e:
            st.error(f"❌ Erro ao gerar o documento ETP. Detalhes: {e}")
            st.exception(e)