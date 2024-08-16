# -*- coding: utf-8 -*-
"""emma.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15YsDsyz4O2f8ZRb0WDs_4iQUYaPpnzvj
"""
import os
from flask import Flask, request, jsonify, render_template_string
import pandas as pd

app = Flask(__name__)

# Caminho do arquivo Excel
file_path = 'teste 1.xlsx'

# Carregar a planilha Excel
df = pd.read_excel(file_path)

def search_in_spreadsheet(term):
    if not isinstance(term, str) or not term:
        return []
    results = df[df['Palavras chaves'].str.contains(term, case=False, na=False)]
    if not results.empty:
        return results['Título do documento'].tolist()
    else:
        return []

def get_link_by_title(title):
    result = df[df['Título do documento'] == title]
    if not result.empty:
        return result['Link Qualyteam'].values[0]
    else:
        return None

@app.route('/')
def home():
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Emaboot Chatbot</title>
    </head>
    <body>
        <h1>Emaboot Chatbot</h1>
        <form action="/chatbot" method="post">
            <label for="input">Digite o termo de busca:</label><br><br>
            <input type="text" id="input" name="input"><br><br>
            <input type="submit" value="Enviar">
        </form>
        {% if response %}
            <p>{{ response | safe }}</p>
        {% endif %}
    </body>
    </html>
    '''
    return render_template_string(html_content)

@app.route('/chatbot', methods=['POST'])
def chatbot_interaction():
    user_input = request.form.get("input", "")
    
    term = user_input.strip()
    results = search_in_spreadsheet(term)
    
    if results:
        response = "🤖 Emaboot: Documentos encontrados:<br>"
        for i, title in enumerate(results, 1):
            response += f"{i}. {title}<br>"
        return render_template_string(open('index.html').read(), response=response)
    else:
        return render_template_string(open('index.html').read(), response="🤖 Emaboot: Nenhum documento encontrado com essas palavras-chave.")

@app.route('/get_link', methods=['POST'])
def get_link():
    title = request.form.get("title", "")
    link = get_link_by_title(title)
    
    if link:
        return jsonify({"response": f"🤖 Emaboot: Aqui está o link para '{title}': {link}"})
    else:
        return jsonify({"response": "🤖 Emaboot: Link não encontrado para o título selecionado."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
