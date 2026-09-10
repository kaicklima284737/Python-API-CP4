// ------------------------------------------------------------------
// Estado global
// ------------------------------------------------------------------
let usuariosCache = [];
let produtosCache = [];
let historicoVisivel = false;

let produtoModalSelecionado = null;
let quantidadeModal = 1;

// Mapeamento preciso de imagens para e-commerce de supermercado (1 e 2)
const galeriaPorPalavraChave = {
  // 1. Carne - 2 imagens de carne moída crua
  carne: [
    "https://img.freepik.com/fotos-premium/imagens-de-carne-crua-imagens-de-carne-bovina-crua-imagens-de-carne-suina-crua-imagens-de-carne-processada-em-restaurantes_848048-6848.jpg?w=2000",
    "https://tse2.mm.bing.net/th/id/OIP.RzJI1P2yxR_u9Lx3RVV95wHaGC?r=0&rs=1&pid=ImgDetMain&o=7&rm=3"
  ],
  // 2. Arroz - 2 imagens de arroz cru
  arroz: [
    "https://th.bing.com/th/id/OIP.7Wyh8u8L8TjhSVdLnShj9AHaHa?w=214&h=214&c=7&r=0&o=7&dpr=2&pid=1.7&rm=3",
    "https://tse1.mm.bing.net/th/id/OIP.5ZJZJZJZJZJZJZJZJZJZJZJZJZJZJZJZ?r=0&rs=1&pid=ImgDetMain&o=7&rm=3"
  ],
  // 3. Feijão - 2 imagens de feijão cru
  feijao: [
    "https://carrefourbrfood.vtexassets.com/arquivos/ids/16593089/feijao-carioca-tipo-1-broto-legal-1-kg-1.jpg?v=637552304969170000",
    "https://carrefourbrfood.vtexassets.com/arquivos/ids/16593089/feijao-carioca-tipo-1-broto-legal-1-kg-1.jpg?v=637552304969170000"
  ],
  // 4. Papel Higiênico - 2 imagens de papel higiênico
  papel: [
    "https://images.unsplash.com/photo-1584556812952-905ffd0c611a?w=500&auto=format&fit=crop&q=80",
    "https://th.bing.com/th/id/OIP.r5mKN_-OWshTc9T6BRyhcgHaHa?w=204&h=204&c=7&r=0&o=7&dpr=2&pid=1.7&rm=3"
  ],
  // 5. Batata - 2 imagens de batatas cruas
  batata: [
    "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=500&auto=format&fit=crop&q=80",
    "https://tse1.explicit.bing.net/th/id/OIP.WLKplkBUUG9ebRzQKeXdRgHaE8?r=0&rs=1&pid=ImgDetMain&o=7&rm=3"
  ],
  // 6. Tomate - 2 imagens de tomates crus frescos
  tomate: [
    "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&auto=format&fit=crop&q=80",
    "https://tse3.mm.bing.net/th/id/OIP.whmPtXjX7WeuvpgiQMzJtgHaE7?r=0&rs=1&pid=ImgDetMain&o=7&rm=3"
  ],
  // 7. Manteiga - 2 imagens funcionais de manteiga
  manteiga: [
    "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=500&auto=format&fit=crop&q=80",
    "https://muffatosupermercados.vtexassets.com/arquivos/ids/337657-800-auto?v=638061914258370000&width=800&height=auto&aspect=true"
  ],
  // 8. Queijo - 2 imagens exclusivas de queijos
  queijo: [
    "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=500&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1618160702438-9b02ab6515c9?w=500&auto=format&fit=crop&q=80"
  ],
  // 9. Detergente - 2 imagens de detergente/sabão líquido
  detergente: [
    "https://tse1.mm.bing.net/th/id/OIP.AoSww3yvAQDoS4wtlZ1AoQHaHa?r=0&rs=1&pid=ImgDetMain&o=7&rm=3",
    "https://joripapel.com.br/cdn/shop/products/agifacil500ml.jpg?v=1595523460&width=1946"
  ],
  // 10. Sabão em pó - 2 imagens de sabão em pó / produtos para roupas
  sabao: [
    "https://tse3.mm.bing.net/th/id/OIP.K4ojqhgEALPI6eLAjpFxlQHaIP?r=0&rs=1&pid=ImgDetMain&o=7&rm=3",
    "https://tse4.mm.bing.net/th/id/OIP.H9h-GfCigbQ_CzYS6u8xdgHaHa?r=0&w=1000&h=1000&rs=1&pid=ImgDetMain&o=7&rm=3"
  ],
  // 11. Macarrão - 2 imagens de pacotes de macarrão seco cru
  macarrao: [
    "https://destro.fbitsstatic.net/img/p/macarrao-espaguetinho-9-com-ovos-renata-500g-77306/263860-1.jpg?w=1000&h=1000&v=202501031703&qs=ignore",
    "https://renata.com.br/images/produtos/134/renata-imagem-produtos-macarrao-renata-ovos-espaguetinho-9-embalagem-mini.png"
  ],
  // 12. Açúcar - 2 imagens de açúcar cristal/refinado
  acucar: [
    "https://tse3.mm.bing.net/th/id/OIP.sqBcnO3YxRNYRbfK7ZPu9wHaHa?r=0&rs=1&pid=ImgDetMain&o=7&rm=3",
    "https://www.syspanimagens.com.br/img/07891910000197.jpg"
  ],
  // 13. Molho de Tomate - 2 imagens de molho/extrato de tomate
  molho: [
    "https://tse1.mm.bing.net/th/id/OIP.bQ9opcnEIfKcfZ3VyeaE2AHaHa?r=0&rs=1&pid=ImgDetMain&o=7&rm=3",
    "https://receitadaboa.com.br/wp-content/uploads/2024/04/iStock-167229436.jpg"
  ],
  // 14. Óleo de Soja - 2 imagens funcionais de garrafas de óleo
  oleo: [
    "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1620706857399-e1b37c065db6?w=500&auto=format&fit=crop&q=80"
  ],
  // 15. Pão de Forma - 2 imagens de pão de forma ensacado / fatiado
  pao: [
    "https://images.unsplash.com/photo-1586444248902-2f64eddc13df?w=500&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&auto=format&fit=crop&q=80"
  ],
  // Itens secundários de suporte
  cafe: [
    "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=500&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1587734195503-904fca47e0e9?w=500&auto=format&fit=crop&q=80"
  ],
  leite: [
    "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=500&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=500&auto=format&fit=crop&q=80"
  ],
  ovo: [
    "https://images.unsplash.com/photo-1506976785307-8732e854ad03?w=500&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1516448620398-c5f44bf9f441?w=500&auto=format&fit=crop&q=80"
  ],
  banana: [
    "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=500&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1543218024-57a70143c369?w=500&auto=format&fit=crop&q=80"
  ],
  frango: [
    "https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=500&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=500&auto=format&fit=crop&q=80"
  ]
};

