"""
Repositório das regras/limites de alerta (tabela regras_alerta).
"""
from database.connection import Database
from models.sensor_data import RegraAlerta


class RegraRepository:

    @staticmethod
    def _de_linha(linha) -> RegraAlerta:
        return RegraAlerta(
            id=linha["id"],
            nome=linha["nome"],
            sensor=linha["sensor"],
            valor_maximo=linha["valor_maximo"],
            ativa=bool(linha["ativa"]),
        )

    @staticmethod
    def _executar_insert(conn, regra: RegraAlerta) -> int:
        cursor = conn.execute(
            "INSERT INTO regras_alerta (nome, sensor, valor_maximo, ativa) VALUES (?, ?, ?, ?)",
            (regra.nome, regra.sensor, regra.valor_maximo, int(regra.ativa)),
        )
        regra.id = cursor.lastrowid
        return regra.id

    @staticmethod
    def inserir(regra: RegraAlerta) -> int:
        with Database.transacao() as conn:
            return RegraRepository._executar_insert(conn, regra)

    @staticmethod
    def listar_todos() -> list[RegraAlerta]:
        with Database.transacao() as conn:
            linhas = conn.execute(
                "SELECT id, nome, sensor, valor_maximo, ativa FROM regras_alerta ORDER BY id ASC"
            ).fetchall()
        return [RegraRepository._de_linha(linha) for linha in linhas]

    @staticmethod
    def buscar_por_id(regra_id: int) -> RegraAlerta | None:
        with Database.transacao() as conn:
            linha = conn.execute(
                "SELECT id, nome, sensor, valor_maximo, ativa FROM regras_alerta WHERE id = ?",
                (regra_id,),
            ).fetchone()
        return RegraRepository._de_linha(linha) if linha else None

    @staticmethod
    def atualizar(regra: RegraAlerta) -> bool:
        with Database.transacao() as conn:
            cursor = conn.execute(
                "UPDATE regras_alerta SET nome = ?, sensor = ?, valor_maximo = ?, ativa = ? WHERE id = ?",
                (regra.nome, regra.sensor, regra.valor_maximo, int(regra.ativa), regra.id),
            )
        return cursor.rowcount > 0

    @staticmethod
    def deletar(regra_id: int) -> bool:
        with Database.transacao() as conn:
            cursor = conn.execute("DELETE FROM regras_alerta WHERE id = ?", (regra_id,))
        return cursor.rowcount > 0

    @staticmethod
    def substituir_todas(regras: list[RegraAlerta]) -> None:
        """
        Troca o conjunto inteiro de regras numa ÚNICA transação (tudo ou nada).
        Usado quando o operador confirma o QDialog de regras: se qualquer INSERT
        falhar (ex.: CHECK valor_maximo > 0), as regras antigas continuam intactas.
        """
        with Database.transacao() as conn:
            conn.execute("DELETE FROM regras_alerta")
            for regra in regras:
                RegraRepository._executar_insert(conn, regra)
