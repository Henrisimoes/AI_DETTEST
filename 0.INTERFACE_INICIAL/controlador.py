# controlador.py - VERSÃO FINAL 2.0 (COM MODO HEADLESS)

from flask import Flask, jsonify
import subprocess
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- LISTA DE APLICAções PARA INICIAR ---
APPS_PARA_INICIAR = [
    {
        "nome": "DFD",
        "caminho_app": "C:/Users/pedrosilva/Desktop/PROJETO IA DETRAN/DFD - DOCUMENTO DE FORMALIZAÇÃO DE DEMANDA/app.py",
        "porta": "8501"
    },
    {
        "nome": "ETP",
        "caminho_app": "C:/Users/pedrosilva/Desktop/PROJETO IA DETRAN/ETP - ESTUDO TÉCNICO PRELIMINAR/app.py",
        "porta": "8503"
    }
]
# -----------------------------------------

services_started = False
running_processes = []

@app.route("/start_services")
def start_services():
    global services_started
    
    if services_started:
        print("Servicos ja foram iniciados anteriormente.")
        return jsonify({"status": "already_running", "message": "Os servicos ja foram iniciados."})

    try:
        print("Recebido comando para iniciar os servicos diretamente via Python...")
        for app_info in APPS_PARA_INICIAR:
            print(f"Iniciando {app_info['nome']} na porta {app_info['porta']} de forma silenciosa e sem abrir navegador...")
            
            if not os.path.exists(app_info['caminho_app']):
                print(f"!!! ERRO: O arquivo nao foi encontrado em: {app_info['caminho_app']}")
                continue 

            command = [
                "python", "-m", "streamlit", "run",
                app_info['caminho_app'],
                "--server.port", app_info['porta'],
                # --- A GRANDE MUDANÇA ESTÁ AQUI ---
                # Este argumento diz ao Streamlit para NAO abrir o navegador automaticamente
                "--server.headless=true"
                # ----------------------------------
            ]
            
            creation_flags = subprocess.CREATE_NO_WINDOW
            
            process = subprocess.Popen(command, creationflags=creation_flags)
            running_processes.append(process)

        services_started = True
        print("Todos os comandos de inicializacao foram enviados. Servicos estao rodando em segundo plano.")
        return jsonify({"status": "success", "message": "Servicos iniciados em segundo plano com sucesso."})

    except Exception as e:
        print(f"Ocorreu um erro critico ao tentar iniciar os processos: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print("Servidor de Controle (versao final e headless) rodando em http://localhost:5000")
    print("Acesse seu index.html e clique no botao 'Iniciar Servicos'.")
    app.run(port=5000)