const imagemPadrao1 = "https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&auto=format&fit=crop&q=80";
const imagemPadrao2 = "https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=500&auto=format&fit=crop&q=80";

// Função para buscar as 2 imagens com base no nome do produto
function obterImagensProduto(produto) {
  if (!produto || !produto.nome) return [imagemPadrao1, imagemPadrao2];

  const nomeNormalizado = produto.nome
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");

  for (const chave in galeriaPorPalavraChave) {
    if (nomeNormalizado.includes(chave)) {
      return galeriaPorPalavraChave[chave];
    }
  }

  return [imagemPadrao1, imagemPadrao2];
}

// Utilitário de chamadas à API
async function api(path, options = {}) {
  const resposta = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const dados = await resposta.json().catch(() => null);
  if (!resposta.ok) {
    const detalhe = (dados && dados.detail) || "Erro inesperado na API";
    throw new Error(detalhe);
  }
  return dados;
}

function mostrarMensagem(elementoId, texto, tipo = "ok") {
  const el = document.getElementById(elementoId);
  if (!el) return;
  el.textContent = texto;
  el.className = `msg show ${tipo}`;
  setTimeout(() => el.classList.remove("show"), 4000);
}

function formatarPreco(valor) {
  return `R$ ${Number(valor).toFixed(2).replace(".", ",")}`;
}

