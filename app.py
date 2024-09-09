# -*- coding: utf-8 -*-
"""emma.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15YsDsyz4O2f8ZRb0WDs_4iQUYaPpnzvj
"""
from flask import Flask, request, render_template_string, redirect, url_for, session
import pandas as pd
import os
from unidecode import unidecode
from fuzzywuzzy import fuzz

app = Flask(__name__)

# Configuração da chave secreta para a sessão
app.secret_key = 'sua_chave_secreta_aqui'

# Caminho do arquivo no servidor
file_path = 'teste 1.xlsx'

# Verifica se o arquivo existe
if os.path.exists(file_path):
    # Carregar a planilha Excel, incluindo a coluna "Data elaboração"
    df = pd.read_excel(file_path)
else:
    df = pd.DataFrame(columns=["Palavras chaves", "Título do documento", "Link Qualyteam", "Resumo", "Data elaboração"])

# Emoji de rosto humano
face_emoji = "😊"

# Função para normalizar o texto, removendo acentuação e convertendo para minúsculas
def normalize(text):
    return unidecode(text.strip().lower()) if text else ""

# Função de busca na planilha usando uma combinação de similaridade de texto
def search_in_spreadsheet(term):
    normalized_term = normalize(term)

    # Define uma pontuação mínima de similaridade para considerar uma correspondência relevante
    strict_threshold = 75  # Limiar para correspondência estrita
    relaxed_threshold = 60  # Limiar para correspondência mais relaxada

    # Função para calcular similaridade usando `token_sort_ratio` para precisão e `partial_ratio` para recall
    def is_relevant(row):
        # Calcula a similaridade com 'Palavras chaves' e 'Resumo' usando token_sort_ratio
        keywords_strict_similarity = fuzz.token_sort_ratio(normalized_term, normalize(str(row['Palavras chaves'])))
        summary_strict_similarity = fuzz.token_sort_ratio(normalized_term, normalize(str(row['Resumo'])))
       
        # Calcula a similaridade com 'Palavras chaves' e 'Resumo' usando partial_ratio
        keywords_relaxed_similarity = fuzz.partial_ratio(normalized_term, normalize(str(row['Palavras chaves'])))
        summary_relaxed_similarity = fuzz.partial_ratio(normalized_term, normalize(str(row['Resumo'])))
       
        # Verifica se a similaridade atende ao limiar estrito ou ao limiar relaxado
        return (keywords_strict_similarity >= strict_threshold or summary_strict_similarity >= strict_threshold or
                keywords_relaxed_similarity >= relaxed_threshold or summary_relaxed_similarity >= relaxed_threshold)

    # Filtra o DataFrame usando a função de relevância
    results = df[df.apply(is_relevant, axis=1)]

    if not results.empty:
        return results[['Título do documento', 'Link Qualyteam', 'Resumo', 'Data elaboração']].to_dict('records')
    else:
        return []

# Função para inicializar o histórico de chat na sessão
def initialize_chat_history():
    # Inicializa o histórico de chat na sessão se ainda não estiver presente
    if 'chat_history' not in session:
        session['chat_history'] = [
            "🤖 Emabot: Olá, me chamo Emaboot da Diplan. Sou sua assistente de busca de documentos. Como posso ajudar? Digite uma palavra-chave ou uma frase."
        ]
    return session['chat_history']

# Rota principal
@app.route('/', methods=['GET', 'POST'])
def home():
    # Limpa o histórico da sessão em uma requisição GET (quando a página é recarregada)
    if request.method == 'GET':
        session.pop('chat_history', None)  # Limpa apenas o histórico de chat da sessão

    # Inicializa o histórico de chat na sessão
    chat_history = initialize_chat_history()

    if request.method == 'POST':
        user_input = request.form['user_input'].strip()

        if user_input:
            chat_history.append(f"{face_emoji}: {user_input}")
            results = search_in_spreadsheet(user_input)
            if results:
                chat_history.append("🤖 Emabot: Documentos encontrados:")
                for result in results:
                    chat_history.append(f"📄 <a href='/get_link?title={result['Título do documento']}'>{result['Título do documento']}</a>")
            else:
                chat_history.append("🤖 Emabot: Nenhum documento encontrado com o termo ou frase fornecida.")
        else:
            chat_history.append("🤖 Emabot: Por favor, insira uma palavra-chave ou frase para realizar a busca.")

        # Atualiza o histórico de chat na sessão
        session['chat_history'] = chat_history

    return render_template_string(template, chat_history=chat_history)

