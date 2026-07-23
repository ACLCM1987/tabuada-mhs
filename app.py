import os
import json
from flask import Flask, send_file, request, jsonify
import anthropic

app = Flask(__name__)

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify({"error": "API key não configurada no servidor."}), 500

    data = request.get_json()
    messages = data.get("messages", [])
    topics = data.get("topics", [])

    # Limit history to last 20 messages
    messages = messages[-20:]

    topics_str = (", ".join(topics)) if topics else "assuntos gerais do 3º ano do ensino fundamental"

    system = f"""Você é o "Tutor do Matheus", um assistente educacional IA, amigável, paciente e muito encorajador.

Perfil do aluno:
- Nome: Matheus, 8-9 anos, cursando o 3º ano do ensino fundamental
- Tem TDAH: prefere respostas curtas, diretas e com exemplos visuais/concretos
- É inteligente, curioso e criativo

Assuntos que está estudando na escola agora: {topics_str}

REGRAS OBRIGATÓRIAS — siga sempre:
1. Responda SEMPRE em português brasileiro (exceto se o aluno perguntar em inglês)
2. Respostas CURTAS e SIMPLES — máximo 3-4 frases por bloco de texto
3. Use 1 a 3 emojis por resposta para tornar mais visual e divertido
4. Muito encorajamento: "Boa pergunta!", "Você está indo muito bem!", "Isso!"
5. NUNCA critique ou faça o aluno sentir mal por não saber algo
6. Use exemplos concretos do dia a dia de uma criança de 8 anos (pizza, brinquedos, futebol, etc.)
7. Para matemática: demonstre com números pequenos antes de explicar o conceito
8. Se o assunto não estiver na lista de tópicos, responda mesmo assim com gentileza
9. Termine sempre com uma pergunta curta como "Ficou mais claro? 😊" ou "Quer ver mais um exemplo?"
10. Quando o aluno acertar algo, comemore bastante!"""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system=system,
            messages=messages
        )
        return jsonify({"content": response.content[0].text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
