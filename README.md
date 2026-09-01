# API de Usuários & Lista de Compras

API em Python com FastAPI para cadastro de usuários, catálogo de produtos e
lista de compras individual por usuário, persistidos em um banco de dados
relacional **SQLite**. Inclui também uma landing page simples (HTML/CSS/JS)
para testar todas as funcionalidades sem precisar do Swagger.

## 1. Tecnologias utilizadas

| Tecnologia | Papel no projeto |
|---|---|
| **Python 3** | Linguagem principal do backend. |
| **FastAPI** | Framework web usado para criar as rotas/endpoints da API. |
| **Uvicorn** | Servidor ASGI que executa a aplicação FastAPI. |
| **SQLite (`sqlite3`, biblioteca padrão do Python)** | Banco de dados relacional usado para persistir usuários, produtos, pedidos e histórico. Não exige instalação de servidor: os dados ficam em um único arquivo (`database.db`), criado automaticamente na primeira execução. |
| **HTML + CSS + JavaScript puro** | Landing page servida pela própria API (pasta `static/`), que consome os endpoints via `fetch`. Não usa nenhum framework de frontend. |

O projeto continua **sem orientação a objetos**: os dados trafegam como
dicionários/listas (JSON), e o SQLite substitui o antigo arquivo
`usuarios.json` como forma de persistência.

## 2. Requisitos de instalação

- Python 3.10 ou superior instalado.
- Não é necessário instalar nenhum banco de dados separadamente: o SQLite já
  vem embutido no Python.

Passo a passo (Windows, Linux ou macOS):

```bash
# 1. Crie o ambiente virtual
python -m venv .venv
```

Ativar o ambiente virtual:

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

```bash
# 2. Instale as dependências
pip install -r requirements.txt

# 3. Suba o servidor
uvicorn main:app --reload
```

A aplicação estará disponível em:

```text
http://localhost:8000
```

- **Landing page** (interface visual): `http://localhost:8000`
- **Swagger** (documentação interativa da API): `http://localhost:8000/docs`

Na primeira execução, o arquivo `database.db` é criado automaticamente na
raiz do projeto, com as tabelas já criadas e o catálogo de produtos
pré-cadastrado (20 itens).

## 3. Como o projeto funciona

### Estrutura de pastas

```text
api_usuarios/
├── main.py                 # cria a aplicação, inicializa o banco e registra as rotas
├── database.py              # conexão SQLite, criação das tabelas e seed de produtos
├── controller_usuarios.py   # rotas HTTP de usuários
├── controller_produtos.py   # rotas HTTP de produtos
├── controller_pedidos.py    # rotas HTTP da lista de compras (pedidos)
├── service_usuarios.py      # regras de negócio + acesso ao banco (usuários)
├── service_produtos.py      # regras de negócio + acesso ao banco (produtos)
├── service_pedidos.py       # regras de negócio + acesso ao banco (lista de compras)
├── static/
│   ├── index.html            # landing page
│   ├── style.css              # estilos da landing page
│   └── app.js                  # lógica da landing page (chamadas fetch para a API)
├── database.db               # criado automaticamente na 1ª execução (não versionar)
├── requirements.txt
└── README.md
```

### Camadas da aplicação

- **`main.py`**: ponto de entrada. Cria a instância do FastAPI, chama
  `inicializar_banco()` para garantir que as tabelas existam, registra os
  três roteadores (`usuarios`, `produtos`, `pedidos`) e serve a pasta
  `static/` como landing page.
- **`controller_*.py`**: concentram as rotas HTTP (equivalente ao antigo
  `controller.py`, agora dividido por assunto). Validam o formato básico da
  entrada e traduzem os retornos dos serviços em respostas HTTP (200, 404,
  400, etc.).
- **`service_*.py`**: concentram a lógica de negócio e o acesso ao banco
  (equivalente ao antigo `service.py`, agora dividido por assunto).
- **`database.py`**: abre conexões com o SQLite e define o schema das 4
  tabelas (`usuarios`, `produtos`, `pedidos`, `pedidos_historico`).

### Modelo de dados (SQLite)

- **usuarios**: `id, nome, email, idade`
- **produtos**: `id, nome, categoria, preco` — catálogo fixo, cadastrado uma
  única vez (seed) e compartilhado por todos os usuários.
- **pedidos**: representa a lista de compras atual de cada usuário. Cada
  linha é um produto + quantidade associados a um `usuario_id`, com um
  `status` (`ativo` ou `removido`). Remover um item da lista não apaga a
  linha do banco — apenas marca `status = 'removido'` (soft delete), para
  preservar o registro.
- **pedidos_historico**: toda ação sobre um item da lista (adicionar,
  atualizar quantidade, remover) gera uma linha aqui, com data/hora. Serve
  como auditoria/registro completo, mesmo depois que um item já foi
  removido da lista atual.

## 4. Funcionalidades

### Usuários (`/usuarios`)

- `POST /usuarios` — cadastra um novo usuário (`nome`, `email`, `idade`).
- `GET /usuarios` — lista todos os usuários.
- `GET /usuarios/{id}` — busca um usuário específico.
- `PUT /usuarios/{id}` — edita os dados de um usuário.
- `DELETE /usuarios/{id}` — exclui um usuário (os itens da lista de compras
  desse usuário também são removidos em cascata; o histórico é preservado).

### Produtos (`/produtos`)

- `GET /produtos` — lista o catálogo de produtos disponíveis (20 itens
  pré-cadastrados, cobrindo mercearia, hortifruti, laticínios, carnes,
  limpeza e higiene). Pode ser consultado a qualquer momento por qualquer
  usuário, sem precisar recadastrar nada.
- `GET /produtos/{id}` — busca um produto específico.

### Lista de compras / Pedidos (`/pedidos`)

- `POST /pedidos` — adiciona um produto (do catálogo) à lista de compras de
  um usuário, com uma quantidade. Se o mesmo produto já estiver ativo na
  lista, a quantidade é somada em vez de duplicar o item.
- `GET /pedidos/usuario/{usuario_id}` — lista os itens ativos na lista de
  compras de um usuário (use `?incluir_removidos=true` para ver também os
  itens já removidos).
- `PUT /pedidos/{pedido_id}` — atualiza a quantidade de um item da lista.
- `DELETE /pedidos/{pedido_id}` — remove um item da lista (soft delete,
  mantendo o histórico).
- `GET /pedidos/usuario/{usuario_id}/historico` — retorna o histórico
  completo de alterações da lista de compras de um usuário (o que foi
  adicionado, atualizado ou removido, e quando).

### Landing page (`/`)

Interface web simples com três abas:

1. **Usuários** — formulário de cadastro e tabela com edição/exclusão
   inline.
2. **Produtos** — tabela somente leitura com o catálogo disponível.
3. **Lista de Compras** — seleção de um usuário, formulário para adicionar
   produtos do catálogo à lista dele (com quantidade), tabela dos itens
   atuais (com edição de quantidade e remoção) e um botão para exibir o
   histórico de alterações daquele usuário.

Todas as ações da página usam a própria API (`fetch`) e refletem
imediatamente qualquer alteração feita — não há necessidade de recarregar a
página.
