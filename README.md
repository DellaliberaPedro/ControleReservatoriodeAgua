# Controle de Reservatório de Água

Sistema de Supervisão e Controle Desktop (SCADA) para monitoramento de qualidade e nível de reservatórios de água, desenvolvido para a disciplina **Desenvolvimento de Aplicações Computacionais**.

> 🚧 Em desenvolvimento

## Sobre o projeto

A aplicação atua como uma Interface Homem-Máquina (IHM) de supervisão, recebendo leituras de sensores de um microcontrolador **STM32F4** e permitindo a intervenção do operador em tempo real sobre o reservatório monitorado.

### Sensores (hardware alvo)

| Grandeza | Tipo | Sensor de referência |
|---|---|---|
| Temperatura da água | Digital | DS18B20 |
| TDS (sólidos dissolvidos) | Analógico | Gravity Analog TDS Sensor |
| Turbidez | Analógico | SEN0189 |

Nesta fase de desenvolvimento os dados ainda são simulados em software; a integração serial real com o STM32F4 é uma etapa futura.

## Stack

- **Python 3**
- **[PySide6](https://doc.qt.io/qtforpython/)** (Qt for Python) para a interface gráfica
- **Qt Designer** para as telas (`.ui`), compiladas via `pyside6-uic`

## Arquitetura (MVC) — estrutura planejada

```
controle-reservatorio-agua/
├── main.py            # ponto de entrada da aplicação
├── controller/         # lógica das janelas (signals & slots)
├── models/             # dados, simulação de sensores e regras
├── ui/                 # telas do Qt Designer (.ui + compiladas)
└── resources/           # estilos (.qss), ícones etc.
```

As pastas já existem no repositório; os arquivos vão sendo adicionados aos poucos, com commits de cada integrante.

## Equipe

- Pedro Henrique Devens Dellalibera
- João Gabriel Trevizol
- Alan Hoffman dos Santos
- Diogo Hoffman


