"""
Camada de acesso ao SQLite (data/smartgrid.db).

Responsabilidades:
  - abrir conexões já configuradas (timeout contra 'database is locked',
    row_factory para acessar colunas pelo nome e PRAGMA foreign_keys = ON);
  - oferecer um gerenciador de TRANSAÇÃO que faz commit/rollback e sempre
    fecha a conexão;
  - criar/validar o esquema na inicialização (Database.init_db()).

Nenhum SQL aqui usa f-string/concatenação: valores sempre via placeholder '?'.
"""
import logging
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)

PASTA_DATA = Path(__file__).resolve().parent.parent / "data"

ESQUEMA_SQL = """
CREATE TABLE IF NOT EXISTS dispositivos (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    tag                TEXT    NOT NULL UNIQUE,
    tipo               TEXT    NOT NULL CHECK (tipo IN ('VALVULA', 'RELE')),
    descricao          TEXT    NOT NULL,
    status             TEXT    NOT NULL CHECK (status IN ('ABERTO', 'FECHADO')),
    ultima_atualizacao DATETIME NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS eventos (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    data_hora      DATETIME NOT NULL,
    tipo_evento    TEXT     NOT NULL CHECK (tipo_evento IN ('Comando', 'Alerta', 'Status')),
    descricao      TEXT     NOT NULL CHECK (length(trim(descricao)) > 0),
    valor_medido   TEXT     NOT NULL DEFAULT '-',
    dispositivo_id INTEGER  REFERENCES dispositivos(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_eventos_data_hora ON eventos (data_hora);

CREATE TABLE IF NOT EXISTS regras_alerta (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT    NOT NULL CHECK (length(trim(nome)) > 0),
    sensor       TEXT    NOT NULL CHECK (sensor IN ('TDS (ppm)', 'Turbidez (NTU)', 'Temperatura (°C)')),
    valor_maximo REAL    NOT NULL CHECK (valor_maximo > 0),
    ativa        INTEGER NOT NULL DEFAULT 1 CHECK (ativa IN (0, 1))
);
"""

TABELAS_OBRIGATORIAS = {"dispositivos", "eventos", "regras_alerta"}

# dispositivos físicos do reservatório (inseridos só se ainda não existirem)
#   VALV-01  -> válvula solenoide de entrada: ABERTO = água entrando (normal)
#   RELE-EMG -> relé de corte emergencial:   FECHADO = circuito normal, ABERTO = corte acionado
DISPOSITIVOS_PADRAO = (
    ("VALV-01", "VALVULA", "Válvula solenoide de entrada do reservatório", "ABERTO"),
    ("RELE-EMG", "RELE", "Relé de corte emergencial da válvula", "FECHADO"),
)


class Database:
    DB_PATH = PASTA_DATA / "smartgrid.db"
    TIMEOUT_SEGUNDOS = 5.0  # espera até 5 s se outro processo estiver escrevendo
    FORMATO_DATA_HORA = "%Y-%m-%d %H:%M:%S"  # formato gravado nas colunas DATETIME

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        """Abre uma conexão configurada. Quem chama é responsável por fechar (prefira transacao())."""
        conn = sqlite3.connect(cls.DB_PATH, timeout=cls.TIMEOUT_SEGUNDOS)
        conn.row_factory = sqlite3.Row
        # o SQLite NÃO guarda essa opção no arquivo: precisa ligar em TODA conexão
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    @classmethod
    @contextmanager
    def transacao(cls):
        """
        Executa o bloco `with` como UMA transação atômica e sempre fecha a conexão:

            with Database.transacao() as conn:
                conn.execute(...)   # passo 1
                conn.execute(...)   # passo 2

          - bloco terminou sem erro -> COMMIT (os dois passos ficam gravados)
          - bloco lançou exceção    -> ROLLBACK (nenhum passo fica gravado) e a
                                       exceção sobe para quem chamou tratar
        """
        conn = cls.get_connection()
        try:
            with conn:  # gerenciador de transação do sqlite3: commit/rollback
                yield conn
        finally:
            conn.close()  # o `with conn` NÃO fecha a conexão, por isso o finally

    @classmethod
    def init_db(cls) -> None:
        """Cria o arquivo data/smartgrid.db, as tabelas e os dispositivos padrão, e valida o esquema."""
        try:
            os.makedirs(PASTA_DATA, exist_ok=True)
            with cls.transacao() as conn:
                conn.executescript(ESQUEMA_SQL)
                conn.executemany(
                    "INSERT OR IGNORE INTO dispositivos (tag, tipo, descricao, status) VALUES (?, ?, ?, ?)",
                    DISPOSITIVOS_PADRAO,
                )
                cls._validar_esquema(conn)
        except (sqlite3.Error, OSError, RuntimeError) as erro:
            logger.error("Falha ao inicializar o banco SQLite (%s): %s", cls.DB_PATH, erro)
            raise

        logger.info("Conexão com SQLite estabelecida e esquema validado (%s).", cls.DB_PATH.name)

    @staticmethod
    def _validar_esquema(conn: sqlite3.Connection) -> None:
        tabelas = {linha["name"] for linha in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        faltando = TABELAS_OBRIGATORIAS - tabelas
        if faltando:
            raise RuntimeError(f"tabelas ausentes no banco: {', '.join(sorted(faltando))}")

        if conn.execute("PRAGMA foreign_keys;").fetchone()[0] != 1:
            raise RuntimeError("PRAGMA foreign_keys não está ativo")

        resultado = conn.execute("PRAGMA quick_check;").fetchone()[0]
        if resultado != "ok":
            raise RuntimeError(f"verificação de integridade falhou: {resultado}")
