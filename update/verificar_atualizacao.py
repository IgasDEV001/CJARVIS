import os
import sys
import requests
import subprocess


# =========================================================
# DIRETÓRIO RAIZ DO CJARVIS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# =========================================================
# SERVIDOR DE TESTE LOCAL
# =========================================================

URL_VERSAO = (
    "http://127.0.0.1:8000/version.json"
)

URL_DOWNLOAD = (
    "http://127.0.0.1:8000/CJARVIS.zip"
)


# =========================================================
# VERSÃO ATUAL
# =========================================================

def obter_versao_atual():

    try:

        from core.versao import (
            VERSAO_JARVIS
        )

        return VERSAO_JARVIS

    except Exception:

        return "0.0.0"


# =========================================================
# COMPARAR VERSÕES
# =========================================================

def comparar_versoes(
    atual,
    nova
):

    try:

        atual = tuple(
            int(
                parte
            )
            for parte in str(atual).split(".")
        )

        nova = tuple(
            int(
                parte
            )
            for parte in str(nova).split(".")
        )

        return nova > atual

    except (
        ValueError,
        TypeError
    ):

        return False


# =========================================================
# VERIFICAR ATUALIZAÇÃO
# =========================================================

def verificar_atualizacao():

    try:

        resposta = requests.get(
            URL_VERSAO,
            timeout=10
        )

        resposta.raise_for_status()

        dados = resposta.json()

        nova_versao = str(
            dados.get(
                "versao",
                ""
            )
        ).strip()

        versao_atual = (
            obter_versao_atual()
        )

        # -------------------------------------------------
        # SERVIDOR NÃO INFORMOU VERSÃO
        # -------------------------------------------------

        if not nova_versao:

            return {
                "atualizacao": False,
                "versao_atual": versao_atual,
                "erro": "Versão não informada pelo servidor."
            }

        # -------------------------------------------------
        # NOVA VERSÃO DISPONÍVEL
        # -------------------------------------------------

        if comparar_versoes(
            versao_atual,
            nova_versao
        ):

            return {
                "atualizacao": True,
                "versao_atual": versao_atual,
                "nova_versao": nova_versao,
                "download": dados.get(
                    "download",
                    URL_DOWNLOAD
                ),
                "notas": dados.get(
                    "notas",
                    ""
                )
            }

        # -------------------------------------------------
        # JÁ ESTÁ ATUALIZADO
        # -------------------------------------------------

        return {
            "atualizacao": False,
            "versao_atual": versao_atual,
            "nova_versao": nova_versao,
            "notas": dados.get(
                "notas",
                ""
            )
        }

    # =====================================================
    # ERRO DE INTERNET / SERVIDOR
    # =====================================================

    except requests.exceptions.RequestException as erro:

        return {
            "atualizacao": False,
            "versao_atual": obter_versao_atual(),
            "erro": (
                "Não foi possível consultar "
                f"o servidor de atualização: {erro}"
            )
        }

    # =====================================================
    # ERRO GERAL
    # =====================================================

    except Exception as erro:

        return {
            "atualizacao": False,
            "versao_atual": obter_versao_atual(),
            "erro": str(
                erro
            )
        }


# =========================================================
# INICIAR UPDATER
# =========================================================

def iniciar_updater(
    download_url
):

    updater = os.path.join(
        BASE_DIR,
        "update",
        "updater.py"
    )

    try:

        if not os.path.exists(
            updater
        ):

            print(
                "UPDATER NÃO ENCONTRADO:",
                updater
            )

            return False

        subprocess.Popen(
            [
                sys.executable,
                updater,
                "--download",
                str(download_url),
                "--target",
                BASE_DIR
            ],
            creationflags=(
                subprocess.CREATE_NEW_PROCESS
            )
        )

        return True

    except Exception as erro:

        print(
            "ERRO AO INICIAR UPDATER:",
            erro
        )

        return False


# =========================================================
# TESTE DIRETO
# =========================================================

if __name__ == "__main__":

    resultado = (
        verificar_atualizacao()
    )

    print()
    print("=" * 55)
    print(" JARVIS UPDATE CHECK")
    print("=" * 55)

    print(
        "Versão atual:",
        resultado.get(
            "versao_atual",
            "--"
        )
    )

    print(
        "Nova versão:",
        resultado.get(
            "nova_versao",
            "--"
        )
    )

    print(
        "Atualização:",
        resultado.get(
            "atualizacao",
            False
        )
    )

    if resultado.get(
        "notas"
    ):

        print(
            "Notas:",
            resultado["notas"]
        )

    if resultado.get(
        "erro"
    ):

        print(
            "Erro:",
            resultado["erro"]
        )

    print("=" * 55)