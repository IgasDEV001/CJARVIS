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
# CONFIGURAÇÃO DO GITHUB
# =========================================================

GITHUB_USUARIO = "IgasDEV001"

GITHUB_REPOSITORIO = "CJARVIS"


URL_RELEASES = (
    f"https://api.github.com/repos/"
    f"{GITHUB_USUARIO}/"
    f"{GITHUB_REPOSITORIO}/releases/latest"
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
# NORMALIZAR VERSÃO
# =========================================================

def normalizar_versao(
    versao
):

    versao = str(
        versao
    ).strip()

    if versao.startswith("v"):

        versao = versao[1:]

    return versao


# =========================================================
# COMPARAR VERSÕES
# =========================================================

def comparar_versoes(
    atual,
    nova
):

    try:

        atual = normalizar_versao(
            atual
        )

        nova = normalizar_versao(
            nova
        )

        atual = tuple(
            int(
                parte
            )
            for parte in atual.split(".")
        )

        nova = tuple(
            int(
                parte
            )
            for parte in nova.split(".")
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
            URL_RELEASES,
            timeout=10,
            headers={
                "Accept": (
                    "application/vnd.github+json"
                )
            }
        )

        resposta.raise_for_status()

        dados = resposta.json()

        versao_atual = (
            obter_versao_atual()
        )

        tag = str(
            dados.get(
                "tag_name",
                ""
            )
        ).strip()

        nova_versao = normalizar_versao(
            tag
        )

        nome_release = dados.get(
            "name",
            ""
        )

        notas = dados.get(
            "body",
            ""
        )

        assets = dados.get(
            "assets",
            []
        )

        download_url = None

        # =================================================
        # PROCURAR CJARVIS.ZIP
        # =================================================

        for asset in assets:

            nome = str(
                asset.get(
                    "name",
                    ""
                )
            ).lower()

            if nome == "cjarvis.zip":

                download_url = asset.get(
                    "browser_download_url"
                )

                break

        # =================================================
        # SEM NOVA VERSÃO
        # =================================================

        if not nova_versao:

            return {
                "atualizacao": False,
                "versao_atual": versao_atual,
                "erro": (
                    "A Release não possui "
                    "uma tag válida."
                )
            }

        # =================================================
        # NOVA VERSÃO
        # =================================================

        if comparar_versoes(
            versao_atual,
            nova_versao
        ):

            return {
                "atualizacao": True,
                "versao_atual": versao_atual,
                "nova_versao": nova_versao,
                "nome_release": nome_release,
                "download": download_url,
                "notas": notas
            }

        # =================================================
        # ATUALIZADO
        # =================================================

        return {
            "atualizacao": False,
            "versao_atual": versao_atual,
            "nova_versao": nova_versao,
            "nome_release": nome_release,
            "download": download_url,
            "notas": notas
        }

    except requests.exceptions.RequestException as erro:

        return {
            "atualizacao": False,
            "versao_atual": obter_versao_atual(),
            "erro": (
                "Não foi possível consultar "
                "o GitHub: "
                f"{erro}"
            )
        }

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

    if not download_url:

        print(
            "ERRO: URL do ZIP não encontrada."
        )

        return False

    updater = os.path.join(
        BASE_DIR,
        "update",
        "updater.py"
    )

    if not os.path.exists(
        updater
    ):

        print(
            "ERRO: updater.py não encontrado:",
            updater
        )

        return False

    try:

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
    print("=" * 60)
    print(" JARVIS UPDATE CHECK")
    print("=" * 60)

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

    print(
        "Download:",
        resultado.get(
            "download",
            "--"
        )
    )

    if resultado.get("notas"):

        print()
        print("Notas:")
        print(
            resultado["notas"]
        )

    if resultado.get("erro"):

        print()
        print(
            "Erro:",
            resultado["erro"]
        )

    print("=" * 60)