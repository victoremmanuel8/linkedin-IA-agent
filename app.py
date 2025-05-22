from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import date
import textwrap
from IPython.display import Markdown
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
import warnings
import openai

# Suprimir avisos
warnings.filterwarnings("ignore")

# Carrega as variáveis do arquivo .env
load_dotenv()

# Chaves da API
api_key = os.getenv("GOOGLE_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Verifique se carregou corretamente
print("Chave carregada google:", bool(api_key))
print("Chave carregada openai:", bool(openai.api_key))

from google import genai
client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-2.0-flash"

# Iniciar aplicação
app = Flask(__name__)
CORS(app)


# ========= AGENTES =========

def call_agent(agent: Agent, message_text: str) -> str:
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)

    content = types.Content(role="user", parts=[types.Part(text=message_text)])
    final_response = ""

    for event in runner.run(user_id="user1", session_id="session1", new_message=content):
        if event.is_final_response():
            final_response = event.content.parts[0].text
            break
    return final_response


def agente_buscador(topico, data_de_hoje):
    buscador = Agent(
        name="agente_buscador",
        model=MODEL_ID,
        description="Agente que busca notícias sobre o tópico indicado",
        tools=[google_search],
        instruction="""
        Você é um assistente de pesquisa. Sua tarefa é utilizar a ferramenta de busca do Google (google_search) para recuperar as notícias mais recentes sobre o tema indicado abaixo.
        Critérios:
        - Máximo de 5 lançamentos relevantes.
        - Priorize tópicos com maior volume de notícias e entusiasmo.
        - Notícias com até 30 dias.
        - Caso o tema seja fraco, mencione isso e sugira substituição.
        """
    )
    entrada = f"Tópico: {topico}\nData de hoje: {data_de_hoje}"
    return call_agent(buscador, entrada)


def agente_planejador(topico, lancamentos_buscados):
    planejador = Agent(
        name="agente_planejador",
        model=MODEL_ID,
        description="Agente que planeja posts",
        tools=[google_search],
        instruction="""
        Você é um planejador de conteúdo. Analise os lançamentos, use google_search para aprofundar e:
        1. Liste os principais pontos para cada lançamento.
        2. Escolha o mais relevante.
        3. Dê um plano de conteúdo e resumo do tema escolhido.
        """
    )
    entrada = f"Tópico: {topico}\nLançamentos buscados: {lancamentos_buscados}"
    return call_agent(planejador, entrada)


def agente_redator(topico, plano_de_post):
    redator = Agent(
        name="agente_redator",
        model=MODEL_ID,
        description="Agente redator de posts engajadores para LinkedIn",
        instruction="""
        Você é um Redator Criativo. Escreva um rascunho de post para LinkedIn baseado no plano fornecido.
        O post deve ser claro, engajador e conter de 2 a 4 hashtags.
        """
    )
    entrada = f"Tópico: {topico}\nPlano de post: {plano_de_post}"
    return call_agent(redator, entrada)

def agente_revisor(topico, rascunho_do_post):
    revisor = Agent(
        name="agente_revisor",
        model=MODEL_ID,
        description="Agente revisor de textos para posts de LinkedIn",
        instruction="""
        Revise o post com foco em:
        - Gramática e ortografia
        - Clareza, concisão e engajamento
        - Tom e linguagem adequados para LinkedIn
        - Hashtags relevantes e formatação apropriada
        """
    )
    entrada = f"Tópico: {topico}\nRascunho do post: {rascunho_do_post}"
    return call_agent(revisor, entrada)


# ========= ROTAS =========

@app.route('/buscar')
def buscar():
    topico = request.args.get('topico')
    data_de_hoje = date.today().strftime("%d/%m/%Y")
    resultado = agente_buscador(topico, data_de_hoje)
    return jsonify({'resultado_busca': resultado})


@app.route('/planejar')
def planejar():
    topico = request.args.get('topico')
    busca = request.args.get('busca')
    plano = agente_planejador(topico, busca)
    return jsonify({'plano_post': plano})


@app.route('/redigir')
def redigir():
    topico = request.args.get('topico')
    plano = request.args.get('plano')
    rascunho = agente_redator(topico, plano)
    return jsonify({'rascunho_post': rascunho})
    
@app.route('/revisar')
def revisar():
    topico = request.args.get('topico')
    rascunho = request.args.get('rascunho')
    texto = agente_revisor(topico, rascunho)
    return jsonify({'texto_revisado': texto})


# ========= MAIN =========

if __name__ == '__main__':
    app.run(debug=True)
