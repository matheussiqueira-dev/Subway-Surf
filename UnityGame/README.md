# SubwaySurfersClone-Unity + Computer Vision

Projeto unificado com o clone em Unity e o controlador por gestos do repositorio
[`matheussiqueira-dev/Subway-Surf`](https://github.com/matheussiqueira-dev/Subway-Surf).

## Estrutura

- `Assets/Scenes/Main.unity`: cena jogavel reconstruida para o projeto abrir no Unity.
- `Assets/MergedGame/Scripts/`: endless runner simples criado por codigo, sem depender dos
  prefabs originais ausentes.
- `Assets/SubwayOriginal/`: scripts e shaders do clone original preservados dentro da estrutura
  padrao do Unity.
- `../`: controlador Python com OpenCV, MediaPipe, API, dashboard, perfis e testes.
- `run_game_with_cv.ps1`: inicia o controlador por gestos e, opcionalmente, o executavel do jogo.
- `build_unity_windows.ps1`: gera um build Windows quando o Unity 2022.3 LTS estiver instalado.
- `run_tests.ps1`: valida JSON de input do Unity, checa imports proibidos de `UnityEditor` e roda
  os testes do controlador.

## Como jogar

Na cena reconstruida `Assets/Scenes/Main.unity`:

- `A` ou seta esquerda: mover para a esquerda.
- `D` ou seta direita: mover para a direita.
- `W` ou seta para cima: pular / iniciar.
- `S` ou seta para baixo: rolar.
- `Space` ou `H`: ativar hoverboard/protecao.
- `R`: recomecar apos game over.

Gestos do controlador:

- Mao aberta: pular.
- Polegar + minimo: rolar.
- Indicador + medio: hoverboard.
- Mao para a esquerda/direita da camera: troca de faixa.

## Abrindo no Unity

Abra esta pasta no Unity Hub com Unity 2022.3 LTS e carregue a cena:

```text
Assets/Scenes/Main.unity
```

Para build Windows via PowerShell:

```powershell
.\build_unity_windows.ps1
```

O executavel sera criado em `Builds/Windows/SubwaySurfVisionRunner.exe`.

## Rodando com visao computacional

No PowerShell, dentro desta pasta:

```powershell
.\run_game_with_cv.ps1 -Mode all
```

O script usa o perfil `easy` por padrao, com cooldown mais calmo e limites de faixa mais
tolerantes para facilitar os primeiros testes. O controlador precisa de Python 3.10, 3.11 ou
3.12; quando estiver rodando dentro do Codex, os scripts preferem automaticamente o Python 3.12
empacotado.

Se voce ja tiver um build do Unity, passe o executavel:

```powershell
.\run_game_with_cv.ps1 -Mode all -GamePath "C:\caminho\Subway Surfers.exe"
```

Dashboard e documentacao da API ficam em:

- `http://127.0.0.1:8000/dashboard/game.html`
- `http://127.0.0.1:8000/dashboard`
- `http://127.0.0.1:8000/docs`

## Testes

```powershell
.\run_tests.ps1
```

Esse comando valida a estrutura Unity reconstruida e roda a suite do controlador Python.

## Creditos

Integracao de visao computacional e creditos do projeto:
**Matheus Siqueira** - [www.matheussiqueira.dev](https://www.matheussiqueira.dev)

Base Unity original: Subway Surfers clone por Batuhan Yigit, licenciado em MIT.
