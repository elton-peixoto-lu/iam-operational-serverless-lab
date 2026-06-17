const state = {
  data: null,
};

const els = {
  title: document.getElementById("title"),
  subtitle: document.getElementById("subtitle"),
  roleMode: document.getElementById("role-mode"),
  architectureCanvas: document.getElementById("architecture-canvas"),
  connectorLayer: document.getElementById("connector-layer"),
  groupLayer: document.getElementById("group-layer"),
  nodeLayer: document.getElementById("node-layer"),
  deploymentInfo: document.getElementById("deployment-info"),
  notesList: document.getElementById("notes-list"),
  iconsList: document.getElementById("icons-list"),
  refreshButton: document.getElementById("refresh-button"),
  cardTemplate: document.getElementById("service-card-template"),
  groupTemplate: document.getElementById("group-template"),
};

async function loadData() {
  const response = await fetch(`./data/architecture.generated.json?ts=${Date.now()}`);
  if (!response.ok) {
    throw new Error(`failed to load data: ${response.status}`);
  }
  state.data = await response.json();
  render();
}

function serviceCard(service) {
  const fragment = els.cardTemplate.content.cloneNode(true);
  fragment.querySelector(".service-icon").src = service.icon;
  fragment.querySelector(".service-icon").alt = service.title;
  fragment.querySelector(".service-title").textContent = service.title;
  fragment.querySelector(".service-subtitle").textContent = service.subtitle;

  const details = fragment.querySelector(".service-details");
  service.details.forEach((detail) => {
    const li = document.createElement("li");
    li.textContent = detail;
    details.appendChild(li);
  });

  return fragment;
}

function renderGroups() {
  els.groupLayer.innerHTML = "";
  state.data.groups.forEach((group) => {
    const fragment = els.groupTemplate.content.cloneNode(true);
    const node = fragment.querySelector(".aws-group");
    const title = fragment.querySelector(".aws-group-title");
    node.dataset.kind = group.kind;
    node.style.left = `${group.x}px`;
    node.style.top = `${group.y}px`;
    node.style.width = `${group.w}px`;
    node.style.height = `${group.h}px`;
    title.textContent = group.title;
    els.groupLayer.appendChild(fragment);
  });
}

function renderNodes() {
  els.nodeLayer.innerHTML = "";
  state.data.services.forEach((service) => {
    const fragment = serviceCard(service);
    const card = fragment.querySelector(".service-card");
    card.dataset.id = service.id;
    card.style.left = `${service.x}px`;
    card.style.top = `${service.y}px`;
    els.nodeLayer.appendChild(fragment);
  });
}

function centerOf(el) {
  return {
    x: el.offsetLeft + el.offsetWidth / 2,
    y: el.offsetTop + el.offsetHeight / 2,
  };
}

function renderConnectors() {
  els.connectorLayer.innerHTML = `
    <defs>
      <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
        <path d="M0 0 L10 5 L0 10 Z" fill="#6a7f94"></path>
      </marker>
    </defs>
  `;

  state.data.connectors.forEach((connector) => {
    const from = els.nodeLayer.querySelector(`[data-id="${connector.from}"]`);
    const to = els.nodeLayer.querySelector(`[data-id="${connector.to}"]`);
    if (!from || !to) return;

    const a = centerOf(from);
    const b = centerOf(to);
    const horizontal = Math.abs(a.x - b.x) > Math.abs(a.y - b.y);

    let x1 = a.x;
    let y1 = a.y;
    let x2 = b.x;
    let y2 = b.y;

    if (horizontal) {
      x1 = from.offsetLeft + from.offsetWidth;
      y1 = a.y;
      x2 = to.offsetLeft;
      y2 = b.y;
    } else {
      x1 = a.x;
      y1 = from.offsetTop + from.offsetHeight;
      x2 = b.x;
      y2 = to.offsetTop;
    }

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    const midX = (x1 + x2) / 2;
    const midY = (y1 + y2) / 2;
    const d = horizontal
      ? `M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`
      : `M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`;
    path.setAttribute("d", d);
    path.setAttribute("class", `connector${connector.dashed ? " dashed" : ""}`);
    path.setAttribute("marker-end", "url(#arrowhead)");
    els.connectorLayer.appendChild(path);
  });
}

function renderDeployment() {
  els.deploymentInfo.innerHTML = "";
  const entries = [
    ["Região", state.data.deployment.region],
    ["Modo", state.data.deployment.roleMode],
    ["API", state.data.deployment.apiEndpoint],
    ["Bucket", state.data.deployment.bucketName],
    ["Tabela", state.data.deployment.tableName],
    ["Fila", state.data.deployment.queueUrl],
  ];

  entries.forEach(([key, value]) => {
    const dt = document.createElement("dt");
    dt.textContent = key;
    const dd = document.createElement("dd");
    dd.textContent = value;
    els.deploymentInfo.append(dt, dd);
  });
}

function renderNotes() {
  els.notesList.innerHTML = "";
  state.data.notes.forEach((note) => {
    const li = document.createElement("li");
    li.textContent = note;
    els.notesList.appendChild(li);
  });
}

function renderIcons() {
  els.iconsList.innerHTML = "";
  state.data.officialIcons.forEach((icon) => {
    const row = document.createElement("div");
    row.className = "icon-row";
    row.innerHTML = `<strong>${icon.service}</strong><code>${icon.officialAssetName}</code>`;
    els.iconsList.appendChild(row);
  });
}

function render() {
  els.title.textContent = state.data.meta.title;
  els.subtitle.textContent = state.data.meta.subtitle;
  els.roleMode.textContent = state.data.deployment.roleMode;
  renderGroups();
  renderNodes();
  renderConnectors();
  renderDeployment();
  renderNotes();
  renderIcons();
}

els.refreshButton.addEventListener("click", async () => {
  els.refreshButton.disabled = true;
  els.refreshButton.textContent = "Recarregando...";
  try {
    await loadData();
  } finally {
    els.refreshButton.disabled = false;
    els.refreshButton.textContent = "Recarregar dados";
  }
});

loadData().catch((error) => {
  console.error(error);
  els.subtitle.textContent = "Não foi possível carregar os dados gerados da arquitetura.";
});
