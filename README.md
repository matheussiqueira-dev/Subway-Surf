# 🏄‍♂️ Subway Surfers - Virtual Motion Controller v2.0

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-green?style=for-the-badge)
![OpenCV](https://img.shields.io/badge/OpenCV-Advanced_UI-orange?style=for-the-badge)

Transforme seus movimentos reais em ações no jogo! Este projeto utiliza visão computacional de ponta para controlar o **Subway Surfers** através de gestos manuais capturados via webcam.

---

## 🚀 Visão Geral

O **Virtual Motion Controller** é uma interface inteligente que mapeia marcos (landmarks) da mão humana em comandos de teclado. Utilizando o modelo **MediaPipe Hand Landmarker**, o sistema identifica gestos específicos e a posição da mão no espaço 3D para simular movimentos de corrida, pulo e esquiva com baixíssima latência.

### Principais Melhorias na v2.0:
- **Arquitetura Modular**: Código totalmente refatorado seguindo princípios SOLID.
- **Gamer HUD**: Interface de usuário (UI) inspirada em jogos, com efeitos neon e feedback visual em tempo real.
- **Auto-Focus**: Sistema inteligente que foca automaticamente na janela do jogo ao detectar atividade.
- **Detecção Robusta**: Algoritmos aprimorados para reconhecimento de gestos (JUMP, SLIDE, HOVERBOARD).

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**: Linguagem base do projeto.
- **MediaPipe**: Framework do Google para processamento de IA em tempo real.
- **OpenCV**: Renderização da interface e processamento de imagem.
- **Pynput**: Emulação de periféricos de entrada (teclado).
- **PyGetWindow**: Gerenciamento e automação de janelas do sistema.

---

## 🎮 Funcionalidades e Controles

| Gesto / Posição | Ação no Jogo | Descrição |
| :--- | :--- | :--- |
| **Mão Aberta** | ⬆️ Pulo (JUMP) | Todos os 5 dedos estendidos. |
| **Polegar + Mindinho** | ⬇️ Rolagem (SLIDE) | Apenas os dedos das extremidades estendidos. |
| **Indicador + Médio** | ⌨️ Prancha (SPACE) | Tradicional gesto de "V" para ativar o hoverboard. |
| **Lado Esquerdo** | ⬅️ Esquerda (LEFT) | Mover a mão para a zona esquerda da câmera. |
| **Lado Direito** | ➡️ Direita (RIGHT) | Mover a mão para a zona direita da câmera. |

---

## 📦 Estrutura do Projeto

```text
subway-surfer/
├── src/
│   ├── core/
│   │   ├── controller.py   # Lógica de input e auto-focus
│   │   └── detector.py     # Processamento de IA e Gestos
│   ├── ui/
│   │   └── display.py      # Renderização do Gamer HUD
│   └── utils/
│       └── config.py       # Configurações centralizadas
├── legacy/                 # Versões anteriores do projeto
├── main.py                 # Ponto de entrada da aplicação
├── hand_landmarker.task    # Modelo de IA treinado
└── requirements.txt        # Dependências do projeto
```

---

## 🔧 Instalação e Uso

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/matheussiqueira-dev/subway-surfer.git
   cd subway-surfer
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Inicie o jogo:**
   Abra o Subway Surfers (versão PC ou Emulador).

4. **Execute o controlador:**
   ```bash
   python main.py
   ```

---

## 💡 Boas Práticas e Performance

- **Iluminação**: Garanta que sua mão esteja bem iluminada para evitar falhas no rastreamento.
- **Fundo**: Utilize um fundo neutro para reduzir o ruído visual.
- **Estabilidade**: O controlador foi otimizado para câmeras de 30 FPS ou superior (Recomendado: Logitech BRIO).

---

## 🚀 Melhorias Futuras

- [ ] Suporte para múltiplos perfis de jogo.
- [ ] Calibração dinâmica de zonas de movimento.
- [ ] Interface gráfica (GUI) em CustomTkinter para ajustes de sensibilidade.
- [ ] Comandos de voz para power-ups especiais.

---

### Autoria: Matheus Siqueira  
**Website:** [www.matheussiqueira.dev](https://www.matheussiqueira.dev/)
