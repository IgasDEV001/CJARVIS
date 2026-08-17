import os
import sys
import time
import zipfile
import shutil
import tempfile
import argparse
import requests
import subprocess


parser = argparse.ArgumentParser()

parser.add_argument(
    "--download",
    required=True
)

parser.add_argument(
    "--target",
    required=True
)

parser.add_argument(
    "--restart",
    default=""
)

args = parser.parse_args()


URL_DOWNLOAD = args.download

PASTA_DESTINO = os.path.abspath(
    args.target
)


def baixar_arquivo(
    url,
    destino
):

    resposta = requests.get(
        url,
        stream=True,
        timeout=120
    )

    resposta.raise_for_status()

    with open(
        destino,
        "wb"
    ) as arquivo:

        for bloco in resposta.iter_content(
            chunk_size=1024 * 1024
        ):

            if bloco:

                arquivo.write(
                    bloco
                )


def extrair_atualizacao(
    arquivo_zip,
    pasta_temp
):

    with zipfile.ZipFile(
        arquivo_zip,
        "r"
    ) as arquivo:

        arquivo.extractall(
            pasta_temp
        )


def localizar_raiz(
    pasta_temp
):

    itens = os.listdir(
        pasta_temp
    )

    if (
        len(itens) == 1
        and
        os.path.isdir(
            os.path.join(
                pasta_temp,
                itens[0]
            )
        )
    ):

        return os.path.join(
            pasta_temp,
            itens[0]
        )

    return pasta_temp


def copiar_arquivos(
    origem,
    destino
):

    for raiz, diretorios, arquivos in os.walk(
        origem
    ):

        relativa = os.path.relpath(
            raiz,
            origem
        )

        if relativa == ".":

            pasta_destino = destino

        else:

            pasta_destino = os.path.join(
                destino,
                relativa
            )

        os.makedirs(
            pasta_destino,
            exist_ok=True
        )

        for nome in arquivos:

            origem_arquivo = os.path.join(
                raiz,
                nome
            )

            destino_arquivo = os.path.join(
                pasta_destino,
                nome
            )

            shutil.copy2(
                origem_arquivo,
                destino_arquivo
            )


def main():

    print(
        "JARVIS UPDATER"
    )

    time.sleep(
        2
    )

    pasta_temp = tempfile.mkdtemp(
        prefix="cjarvis_update_"
    )

    arquivo_zip = os.path.join(
        pasta_temp,
        "CJARVIS_update.zip"
    )

    extracao = os.path.join(
        pasta_temp,
        "extraido"
    )

    try:

        baixar_arquivo(
            URL_DOWNLOAD,
            arquivo_zip
        )

        os.makedirs(
            extracao,
            exist_ok=True
        )

        extrair_atualizacao(
            arquivo_zip,
            extracao
        )

        raiz = localizar_raiz(
            extracao
        )

        copiar_arquivos(
            raiz,
            PASTA_DESTINO
        )

        print(
            "Atualização concluída."
        )

        if args.restart:

            caminho = os.path.join(
                PASTA_DESTINO,
                args.restart
            )

            if os.path.exists(
                caminho
            ):

                subprocess.Popen(
                    [
                        caminho
                    ]
                )

        else:

            main_py = os.path.join(
                PASTA_DESTINO,
                "main.py"
            )

            if os.path.exists(
                main_py
            ):

                subprocess.Popen(
                    [
                        sys.executable,
                        main_py
                    ]
                )

    except Exception as erro:

        print(
            "ERRO NA ATUALIZAÇÃO:",
            erro
        )

    finally:

        shutil.rmtree(
            pasta_temp,
            ignore_errors=True
        )


if __name__ == "__main__":

    main()