"""
Repositório dos dispositivos/atuadores (tabela dispositivos):
válvula de entrada (VALV-01) e relé de corte emergencial (RELE-EMG).
"""
from datetime import datetime

from database.connection import Database
from models.sensor_data import Dispositivo, StatusDispositivo

TAG_VALVULA = "VALV-01"
TAG_RELE_EMERGENCIA = "RELE-EMG"


class DispositivoRepository:

    @staticmethod
    def _de_linha(linha) -> Dispositivo:
        return Dispositivo(
            id=linha["id"],
            tag=linha["tag"],
            tipo=linha["tipo"],
            descricao=linha["descricao"],
            status=StatusDispositivo(linha["status"]),
            ultima_atualizacao=datetime.strptime(linha["ultima_atualizacao"], Database.FORMATO_DATA_HORA),
        )

    @staticmethod
    def _agora() -> str:
        return datetime.now().strftime(Database.FORMATO_DATA_HORA)

    @staticmethod
    def inserir(dispositivo: Dispositivo) -> int:
        with Database.transacao() as conn:
            cursor = conn.execute(
                "INSERT INTO dispositivos (tag, tipo, descricao, status, ultima_atualizacao) VALUES (?, ?, ?, ?, ?)",
                (
                    dispositivo.tag,
                    dispositivo.tipo,
                    dispositivo.descricao,
                    dispositivo.status.value,
                    DispositivoRepository._agora(),
                ),
            )
        dispositivo.id = cursor.lastrowid
        return dispositivo.id

    @staticmethod
    def listar_todos() -> list[Dispositivo]:
        with Database.transacao() as conn:
            linhas = conn.execute(
                "SELECT id, tag, tipo, descricao, status, ultima_atualizacao FROM dispositivos ORDER BY id ASC"
            ).fetchall()
        return [DispositivoRepository._de_linha(linha) for linha in linhas]

    @staticmethod
    def buscar_por_id(dispositivo_id: int) -> Dispositivo | None:
        with Database.transacao() as conn:
            linha = conn.execute(
                "SELECT id, tag, tipo, descricao, status, ultima_atualizacao FROM dispositivos WHERE id = ?",
                (dispositivo_id,),
            ).fetchone()
        return DispositivoRepository._de_linha(linha) if linha else None

    @staticmethod
    def buscar_por_tag(tag: str) -> Dispositivo | None:
        with Database.transacao() as conn:
            linha = conn.execute(
                "SELECT id, tag, tipo, descricao, status, ultima_atualizacao FROM dispositivos WHERE tag = ?",
                (tag,),
            ).fetchone()
        return DispositivoRepository._de_linha(linha) if linha else None

    @staticmethod
    def atualizar(dispositivo: Dispositivo) -> bool:
        with Database.transacao() as conn:
            cursor = conn.execute(
                "UPDATE dispositivos SET tag = ?, tipo = ?, descricao = ?, status = ?, ultima_atualizacao = ? "
                "WHERE id = ?",
                (
                    dispositivo.tag,
                    dispositivo.tipo,
                    dispositivo.descricao,
                    dispositivo.status.value,
                    DispositivoRepository._agora(),
                    dispositivo.id,
                ),
            )
        return cursor.rowcount > 0

    @staticmethod
    def deletar(dispositivo_id: int) -> bool:
        with Database.transacao() as conn:
            cursor = conn.execute("DELETE FROM dispositivos WHERE id = ?", (dispositivo_id,))
        return cursor.rowcount > 0
