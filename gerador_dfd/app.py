import streamlit as st
from gerar_dfd import gerar_dfd_completo
from datetime import datetime

# ========== ESTILO VISUAL ==========
st.markdown("""
    <style>
        body {
            background-color: #0a2540;
        }
        .stApp {
            background-color: #0a2540;
        }
        .title {
            color: white;
            font-size: 28px;
            font-weight: bold;
            padding: 20px 10px 10px 10px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .title img {
            height: 55px;
        }
        .st-emotion-cache-1r4qj8v {
            padding: 0rem 2rem;
        }
    </style>
    <div class="title">
        <img src="gerador_dfd\static\logo_detran.png" alt="logo">
        <span>Gerador de Documento de Formalização da Demanda - DETRAN-MT</span>
    </div>
""", unsafe_allow_html=True)

# ========== FORMULÁRIO ==========
with st.form("dfd_form"):
    item = st.text_input("Item")
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

        dados = {
            "item": item,
            "quantidade": quantidade,
            "finalidade": finalidade,
            "tipo_objeto": map_tipo[tipo_objeto],
            "forma_contratacao": map_forma[forma_contratacao],

            # Campos fixos institucionais
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
                "catmat": "39375273",
                "unidade": "UN",
                "qtd": quantidade,
                "descricao": item.upper(),
                "marca": "GENÉRICA"
            }
        ]

        caminho_arquivo = gerar_dfd_completo(dados, lista_itens)

    # Download
    with open(caminho_arquivo, "rb") as f:
        st.success("✅ Documento gerado com sucesso!")
        st.download_button("📥 Baixar Documento", f, file_name=caminho_arquivo.split("/")[-1])
