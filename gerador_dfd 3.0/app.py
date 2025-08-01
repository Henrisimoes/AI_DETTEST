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

# ======== set locale e valores em PT BR ===========
locale.setlocale(locale.LC_ALL, 'C') # Reset para um locale padrão antes de tentar pt_BR
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, '') # Fallback para o padrão do sistema

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
            margin-bottom: 20px; /* Adiciona espaço entre os formulários */
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
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.markdown('<div class="title-container">', unsafe_allow_html=True)
    st.image(logo, width=60)
    st.markdown('<div class="title-text">Gerador de Documento de Formalização da Demanda - DETRAN-MT</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="title-container">', unsafe_allow_html=True)
    st.markdown('<div class="title-text">Gerador de Documento de Formalização da Demanda - DETRAN-MT</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.warning(f"Logo não encontrada em: {logo_path}. Verifique o caminho.")


# ====== Função de busca no SIAG ==========
@st.cache_data(show_spinner="Buscando produtos no SIAG...", ttl=3600) # Adicione cache para evitar re-execuções desnecessárias
def buscar_siag_selenium(termo_pesquisa):
    url = "http://aquisicoes.gestao.mt.gov.br/sgc/faces/pub/sgc/central/ItemCompraPageList.jsp"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Para ambientes de deploy (Docker, Streamlit Cloud), pode ser necessário apontar para o Chromedriver
    # chrome_options.binary_location = "/usr/bin/google-chrome" # Exemplo para Linux
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        st.error(f"Erro ao inicializar o navegador. Verifique se o Chromedriver está instalado e configurado corretamente. Erro: {e}")
        return []

    driver.get(url)

    wait = WebDriverWait(driver, 30)
    html = None

    try:
        opcao_radio = wait.until(EC.element_to_be_clickable(
            (By.ID, "form_PesquisaItemPageList:procurarPorCombo:2")))
        opcao_radio.click()

        campo_busca = wait.until(EC.presence_of_element_located(
            (By.ID, "form_PesquisaItemPageList:palavraChaveInput")))

        campo_busca.clear()
        campo_busca.send_keys(termo_pesquisa)

        botao_pesquisar = wait.until(EC.element_to_be_clickable(
            (By.ID, "form_PesquisaItemPageList:pesquisarButton")))

        botao_pesquisar.click()

        time.sleep(5) # Pausa para aguardar o carregamento da página. Pode precisar de ajuste.
        html = driver.page_source

    except TimeoutException:
        st.error("Tempo limite excedido ao buscar no SIAG. A página demorou muito para carregar ou os elementos não foram encontrados.")
        return []
    except Exception as e:
        st.error(f"Ocorreu um erro durante a busca no SIAG: {e}")
        return []
    finally:
        driver.quit()

    if html is None:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    tabela = soup.find('table', {'id': 'form_PesquisaItemPageList:editalDataTable'})

    if not tabela:
        return []

    linhas = tabela.find_all('tr')[1:] # Ignora o cabeçalho
    resultados = []

    for linha in linhas:
        colunas = linha.find_all('td')
        if len(colunas) >= 2: # Garante que há colunas suficientes
            codigo = colunas[0].get_text(strip=True)
            descricao = colunas[1].get_text(strip=True)
            if codigo: # Garante que o código não é vazio
                resultados.append({'codigo': codigo, 'descricao': descricao})

    return resultados

# ====== ESTADO DA SESSÃO PARA PERSISTÊNCIA DE DADOS ==========
# Inicializar st.session_state para persistir os dados
if 'opcoes_itens_siag' not in st.session_state:
    st.session_state.opcoes_itens_siag = [] # Itens retornados da busca no SIAG
if 'item_selecionado_siag' not in st.session_state:
    st.session_state.item_selecionado_siag = None # Item atualmente selecionado no selectbox da busca
if 'quantidade_item_adicionar' not in st.session_state:
    st.session_state.quantidade_item_adicionar = "" # Quantidade do item a ser adicionado
if 'finalidade_item_adicionar' not in st.session_state:
    st.session_state.finalidade_item_adicionar = "" # Finalidade específica do item a ser adicionado
if 'unidade_item_adicionar' not in st.session_state:
    st.session_state.unidade_item_adicionar = "UN" # Unidade do item a ser adicionado
if 'termo_pesquisa' not in st.session_state:
    st.session_state.termo_pesquisa = "" # Termo de pesquisa SIAG
if 'lista_de_itens_dfd' not in st.session_state: # <<--- NOVA LISTA PARA ACUMULAR ITENS DO DFD
    st.session_state.lista_de_itens_dfd = []
if 'finalidade_geral_dfd' not in st.session_state:
    st.session_state.finalidade_geral_dfd = ""
if 'tipo_objeto' not in st.session_state:
    st.session_state.tipo_objeto = "Material de consumo"
if 'forma_contratacao' not in st.session_state:
    st.session_state.forma_contratacao = "Modalidades da Lei nº 14.133/21"
if 'arp_seplag' not in st.session_state:
    st.session_state.arp_seplag = ""
if 'data_pretendida' not in st.session_state:
    st.session_state.data_pretendida = datetime.now().date() # Inicializa com a data atual
if 'fiscal_nome' not in st.session_state:
    st.session_state.fiscal_nome = ""
if 'fiscal_matricula' not in st.session_state:
    st.session_state.fiscal_matricula = ""

# --- NOVOS ITENS DE SESSION_STATE PARA O ITEM 6 ---
if 'programa' not in st.session_state:
    st.session_state.programa = "036"
if 'subacao' not in st.session_state:
    st.session_state.subacao = "02"
if 'elemento_despesa' not in st.session_state:
    st.session_state.elemento_despesa = "3390.3000"
if 'projeto_atividade' not in st.session_state:
    st.session_state.projeto_atividade = "2009"
if 'etapa' not in st.session_state:
    st.session_state.etapa = "01"
if 'fonte' not in st.session_state:
    st.session_state.fonte = "15010000"
# --- FIM DOS NOVOS ITENS ---

# ====================================================================
# FORMULÁRIO 1: ADICIONAR ITENS
# ====================================================================
with st.form("form_adicionar_itens", clear_on_submit=False): 
    st.subheader("1. Adicionar Itens ao Documento (DFD)")

    col1, col2 = st.columns([3, 1])
    with col1:
        termo_pesquisa_input = st.text_input("Digite o nome do produto para buscar no SIAG", value=st.session_state.termo_pesquisa, key="termo_pesquisa_siag_input")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True) 
        buscar_siag_button = st.form_submit_button("🔍 Buscar no SIAG", type="primary")

    if buscar_siag_button:
        if termo_pesquisa_input:
            st.session_state.opcoes_itens_siag = buscar_siag_selenium(termo_pesquisa_input)
            st.session_state.termo_pesquisa = termo_pesquisa_input 

            if not st.session_state.opcoes_itens_siag:
                st.error("❌ Nenhum produto encontrado no SIAG com este termo. Tente outro termo de busca.")
                st.session_state.item_selecionado_siag = None # Garante que nada está selecionado
            else:
                # Pré-seleciona o primeiro item encontrado após uma busca bem-sucedida
                st.session_state.item_selecionado_siag = st.session_state.opcoes_itens_siag[0]['descricao']
        else:
            st.warning("Por favor, digite um termo para buscar no SIAG.")
            st.session_state.opcoes_itens_siag = [] # Limpa opções anteriores
            st.session_state.item_selecionado_siag = None # Limpa seleção anterior
    
    # Lógica para exibir o selectbox de seleção de item do SIAG
    # Só exibe e permite seleção se houver opções na lista de resultados da busca
    if st.session_state.opcoes_itens_siag:
        nomes_disp = [item['descricao'] for item in st.session_state.opcoes_itens_siag]
        
        # Garante que o item selecionado está entre as opções válidas
        current_idx = 0
        if st.session_state.item_selecionado_siag in nomes_disp:
            current_idx = nomes_disp.index(st.session_state.item_selecionado_siag)
        elif nomes_disp: # Se houver opções mas o item_selecionado_siag não está, seleciona o primeiro
             st.session_state.item_selecionado_siag = nomes_disp[0]
        else: # Se não há opções (lista vazia), reseta a seleção
            st.session_state.item_selecionado_siag = None


        st.session_state.item_selecionado_siag = st.selectbox(
            "Selecione o item do SIAG",
            nomes_disp,
            index=current_idx,
            key="sb_item_siag_selection",
            help="Selecione um dos produtos encontrados na busca do SIAG."
        )
    else:
        st.session_state.item_selecionado_siag = None # Garante que está None se não há opções
        st.selectbox("Selecione o item do SIAG", [], disabled=True, 
                     help="Use o campo acima para buscar um produto no SIAG primeiro. Nenhum item disponível para seleção.")


    st.session_state.quantidade_item_adicionar = st.text_input(
        "Quantidade deste item",
        value=st.session_state.quantidade_item_adicionar,
        key="qtd_item_add_input"
    )
    st.session_state.unidade_item_adicionar = st.selectbox(
        "Unidade deste item",
        ["UN", "KG", "L", "CX", "M", "M2", "M3", "OUTRO"], 
        index=["UN", "KG", "L", "CX", "M", "M2", "M3", "OUTRO"].index(st.session_state.unidade_item_adicionar),
        key="unidade_item_add_selectbox"
    )
    st.session_state.finalidade_item_adicionar = st.text_area(
        "Finalidade ESPECÍFICA deste item (ex: para impressoras do setor X, para licenças de software Y)",
        value=st.session_state.finalidade_item_adicionar,
        key="finalidade_item_add_textarea",
        height=70
    )
    
    # O botão de adicionar só é habilitado se um item do SIAG foi selecionado
    adicionar_item_button = st.form_submit_button(
        "➕ Adicionar Este Item ao DFD",
        disabled=st.session_state.item_selecionado_siag is None,
        type="secondary" 
    )

    if adicionar_item_button:
        # Agora a validação verifica se há um item selecionado do SIAG E os outros campos
        if st.session_state.item_selecionado_siag and st.session_state.quantidade_item_adicionar and st.session_state.finalidade_item_adicionar:
            # Encontra o produto completo do SIAG para obter o código
            produto_para_add = next((item for item in st.session_state.opcoes_itens_siag if item['descricao'] == st.session_state.item_selecionado_siag), None)
            
            if produto_para_add:
                novo_item = {
                    "item": str(len(st.session_state.lista_de_itens_dfd) + 1).zfill(3), # Contador sequencial (001, 002...)
                    "catmat": produto_para_add["codigo"],
                    "unidade": st.session_state.unidade_item_adicionar,
                    "qtd": st.session_state.quantidade_item_adicionar,
                    "descricao": produto_para_add["descricao"].upper(),
                    "finalidade_especifica": st.session_state.finalidade_item_adicionar # Guarda a finalidade específica
                }
                st.session_state.lista_de_itens_dfd.append(novo_item)
                st.success(f"Item '{novo_item['descricao']}' adicionado com sucesso ao DFD!")
                
                # Limpa os campos de adição para o próximo item
                st.session_state.quantidade_item_adicionar = ""
                st.session_state.finalidade_item_adicionar = ""
                st.session_state.item_selecionado_siag = None 
                st.session_state.opcoes_itens_siag = [] # Força uma nova busca para o próximo item
                st.session_state.termo_pesquisa = "" 
                
                st.rerun() # <<< CORRIGIDO: st.experimental_rerun() para st.rerun()
            else:
                st.error("Erro interno: Produto selecionado não foi encontrado nas opções do SIAG. Tente buscar novamente.")
        else:
            st.error("Por favor, preencha todos os campos do item (Produto selecionado do SIAG, Quantidade, Unidade e Finalidade específica) para adicionar.")



