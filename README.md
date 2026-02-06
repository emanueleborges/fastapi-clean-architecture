# FastAPI - Documentacao

## Visao geral
API FastAPI Assíncrona com CRUD de usuarios, implementando Clean Architecture (Service/Repository Pattern) e filtro dinamico.

## Estrutura do projeto
```
fastapi/
  app/
    api/
      v1/
        endpoints/
          users.py
        api.py
    core/
      config.py
    db/
      session.py
      session_async.py
    models/
      user.py
    repositories/
      base.py
      user_repository.py
    schemas/
      user.py
    service/
      user_service.py
    main.py
  tests/
    test_users.py
  requirements.txt
  .env
  sql_app.db
```

### O que cada pasta faz
- app/api: rotas e organizacao dos endpoints.
- app/core: configuracoes e variaveis de ambiente.
- app/db: conexao assincrona com SQLAlchemy + aiosqlite.
- app/models: modelos do SQLAlchemy.
- app/repositories: camada de acesso a dados (Repository Pattern).
- app/schemas: schemas Pydantic para validacao e resposta.
- app/service: regras de negocio.
- app/main.py: ponto de entrada da aplicacao.
- tests: testes automatizados (AsyncClient).
### Por que essa estrutura
- **Async First**: Suporte a alta concorrencia em I/O (Banco de Dados).
- **Clean Architecture**: Separacao clara em Camadas (Endpoint -> Service -> Repository -> Model).
- **Repository Pattern**: Desacoplamento do ORM e facilidade para Mock em testes.
- **Generic Repository**: CRUD padrao reutilizavel para qualquer entidade.

### Fluxo de requisicao
1. Requisicao chega no endpoint em app/api.
2. Schema valida os dados.
3. Service executa regra de negocio.
4. Repository monta a query assincrona.
5. Banco executa e retorna para as camadas superiores.

### Diagrama do fluxo
```mermaid
flowchart LR
  Client[Cliente] --> API[app/api]
  API --> Schemas[app/schemas]
  Schemas --> Service[app/service]
  Service --> Repository[app/repositories]
  Repository --> Models[app/models]
  Repository --> DB[(Banco Async)]
  DB --> Repository --> Service --> Schemas --> API --> Client

## Requisitos
- Python 3.10+ (recomendado)
- pip

## Clonar o repositorio
```bash
git clone <URL_DO_REPOSITORIO>
cd fastapi
```

## Configuracao de ambiente
Crie e ative um ambiente virtual.

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Instalar dependencias
```bash
pip install -r requirements.txt
```

## Variaveis de ambiente
O projeto usa o arquivo .env na raiz.
Exemplo (ja existe no repositorio):
```
PROJECT_NAME="FastAPI Professional"
API_V1_STR="/api/v1"
DATABASE_URL="sqlite+aiosqlite:///./sql_app.db"
```

## Ativar venv
Ative o ambiente virtual antes de rodar a aplicacao ou os testes.

Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:
```bash
source .venv/bin/activate
```

## Rodar a aplicacao
```bash
uvicorn app.main:app --reload
```
Atalho (ativar venv + rodar):

Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Linux/macOS:
```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```
Acesse a documentacao interativa:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Testar a aplicacao
```bash
python -m pytest
```
Atalho (ativar venv + testar):

Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest
```

Linux/macOS:
```bash
source .venv/bin/activate
python -m pytest
```

## Endpoints principais
Base path: /api/v1

- POST /users/
- GET /users/
- GET /users/{user_id}
- PUT /users/{user_id}
- DELETE /users/{user_id}

## Exemplos de uso

### Criar usuario
Request:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
	-H "Content-Type: application/json" \
	-d '{"email":"user@example.com","password":"string","is_active":true}'
```

Response (200):
```json
{
	"id": 1,
	"email": "user@example.com",
	"is_active": true
}
```

### Listar usuarios (com filtro)
Request:
```bash
curl "http://127.0.0.1:8000/api/v1/users/?is_active=true"
```

Response (200):
```json
[
	{
		"id": 1,
		"email": "user@example.com",
		"is_active": true
	}
]
```

### Buscar usuario por ID
Request:
```bash
curl "http://127.0.0.1:8000/api/v1/users/1"
```

Response (200):
```json
{
	"id": 1,
	"email": "user@example.com",
	"is_active": true
}
```

### Atualizar usuario
Request:
```bash
curl -X PUT "http://127.0.0.1:8000/api/v1/users/1" \
	-H "Content-Type: application/json" \
	-d '{"email":"new@example.com","is_active":false}'
```

Response (200):
```json
{
	"id": 1,
	"email": "new@example.com",
	"is_active": false
}
```

### Remover usuario
Request:
```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/users/1"
```

Response (204):
```
Sem conteudo
```

## Exemplos com httpie
Criar usuario:
```bash
http POST :8000/api/v1/users/ email="user@example.com" password="string" is_active:=true
```

Listar usuarios:
```bash
http :8000/api/v1/users/
```

Buscar usuario por ID:
```bash
http :8000/api/v1/users/1
```

Atualizar usuario:
```bash
http PUT :8000/api/v1/users/1 email="new@example.com" is_active:=false
```

Remover usuario:
```bash
http DELETE :8000/api/v1/users/1
```

## Exemplos de erro (httpie)
Email duplicado (400):
```bash
http POST :8000/api/v1/users/ email="user@example.com" password="string" is_active:=true
```

Usuario nao encontrado (404):
```bash
http :8000/api/v1/users/999999
```

Erro de validacao (422) - email invalido:
```bash
http POST :8000/api/v1/users/ email="email-invalido" password="string" is_active:=true
```

Erro de validacao (422) - update com email invalido:
```bash
http PUT :8000/api/v1/users/1 email="email-invalido" is_active:=true
```

## Colecoes
- Postman: importar [postman/fastapi_users.postman_collection.json](postman/fastapi_users.postman_collection.json)
- Insomnia: importar [insomnia/fastapi_users.insomnia.json](insomnia/fastapi_users.insomnia.json)

Variaveis usadas nas colecoes:
- base_url: http://127.0.0.1:8000
- user_id: 1

## Observacoes
- O banco padrao eh SQLite em [sql_app.db](sql_app.db).
- A tabela de usuarios eh criada no startup da aplicacao.
