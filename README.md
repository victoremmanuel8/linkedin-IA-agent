# linkedin-autoposter

**linkedin-autoposter** é um sistema automatizado de geração de conteúdos para LinkedIn, baseado em agentes de IA colaborativos, utilizando a API do Gemini.  
O usuário fornece um tópico e o sistema retorna um texto pronto para publicação.

## 🧠 Arquitetura do Sistema

O sistema é composto por quatro agentes de IA, cada um com uma função especializada:

### 🔍 Buscador
Realiza pesquisas na web para coletar informações atualizadas sobre o tópico fornecido.

### 🗺️ Planejador
Analisa e organiza os dados coletados, selecionando os insights mais relevantes e estruturando um roteiro para o texto.

### ✍️ Redator
Gera um texto fluido e coerente a partir do roteiro, com estilo adequado para posts profissionais no LinkedIn.

### 🕵️‍♂️ Revisor
Faz a revisão do texto, corrigindo erros gramaticais, aprimorando a clareza e ajustando o tom de comunicação.

## 🚀 Tecnologias Utilizadas

- 🐍 **Backend:** Python + API Gemini para processamento de linguagem natural e geração de conteúdo.
- ⚛️ **Frontend:** React + Next.js + Styled Components para uma interface web responsiva e intuitiva.
- 🔗 **API REST:** Comunicação entre frontend e backend.

## ✨ Funcionalidades

- Entrada de tópicos pelo usuário para iniciar o processo.
- Processamento sequencial dos agentes de IA, simulando um fluxo colaborativo.
- Geração automática de textos otimizados para LinkedIn.
- ✅ **Em desenvolvimento:** Integração com geradores de imagem por IA para enriquecer os posts.
