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
print("Chave carregada:", bool(api_key))
print("Chave carregada:", bool(openai.api_key))

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


# def agente_redator_de_imagem(topico, plano_de_post):
#     redator_imagem = Agent(
#         name="agente_redator_imagem",
#         model=MODEL_ID,
#         instruction="""
#         Você é um redator criativo de prompt de imagens, sempre começa seu texto com 'gere uma imagem' e pega os pontos principais do plano de post para gerar um prompt que sejá coerente para criação de imagens usando IA.
#         """
#     )
#     entrada = f"Tópico: {topico}\nPlano de post: {plano_de_post}"
#     return call_agent(redator_imagem, entrada)


# from openai import OpenAI
# import base64


# client_openAI = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# prompt="a red apple on a wooden table"

# def agente_gerador_de_imagem(prompt):
    
#     response = client_openAI.images.generate(
#         model="dall-e-3",
#         prompt=prompt,
#         size="1024x1024",
#         n=1,
#         response_format="b64_json"
#     )


#     base64_image = response.data[0].b64_json

#     # Salvar em arquivo local
#     with open("apple.png", "wb") as f:
#         f.write(base64.b64decode(base64_image))


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


# @app.route('/gerar_prompt', methods=['GET'])
# def gerar_prompt():
#     topico = request.args.get('topico')
#     plano = request.args.get('plano')

#     if not topico or not plano:
#         return jsonify({"erro": "Parâmetros 'topico' e 'plano' são obrigatórios."}), 400

#     prompt_imagem = agente_redator_de_imagem(topico, plano)
#     return jsonify({'rascunho_do_post_imagem': prompt_imagem})

# @app.route('/gerar_imagem_get')
# def gerar_imagem_get():
#     data = request.get_json()
#     prompt = data.get('rascunho_do_post_imagem')
#     if not prompt:
#         return jsonify({"erro": "Parâmetro 'rascunho_do_post_imagem' é obrigatório."}), 400
#     print("Prompt recebido:", prompt)


#     try:
#         response = client_openAI.images.generate(
#             model="dall-e-3",
#             prompt=prompt,
#             size="1024x1024",
#             n=1,
#             response_format="b64_json"  # para receber base64
#         )
#         # pega a imagem em base64
#         image_b64 = response.data[0].b64_json

#         # opcional: salvar imagem localmente
#         import base64
#         import os

#         pasta = "imagens_geradas"
#         if not os.path.exists(pasta):
#             os.makedirs(pasta)

#         nome_arquivo = os.path.join(pasta, f"imagem_{int(date.today().strftime('%Y%m%d%H%M%S'))}.png")
#         with open(nome_arquivo, "wb") as f:
#             f.write(base64.b64decode(image_b64))

#         return jsonify({
#             "imagem_base64": image_b64,
#             "arquivo_salvo": nome_arquivo,
#             "prompt": prompt
#         })
#     except Exception as e:
#         return jsonify({"erro": f"Erro ao gerar imagem: {str(e)}"}), 500


# import base64
# import os

# @app.route('/gerar_imagem', methods=['POST'])
# def gerar_imagem():
#     data = request.get_json()
#     prompt = data.get('rascunho_do_post_imagem')

#     if not prompt or prompt.strip() == "":
#         return jsonify({"erro": "Parâmetro 'rascunho_do_post_imagem' é obrigatório e não pode ser vazio."}), 400

#     print("Prompt recebido:", prompt)

#     try:
#         response = client_openAI.images.generate(
#             model="dall-e-3",
#             prompt=prompt,
#             size="1024x1024",
#             n=1,
#             response_format="b64_json"
#         )

#         b64_json = response.data[0].b64_json
#         image_data = base64.b64decode(b64_json)

#         # Salvar a imagem em uma pasta local 'imagens'
#         pasta_imagens = "imagens"
#         if not os.path.exists(pasta_imagens):
#             os.makedirs(pasta_imagens)

#         nome_arquivo = f"{prompt[:20].replace(' ', '_')}.png"  # nome simples baseado no prompt
#         caminho_arquivo = os.path.join(pasta_imagens, nome_arquivo)

#         with open(caminho_arquivo, "wb") as f:
#             f.write(image_data)

#         return jsonify({
#             "mensagem": "Imagem gerada com sucesso.",
#             "arquivo_salvo": caminho_arquivo,
#             "prompt": prompt
#         })

#     except Exception as e:
#         print("Erro ao gerar imagem:", e)
#         return jsonify({"erro": f"Erro ao gerar imagem: {str(e)}"}), 500



    
@app.route('/revisar')
def revisar():
    topico = request.args.get('topico')
    rascunho = request.args.get('rascunho')
    texto = agente_revisor(topico, rascunho)
    return jsonify({'texto_revisado': texto})


# ========= MAIN =========

if __name__ == '__main__':
    app.run(debug=True)
