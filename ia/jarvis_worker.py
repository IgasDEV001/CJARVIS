from PySide6.QtCore import (
    QObject,
    Signal,
    Slot
)

from ia.jarvis_ia import JarvisIA


class JarvisWorker(QObject):

    resposta_pronta = Signal(str)

    erro = Signal(str)

    iniciado = Signal()

    finalizado = Signal()

    def __init__(
        self,
        pergunta,
        contexto
    ):

        super().__init__()

        self.pergunta = pergunta

        self.contexto = contexto

        self.ia = JarvisIA()

    @Slot()
    def executar(self):

        self.iniciado.emit()

        try:

            resposta = self.ia.responder(
                self.pergunta,
                self.contexto
            )

            self.resposta_pronta.emit(
                resposta
            )

        except Exception as erro:

            self.erro.emit(
                str(erro)
            )

        finally:

            self.finalizado.emit()