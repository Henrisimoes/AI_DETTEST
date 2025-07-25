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
from selenium.webdriver.chrome.options import Options # Importar Options
from bs4 import BeautifulSoup
import time

# ======== set locale e valores em PT BR ===========
locale.setlocale(locale.LC_ALL, 'C')
locale.setlocale(locale.LC_TIME, '')        # datetime.now().strftime("Cuiabá-MT, %d de %B de %Y") = 'Cuiabá-MT, 04 de julho de 2025'
locale.setlocale(locale.LC_CTYPE, '')      # Caracteres especiais
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

        div[data-testid="stForm"] {
            background-color: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 0 10px rgba(0,0,0,0);
        }

        input, textarea, select {
            background-color: white !important;
            color: black !important;
            border: 1px solid #ccc !important;
        }

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

# ====== Função de busca no SIAG ==========
def buscar_siag_selenium(termo_pesquisa):
    url = "http://aquisicoes.gestao.mt.gov.br/sgc/faces/pub/sgc/central/ItemCompraPageList.jsp"
    
    # --- ALTERAÇÃO AQUI: CONFIGURAR O CHROME PARA MODO HEADLESS ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executa o navegador em modo invisível
    chrome_options.add_argument("--no-sandbox") # Necessário para alguns ambientes Linux
    chrome_options.add_argument("--disable-dev-shm-usage") # Previne problemas com memória em alguns ambientes
    # --- FIM DA ALTERAÇÃO ---

    driver = webdriver.Chrome(options=chrome_options) # Passa as opções para o driver
    driver.get(url)

    wait = WebDriverWait(driver, 30)
    html = None

    try:
        # Esperando que a opção "Qualquer parte descrição" seja clicável
        opcao_radio = wait.until(EC.element_to_be_clickable(
            (By.ID, "form_PesquisaItemPageList:procurarPorCombo:2")))
        opcao_radio.click()

        # Esperando o campo de pesquisa estar presente
        campo_busca = wait.until(EC.presence_of_element_located(
            (By.ID, "form_PesquisaItemPageList:palavraChaveInput")))

        campo_busca.clear()
        campo_busca.send_keys(termo_pesquisa)

        # Esperando o botão de pesquisa ser clicável
        botao_pesquisar = wait.until(EC.element_to_be_clickable(
            (By.ID, "form_PesquisaItemPageList:pesquisarButton")))

        botao_pesquisar.click()

        time.sleep(5) # Pausa para aguardar o carregamento da página
        html = driver.page_source

    finally:
        driver.quit()

    if html is None:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    tabela = soup.find('table', {'id': 'form_PesquisaItemPageList:editalDataTable'})

    if not tabela:
        return []

    linhas = tabela.find_all('tr')[1:]
    resultados = []

    for linha in linhas:
        colunas = linha.find_all('td')
        if len(colunas) >= 2:
            codigo = colunas[0].get_text(strip=True)
            descricao = colunas[1].get_text(strip=True)
            if codigo:
                resultados.append({'codigo': codigo, 'descricao': descricao})

    return resultados

# ====== FORMULÁRIO ==========

# Inicializar st.session_state para persistir os dados
if 'opcoes_itens' not in st.session_state:
    st.session_state.opcoes_itens = []
if 'item_selecionado' not in st.session_state:
    st.session_state.item_selecionado = None
if 'quantidade' not in st.session_state:
    st.session_state.quantidade = ""
if 'finalidade' not in st.session_state:
    st.session_state.finalidade = ""
if 'tipo_objeto' not in st.session_state:
    st.session_state.tipo_objeto = "Material de consumo"
if 'forma_contratacao' not in st.session_state:
    st.session_state.forma_contratacao = "Modalidades da Lei nº 14.133/21"
if 'produto_buscado' not in st.session_state:
    st.session_state.produto_buscado = None
if 'termo_pesquisa' not in st.session_state:
    st.session_state.termo_pesquisa = ""
if 'unidade_selecionada' not in st.session_state:
    st.session_state.unidade_selecionada = "UN" # Novo: Inicializa a unidade


