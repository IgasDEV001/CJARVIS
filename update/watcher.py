import os
import sys
import time
import subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


ARQUIVOS_MONITORADOS = {
    "main.py",
    "interface.py",
    "banco.py",
    "cerebro.py",
    "economia.py",
    "investimentos.py",
    "jarvis_ia.py",
    "jarvis_worker.py",
    "versao.py",
    "jarvis_config.json"
}


class RecarregarJARVIS(
    FileSystemEventHandler
):

    def __init__(self):

        super().__init__()

        self.recarregando = False

        self.ultimo_evento = 0

    def evento_valido(
        self,
        caminho
    ):

        nome = os.path.basename(
            caminho
        )

        return (
            nome
            in
            ARQUIVOS_MONITORADOS
        )

    def reiniciar(self):

        agora = time.time()

        if (
            agora - self.ultimo_evento
            < 1.0
        ):

            return

        self.ultimo_evento = agora

        if self.recarregando:

            return

        self.recarregando = True

        print(
            "\n===================================="
        )

        print(
            "ALTERAÇÃO DETECTADA"
        )

        print(
            "Reiniciando JARVIS..."
        )

        print(
            "====================================\n"
        )

        time.sleep(
            0.7
        )

        subprocess.Popen(
            [
                sys.executable,
                os.path.join(
                    BASE_DIR,
                    "main.py"
                )
            ]
        )

        os._exit(
            0
        )

    def on_modified(
        self,
        event
    ):

        if event.is_directory:

            return

        if self.evento_valido(
            event.src_path
        ):

            self.reiniciar()


def iniciar_watcher():

    observador = Observer()

    handler = (
        RecarregarJARVIS()
    )

    observador.schedule(
        handler,
        BASE_DIR,
        recursive=False
    )

    observador.start()

    print(
        "===================================="
    )

    print(
        "JARVIS HOT RELOAD ATIVO"
    )

    print(
        "Salve um arquivo para reiniciar."
    )

    print(
        "===================================="
    )

    try:

        while True:

            time.sleep(
                1
            )

    except KeyboardInterrupt:

        observador.stop()

    observador.join()


if __name__ == "__main__":

    iniciar_watcher()