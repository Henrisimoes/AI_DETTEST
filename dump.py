import streamlit as st
from gerar_dfd import gerar_dfd_completo
from datetime import datetime
from PIL import Image
import os
import locale
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import json

# ======== set locale e valores em PT BR ===========
locale.setlocale(locale.LC_ALL, 'C') 
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, '')

# ... (Todo o resto do seu código, do estilo ao primeiro formulário, permanece igual) ...
# ...
# ... (Vou pular para a seção do formulário final para focar na mudança)
# ...


# ====================================================================
# FORMULÁRIO 2: DETALHES GERAIS DO DFD E GERAÇÃO
# ====================================================================
with st.form("form_gerar_dfd"):
    st.subheader("3. Detalhes Gerais do DFD")

    # ... (Todos os seus campos de formulário como tipo_objeto, forma_contratacao, etc. continuam aqui)
    # ...
    st.session_state.tipo_objeto = st.selectbox(
        "Tipo de objeto (Tópico 1)",
        ["Material de consumo", "Material permanente", "Equipamento de TI", "Serviço não continuado", "Serviço sem dedicação exclusiva de mão de obra", "Serviço com dedicação exclusiva de mão de obra"],
        index=["Material de consumo", "Material permanente", "Equipamento de TI", "Serviço não continuado", "Serviço sem dedicação exclusiva de mão de obra", "Serviço com dedicação exclusiva de mão de obra"].index(st.session_state.tipo_objeto),
        key="tipo_objeto_final"
    )
    # (etc... todos os outros campos do formulário)
    # ...
    # ...
    st.session_state.fiscal_matricula = st.text_input(
        "Item 13: Matrícula do Responsável pela Fiscalização Contratual",
        value=st.session_state.fiscal_matricula,
        key="fiscal_matricula_input",
        help="Matrícula do servidor responsável pela fiscalização do contrato."
    )
    # --- FIM DOS CAMPOS ANTERIORES ---


    # <--- MUDANÇA: Adicionando os botões em colunas ---
    st.markdown("---") # Linha divisória para separar os botões

    col1, col2 = st.columns(2)

    with col1:
        gerar_dfd_button = st.form_submit_button(
            "📥 Gerar Documento DFD Completo",
            disabled=(not st.session_state.lista_de_itens_dfd or not st.session_state.finalidade_geral_dfd),
            type="primary",
            use_container_width=True
        )

    with col2:
        exportar_json_button = st.form_submit_button(
            "📄 Exportar Apenas Dados (JSON)",
            disabled=(not st.session_state.lista_de_itens_dfd or not st.session_state.finalidade_geral_dfd),
            type="secondary",
            use_container_width=True
        )
    # <--- FIM DA MUDANÇA ---


# <--- MUDANÇA: Lógica para o novo botão de exportar JSON ---
if exportar_json_button:
    if not st.session_state.lista_de_itens_dfd:
        st.error("❌ Para exportar, adicione ao menos um item ao DFD.")
        st.stop()
    if not st.session_state.finalidade_geral_dfd:
        st.error("❌ Para exportar, preencha a 'Finalidade GERAL da demanda'.")
        st.stop()
    
    # Monta o dicionário de dados gerais (mesma lógica do botão de gerar DFD)
    dados_gerais = {
        "finalidade": st.session_state.finalidade_geral_dfd,
        "tipo_objeto": st.session_state.tipo_objeto,
        "forma_contratacao": st.session_state.forma_contratacao,
        "orgao": "DEPARTAMENTO ESTADUAL DE TRÂNSITO DE MATO GROSSO – DETRAN-MT",
        "unidade_orcamentaria": "19301",
        "setor": "COORDENADORIA DE TECNOLOGIA DA INFORMAÇÃO",
        "responsavel": "DANILO VIEIRA DA CRUZ",
        "matricula": "246679",
        "telefone": "(65) 3615-4811",
        "email": "danilocruz@detran.mt.gov.br",
        'necessidade_etp': st.session_state.necessidade_etp,
        'justificativa_etp': st.session_state.justificativa_etp,
        'previsao_pca': st.session_state.previsao_pca,
        'justificativa_pca': st.session_state.justificativa_pca,
        "programa": st.session_state.programa,
        "subacao": st.session_state.subacao,
        "elemento_despesa": st.session_state.elemento_despesa,
        "projeto_atividade": st.session_state.projeto_atividade,
        "etapa": st.session_state.etapa,
        "fonte": st.session_state.fonte,
        "arp_seplag": st.session_state.arp_seplag,
        "data_pretendida": st.session_state.data_pretendida.strftime("%Y-%m-%d"), # Formato ISO para JSON
        "fiscal_nome": st.session_state.fiscal_nome,
        "fiscal_matricula": st.session_state.fiscal_matricula
    }

    # Combina os dados gerais e a lista de itens em um único objeto
    dados_completos_para_exportar = {
        "dados_gerais_dfd": dados_gerais,
        "lista_de_itens_dfd": st.session_state.lista_de_itens_dfd
    }

    # Converte o dicionário completo para uma string JSON formatada
    json_string = json.dumps(
        dados_completos_para_exportar, 
        indent=4, 
        ensure_ascii=False
    )

    # Cria o botão de download
    st.download_button(
        label="📥 Baixar Arquivo JSON",
        data=json_string,
        file_name=f"export_dfd_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

# ====== PROCESSAMENTO E GERAÇÃO DO DFD (Lógica antiga) ========
if gerar_dfd_button:
    # ... (toda a sua lógica existente para gerar o documento Word continua aqui, sem alterações)
    if not st.session_state.lista_de_itens_dfd: 
        st.error("❌ Por favor, adicione ao menos um item ao DFD antes de gerar o documento.")
        st.stop()
    # ... etc