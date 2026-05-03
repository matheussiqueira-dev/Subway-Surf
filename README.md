# Subway Surf Motion Controller

[![CI](https://github.com/matheussiqueira-dev/Subway-Surf/actions/workflows/ci.yml/badge.svg)](https://github.com/matheussiqueira-dev/Subway-Surf/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Controlador por gestos para Subway Surfers usando visão computacional (MediaPipe + OpenCV), com API REST, dashboard web, perfis de calibração e telemetria em tempo real.

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Arquitetura](#2-arquitetura)
3. [Instalação](#3-instalação)
4. [Executando](#4-executando)
5. [Configuração (Variáveis de Ambiente)](#5-configuração)
6. [API REST](#6-api-rest)
7. [Testes](#7-testes)
8. [Gestos Suportados](#8-gestos-suportados)
9. [Stack Tecnológica](#9-stack-tecnológica)
10. [Melhorias Futuras](#10-melhorias-futuras)

---

## 1. Visão Geral

O projeto transforma movimentos da mão em comandos de teclado para jogos de corrida, com foco em Subway Surfers.

**O que ele resolve:**
- Elimina a dependência de teclado/mouse para ações repetitivas durante o jogo.
- Permite calibrar sensibilidade por ambiente (iluminação, câmera, distância).
- Oferece monitoramento operacional em tempo real: FPS, ação ativa, perfil.

**Público-alvo:** jogadores, desenvolvedores de HCI e times de produto que precisam de uma base extensível para visão computacional em tempo real.

---

## 2. Arquitetura

O projeto segue **Clean Architecture** com separação estrita entre camadas:

```
src/
├── domain/          # Entidades e regras de negócio puras (Action, Profile, Snapshots)
├── services/        # Casos de uso (GestureInterpreter, ProfileService, TelemetryService)
├── core/            # Orquestração de baixo nível (HandDetector, GameController)
├── infrastructure/  # Adaptadores externos (CameraStream, KeyboardAdapter)
├── ui/              # HUD OpenCV (Display)
├── api/             # Backend FastAPI (rotas, schemas, segurança)
├── app/             # Runner principal (VirtualControllerApp)
├── ports.py         # Interfaces Protocol para inversão de dependência
└── utils/           # Config, Logger
```

**Princípios aplicados:**
- **SOLID** — responsabilidade única por módulo, dependências explícitas via injeção.
- **Protocol interfaces** — `CameraPort`, `DetectorPort`, `KeyboardPort`, `GestureInterpreterPort` permitem trocar implementações sem alterar o domínio.
- **Imutabilidade de config** — `AppConfig` é criado uma vez via `load_config()` e sobrescrito apenas em bootstrap.

### Fluxo de execução (modo `controller`)

```
Webcam → CameraStream.read()
       → cv2.flip + cvtColor(BGR→RGB)
       → HandDetector.detect()        (MediaPipe VIDEO mode)
       → GestureInterpreter.interpret()
       → GameController.perform_action()
       → KeyboardAdapter.send()       (pynput key press/release)
       → HUD.draw()                   (OpenCV overlay)
       → TelemetryService.publish()   (async-safe, in-memory + JSON)
```

---

## 3. Instalação

```bash
git clone https://github.com/matheussiqueira-dev/Subway-Surf.git
cd Subway-Surf

# Produção
pip install -r requirements.txt

# Desenvolvimento (inclui ruff, mypy, pytest-cov, pre-commit)
pip install -r requirements-dev.txt
pre-commit install
```

Copie o template de variáveis de ambiente:

```bash
cp .env.example .env
```

---

## 4. Executando

### Via Makefile (recomendado)

```bash
make run        # Somente o controlador gestual
make run-api    # Somente API + dashboard
make run-all    # API em background + controlador
```

### Via CLI diretamente

```bash
# Controlador (requer câmera)
python main.py --mode controller

# Apenas API + dashboard
python main.py --mode api --api-host 127.0.0.1 --api-port 8000

# Ambos simultaneamente
python main.py --mode all

# Ativar um perfil específico na inicialização
python main.py --mode controller --profile competitive

# Outras opções
python main.py --help
```

### Dashboard e Docs

| URL | Descrição |
|-----|-----------|
| `http://127.0.0.1:8000/dashboard/game.html` | Jogo web jogável integrado ao controlador |
| `http://127.0.0.1:8000/dashboard` | Dashboard web |
| `http://127.0.0.1:8000/docs` | Swagger UI |
| `http://127.0.0.1:8000/redoc` | ReDoc |

### Jogo web integrado

O dashboard agora inclui um runner jogável em canvas, sem depender do Unity instalado:

```bash
python main.py --mode api --api-host 127.0.0.1 --api-port 8000
```

Abra `http://127.0.0.1:8000/dashboard/game.html`.

Controles:

| Tecla | Ação |
|-------|------|
| `A` / `←` | Mover esquerda |
| `D` / `→` | Mover direita |
| `W` / `↑` | Pular |
| `S` / `↓` | Rolar |
| `Espaço` / `H` | Hoverboard |
| `R` | Reiniciar após game over |

Quando o controlador por webcam está rodando, a página pode consumir a telemetria de gestos
e converter `LEFT`, `RIGHT`, `JUMP`, `SLIDE` e `HOVERBOARD` em comandos do jogo.

### Projeto Unity reconstruído

Além do jogo web, este repositório inclui `UnityGame/`, um projeto Unity 2022.3 LTS com uma
cena jogável reconstruída em `UnityGame/Assets/Scenes/Main.unity`.

Para gerar um build Windows quando o Unity estiver instalado:

```powershell
cd UnityGame
.\build_unity_windows.ps1
```

### Controles do HUD OpenCV

| Tecla | Ação |
|-------|------|
| `Q` | Encerrar o controlador |
| `P` | Ciclar para o próximo perfil |
| `H` | Mostrar/ocultar legenda de gestos |

---

## 5. Configuração

Todas as variáveis têm valores padrão funcionais. Veja `.env.example` para descrições completas.

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `CAMERA_INDEX` | `0` | Índice do dispositivo OpenCV |
| `FRAME_WIDTH` / `FRAME_HEIGHT` | `640` / `480` | Resolução de captura |
| `LEFT_BOUND` / `RIGHT_BOUND` | `0.35` / `0.65` | Divisão das faixas X normalizadas |
| `DETECTION_CONFIDENCE` | `0.70` | Threshold de detecção MediaPipe |
| `ACTION_COOLDOWN_MS` | `220` | Intervalo mínimo entre key-presses |
| `API_HOST` / `API_PORT` | `127.0.0.1` / `8000` | Endereço da API |
| `API_KEY` | _(vazio)_ | Chave para `x-api-key` (desativa auth se vazio) |
| `API_ALLOW_ORIGINS` | `*` | CORS — separar por vírgula |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

---

## 6. API REST

Todos os endpoints protegidos requerem o header `x-api-key` quando `API_KEY` está configurado.

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/v1/health` | Status do serviço |
| `GET` | `/v1/config` | Configuração pública em runtime |
| `GET` | `/v1/profiles` | Lista todos os perfis |
| `GET` | `/v1/profiles/{name}` | Detalhes de um perfil |
| `PUT` | `/v1/profiles/{name}` | Criar ou atualizar perfil |
| `POST` | `/v1/profiles/{name}/activate` | Ativar perfil |
| `GET` | `/v1/telemetry?limit=30` | Telemetria recente |

---

## 7. Testes

```bash
# Roda a suite completa
make test

# Com cobertura HTML
make test-cov

# Verificação de lint e formatação
make lint

# Type-check (mypy strict)
make type-check
```

Cobertura atual inclui: `GestureInterpreter`, `GameController`, `TelemetryService`, `ProfileService`, domain models, `AppConfig` e contratos da API REST.

---

## 8. Gestos Suportados

| Gesto | Ação | Tecla |
|-------|------|-------|
| Mão aberta (todos os dedos) | Pular | `↑` |
| Polegar + mínimo | Rolar | `↓` |
| Indicador + médio | Hoverboard | `Espaço` |
| Mão à esquerda de `LEFT_BOUND` | Mover esquerda | `←` |
| Mão à direita de `RIGHT_BOUND` | Mover direita | `→` |

---

## 9. Stack Tecnológica

| Componente | Tecnologia |
|------------|-----------|
| Visão computacional | OpenCV 4.10+, MediaPipe 0.10+ |
| API & validação | FastAPI 0.115+, Pydantic 2.10+ |
| Servidor ASGI | Uvicorn |
| Entrada de teclado | pynput |
| Foco de janela | pygetwindow |
| Testes | pytest, pytest-cov, httpx |
| Linting / Formatação | ruff |
| Type checking | mypy (strict) |
| CI | GitHub Actions |

---

## 10. Melhorias Futuras

- WebSocket para telemetria live (eliminar polling do dashboard).
- Modelo de gesture classification treinado (maior precisão em cenários adversos).
- Persistência em banco SQL para analytics de sessões longas.
- Suporte a múltiplas mãos e gestos bimanais.
- Perfil por usuário com autenticação JWT.

---

## Créditos

Desenvolvido por **[Matheus Siqueira](https://www.matheussiqueira.dev/)** — Engenheiro de Software especializado em visão computacional, automação e desenvolvimento fullstack.

- Website: [matheussiqueira.dev](https://www.matheussiqueira.dev/)
- GitHub: [@matheussiqueira-dev](https://github.com/matheussiqueira-dev)

> Sinta-se livre para abrir issues ou contribuir com pull requests.
