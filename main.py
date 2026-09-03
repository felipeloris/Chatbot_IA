import os
import ssl
import unicodedata
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
from openai import APIConnectionError, AuthenticationError, RateLimitError, APIStatusError
from dotenv import load_dotenv
import httpx
import truststore

load_dotenv()

#  inicia API
app = FastAPI()

#  caminhos de arquivos locais
BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"
STATIC_DIR = BASE_DIR / "static"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Garante que a pasta static exista antes de montar os arquivos estaticos.
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

#  Cardápio da lanchonete
CARDAPIO = {
    "hamburguer": 15.00,
    "cheeseburguer": 18.00,
    "batata": 10.00,
    "refrigerante": 8.00,
    "milkshake": 12.00
}

#  carrinho de compras (sessão única por simplicidade)
carrinho_global = []

#  cliente OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()


def criar_client_openai():
    if not OPENAI_API_KEY:
        return None

    ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    http_client = httpx.Client(verify=ssl_context, timeout=30.0)

    return OpenAI(api_key=OPENAI_API_KEY, http_client=http_client)


client = criar_client_openai()

mensagens = [
    {
        "role": "system",
        "content": (
            "Você é um atendente de delivery direto e útil. "
            "Ajude o usuário com dúvidas, sugestões e equivalências de itens do cardápio. "
            f"Cardápio disponível: {', '.join(f'{item} (R$ {preco:.2f})' for item, preco in CARDAPIO.items())}. "
            "Se o item pedido não existir exatamente, sugira os itens mais próximos do cardápio. "
            "Responda de forma curta e em português do Brasil."
        )
    }
]

#  funções do chatbot de delivery
def normalizar(texto: str) -> str:
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto.lower()

def saudacao():
    return "Olá! Bem-vindo ao FoodFlow Delivery.\nAqui estão nossas opções:\n" + listar_cardapio()

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
    carrinho.clear()
    return f"Seu pedido: {itens}\nTotal: R$ {total:.2f}\nObrigado pela preferência!"

def sair():
    return "Encerrando atendimento. Obrigado e volte sempre!"

#  Intenções do chatbot
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

#  modelo da requisição
class ChatRequest(BaseModel):
    pergunta: str


@app.get("/", include_in_schema=False)
def index_root():
    if not INDEX_FILE.exists():
        raise HTTPException(status_code=404, detail="Arquivo index.html nao encontrado.")
    return FileResponse(INDEX_FILE)


@app.get("/index.html", include_in_schema=False)
def index_file():
    if not INDEX_FILE.exists():
        raise HTTPException(status_code=404, detail="Arquivo index.html nao encontrado.")
    return FileResponse(INDEX_FILE)


@app.get("/cardapio")
def get_cardapio():
    return {"cardapio": CARDAPIO}


@app.post("/chat")
def chat(req: ChatRequest):
    global carrinho_global, mensagens

    pergunta = normalizar(req.pergunta.strip())

    if not pergunta:
        return {"resposta": "Digite algo."}

    try:
        respostas, encerrar = detectar_intencoes(pergunta, carrinho_global)

        if not respostas:
            if client is None:
                resposta_texto = "Não entendi... Digite 'cardapio' para ver opções ou o nome do lanche."
            else:
                mensagens.append({"role": "user", "content": req.pergunta.strip()})

                resposta = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=mensagens,
                    temperature=0.3,
                    frequency_penalty=0.4,
                    presence_penalty=0.2
                )

                resposta_texto = resposta.choices[0].message.content
                mensagens.append({"role": "assistant", "content": resposta_texto})

                if len(mensagens) > 10:
                    mensagens = [mensagens[0]] + mensagens[-9:]
        else:
            resposta_texto = "\n".join(respostas)

    except AuthenticationError:
        resposta_texto = "Falha de autenticação na OpenAI (chave inválida ou expirada)."
    except RateLimitError:
        resposta_texto = "Limite de requisições/créditos atingido na OpenAI."
    except APIConnectionError as e:
        causa = str(e)
        if "CERTIFICATE_VERIFY_FAILED" in causa or "certificate verify failed" in causa:
            resposta_texto = "Falha SSL: certificado da rede não confiável. Configure o certificado corporativo no Python."
        else:
            resposta_texto = "Falha de conexão com a OpenAI (rede/timeout)."
    except APIStatusError as e:
        resposta_texto = f"Erro da OpenAI: status {e.status_code}."
    except Exception as e:
        resposta_texto = f"Erro ao processar pedido: {str(e)}"

    return {"resposta": resposta_texto}