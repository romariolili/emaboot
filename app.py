# -*- coding: utf-8 -*-
"""emma.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15YsDsyz4O2f8ZRb0WDs_4iQUYaPpnzvj
"""
from flask import Flask, request, render_template_string, redirect, url_for
import pandas as pd
import os

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
face_emoji = "👤"

def search_in_spreadsheet(term):
    term = term.lower()  # Converte a entrada do usuário para minúsculas
    results = df[df['Palavras chaves'].str.contains(term, case=False, na=False)]
    if not results.empty:
        return results[['Título do documento', 'Link Qualyteam', 'Resumo']].to_dict('records')
    else:
        return []

@app.route('/', methods=['GET', 'POST'])
def home():
    # Inicializa o histórico de chat a cada nova sessão
    chat_history = ["🤖 Emabot: Olá, eu sou a Emabot da Diplan. Sua assistente de busca... Como posso ajudar? Fale comigo somente por palavras-chave. Exemplo: Processos.."]

    if request.method == 'POST':
        user_input = request.form['user_input'].strip().lower()  # Converte a entrada do usuário para minúsculas e remove espaços em branco
        
        # Substitui o texto do usuário pelo emoji de rosto humano
        user_message = f"{face_emoji}: {user_input}"
        chat_history.append(user_message)  # Adiciona a interação atual ao histórico
        
        results = search_in_spreadsheet(user_input)
        if results:
            chat_history.append("🤖 Emabot: Documentos encontrados:")
            for result in results:
                chat_history.append(f"📄 <a href='/get_link?title={result['Título do documento']}'> {result['Título do documento']}</a>")
        else:
            chat_history.append("🤖 Emabot: Nenhum documento encontrado com essas palavras-chave.")
        
    return render_template_string('''
        <div style="text-align:center;">
            <img src="{{ url_for('static', filename='images/DIPLAN.png') }}" alt="DIPLAN Logo" style="width: 200px;">
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
    ''', chat_history=chat_history)

@app.route('/get_link', methods=['GET'])
def get_link():
    # Inicializa o histórico de chat a cada nova sessão
    chat_history = ["🤖 Emabot: Olá, eu sou a Emabot da Diplan. Sua assistente de busca... Como posso ajudar? Fale comigo somente por palavras-chave. Exemplo: Processos.."]

    title = request.args.get('title')
    result = df[df['Título do documento'] == title]
    
    if not result.empty:
        link = result['Link Qualyteam'].values[0]
        resumo = result['Resumo'].values[0]  # Obtém o resumo
        chat_history.append(f"🤖 Emabot: Aqui está o link para '{title}': <a href='{link}' target='_blank'>{link}</a>")
        chat_history.append(f"📄 Resumo: {resumo}")
    else:
        chat_history.append("🤖 Emabot: Link ou resumo não encontrados para o título selecionado.")
    
    return render_template_string('''
        <div style="text-align:center;">
            <img src="{{ url_for('static', filename='images/DIPLAN.png') }}" alt="DIPLAN Logo" style="width: 200px;">
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
    ''', chat_history=chat_history)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))