function formatarData(iso) {
  if (!iso) return "-";
  return iso.replace("T", " ");
}

// Controle das Abas Navegação
document.querySelectorAll(".tab-btn").forEach((botao) => {
  botao.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach((s) => s.classList.remove("active"));
    botao.classList.add("active");
    document.getElementById(`tab-${botao.dataset.tab}`).classList.add("active");
  });
});

// USUÁRIOS
async function carregarUsuarios() {
  usuariosCache = await api("/usuarios");
  renderUsuarios();
  preencherSelectUsuarios();
}

function renderUsuarios() {
  const corpo = document.getElementById("tabela-usuarios");
  if (!corpo) return;
  corpo.innerHTML = "";

  if (usuariosCache.length === 0) {
    corpo.innerHTML = `<tr><td colspan="5" class="text-center text-muted">Nenhum usuário cadastrado ainda.</td></tr>`;
    return;
  }

  usuariosCache.forEach((usuario) => {
    const linha = document.createElement("tr");
    linha.dataset.id = usuario.id;
    linha.innerHTML = `
      <td>${usuario.id}</td>
      <td class="col-nome">${usuario.nome}</td>
      <td class="col-email">${usuario.email}</td>
      <td class="col-idade">${usuario.idade ?? "-"}</td>
      <td class="actions text-center">
        <button class="btn secondary small" data-acao="editar">Editar</button>
        <button class="btn danger small" data-acao="excluir">Excluir</button>
      </td>
    `;
    corpo.appendChild(linha);
  });
}

document.getElementById("form-usuario").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const nome = document.getElementById("usuario-nome").value.trim();
  const email = document.getElementById("usuario-email").value.trim();
  const idadeValor = document.getElementById("usuario-idade").value;
  const idade = idadeValor === "" ? null : Number(idadeValor);

  try {
    await api("/usuarios", {
      method: "POST",
      body: JSON.stringify({ nome, email, idade }),
    });
    evento.target.reset();
    mostrarMensagem("msg-usuarios", "Usuário cadastrado com sucesso.");
    await carregarUsuarios();
  } catch (erro) {
    mostrarMensagem("msg-usuarios", erro.message, "error");
  }
});

document.getElementById("tabela-usuarios").addEventListener("click", async (evento) => {
  const botao = evento.target.closest("button");
  if (!botao) return;

  const linha = botao.closest("tr");
  const usuarioId = Number(linha.dataset.id);
  const acao = botao.dataset.acao;

  if (acao === "excluir") {
    try {
      await api(`/usuarios/${usuarioId}`, { method: "DELETE" });
      mostrarMensagem("msg-usuarios", "Usuário excluído.");
      await carregarUsuarios();
    } catch (erro) {
      mostrarMensagem("msg-usuarios", erro.message, "error");
    }
  } else if (acao === "editar") {
    ativarEdicaoUsuario(linha);
  } else if (acao === "salvar-edicao") {
    await salvarEdicaoUsuario(linha, usuarioId);
  } else if (acao === "cancelar-edicao") {
    renderUsuarios();
  }
});

function ativarEdicaoUsuario(linha) {
  const nomeAtual = linha.querySelector(".col-nome").textContent;
  const emailAtual = linha.querySelector(".col-email").textContent;
  const idadeAtual = linha.querySelector(".col-idade").textContent;

  linha.querySelector(".col-nome").innerHTML = `<input class="shopee-input edit-nome" value="${nomeAtual}" />`;
  linha.querySelector(".col-email").innerHTML = `<input class="shopee-input edit-email" value="${emailAtual}" />`;
  linha.querySelector(".col-idade").innerHTML = `<input class="shopee-input qty-input edit-idade" type="number" min="0" value="${idadeAtual === "-" ? "" : idadeAtual}" />`;
  linha.querySelector(".actions").innerHTML = `
    <button class="btn primary small" data-acao="salvar-edicao">Salvar</button>
    <button class="btn secondary small" data-acao="cancelar-edicao">Cancelar</button>
  `;
}

