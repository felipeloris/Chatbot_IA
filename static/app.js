const THEME_KEY = "foodflow_theme";

let cardapioData = {};

const IMAGENS_CARDAPIO = {
    hamburguer: "/static/images/hamburguer.svg",
    cheeseburguer: "/static/images/cheeseburguer.svg",
    batata: "/static/images/batata.svg",
    refrigerante: "/static/images/refrigerante.svg",
    milkshake: "/static/images/milkshake.svg"
};

// Sincronia de tema entre a página principal e o iframe
function sincronizarTemaComIframe() {
    const iframe = document.getElementById("chatIframe");
    const tema = document.body.getAttribute("data-theme") || "dark";
    
    iframe.onload = () => {
        try {
            iframe.contentWindow.localStorage.setItem(THEME_KEY, tema);
            iframe.contentWindow.document.body.setAttribute("data-theme", tema);
        } catch (e) {
            // iframe pode ter restrições de acesso
        }
    };
}

// Carrega o cardápio do backend ao iniciar
async function carregarCardapio() {
    try {
        const response = await fetch("http://127.0.0.1:8000/cardapio");
        if (!response.ok) throw new Error("Falha ao carregar cardápio");
        
        const data = await response.json();
        cardapioData = data.cardapio || {};
        
        renderizarCardapio();
    } catch (error) {
        console.error("Erro ao carregar cardápio:", error);
        document.getElementById("cardapioContainer").innerHTML = 
            '<div class="quick-item">Erro ao carregar cardápio</div>';
    }
}

// Renderiza os itens do cardápio na interface
function renderizarCardapio() {
    const container = document.getElementById("cardapioContainer");
    container.innerHTML = "";
    
    for (const [item, preco] of Object.entries(cardapioData)) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "quick-item";
        button.innerHTML = `
            <span class="quick-item-main">
                <img class="quick-item-image" src="${getImagemProduto(item)}" alt="" loading="lazy">
                <span class="quick-item-label">${item.charAt(0).toUpperCase() + item.slice(1)}</span>
            </span>
            <strong>R$ ${preco.toFixed(2)}</strong>
        `;
        button.addEventListener("click", () => {
            adicionarAoPedido(item, preco);
        });
        container.appendChild(button);
    }
}

function getImagemProduto(item) {
    return IMAGENS_CARDAPIO[item] || IMAGENS_CARDAPIO.hamburguer;
}

// Adiciona item ao pedido no chat (dentro do iframe)
function adicionarAoPedido(item, preco) {
    const iframe = document.getElementById("chatIframe");
    try {
        const input = iframe.contentDocument.getElementById("pergunta");
        const botao = iframe.contentDocument.getElementById("btnEnviar");
        
        input.value = item;
        input.focus();
        botao.click();
    } catch (e) {
        console.error("Erro ao interagir com iframe:", e);
    }
}

function aplicarTema(tema) {
    document.body.setAttribute("data-theme", tema);
    const botaoTema = document.getElementById("themeToggle");
    botaoTema.textContent = tema === "light" ? "Dia" : "Noite";
    localStorage.setItem(THEME_KEY, tema);
    
    // Tenta sincronizar tema com iframe
    sincronizarTemaComIframe();
}

function alternarTema() {
    const atual = document.body.getAttribute("data-theme") || "dark";
    aplicarTema(atual === "dark" ? "light" : "dark");
}

document.getElementById("themeToggle").addEventListener("click", alternarTema);

const temaSalvo = localStorage.getItem(THEME_KEY);
aplicarTema(temaSalvo === "light" ? "light" : "dark");

// Carrega o cardápio ao inicializar a página
carregarCardapio();

// Aguarda o iframe carregar antes de sincronizar tema
window.addEventListener("load", sincronizarTemaComIframe);

