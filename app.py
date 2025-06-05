from flask import Flask, json, request, jsonify
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
import requests
import base64

# Suprimir avisos
warnings.filterwarnings("ignore")

# Carrega as variáveis do arquivo .env
load_dotenv()

# Chaves da API
api_key = os.getenv("GOOGLE_API_KEY")
api_key_aiml = os.getenv("AIML_API_KEY")

# API URL
api_url = os.getenv("AIML_API_URL")

# Verifique se carregou corretamente
print("Chave carregada google:", bool(api_key))
print("Chave carregada aiml:", bool(api_key_aiml))

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


def agente_redator(topico, lancamentos_buscados):
    redator = Agent(
        name="agente_redator",
        model=MODEL_ID,
        description="Agente redator de posts engajadores para LinkedIn",
        instruction="""
        Você é um Redator Criativo.
        Escreva um rascunho de post para LinkedIn baseado nos lançamentos buscados no modelo de noticia.
        sempre tente trazer os principais tópicos da pesquisa e dissertar como se fosse um reporter.
        seguindo esse modelo (🚀 titulo 🚀

        paragrafo 1 🚀

        paragrafo 2 🚀

        trecho que faz uma pergunta ao usuário referente ao conteudo do post 😊)

        muito objetivo e sempre escreve de forma profissional.
        O post deve ser claro, engajador e conter de 2 a 4 hashtags.

        você não fala em primeira pessoa, fala de forma culta como se fosse um jornalista em um jornal

        quero que no final mostre esse trecho dessa mesma forma "[*Post criado com a ajuda de um sistema de agentes de IA que desenvolvi!* - Link para o repositório: https://github.com/victoremmanuel8/linkedin-IA-agent]"
        
        """
    )
    entrada = f"Tópico: {topico}\nPlano de post: {lancamentos_buscados}"
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

        verifique se segue esse padrão (🚀 titulo 🚀

        paragrafo 1 🚀

        paragrafo 2 🚀

        trecho que faz uma pergunta ao usuário referente ao conteudo do post 😊), titulo em destaque, divisão por paragrafos e uso de emojis em cada final de paragrafo.
        """
    )
    entrada = f"Tópico: {topico}\nRascunho do post: {rascunho_do_post}"
    return call_agent(revisor, entrada)

def agente_gerador_de_prompt(topico ,rascunho_do_post):
    prompt_imagem = Agent(
        name="gerador_de_prompt",
        model=MODEL_ID,
        description="Agente que gera um prompt para a geração de uma imagem",
        instruction="""
        Você é um gerador de prompt para a geração de uma imagem.
        tentando sempre criar imagens que sejam relevantes para o post.
        o prompt deve ser em inglêS e detalhado.
        """
    )
    entrada = f"Tópico: {topico}\nRascunho do post: {rascunho_do_post}"
    return call_agent(prompt_imagem, entrada)

# def gerar_imagem_flux(prompt_imagem):
#     response = requests.post(
#         "https://api.aimlapi.com/v1/images/generations",
#             headers = {
#             "Authorization": f"Bearer {api_key_aiml}",
#             "Content-Type": "application/json",
#             "Accept": "*/*"
#         },
#         payload= {
#         "model": "flux-pro/v1.1",
#         'image_size': {
#                     "width": 1024,
#                     "height": 320
#                 },
#         "guidance_scale": 1,
#         "num_inference_steps": 1,
#         "enable_safety_checker": True,
#         "prompt": prompt_imagem,
#         "num_images": 1,
#         "seed": 1
#         }
#     )

#     try: 
#         response.raise_for_status()
#         data = response.json()

#         print("Generation:", data)

#         if "images" in data and len(data["images"]) > 0:
#             image_base64 = data["images"][0]["b64_json"]
#             img_data = base64.b64decode(image_base64)
#             with open("imagem_flux.png", "wb") as f:
#                 f.write(img_data)
#             print("Imagem gerada com sucesso!")
#             return "imagem_flux.png"
#         else:
#             print("Nenhuma imagem gerada")
#             return None
#     except Exception as e:
#         print(f"Erro ao gerar imagem: {e}")
#         return None

# if __name__ == "__main__":
#     gerar_imagem_flux()

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

@app.route('/prompt')
def prompt():
    topico = request.args.get('topico')
    rascunho = request.args.get('rascunho')
    texto = agente_gerador_de_prompt(topico, rascunho)
    return jsonify({'prompt_imagem': texto})

# @app.route('/gerar_imagem', methods=['POST'])
# def gerar_imagem_endpoint():
#     # 1. Obtenha os dados JSON do corpo da requisição
#     request_data = request.json

#     # 2. Extraia o prompt usando a chave que seu frontend está enviando
#     prompt = request_data.get('rascunho_do_post_imagem')

#     if not prompt:
#         return jsonify({"error": "Parâmetro 'rascunho_do_post_imagem' é obrigatório no corpo JSON"}), 400

#     # Você pode adicionar validações adicionais aqui se desejar (ex: prompt muito curto)

#     # Parâmetros opcionais para a API do Flux AI.
#     # Você pode passá-los do frontend ou defini-los aqui.
#     modelo = request_data.get('modelo', 'flux/dev') # Padrão para flux/dev
#     tamanho_imagem = request_data.get('tamanho_imagem', '1024x768') # Padrão
#     num_images = int(request_data.get('num_images', 1)) # Quantidade de imagens

#     headers = {
#         "Authorization": f"Bearer {api_key_aiml}",
#         "Content-Type": "application/json",
#         "Accept": "*/*"
#     }
#     payload = {
#         "model": modelo,
#         "prompt": prompt,
#         "image_size": tamanho_imagem,
#         "num_images": num_images
#         # Você pode adicionar outros parâmetros da API da AIMLAPI aqui
#     }

#     try:
#         response = requests.post(api_url, headers=headers, json=payload, timeout=60) # Adicione um timeout
#         response.raise_for_status() # Levanta um erro para status 4xx/5xx

#         api_response_data = response.json()

#         if "images" in api_response_data and len(api_response_data["images"]) > 0:
#             # A AIMLAPI geralmente retorna 'b64_json' ou 'url'
#             if "b64_json" in api_response_data["images"][0]:
#                 image_base64 = api_response_data["images"][0]["b64_json"]
#                 # Retorna base64 diretamente (com o prefixo data:image/png;base64, para o frontend)
#                 return jsonify({'imagem_url': f"data:image/png;base64,{image_base64}", 'message': 'Imagem gerada com sucesso!'})
#             elif "url" in api_response_data["images"][0]:
#                 image_url = api_response_data["images"][0]["url"]
#                 # Retorna o URL direto
#                 return jsonify({'imagem_url': image_url, 'message': 'Imagem gerada com sucesso!'})
#             else:
#                 return jsonify({"error": "Formato de resposta de imagem inesperado da API externa."}), 500
#         else:
#             return jsonify({"error": "Nenhuma imagem foi retornada pela API externa ou resposta vazia."}), 500

#     except requests.exceptions.HTTPError as http_err:
#         print(f"Erro HTTP ao comunicar com a API: {http_err} - {response.text}")
#         return jsonify({"error": f"Erro HTTP ao comunicar com a API: {http_err}", "details": response.text}), response.status_code
#     except requests.exceptions.ConnectionError as conn_err:
#         print(f"Erro de Conexão com a API: {conn_err}")
#         return jsonify({"error": f"Erro de conexão com a API: {conn_err}"}), 503
#     except requests.exceptions.Timeout as timeout_err:
#         print(f"Timeout da requisição à API: {timeout_err}")
#         return jsonify({"error": f"Tempo limite da requisição à API excedido: {timeout_err}"}), 504
#     except requests.exceptions.RequestException as req_err:
#         print(f"Erro inesperado na requisição à API: {req_err}")
#         return jsonify({"error": f"Erro inesperado na requisição à API: {req_err}"}), 500
#     except Exception as e:
#         print(f"Erro interno do servidor: {e}")
#         return jsonify({"error": f"Erro interno do servidor: {e}"}), 500

# ========= MAIN =========

if __name__ == '__main__':
    app.run(debug=True, port=5000)
