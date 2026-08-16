# Controle de Reservatório de Água

Sistema de Supervisão e Controle Desktop (SCADA) para monitoramento de qualidade e nível de reservatórios de água, desenvolvido para a disciplina **Desenvolvimento de Aplicações Computacionais**.

> 🚧 Em desenvolvimento

## Sobre o projeto

A aplicação atua como uma Interface Homem-Máquina (IHM) de supervisão, recebendo leituras de sensores de um microcontrolador **STM32F103C8T6** ("Blue Pill") e permitindo a intervenção do operador em tempo real sobre o reservatório monitorado.

### Hardware já disponível

| Componente | Tipo | Peça |
|---|---|---|
| Microcontrolador | — | STM32F103C8T6 ("Blue Pill") |
| Temperatura da água | Sensor digital | DS18B20 (sonda à prova d'água) |
| TDS / condutividade | Sensor analógico | Sensor analógico de condutividade de água |
| Turbidez | Sensor analógico | Sensor de turbidez para monitoramento de água |

Nesta fase de desenvolvimento os dados ainda são simulados em software; a integração serial real com o STM32 (via USB) é uma etapa futura.

## Stack

- **Python 3.14**
- **[PySide6](https://doc.qt.io/qtforpython/)** (Qt for Python) para a interface gráfica
- **Qt Designer** para as telas (`.ui`), compiladas via `pyside6-uic`

## Como rodar

```bash
git clone https://github.com/DellaliberaPedro/ControleReservatoriodeAgua.git
cd ControleReservatoriodeAgua

python -m venv .venv
.venv\Scripts\activate        # Windows (PowerShell)
# source .venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
python main.py
```

## Arquitetura (MVC)

```
ControleReservatorioAgua/
├── main.py                      # ponto de entrada da aplicação
├── requirements.txt
├── .gitignore
├── controller/
│   ├── maincontroller.py        # lógica da janela principal
│   └── settingscontroller.py    # lógica do modal de regras de alerta
├── models/
│   ├── sensor_data.py           # estruturas de dados (leitura, evento, regra)
│   └── data_simulator.py        # gerador de leituras simuladas
├── ui/
│   ├── tela.ui / Ui_tela.py                         # janela principal
│   └── tela_configuracoes.ui / Ui_tela_configuracoes.py   # modal de regras
└── resources/
    └── style.qss                 # tema visual (escuro)
```

Regra de organização: nada de lógica de negócio dentro de `ui/` — os arquivos `Ui_*.py` são gerados automaticamente (`pyside6-uic`) e não devem ser editados à mão. Depois de mexer num `.ui` no Qt Designer, regenera com:

```bash
pyside6-uic ui/tela.ui -o ui/Ui_tela.py
pyside6-uic ui/tela_configuracoes.ui -o ui/Ui_tela_configuracoes.py
```

## Sobre o .gitignore

O `.gitignore` diz pro Git quais arquivos **não** devem entrar no repositório: a pasta `.venv/` (ambiente virtual — cada um cria o seu localmente), `__pycache__/` e `*.pyc` (bytecode compilado, gerado automaticamente toda vez que o programa roda) e configurações de IDE. Sem isso, esses arquivos mudam sozinhos a cada execução e geram conflito toda hora entre quem está usando o projeto. Se você clonar o projeto e não tiver esse arquivo, copia o conteúdo abaixo pra um arquivo chamado `.gitignore` na raiz:

```
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
env/
.vscode/
.idea/
.DS_Store
Thumbs.db
*.log
*.db
*.sqlite3
```

## Fluxo de trabalho em equipe

- Antes de começar a mexer, sempre dar `git pull origin main` primeiro, pra pegar o que os outros já fizeram.
- Cada um commita com a própria conta GitHub — a atividade audita isso individualmente.
- Prefira commits pequenos e frequentes (com mensagem clara do que mudou) a um commit gigante no final.

## Equipe

- Pedro Henrique Devens Dellalibera
- João Gabriel Trevizol
- Alan Hoffman dos Santos
- Diogo Hoffman