async function salvarEdicaoUsuario(linha, usuarioId) {
  const nome = linha.querySelector(".edit-nome").value.trim();
  const email = linha.querySelector(".edit-email").value.trim();
  const idadeValor = linha.querySelector(".edit-idade").value;
  const idade = idadeValor === "" ? null : Number(idadeValor);

  try {
    await api(`/usuarios/${usuarioId}`, {
      method: "PUT",
      body: JSON.stringify({ nome, email, idade }),
    });
    mostrarMensagem("msg-usuarios", "Usuário atualizado.");
    await carregarUsuarios();
  } catch (erro) {
    mostrarMensagem("msg-usuarios", erro.message, "error");
  }
}

// PRODUTOS
async function carregarProdutos() {
  produtosCache = await api("/produtos");
  renderGridProdutos();
  preencherSelectProdutos();
}

function renderGridProdutos() {
  const grid = document.getElementById("grid-produtos");
  if (!grid) return;
  grid.innerHTML = "";

  produtosCache.forEach((produto) => {
    const imgs = obterImagensProduto(produto);
    const card = document.createElement("div");
    card.className = "product-card";
    card.onclick = () => abrirModalProduto(produto);

    card.innerHTML = `
      <div class="product-badge">OFERTA</div>
      <img src="${imgs[0]}" alt="${produto.nome}" class="product-img">
      <div class="product-info">
        <div class="product-title">${produto.nome}</div>
        <div class="product-category">${produto.categoria ?? "Geral"}</div>
        <div class="product-price">${formatarPreco(produto.preco)}</div>
      </div>
    `;
    grid.appendChild(card);
  });
}

function preencherSelectProdutos() {
  const select = document.getElementById("select-produto");
  if (!select) return;
  select.innerHTML = produtosCache
    .map((produto) => `<option value="${produto.id}">${produto.nome} — ${formatarPreco(produto.preco)}</option>`)
    .join("");
}

// MODAL DE SELEÇÃO
function abrirModalProduto(produto) {
  produtoModalSelecionado = produto;
  quantidadeModal = 1;

  const imgs = obterImagensProduto(produto);
  document.getElementById("modal-img-1").src = imgs[0];
  document.getElementById("modal-img-2").src = imgs[1];
  document.getElementById("modal-nome").textContent = produto.nome;
  document.getElementById("modal-categoria").textContent = produto.categoria ?? "Geral";
  document.getElementById("modal-descricao").textContent = `Item do setor de ${produto.categoria ?? "Geral"}: ${produto.nome}. Embalagem padrão de mercado.`;

  atualizarValoresModal();
  document.getElementById("modal-produto").classList.add("active");
}

function fecharModalProduto() {
  document.getElementById("modal-produto").classList.remove("active");
}

function alterarQtdModal(delta) {
  if (quantidadeModal + delta >= 1) {
    quantidadeModal += delta;
    atualizarValoresModal();
  }
}

function atualizarValoresModal() {
  document.getElementById("modal-qtd").textContent = quantidadeModal;
  const precoTotal = produtoModalSelecionado.preco * quantidadeModal;
  document.getElementById("modal-preco-total").textContent = formatarPreco(precoTotal);
}

