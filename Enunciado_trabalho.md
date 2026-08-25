Neste semestre, cada equipe desenvolverá um Sistema de Supervisão e Controle Desktop. 
O tema central de referência é o Monitor de Consumo e Qualidade de Energia (Smart Grid).

Na última entrega (Dezembro)

O software desktop atuará como uma Interface Homem-Máquina de supervisão energética, sendo responsável por processar os sinais analógicos e digitais recebidos do microcontrolador e permitir a intervenção do operador em tempo real.
1. Processamento e Apresentação de Telemetria (Hardware → Desktop)

O software receberá continuamente as amostras brutas dos sensores do microcontrolador (via comunicação serial no futuro ou simuladas nesta entrega):

    Leitura e Tratamento de Tensão (V) e Corrente (A):

        O software deve ler a tensão eficaz (VRMS) e a corrente (IRMS) enviadas pelo sensor (ex.: ACS712 / ZMPT101B).

    Cálculo da Potência Ativa (P):

        O software calcula a potência instantânea aproximada em Watts (W) ou Quilowatts (kW) através da relação:
        P=V×I

    Renderização no Dashboard:

        Exibir os valores instantâneos de V, I e P em indicadores numéricos de alta visibilidade (QLCDNumber ou QLabel customizadas com destaque de cor).

        Atualizar o Gráfico de Tendência Temporal (PyQtGraph ou Matplotlib) plotando a curva de consumo de potência ao longo do tempo. O gráfico deve ser inicializado com histórico pré-carregado no momento da abertura da tela.

2. Monitoramento de Estado Binário e Segurança (Hardware → Desktop)

O software deve monitorar o estado físico do disjuntor/chave de proteção geral da instalação:

    Sinalização Visual de Estado (Aberto / Fechado):

        Fechado (Energizado / Normal): Exibir um indicador gráfico de status verde (ex.: badge/LED virtual com o texto "Disjuntor: FECHADO / NORMAL").

        Aberto (Desenergizado / Trip/Falha): Exibir o indicador em vermelho (ex.: "Disjuntor: ABERTO / PROTEÇÃO ATIVADA").

    Detecção e Registro de Eventos de Disparo:

        Sempre que o estado mudar espontaneamente no hardware (ex.: disjuntor caiu por sobrecarga), o software deve disparar um aviso visual (QMessageBox.warning) e gerar um registro automático na tabela de histórico.

3. Atuação e Parametrização do Sistema (Desktop → Hardware)

O software fornecerá ao operador meios de intervir na carga e definir parâmetros operacionais:

    Corte Emergencial da Carga (Relé de Saída):

        Disponibilizar um botão de grande destaque ("CORTE DE EMERGÊNCIA" ou "DESLIGAR CARGA").

        Ao ser acionado, o software exibirá uma caixa de confirmação modal (QMessageBox.question). Se confirmado, enviará o comando binário (ex.: RELAY_OFF) para o microcontrolador abrir o relé.

    Ajuste de Limite de Alerta de Consumo (Setpoints):

        O operador poderá definir um limite máximo tolerável de corrente ou potência através de um campo numérico (QSpinBox / QDoubleSpinBox) ou seletor (QSlider).

    Lógica Local de Proteção de Software:

        Se a potência calculada pelo software ultrapassar o limite (setpoint) configurado pelo usuário, o software deve alterar a cor do dashboard para amarelo/vermelho, emitir um alerta visual e registrar a ocorrência de sobrecorrente.

4. Gestão de Histórico e Auditoria (Logs em Tabela)

Toda a atividade do sistema deve ser centralizada na QTableWidget de registros:
Coluna 	Descrição do Dado 	Exemplo de Preenchimento
Data / Hora 	Carimbo de data/hora exato do evento (Timestamp) 	10/08/2026 10:30:15
Tipo de Evento 	Categoria do evento registrado 	Comando, Alerta ou Status
Descrição 	Detalhes do evento ou valor medido na ocorrência 	Corte de emergência acionado via software
Valor Medido 	Potência/Corrente no momento do evento 	12.5 A / 2750 W

    💡 Opção de Tema Livre (Prototipagem de Microcontroladores):

    As equipes que preferirem podem aplicar o software supervisor a um protótipo físico/projeto desenvolvido em disciplinas como Microcontroladores, Microprocessadores ou Sistemas Embarcados, desde que o projeto atenda aos mesmos requisitos de leitura analógica/digital e acionamento de atuadores.