st.subheader("2. Itens Adicionados ao Documento")
if st.session_state.lista_de_itens_dfd:
    # Exibe os itens adicionados em uma tabela para visualização
    st.dataframe(
        st.session_state.lista_de_itens_dfd,
        column_order=["item", "descricao", "qtd", "unidade", "finalidade_especifica"],
        hide_index=True,
        column_config={
            "item": st.column_config.Column("Nº", width="small"),
            "descricao": st.column_config.Column("Descrição do Item", width="large"),
            "qtd": st.column_config.Column("Quantidade", width="small"),
            "unidade": st.column_config.Column("Unidade", width="small"),
            "finalidade_especifica": st.column_config.Column("Finalidade Específica (deste item)", width="medium")
        }
    )
    
    # Botão para remover o último item (opcional, mas útil para correções)
    if st.button("Remover Último Item Adicionado", key="remove_last_item_button"):
        if st.session_state.lista_de_itens_dfd:
            st.session_state.lista_de_itens_dfd.pop()
            st.info("Último item removido.")
            st.rerun() # <<< CORRIGIDO: st.experimental_rerun() para st.rerun()
else:
    st.info("Nenhum item adicionado ainda. Use a seção 'Adicionar Itens ao Documento (DFD)' acima para buscar e adicionar produtos.")

