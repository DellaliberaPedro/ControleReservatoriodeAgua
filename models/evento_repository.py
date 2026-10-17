"""
Repositório do histórico de eventos (tabela eventos).

Todos os comandos usam placeholders '?'. O parâmetro opcional `conn` permite
que o INSERT participe de uma transação maior aberta por outro repositório
(ex.: corte emergencial = UPDATE do dispositivo + INSERT do evento).
"""
from datetime import datetime

from database.connection import Database
from models.sensor_data import RegistroEvento, TipoEvento


class EventoRepository:

    @staticmethod
    def _de_linha(linha) -> RegistroEvento:
        return RegistroEvento(
            id=linha["id"],
            timestamp=datetime.strptime(linha["data_hora"], Database.FORMATO_DATA_HORA),
            tipo=TipoEvento(linha["tipo_evento"]),
            descricao=linha["descricao"],
            valor_medido=linha["valor_medido"],
            dispositivo_id=linha["dispositivo_id"],
        )

    @staticmethod
    def _executar_insert(conn, evento: RegistroEvento) -> int:
        cursor = conn.execute(
            "INSERT INTO eventos (data_hora, tipo_evento, descricao, valor_medido, dispositivo_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                evento.timestamp.strftime(Database.FORMATO_DATA_HORA),
                evento.tipo.value,
                evento.descricao,
                evento.valor_medido or "-",
                evento.dispositivo_id,
            ),
        )
        evento.id = cursor.lastrowid
        return evento.id

    @staticmethod
    def inserir(evento: RegistroEvento, conn=None) -> int:
        """Grava o evento e preenche evento.id. Com `conn`, participa da transação de quem chamou."""
        if conn is not None:
            return EventoRepository._executar_insert(conn, evento)
        with Database.transacao() as nova_conn:
            return EventoRepository._executar_insert(nova_conn, evento)

    @staticmethod
    def listar_todos() -> list[RegistroEvento]:
        with Database.transacao() as conn:
            linhas = conn.execute(
                "SELECT id, data_hora, tipo_evento, descricao, valor_medido, dispositivo_id "
                "FROM eventos ORDER BY data_hora ASC, id ASC"
            ).fetchall()
        return [EventoRepository._de_linha(linha) for linha in linhas]

    @staticmethod
    def buscar_por_id(evento_id: int) -> RegistroEvento | None:
        with Database.transacao() as conn:
            linha = conn.execute(
                "SELECT id, data_hora, tipo_evento, descricao, valor_medido, dispositivo_id "
                "FROM eventos WHERE id = ?",
                (evento_id,),
            ).fetchone()
        return EventoRepository._de_linha(linha) if linha else None

    @staticmethod
    def atualizar(evento: RegistroEvento) -> bool:
        with Database.transacao() as conn:
            cursor = conn.execute(
                "UPDATE eventos SET data_hora = ?, tipo_evento = ?, descricao = ?, valor_medido = ?, "
                "dispositivo_id = ? WHERE id = ?",
                (
                    evento.timestamp.strftime(Database.FORMATO_DATA_HORA),
                    evento.tipo.value,
                    evento.descricao,
                    evento.valor_medido,
                    evento.dispositivo_id,
                    evento.id,
                ),
            )
        return cursor.rowcount > 0

    @staticmethod
    def deletar(evento_id: int) -> bool:
        with Database.transacao() as conn:
            cursor = conn.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
        return cursor.rowcount > 0
