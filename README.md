# Subway Surfer - Virtual Controller

Controle o Subway Surfers com gestos da mao usando webcam + MediaPipe.

## Requisitos
- Windows
- Python 3.14 (recomendado para este repo)
- Webcam (Logitech BRIO recomendado)

## Instalacao
```
python -m pip install -r requirements.txt
```

## Arquivos
- `Virtual_controller.py`: controlador principal
- `hand_landmarker.task`: modelo do MediaPipe (obrigatorio)

## Execucao
```
python .\Virtual_controller.py
```

## Webcam BRIO (priorizar por nome)
Opcionalmente, instale o `pygrabber` para selecionar a camera pelo nome:
```
py -3.11 -m pip install pygrabber
```

Defina as variaveis antes de executar:
```
$env:CAMERA_NAME="BRIO"
# ou, para forcar indice:
$env:CAMERA_INDEX="1"
```

## Controles
- Mao aberta (5 dedos) -> JUMP
- Polegar + mindinho -> SLIDE
- Indicador + medio -> HOVERBOARD
- Mao na esquerda -> LEFT
- Mao na direita -> RIGHT

## Dicas
- Feche apps que estejam usando a webcam.
- Deixe a janela do emulador em foco para receber as teclas.

