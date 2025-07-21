# app.py
import streamlit as st
from gerar_dfd import gerar_dfd_completo
from datetime import datetime
from PIL import Image
import os
import locale
from conexao_mysql import listar_nomes_produtos, buscar_produto_por_nome

# ======== set locale e valores em PT BR ===========
locale.setlocale(locale.LC_ALL, 'C')
locale.setlocale(locale.LC_TIME, '')        # datetime.now().strftime("Cuiabá-MT, %d de %B de %Y") = 'Cuiabá-MT, 04 de julho de 2025'
locale.setlocale(locale.LC_CTYPE, '')       # Caracteres especiais
locale.setlocale(locale.LC_MONETARY, '')    # locale.currency(1200, grouping=True) = 'R$ 1.200,00'

# ========== ESTILO VISUAL ==========
st.markdown("""
    <style>
        body, .stApp {
            background-color: #0a2540;
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

        /* Fundo branco para o formulário */
        div[data-testid="stForm"] {
            background-color: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 0 10px rgba(0,0,0,0);
        }

        /* Inputs */
        input, textarea, select {
            background-color: white !important;
            color: black !important;
            border: 1px solid #ccc !important;
        }

        /* Corrigir padding geral */
        .st-emotion-cache-1r4qj8v {
            padding: 0rem 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# ========== TÍTULO COM LOGO ==========
logo_path = os.path.join("static", "logo_detran.png")
logo = Image.open(logo_path)

st.markdown('<div class="title-container">', unsafe_allow_html=True)
st.image(logo, width=60)
st.markdown('<div class="title-text">Gerador de Documento de Formalização da Demanda - DETRAN-MT</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ========== FORMULÁRIO ==========
with st.form("dfd_form"):
    opcoes_itens = listar_nomes_produtos()
    item = st.selectbox("Selecione o item", opcoes_itens)
    quantidade = st.text_input("Quantidade")
    finalidade = st.text_area("Finalidade do item")

    tipo_objeto = st.selectbox("Tipo de objeto (Tópico 1)", [
        "Material de consumo",
        "Material permanente",
        "Equipamento de TI",
        "Serviço não continuado",
        "Serviço sem dedicação exclusiva de mão de obra",
        "Serviço com dedicação exclusiva de mão de obra"
    ])

    forma_contratacao = st.selectbox("Forma de contratação sugerida (Tópico 3)", [
        "Modalidades da Lei nº 14.133/21",
        "Utilização à ARP - Órgão Participante",
        "Adesão à ARP de outro Órgão",
        "Dispensa/Inexigibilidade"
    ])

    gerar = st.form_submit_button("📥 Gerar Documento DFD")

# ========== PROCESSAMENTO ==========
if gerar:
    with st.spinner("Gerando documento com apoio da IA..."):
        produto = buscar_produto_por_nome(item)
        if not produto:
            st.error("❌ Produto não encontrado no banco de dados.")
            st.stop()

        map_tipo = {
            "Material de consumo": "consumo",
            "Material permanente": "permanente",
            "Equipamento de TI": "ti",
            "Serviço não continuado": "servico_nao",
            "Serviço sem dedicação exclusiva de mão de obra": "servico_sem_exclusiva",
            "Serviço com dedicação exclusiva de mão de obra": "servico_com_exclusiva"
        }

        map_forma = {
            "Modalidades da Lei nº 14.133/21": "lei14133",
            "Utilização à ARP - Órgão Participante": "arp",
            "Adesão à ARP de outro Órgão": "adesao",
            "Dispensa/Inexigibilidade": "dispensa"
        }

        # Pergunta ao usuário a unidade manualmente
        unidade_selecionada = st.selectbox(
            "Selecione a unidade do produto",
            ["UN", "KG", "L", "CX", "OUTRO"]
        )

        dados = {
            "item": item,
            "quantidade": quantidade,
            "finalidade": finalidade,
            "tipo_objeto": map_tipo[tipo_objeto],
            "forma_contratacao": map_forma[forma_contratacao],
            "orgao": "DEPARTAMENTO ESTADUAL DE TRÂNSITO DE MATO GROSSO – DETRAN-MT",
            "unidade_orcamentaria": "19301",
            "setor": "COORDENADORIA DE TECNOLOGIA DA INFORMAÇÃO",
            "responsavel": "DANILO VIEIRA DA CRUZ",
            "matricula": "246679",
            "telefone": "(65) 3615-4811",
            "email": "danilocruz@detran.mt.gov.br"
        }

        lista_itens = [
    {
        "item": "001",
        "catmat": produto["codigo"],
        "unidade": "un",  # valor padrão, pois não existe na tabela
        "qtd": quantidade,
        "descricao": produto["descricao"].upper()
    }
]

        caminho_arquivo = gerar_dfd_completo(dados, lista_itens)

    with open(caminho_arquivo, "rb") as f:
        st.success("✅ Documento gerado com sucesso!")
        st.download_button("📥 Baixar Documento", f, file_name=os.path.basename(caminho_arquivo))