// Adiciona o produto exibido no modal diretamente para o Usuário Selecionado no momento
async function adicionarAoCarrinhoPeloModal() {
  const usuarioId = usuarioSelecionadoId();

  if (!usuarioId) {
    alert("Nenhum usuário selecionado! Selecione ou cadastre uma conta na aba 'Meu Carrinho'.");
    fecharModalProduto();
    return;
  }

  try {
    await api("/pedidos", {
      method: "POST",
      body: JSON.stringify({
        usuario_id: usuarioId,
        produto_id: produtoModalSelecionado.id,
        quantidade: quantidadeModal,
      }),
    });

    const usuarioAtual = usuariosCache.find((u) => u.id === usuarioId);
    const nomeUsuario = usuarioAtual ? usuarioAtual.nome : `Usuário ${usuarioId}`;

    alert(`✅ ${quantidadeModal}x "${produtoModalSelecionado.nome}" adicionado(s) ao carrinho de ${nomeUsuario}!`);
    fecharModalProduto();

    // Atualiza a tabela do carrinho
    await carregarItensDoUsuarioSelecionado();
    if (historicoVisivel) await carregarHistorico();
  } catch (erro) {
    alert(`Erro ao adicionar item ao carrinho: ${erro.message}`);
  }
}

// CARRINHO E PEDIDOS
function preencherSelectUsuarios() {
  const select = document.getElementById("select-usuario");
  if (!select) return;

  const usuarioSalvo = localStorage.getItem("usuario_ativo_id");

  select.innerHTML = usuariosCache
    .map((usuario) => `<option value="${usuario.id}">${usuario.nome}</option>`)
    .join("");

  if (usuariosCache.length === 0) {
    select.innerHTML = `<option value="">Cadastre um usuário primeiro</option>`;
  } else if (usuarioSalvo && usuariosCache.some((u) => u.id == usuarioSalvo)) {
    select.value = usuarioSalvo;
  }

  carregarItensDoUsuarioSelecionado();
}

document.getElementById("select-usuario").addEventListener("change", (e) => {
  const usuarioId = e.target.value;
  if (usuarioId) {
    localStorage.setItem("usuario_ativo_id", usuarioId);
  }

  historicoVisivel = false;
  document.getElementById("bloco-historico").style.display = "none";
  document.getElementById("btn-toggle-historico").textContent = "Histórico de Pedidos";
  carregarItensDoUsuarioSelecionado();
});

function usuarioSelecionadoId() {
  const select = document.getElementById("select-usuario");
  if (!select) return null;
  const valor = select.value;
  return valor ? Number(valor) : null;
}

async function carregarItensDoUsuarioSelecionado() {
  const usuarioId = usuarioSelecionadoId();
  const corpo = document.getElementById("tabela-itens");
  if (!corpo) return;

  if (!usuarioId) {
    corpo.innerHTML = `<tr><td colspan="6" class="text-center text-muted">Selecione um usuário ativo para visualizar seu carrinho.</td></tr>`;
    return;
  }

  try {
    const itens = await api(`/pedidos/usuario/${usuarioId}`);
    renderItens(itens);
  } catch (erro) {
    mostrarMensagem("msg-lista", erro.message, "error");
  }
}

function renderItens(itens) {
  const corpo = document.getElementById("tabela-itens");
  if (!corpo) return;
  corpo.innerHTML = "";

  if (itens.length === 0) {
    corpo.innerHTML = `<tr><td colspan="6" class="text-center text-muted">O carrinho deste usuário está vazio.</td></tr>`;
    return;
  }

  itens.forEach((item) => {
    const linha = document.createElement("tr");
    linha.dataset.id = item.pedido_id;
    linha.innerHTML = `
      <td><strong>${item.produto_nome}</strong></td>
      <td>${item.produto_categoria ?? "-"}</td>
      <td class="color-primary">${formatarPreco(item.produto_preco)}</td>
      <td>
        <input class="shopee-input qty-input edit-qty" type="number" min="1" value="${item.quantidade}" />
      </td>
      <td>${formatarData(item.atualizado_em)}</td>
      <td class="actions text-center">
        <button class="btn primary small" data-acao="salvar-qtd">Salvar</button>
        <button class="btn danger small" data-acao="remover-item">Remover</button>
      </td>
    `;
    corpo.appendChild(linha);
  });
}