# Campo de finalidade geral do DFD (este é o campo CRÍTICO para a IA)
st.session_state.finalidade_geral_dfd = st.text_area(
    "Finalidade GERAL da demanda (descreva o contexto amplo e a necessidade de TODOS os itens. Este texto será a base para a inteligência artificial gerar as justificativas do DFD).",
    value=st.session_state.finalidade_geral_dfd,
    height=180,
    help="Este campo deve explicar a necessidade da demanda como um todo, agrupando as finalidades específicas dos itens e dando um panorama geral para a IA. **Ex: 'Aquisição de materiais de consumo para manutenção de equipamentos de informática e ampliação de pontos de rede da SEDE e Unidades de Atendimento do DETRAN-MT.'**"
)


# ====================================================================
# FORMULÁRIO 2: DETALHES GERAIS DO DFD E GERAÇÃO
# ====================================================================
with st.form("form_gerar_dfd"):
    st.subheader("3. Detalhes Gerais do DFD")

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
            "Material de consumo", "Material permanente", "Equipamento de TI",
            "Serviço não continuado", "Serviço sem dedicação exclusiva de mão de obra",
            "Serviço com dedicação exclusiva de mão de obra"
        ].index(st.session_state.tipo_objeto),
        key="tipo_objeto_final"
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
            "Modalidades da Lei nº 14.133/21", "Utilização à ARP - Órgão Participante",
            "Adesão à ARP de outro Órgão", "Dispensa/Inexigibilidade"
        ].index(st.session_state.forma_contratacao),
        key="forma_contratacao_final"
    )

    # --- CAMPOS NOVOS PARA O ITEM 6 ---
    st.subheader("Item 6: Dotação Orçamentária ou Previsão Orçamentária")
    st.write("Insira os dados da dotação orçamentária:")

    cols_dotacao = st.columns(3)
    with cols_dotacao[0]:
        st.session_state.programa = st.text_input(
            "Programa",
            value=st.session_state.programa,
            key="programa_input"
        )
    with cols_dotacao[1]:
        st.session_state.subacao = st.text_input(
            "Subação",
            value=st.session_state.subacao,
            key="subacao_input"
        )
    with cols_dotacao[2]:
        st.session_state.elemento_despesa = st.text_input(
            "Elemento de Despesa",
            value=st.session_state.elemento_despesa,
            key="elemento_despesa_input"
        )
    
    cols_dotacao_2 = st.columns(3)
    with cols_dotacao_2[0]:
        st.session_state.projeto_atividade = st.text_input(
            "Projeto/Atividade",
            value=st.session_state.projeto_atividade,
            key="projeto_atividade_input"
        )
    with cols_dotacao_2[1]:
        st.session_state.etapa = st.text_input(
            "Etapa",
            value=st.session_state.etapa,
            key="etapa_input"
        )
    with cols_dotacao_2[2]:
        st.session_state.fonte = st.text_input(
            "Fonte",
            value=st.session_state.fonte,
            key="fonte_input"
        )
    # --- FIM DOS NOVOS CAMPOS PARA O ITEM 6 ---

    # --- CAMPOS NOVOS PARA ITENS 9, 11 e 13 ---
    st.session_state.arp_seplag = st.text_area(
        "Item 9: Informações sobre Atas de Registro de Preços da SEPLAG",
        value=st.session_state.arp_seplag,
        key="arp_seplag_input",
        help="Informe se há ARP da SEPLAG aplicável ou 'Não se aplica'."
    )

    st.session_state.data_pretendida = st.date_input(
        "Item 11: Data Pretendida para Aquisição/Contratação",
        value=st.session_state.data_pretendida,
        key="data_pretendida_input",
        help="Escolha a data limite para a conclusão do processo de contratação."
    )

    st.session_state.fiscal_nome = st.text_input(
        "Item 13: Nome do Responsável pela Fiscalização Contratual",
        value=st.session_state.fiscal_nome,
        key="fiscal_nome_input",
        help="Nome completo do servidor responsável pela fiscalização do contrato."
    )
    st.session_state.fiscal_matricula = st.text_input(
        "Item 13: Matrícula do Responsável pela Fiscalização Contratual",
        value=st.session_state.fiscal_matricula,
        key="fiscal_matricula_input",
        help="Matrícula do servidor responsável pela fiscalização do contrato."
    )
    # --- FIM DOS NOVOS CAMPOS ---


    # O botão de gerar documento só é habilitado se houver itens adicionados e a finalidade geral preenchida
    gerar_dfd_button = st.form_submit_button(
        "📥 Gerar Documento DFD Completo",
        disabled=(not st.session_state.lista_de_itens_dfd or not st.session_state.finalidade_geral_dfd),
        type="primary"
    )

