# FoodFlow Delivery

API de chatbot para uma lanchonete, criada com FastAPI. O atendimento reconhece itens do cardapio, monta um carrinho simples e pode consultar a OpenAI para perguntas que nao correspondem as intencoes locais.

## Requisitos

- Python 3.10 ou superior
- Uma chave de API da OpenAI, caso queira usar as respostas por IA

## Instalacao

No terminal, na pasta do projeto, instale as dependencias:

```powershell
python -m pip install -r requirements.txt
```

Crie ou edite o arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sua_chave_da_openai_aqui
```

O arquivo `.env` esta listado no `.gitignore` e nao deve ser enviado ao GitHub.

## Executar

Inicie a API com recarregamento automatico:

```powershell
python -m uvicorn main:app --reload
```

A aplicacao ficara disponivel em `http://127.0.0.1:8000`.

- Interface web: `http://127.0.0.1:8000/`
- Documentacao da API: `http://127.0.0.1:8000/docs`

## Depurar no VS Code

O projeto inclui a configuracao `.vscode/launch.json` chamada **Debug FastAPI**.

1. Abra a aba **Executar e Depurar** no VS Code.
2. Selecione **Debug FastAPI**.
3. Pressione `F5`.
4. Adicione breakpoints em `main.py` e envie uma requisicao para a API ou use a interface web.

Essa configuracao executa o equivalente a:

```powershell
python -m uvicorn main:app --reload
```

## Possiveis erros

### Porta ocupada

Se aparecer um erro indicando que a porta ja esta em uso, execute em outra porta:

```powershell
python -m uvicorn main:app --reload --port 8001
```

Nesse caso, abra `http://127.0.0.1:8001` no navegador. Para usar a outra porta no debug, adicione `"--port", "8001"` aos `args` de **Debug FastAPI** no arquivo `.vscode/launch.json`.

### API nao rodando ou erro de conexao

A interface exibira erro de conexao quando o servidor FastAPI nao estiver ativo ou estiver em outra porta. Inicie a API e confirme no terminal uma mensagem semelhante a `Uvicorn running on http://127.0.0.1:8000`.

### JSONDecodeError

Esse erro normalmente indica que a API falhou e retornou uma resposta que nao e JSON. Verifique o terminal onde o Uvicorn esta rodando: o traceback exibido ali aponta a causa original da falha.

### Erro de certificado SSL em rede corporativa

Em redes empresariais, um certificado corporativo ou proxy pode impedir a conexao com a OpenAI. O projeto usa `truststore` para aproveitar os certificados confiaveis do Windows. Se o erro persistir, solicite ao time de TI que instale ou disponibilize o certificado raiz corporativo para o Python ou permita o acesso a `api.openai.com`.
