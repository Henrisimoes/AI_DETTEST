import subprocess
from docx import Document
from datetime import datetime

def gerar_texto_ollama_cli(prompt):
    cmd = ['ollama', 'run', 'llama3.2:1b']
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            errors='replace',
            text=True
        )
        stdout, stderr = process.communicate(input=prompt, timeout=120)
    except subprocess.TimeoutExpired:
        process.kill()
        print("Timeout: o processo demorou demais para responder.")
        return None

    if process.returncode != 0:
        print("Erro ao executar Ollama:", stderr.strip())
        return None
    return stdout.strip()

def criar_docx(nome_arquivo: str, texto: str):
    doc = Document()
    doc.add_paragraph(texto)
    doc.save(nome_arquivo)
    print(f"Documento '{nome_arquivo}' criado com sucesso!")

def fluxo_interativo():
    cabecalho = """
DOCUMENTO DE FORMALIZAÇÃO DA DEMANDA (DFD)  
ÓRGÃO: DEPARTAMENTO ESTADUAL DE TRÂNSITO DE MATO GROSSO – DETRAN-MT  
UNIDADE ORÇAMENTÁRIA: 19301  
SETOR REQUISITANTE: COORDENADORIA DE TECNOLOGIA DA INFORMAÇÃO  
RESPONSÁVEL PELA DEMANDA: DANILO VIEIRA DA CRUZ  
MATRÍCULA: 246679  
E-MAIL: danilocruz@detran.mt.gov.br  
TELEFONE: (65) 3615-4811

"""

    print("Informe os dados para gerar o documento de requisição.\n")

    modelo = input("Modelo do item (ex: Mouse sem fio, Cabo HDMI 3m etc): ").strip()
    quantidade = input("Quantidade desejada: ").strip()
    finalidade = input("Finalidade ou descrição resumida (ex: para uso na Coordenadoria de TI): ").strip()

    # Monta prompt para o Ollama com instruções claras para gerar documento formal
    prompt = (
        cabecalho +
        f"1 - OBJETO (TIPO DE MATERIAL): Material de consumo\n" +
        f"2 - DESCRIÇÃO SUCINTA DO OBJETO: Aquisição de {quantidade} unidades do item '{modelo}', {finalidade}.\n" +
        f"3 - FORMA DE CONTRATAÇÃO SUGERIDA: Utilização à ARP - Órgão Participante\n" +
        f"4 - NECESSIDADE DE ESTUDO TÉCNICO PRELIMINAR E ANÁLISE DE RISCOS: NÃO\n" +
        f"5 - OS OBJETOS A SEREM ADQUIRIDOS ESTÃO PREVISTOS NO PLANO DE CONTRATAÇÕES ANUAL? SIM\n" +
        f"6 - DOTAÇÃO ORÇAMENTÁRIA OU PREVISÃO ORÇAMENTÁRIA: Programa: 036 Projeto/Atividade (Ação): 2009 Subação: 02 Etapa: 01 Elemento da Despesa: 3390.3000 Fonte: 15010000\n" +
        f"7 - QUANTIDADE E ESPECIFICAÇÃO DO PRODUTO:\n" +
        f"ITEM ÚNICO - QTDE: {quantidade} - ESPECIFICAÇÃO: {modelo}\n\n" +
        "Por favor, gere o texto formal completo do documento de requisição, conforme modelo oficial do DETRAN-MT."
    )

    print("\nGerando documento com base nas informações fornecidas...\n")

    texto_gerado = gerar_texto_ollama_cli(prompt)

    if texto_gerado:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"Documento_Requisicao_DETRANMT_{timestamp}.docx"
        criar_docx(nome_arquivo, texto_gerado)
    else:
        print("Não foi possível gerar o texto com Ollama.")

if __name__ == "__main__":
    fluxo_interativo()
