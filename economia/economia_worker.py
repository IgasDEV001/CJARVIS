from PySide6.QtCore import (
    QObject,
    Signal,
    Slot
)

from economia import EconomiaJARVIS


class EconomiaWorker(QObject):

    dados_prontos = Signal(dict)

    erro = Signal(str)

    finalizado = Signal()

    def __init__(
        self,
        base_dir
    ):

        super().__init__()

        self.base_dir = base_dir

    @Slot()
    def executar(self):

        try:

            economia = EconomiaJARVIS(
                self.base_dir
            )

            dados = (
                economia.resumo_dashboard(
                    atualizar=True
                )
            )

            if not isinstance(
                dados,
                dict
            ):

                raise RuntimeError(
                    "O módulo de economia "
                    "não retornou um dicionário válido."
                )

            self.dados_prontos.emit(
                dados
            )

        except Exception as erro:

            self.erro.emit(
                str(erro)
            )

        finally:

            self.finalizado.emit()