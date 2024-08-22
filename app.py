# -*- coding: utf-8 -*-
"""emma.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15YsDsyz4O2f8ZRb0WDs_4iQUYaPpnzvj
"""
from flask import Flask, request, render_template_string, redirect, url_for
import pandas as pd
import os
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

app = Flask(__name__)

# Caminho do arquivo no servidor
file_path = 'teste 1.xlsx'

# Verifica se o arquivo existe
if os.path.exists(file_path):
    # Carregar a planilha Excel
    df = pd.read_excel(file_path)
else:
    df = pd.DataFrame(columns=["Palavras chaves", "Título do documento", "Link Qualyteam", "Resumo"])

# Emoji de rosto humano
face_emoji = "😊"

def initialize_chat_history():
    """Inicializa o histórico de chat com a saudação inicial."""
    return [
        "🤖 Emabot: Olá, me chamo Emaboot da Diplan. Sou sua assistente de busca de documentos. Como posso ajudar? Fale comigo somente por palavras-chave. Exemplo: Processos.."
    ]

def search_in_spreadsheet(term):
    # Extrai todas as palavras-chave da planilha
    keywords = df['Palavras chaves'].tolist()
    # Encontra a palavra mais semelhante à entrada do usuário
    best_match, similarity = process.extractOne(term, keywords, scorer=fuzz.token_sort_ratio)
    
    if similarity >= 70:  # Define um limite de similaridade
        # Filtra os documentos com base na palavra-chave mais semelhante encontrada
        results = df[df['Palavras chaves'].str.contains(best_match, case=False, na=False)]
        return results[['Título do documento', 'Link Qualyteam', 'Resumo']].to_dict('records')
    else:
        return []

@app.route('/', methods=['GET', 'POST'])
def home():
    # Inicializa o histórico de chat para cada nova sessão
    chat_history = initialize_chat_history()

    if request.method == 'POST':
        user_input = request.form['user_input'].strip()

        if user_input:  # Verifica se o input não está vazio
            if len(user_input.split()) > 1:  # Verifica se o usuário digitou mais de uma palavra
                chat_history.append(f"{face_emoji}: {user_input}")
                chat_history.append("🤖 Emabot: Só consigo realizar a busca por palavra-chave.")
            else:
                # Adiciona a entrada do usuário ao histórico
                chat_history.append(f"{face_emoji}: {user_input}")
                
                # Busca nos documentos
                results = search_in_spreadsheet(user_input)
                if results:
                    chat_history.append("🤖 Emabot: Documentos encontrados:")
                    for result in results:
                        chat_history.append(f"📄 <a href='/get_link?title={result['Título do documento']}'> {result['Título do documento']}</a>")
                else:
                    chat_history.append("🤖 Emabot: Nenhum documento encontrado com essas palavras-chave.")
        else:
            chat_history.append("🤖 Emabot: Por favor, insira uma palavra-chave para realizar a busca.")

    return render_template_string('''
        <div style="display: flex;">
            <div style="width: 70%;">
                <h1>Emabot da Diplan</h1>
                <div style="border:1px solid #ccc; padding:10px; margin-bottom:10px;">
                    {% for message in chat_history %}
                        <p>{{ message | safe }}</p>
                    {% endfor %}
                </div>
                <form method="post" action="/">
                    <label for="user_input">Digite sua mensagem:</label><br>
                    <input type="text" id="user_input" name="user_input" style="width:80%">
                    <input type="submit" value="Enviar">
                </form>
            </div>
            <div style="width: 30%; text-align: center;">
                <img src="/static/images/your_image_name.png" alt="Diplan Assistant" style="width: 100%;">
            </div>
        </div>
    ''', chat_history=chat_history)

@app.route('/get_link', methods=['GET'])
def get_link():
    # Inicializa o histórico de chat novamente ao acessar um link (reinicia a conversa)
    chat_history = initialize_chat_history()
    title = request.args.get('title')
    result = df[df['Título do documento'] == title]
    if not result.empty:
        link = result['Link Qualyteam'].values[0]
        resumo = result['Resumo'].values[0]
        chat_history.append(f"🤖 Emabot: Aqui está o link para '{title}': <a href='{link}' target='_blank'>{link}</a>")
        chat_history.append(f"📄 Resumo: {resumo}")
    else:
        chat_history.append("🤖 Emabot: Link não encontrado para o título selecionado.")
    
    # Redireciona de volta para a página principal para manter o fluxo de interação
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
