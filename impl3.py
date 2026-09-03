import unicodedata

def normalizar(texto: str) -> str:
    # Remove marcas diacríticas (acentos)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    # Converte para minúsculas
    return texto.lower()

# Funções auxiliares
def saudacao():
    return "Olá! Bem-vindo ao Drive Thru da Lanchonete.\nAqui estão nossas opções:\n" + listar_cardapio()

def listar_cardapio():
    menu = []
    for item, preco in CARDAPIO.items():
        menu.append(f"- {item.capitalize()} (R$ {preco:.2f})")
    return "\n".join(menu)

def adicionar_item(item: str, carrinho: list):
    if item in CARDAPIO:
        carrinho.append(item)
        return f"{item.capitalize()} adicionado ao seu pedido!"
    else:
        return "Esse item não está no cardápio."

def mostrar_total(carrinho: list):
    total = sum(CARDAPIO[item] for item in carrinho)
    itens = ", ".join([i.capitalize() for i in carrinho]) if carrinho else "nenhum item"
    carrinho.clear()  # Limpa o carrinho após mostrar o total
    return f"Seu pedido: {itens}\nTotal: R$ {total:.2f}\nObrigado pela preferência!"

def sair():
    return "Encerrando atendimento. Obrigado e volte sempre!"

# Cardápio da lanchonete
CARDAPIO = {
    "hamburguer": 15.00,
    "cheeseburguer": 18.00,
    "batata": 10.00,
    "refrigerante": 8.00,
    "milkshake": 12.00
}

# Intenções do chatbot
INTENTS = {
    "saudacao": {
        "keywords": ["oi", "ola", "olá", "eae", "menu", "cardapio"],
        "action": saudacao
    },
    "adicionar": {
        "keywords": list(CARDAPIO.keys()),
        "action": adicionar_item
    },
    "total": {
        "keywords": ["total", "valor", "conta", "pedido"],
        "action": mostrar_total
    },
    "sair": {
        "keywords": ["sair", "tchau", "ate mais"],
        "action": sair
    }
}

def detectar_intencoes(user: str, carrinho: list):
    respostas = []
    encerrar = False

    for nome, intent in INTENTS.items():
        if any(keyword in user for keyword in intent["keywords"]):
            if nome == "adicionar":
                for item in CARDAPIO.keys():
                    if item in user:
                        resposta = intent["action"](item, carrinho)
                        respostas.append(resposta)
            elif nome == "total":
                resposta = intent["action"](carrinho)
                respostas.append(resposta)
            else:
                resposta = intent["action"]()
                respostas.append(resposta)

            if intent["action"] == sair:
                encerrar = True

    return respostas, encerrar

def chatbot():
    print("Chat iniciado...")
    carrinho = []

    while True:
        user = normalizar(input("Você: "))
        respostas, encerrar = detectar_intencoes(user, carrinho)

        if not respostas:
            print("Bot: Não entendi... Digite 'cardapio' para ver opções ou o nome do lanche.")
        else:
            for r in respostas:
                print("Bot:", r)

        if encerrar:
            break

chatbot()
