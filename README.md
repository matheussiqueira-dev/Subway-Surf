# Subway Surf Motion Controller v3.0

Controlador por gestos para Subway Surfers com arquitetura profissional, API REST, dashboard web, perfis de calibração e telemetria em tempo real.

## 1) Visão Geral

Este projeto transforma movimentos da mão em comandos de teclado para jogos de corrida (foco: Subway Surfers), usando visão computacional com MediaPipe.

### Problema que resolve
- Reduz dependência de teclado/mouse para ações repetitivas.
- Permite calibrar sensibilidade por ambiente (luz, câmera, distância).
- Oferece monitoramento operacional (FPS, ação ativa, presença de mão, perfil).

### Público-alvo
- Jogadores que querem controle gestual.
- Desenvolvedores que estudam HCI (Human-Computer Interaction).
- Times de produto/engenharia que precisam de base extensível para visão em tempo real.

## 2) Arquitetura e Decisões Técnicas

O sistema foi refatorado para separar domínio, aplicação, infraestrutura e apresentação.

### Camadas
- `domain`: entidades centrais (`Action`, `Profile`, `TelemetrySnapshot`).
- `services`: regras de negócio (interpretação de gesto, gestão de perfis, telemetria).
- `core`: detecção de mão e orquestração de comandos de jogo.
- `infrastructure`: adaptadores de câmera e teclado.
- `ui`: HUD OpenCV focada em legibilidade e feedback em tempo real.
- `api`: backend FastAPI para integração externa e dashboard.

### Princípios aplicados
- `SOLID`: responsabilidade única por módulo e dependências explícitas.
- `DRY`: regras de gesto e validações centralizadas.
- `Clean Architecture`: domínio independente de framework/UI.

## 3) Frontend + UX/UI

Foram implementadas duas experiências:

- HUD OpenCV (tempo real):
  - hierarquia visual mais clara (header, zonas de pista, legenda, status);
  - contraste e feedback de estado por ação;
  - comandos contextuais (`Q`, `P`, `H`) para operação sem interrupção.

- Dashboard Web (`/dashboard`):
  - visual moderno com design tokens e responsividade;
  - monitoramento de telemetria e sparkline de FPS;
  - CRUD de perfis com ativação imediata.

## 4) Backend, Segurança e Confiabilidade

Backend em FastAPI com:
- versionamento de endpoints (`/v1`);
- contratos validados via Pydantic;
- CORS configurável por ambiente;
- autenticação opcional por `x-api-key`;
- validação forte de perfil (nome seguro, ranges e limites);
- telemetria persistida em `runtime/telemetry.json`.

## 5) APIs, Dados e Integrações

### Endpoints principais
- `GET /v1/health`
- `GET /v1/config`
- `GET /v1/profiles`
- `GET /v1/profiles/{name}`
- `PUT /v1/profiles/{name}`
- `POST /v1/profiles/{name}/activate`
- `GET /v1/telemetry?limit=30`

### Persistência
- Perfis JSON versionáveis em `profiles/*.json`.
- Perfil ativo em `runtime/active_profile.txt`.
- Histórico de telemetria em `runtime/telemetry.json` (janela deslizante).

## 6) Novas Features Implementadas

- API REST para gestão de perfis e telemetria.
- Dashboard web para observabilidade e configuração.
- Perfis de calibração com troca dinâmica em runtime (`P` no controlador).
- CLI com modos operacionais:
  - `controller`
  - `api`
  - `all` (API + controlador).
- Logging estruturado com rotação em `runtime/logs`.

## 7) Qualidade e Boas Práticas

Testes automatizados cobrindo:
- interpretação de gestos (`tests/test_gesture_service.py`);
- serviço de perfis (`tests/test_profile_service.py`);
- contratos da API (`tests/test_api.py`).

Execução local dos testes:

```bash
python -m pytest
```

## 8) Stack Tecnológica

- Python 3.10+
- OpenCV
- MediaPipe Tasks
- FastAPI
- Uvicorn
- Pydantic
- PyNput
- PyGetWindow
- Pytest

## 9) Estrutura do Projeto

```text
Subway-Surf-main/
├── dashboard/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── profiles/
│   └── default.json
├── runtime/
├── src/
│   ├── api/
│   │   ├── app.py
│   │   ├── schemas.py
│   │   └── security.py
│   ├── app/
│   │   └── runner.py
│   ├── core/
│   │   ├── controller.py
│   │   └── detector.py
│   ├── domain/
│   │   ├── actions.py
│   │   └── models.py
│   ├── infrastructure/
│   │   ├── camera.py
│   │   └── keyboard_adapter.py
│   ├── services/
│   │   ├── gesture_service.py
│   │   ├── profile_service.py
│   │   └── telemetry_service.py
│   ├── ui/
│   │   └── display.py
│   └── utils/
│       ├── config.py
│       └── logger.py
├── tests/
├── main.py
└── requirements.txt
```

## 10) Instalação, Execução e Deploy

### Instalação

```bash
git clone https://github.com/matheussiqueira-dev/Subway-Surf.git
cd Subway-Surf-main
python -m pip install -r requirements.txt
```

### Executar controlador (desktop)

```bash
python main.py --mode controller
```

### Executar API + dashboard

```bash
python main.py --mode api --api-host 127.0.0.1 --api-port 8000
```

Dashboard:
- `http://127.0.0.1:8000/dashboard`
- Swagger/OpenAPI: `http://127.0.0.1:8000/docs`

### Executar tudo junto

```bash
python main.py --mode all
```

### Deploy recomendado (API)
- Executar com Uvicorn/Gunicorn atrás de Nginx.
- Definir `API_KEY` e `API_ALLOW_ORIGINS`.
- Isolar `runtime/` e `profiles/` em volume persistente.

## 11) Variáveis de Ambiente

- `CAMERA_INDEX` (padrão `0`)
- `CAMERA_NAME` (padrão `BRIO`)
- `LEFT_BOUND` / `RIGHT_BOUND`
- `DETECTION_CONFIDENCE`
- `PRESENCE_CONFIDENCE`
- `TRACKING_CONFIDENCE`
- `ACTION_COOLDOWN_MS`
- `AUTO_FOCUS_WINDOW`
- `API_HOST` / `API_PORT`
- `API_KEY`
- `API_ALLOW_ORIGINS`
- `LOG_LEVEL`

## 12) Melhorias Futuras

- Persistência em banco SQL (PostgreSQL) para analytics de sessões.
- Modelo de gesture classification treinado para maior precisão.
- WebSocket para telemetria live sem polling.
- Perfil por usuário com autenticação JWT e RBAC.
- Pipeline CI/CD com quality gates (lint, test, security scan).

Autoria: Matheus Siqueira  
Website: https://www.matheussiqueira.dev/
