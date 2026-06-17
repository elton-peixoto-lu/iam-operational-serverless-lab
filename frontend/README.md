# Frontend

Visualização local da arquitetura do lab.

Arquivos principais:

- [frontend/index.html](/Users/eltonpeixoto/dev/serverless-incident-labs/frontend/index.html)
- [frontend/styles.css](/Users/eltonpeixoto/dev/serverless-incident-labs/frontend/styles.css)
- [frontend/app.js](/Users/eltonpeixoto/dev/serverless-incident-labs/frontend/app.js)
- [frontend/data/architecture.generated.json](/Users/eltonpeixoto/dev/serverless-incident-labs/frontend/data/architecture.generated.json)

Gerar os dados mais recentes:

```bash
AWS_PROFILE=willian-lab ./scripts/generate_front_architecture_data.py
```

Servir localmente:

```bash
cd frontend
python3 -m http.server 4173
```

Depois abra:

```text
http://localhost:4173
```
