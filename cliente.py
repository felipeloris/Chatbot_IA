import requests

url = "http://127.0.0.1:8000/chat"

print("Cliente iniciado (digite sair)")

while True:
    msg = input("Você: ")

    if msg.lower() == "sair":
        break

    dados = {
        "user_id": "1",
        "mensagem": msg
    }

    try:
        resposta = requests.post(url, json=dados)

        print("Status:", resposta.status_code)

        if resposta.status_code == 200:
            print("Bot:", resposta.json()["resposta"])
        else:
            print("Erro:", resposta.text)

    except Exception as e:
        print("Erro de conexão:", e)