# ====== PROCESSAMENTO E GERAÇÃO DO DFD ========
if gerar_dfd_button:
    if not st.session_state.lista_de_itens_dfd: # Validação redundante, mas segura
        st.error("❌ Por favor, adicione ao menos um item ao DFD antes de gerar o documento.")
        st.stop()
    if not st.session_state.finalidade_geral_dfd: # Validação redundante, mas segura
        st.error("❌ Por favor, preencha a 'Finalidade GERAL da demanda'. Este campo é crucial para a IA.")
        st.stop()

    with st.spinner("Gerando documento com apoio da IA..."):
        # Prepara os dados gerais do DFD
        dados_gerais = {
            "finalidade": st.session_state.finalidade_geral_dfd, # Agora é a finalidade geral
            "tipo_objeto": st.session_state.tipo_objeto,
            "forma_contratacao": st.session_state.forma_contratacao,
            "orgao": "DEPARTAMENTO ESTADUAL DE TRÂNSITO DE MATO GROSSO – DETRAN-MT",
            "unidade_orcamentaria": "19301",
            "setor": "COORDENADORIA DE TECNOLOGIA DA INFORMAÇÃO",
            "responsavel": "DANILO VIEIRA DA CRUZ",
            "matricula": "246679",
            "telefone": "(65) 3615-4811",
            "email": "danilocruz@detran.mt.gov.br",
            # --- NOVOS DADOS PARA ITENS 6, 9, 11 e 13 ---
            "programa": st.session_state.programa,
            "subacao": st.session_state.subacao,
            "elemento_despesa": st.session_state.elemento_despesa,
            "projeto_atividade": st.session_state.projeto_atividade,
            "etapa": st.session_state.etapa,
            "fonte": st.session_state.fonte,
            "arp_seplag": st.session_state.arp_seplag,
            "data_pretendida": st.session_state.data_pretendida.strftime("%d de %B de %Y"), # Formatar a data
            "fiscal_nome": st.session_state.fiscal_nome,
            "fiscal_matricula": st.session_state.fiscal_matricula
            # --- FIM DOS NOVOS DADOS ---
        }
        
        # A `lista_de_itens_dfd` já está pronta para ser usada e passada para gerar_dfd_completo
        
        # O nome do arquivo será baseado na descrição do PRIMEIRO item ou em um nome genérico
        # Adicionei uma verificação para garantir que lista_de_itens_dfd não está vazia
        nome_base_arquivo = st.session_state.lista_de_itens_dfd[0]['descricao'] if st.session_state.lista_de_itens_dfd else "Documento_DFD"

        try:
            # Passe a lista_de_itens_dfd para a função gerar_dfd_completo
            caminho_arquivo = gerar_dfd_completo(dados_gerais, st.session_state.lista_de_itens_dfd)

            with open(caminho_arquivo, "rb") as f:
                st.success("✅ Documento gerado com sucesso!")
                st.download_button(
                    "📥 Baixar Documento DFD",
                    f,
                    file_name=os.path.basename(caminho_arquivo),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            # Opcional: Limpar a lista após a geração para um novo DFD
            # st.session_state.lista_de_itens_dfd = [] 
            # st.session_state.finalidade_geral_dfd = ""
            # st.rerun() # Se for limpar, também deve reran aqui

        except Exception as e:
            st.error(f"❌ Erro ao gerar o documento DFD. Por favor, tente novamente. Detalhes: {e}")
            st.exception(e) # Exibe o traceback para depuração