import sys
import json
import os

from PySide6.QtWidgets import QApplication

from interface.interface import JanelaPrincipal


def obter_versao():

    caminho = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "version.json"
    )

    try:

        with open(
            caminho,
            "r",
            encoding="utf-8"
        ) as arquivo:

            dados = json.load(arquivo)

        return dados.get(
            "version",
            "0.0.0"
        )

    except Exception:

        return "0.0.0"


def main():

    versao = obter_versao()

    print(
        f"CJARVIS versão {versao}"
    )

    app = QApplication(
        sys.argv
    )

    janela = JanelaPrincipal()

    janela.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()