# Rota para obter o link do documento
@app.route('/get_link', methods=['GET'])
def get_link():
    title = request.args.get('title')
    result = df[df['Título do documento'] == title]
    chat_history = initialize_chat_history()
    if not result.empty:
        link = result['Link Qualyteam'].values[0] if pd.notna(result['Link Qualyteam'].values[0]) else "Link indisponível"
        resumo = result['Resumo'].values[0] if pd.notna(result['Resumo'].values[0]) else "Resumo não disponível"
        # Formata a data para o formato brasileiro dd/mm/yyyy
        data_atualizacao = result['Data elaboração'].values[0].strftime('%d/%m/%Y') if pd.notna(result['Data elaboração'].values[0]) else "Data não disponível"
        chat_history.append(f"🤖 Emabot: Aqui está o link para '{title}': <a href='{link}' target='_blank'>{link}</a>")
        chat_history.append(f"📅 Data de Atualização: {data_atualizacao}")  # Exibe como Data de Atualização
        chat_history.append(f"📄 Resumo: {resumo} <button onclick='speakText(`{resumo}`)'>🔊 Ouvir</button>")
    else:
        chat_history.append("🤖 Emabot: Link não encontrado para o título selecionado.")

    # Atualiza o histórico de chat na sessão
    session['chat_history'] = chat_history

    return render_template_string(template, chat_history=chat_history)

# Template HTML com a imagem de fundo, VLibras, Text-to-Speech, e Rolagem Automática adicionados
template = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emabot da Diplan</title>

    <!-- Script do VLibras -->
    <script src="https://vlibras.gov.br/app/vlibras-plugin.js"></script>
    <script>
        new window.VLibras.Widget('https://vlibras.gov.br/app');
    </script>

    <style>
        /* Estilos gerais */
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-image: url('/static/images/Imagem de fundo.png');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            color: white;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            box-sizing: border-box;
        }
        /* Container principal */
        .container {
            display: flex;
            max-width: 1200px;
            width: 100%;
            margin: 0 auto;
            padding: 20px;
            justify-content: flex-start;
            flex-direction: column;
            height: 100%;
            box-sizing: border-box;
        }
        /* Caixa de Chat - Versão Desktop */
        .chat-box {
            width: 100%;
            max-width: 600px;
            background-color: rgba(0, 0, 51, 0.8);
            padding: 20px;
            border-radius: 8px;
            box-sizing: border-box;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            align-self: flex-start;
            margin-top: 10%;
            height: auto;
            max-height: 70vh;
        }
        /* Estilos para histórico de chat */
        .chat-history {
            border: 1px solid #ccc;
            padding: 10px;
            height: auto;
            max-height: 200px;
            overflow-y: auto;
            margin-bottom: 10px;
            border-radius: 4px;
            background-color: rgba(255, 255, 255, 0.1);
            box-sizing: border-box;
        }
        /* Texto do histórico */
        .chat-history p {
            margin: 5px 0;
            color: white;
            word-wrap: break-word;
        }
        /* Campo de entrada e botão de envio */
        .user-input {
            display: flex;
            align-items: center;
            width: 100%;
            box-sizing: border-box;
        }
        .user-input input[type="text"] {
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 1em;
            color: black;
            box-sizing: border-box;
        }
        .user-input input[type="submit"] {
            padding: 10px 20px;
            margin-left: 10px;
            border: none;
            background-color: #3498db;
            color: #fff;
            border-radius: 4px;
            font-size: 1em;
            cursor: pointer;
            box-sizing: border-box;
        }
        .user-input input[type="submit"]:hover {
            background-color: #2980b9;
        }
        /* Estilos para links */
        a {
            color: white;
            text-decoration: underline;
        }
        a:hover {
            color: #ccc;
        }
        /* Estilos para o indicador de carregamento */
        #loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(255, 255, 255, 0.8);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            font-size: 1.5em;
            color: #333;
        }
        /* Animação de rotação */
        @keyframes spin {
            from {transform: rotate(0deg);}
            to {transform: rotate(360deg);}
        }
        .spinner {
            border: 8px solid #f3f3f3;
            border-top: 8px solid #3498db;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <!-- Inclui o Plugin do VLibras -->
    <div vw class="enabled">
        <div vw-access-button class="active"></div>
        <div vw-plugin-wrapper>
            <div class="vw-plugin-top-wrapper"></div>
        </div>
    </div>

    <div id="loading-overlay">
        <div class="spinner"></div>
        <div>Analisando...</div>
    </div>

    <div class="container">
        <div class="chat-box">
            <h1>Emabot da Diplan</h1>
            <div class="chat-history" id="chat-history">
                {% for message in chat_history %}
                    <p>{{ message | safe }}</p>
                {% endfor %}
            </div>
            <form method="post" action="/" onsubmit="showLoading()">
                <div class="user-input">
                    <input type="text" id="user_input" name="user_input" placeholder="Digite sua palavra-chave ou frase aqui...">
                    <input type="submit" value="Enviar">
                </div>
            </form>
        </div>
    </div>

    <script>
        function showLoading() {
            document.getElementById('loading-overlay').style.display = 'flex';
        }

        function speakText(text) {
            if ('speechSynthesis' in window) { 
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'pt-BR'; 
                speechSynthesis.speak(utterance);
            } else {
                alert("Seu navegador não suporta a API de síntese de fala.");
            }
        }

        window.onload = function() {
            var chatHistory = document.getElementById("chat-history");
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    app.run(debug=True)
