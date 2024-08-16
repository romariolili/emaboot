# -*- coding: utf-8 -*-
"""emma.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15YsDsyz4O2f8ZRb0WDs_4iQUYaPpnzvj
"""

from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import os

app = Flask(__name__)

# Carregar a planilha Excel
file_path = 'teste 1.xlsx'
df = pd.read_excel(file_path)

def search_in_spreadsheet(term):
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

# Rota para servir a página HTML
@app.route('/')
def home():
    return render_template_string(open('index.html').read())

@app.route('/chatbot', methods=['POST'])
def chatbot_interaction():
    user_input = request.json.get("input")
    
    if user_input.lower() in ["sair", "exit", "quit"]:
        return jsonify({"response": "🤖 Emaboot: Até logo!"})
    
    term = user_input
    results = search_in_spreadsheet(term)
    
    if results:
        response = "🤖 Emaboot: Documentos encontrados:\n"
        for i, title in enumerate(results, 1):
            response += f"{i}. {title}\n"
        return jsonify({"response": response, "results": results})
    else:
        return jsonify({"response": "🤖 Emaboot: Nenhum documento encontrado com essas palavras-chave."})

@app.route('/get_link', methods=['POST'])
def get_link():
    title = request.json.get("title")
    link = get_link_by_title(title)
    
    if link:
        return jsonify({"response": f"🤖 Emaboot: Aqui está o link para '{title}': {link}"})
    else:
        return jsonify({"response": "🤖 Emaboot: Link não encontrado para o título selecionado."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