document.getElementById("form-item").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const usuarioId = usuarioSelecionadoId();
  const produtoId = Number(document.getElementById("select-produto").value);
  const quantidade = Number(document.getElementById("item-quantidade").value);

  if (!usuarioId) {
    mostrarMensagem("msg-lista", "Selecione um usuário antes de adicionar itens.", "error");
    return;
  }

  try {
    await api("/pedidos", {
      method: "POST",
      body: JSON.stringify({ usuario_id: usuarioId, produto_id: produtoId, quantidade }),
    });
    mostrarMensagem("msg-lista", "Item adicionado ao carrinho!");
    document.getElementById("item-quantidade").value = 1;
    await carregarItensDoUsuarioSelecionado();
    if (historicoVisivel) await carregarHistorico();
  } catch (erro) {
    mostrarMensagem("msg-lista", erro.message, "error");
  }
});

document.getElementById("tabela-itens").addEventListener("click", async (evento) => {
  const botao = evento.target.closest("button");
  if (!botao) return;

  const linha = botao.closest("tr");
  const pedidoId = Number(linha.dataset.id);
  const acao = botao.dataset.acao;

  if (acao === "remover-item") {
    try {
      await api(`/pedidos/${pedidoId}`, { method: "DELETE" });
      mostrarMensagem("msg-lista", "Item removido do carrinho.");
      await carregarItensDoUsuarioSelecionado();
      if (historicoVisivel) await carregarHistorico();
    } catch (erro) {
      mostrarMensagem("msg-lista", erro.message, "error");
    }
  } else if (acao === "salvar-qtd") {
    const quantidade = Number(linha.querySelector(".edit-qty").value);
    try {
      await api(`/pedidos/${pedidoId}`, {
        method: "PUT",
        body: JSON.stringify({ quantidade }),
      });
      mostrarMensagem("msg-lista", "Quantidade atualizada.");
      await carregarItensDoUsuarioSelecionado();
      if (historicoVisivel) await carregarHistorico();
    } catch (erro) {
      mostrarMensagem("msg-lista", erro.message, "error");
    }
  }
});

document.getElementById("btn-toggle-historico").addEventListener("click", async () => {
  historicoVisivel = !historicoVisivel;
  const bloco = document.getElementById("bloco-historico");
  const botao = document.getElementById("btn-toggle-historico");

  if (historicoVisivel) {
    bloco.style.display = "block";
    botao.textContent = "Ocultar Histórico";
    await carregarHistorico();
  } else {
    bloco.style.display = "none";
    botao.textContent = "Histórico de Pedidos";
  }
});

async function carregarHistorico() {
  const usuarioId = usuarioSelecionadoId();
  if (!usuarioId) return;

  try {
    const historico = await api(`/pedidos/usuario/${usuarioId}/historico`);
    renderHistorico(historico);
  } catch (erro) {
    mostrarMensagem("msg-lista", erro.message, "error");
  }
}

function renderHistorico(historico) {
  const corpo = document.getElementById("tabela-historico");
  if (!corpo) return;
  corpo.innerHTML = "";

  if (historico.length === 0) {
    corpo.innerHTML = `<tr><td colspan="4" class="text-center text-muted">Nenhuma alteração registrada.</td></tr>`;
    return;
  }

  const rotulos = { adicionado: "ok", atualizado: "", removido: "off" };

  historico.forEach((registro) => {
    const linha = document.createElement("tr");
    const classeTag = rotulos[registro.acao] ? `tag ${rotulos[registro.acao]}` : "tag";
    linha.innerHTML = `
      <td>${formatarData(registro.data_hora)}</td>
      <td><span class="${classeTag}">${registro.acao}</span></td>
      <td>${registro.produto_nome}</td>
      <td>${registro.quantidade ?? "-"}</td>
    `;
    corpo.appendChild(linha);
  });
}

// Inicialização
(async function iniciar() {
  await carregarProdutos();
  await carregarUsuarios();
})();