with st.form("dfd_form"):
    termo_pesquisa = st.text_input("Digite o nome do produto", value=st.session_state.termo_pesquisa, key="termo_pesquisa_input")

    buscar = st.form_submit_button("🔍 Buscar Produto no SIAG")

    if buscar:
        st.session_state.opcoes_itens = buscar_siag_selenium(termo_pesquisa)
        st.session_state.termo_pesquisa = termo_pesquisa

        if not st.session_state.opcoes_itens:
            st.error("❌ Nenhum produto encontrado no SIAG.")
            st.session_state.item_selecionado = None
            st.session_state.produto_buscado = None # Garante que o produto buscado também seja resetado
            st.stop()
        else:
            nomes_produtos = [item['descricao'] for item in st.session_state.opcoes_itens]
            # Se o item_selecionado anterior não estiver mais na lista, define o primeiro como padrão
            if st.session_state.item_selecionado not in nomes_produtos:
                st.session_state.item_selecionado = nomes_produtos[0] if nomes_produtos else None
            # Atualiza o produto_buscado completo
            st.session_state.produto_buscado = next((item for item in st.session_state.opcoes_itens if item['descricao'] == st.session_state.item_selecionado), None)


    if st.session_state.opcoes_itens:
        nomes_produtos_disp = [item['descricao'] for item in st.session_state.opcoes_itens]
        try:
            current_index = nomes_produtos_disp.index(st.session_state.item_selecionado)
        except ValueError:
            current_index = 0 # Se o item selecionado não estiver na lista (ex: após nova busca), define o primeiro
        
        st.session_state.item_selecionado = st.selectbox(
            "Selecione o item",
            nomes_produtos_disp,
            index=current_index,
            key="item_selecionado_selectbox" # Adiciona uma chave única para o selectbox
        )
        # Garante que produto_buscado esteja atualizado com a seleção atual
        st.session_state.produto_buscado = next((item for item in st.session_state.opcoes_itens if item['descricao'] == st.session_state.item_selecionado), None)
    else:
        st.selectbox("Selecione o item", [], disabled=True, help="Primeiro, busque um produto no SIAG.", key="item_selecionado_selectbox_disabled")
        st.session_state.item_selecionado = None
        st.session_state.produto_buscado = None


    st.session_state.quantidade = st.text_input("Quantidade", value=st.session_state.quantidade, key="quantidade_input")
    st.session_state.finalidade = st.text_area("Finalidade do item", value=st.session_state.finalidade, key="finalidade_input")

    # Novo: Selectbox para a unidade
    st.session_state.unidade_selecionada = st.selectbox(
        "Selecione a unidade do produto",
        ["UN", "KG", "L", "CX", "OUTRO"],
        index=["UN", "KG", "L", "CX", "OUTRO"].index(st.session_state.unidade_selecionada),
        key="unidade_selectbox" # Chave única
    )

    st.session_state.tipo_objeto = st.selectbox(
        "Tipo de objeto (Tópico 1)",
        [
            "Material de consumo",
            "Material permanente",
            "Equipamento de TI",
            "Serviço não continuado",
            "Serviço sem dedicação exclusiva de mão de obra",
            "Serviço com dedicação exclusiva de mão de obra"
        ],
        index=[
            "Material de consumo",
            "Material permanente",
            "Equipamento de TI",
            "Serviço não continuado",
            "Serviço sem dedicação exclusiva de mão de obra",
            "Serviço com dedicação exclusiva de mão de obra"
        ].index(st.session_state.tipo_objeto),
        key="tipo_objeto_selectbox"
    )

    st.session_state.forma_contratacao = st.selectbox(
        "Forma de contratação sugerida (Tópico 3)",
        [
            "Modalidades da Lei nº 14.133/21",
            "Utilização à ARP - Órgão Participante",
            "Adesão à ARP de outro Órgão",
            "Dispensa/Inexigibilidade"
        ],
        index=[
            "Modalidades da Lei nº 14.133/21",
            "Utilização à ARP - Órgão Participante",
            "Adesão à ARP de outro Órgão",
            "Dispensa/Inexigibilidade"
        ].index(st.session_state.forma_contratacao),
        key="forma_contratacao_selectbox"
    )

    gerar = st.form_submit_button("📥 Gerar Documento DFD")

# ====== PROCESSAMENTO ========
if gerar:
    if not st.session_state.item_selecionado or not st.session_state.produto_buscado:
        st.error("❌ Por favor, selecione um item primeiro, buscando-o no SIAG.")
        st.stop()

    with st.spinner("Gerando documento com apoio da IA..."):
        produto = st.session_state.produto_buscado

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

        # A unidade_selecionada agora vem diretamente do st.session_state
        unidade_para_dfd = st.session_state.unidade_selecionada

        dados = {
            "item": st.session_state.item_selecionado, # Nome do item selecionado (descrição)
            "quantidade": st.session_state.quantidade,
            "finalidade": st.session_state.finalidade,
            "tipo_objeto": map_tipo[st.session_state.tipo_objeto],
            "forma_contratacao": map_forma[st.session_state.forma_contratacao],
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
                "item": "001", # Este 'item' é um contador para a linha da tabela no DFD, não o nome do produto.
                "catmat": produto["codigo"], # O código SIAG/TCE para o DFD
                "unidade": unidade_para_dfd, # A unidade selecionada pelo usuário
                "qtd": st.session_state.quantidade,
                "descricao": produto["descricao"].upper() # A descrição do produto para o DFD
            }
        ]

        # Você precisará ter a função gerar_dfd_completo configurada para receber 'dados' e 'lista_itens'
        # e preencher os placeholders do seu modelo DOCX corretamente, incluindo a tabela do ITEM 7.
        caminho_arquivo = gerar_dfd_completo(dados, lista_itens)

    with open(caminho_arquivo, "rb") as f:
        st.success("✅ Documento gerado com sucesso!")
        st.download_button("📥 Baixar Documento", f, file_name=os.path.basename(caminho_arquivo))