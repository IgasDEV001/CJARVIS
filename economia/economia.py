import json
import os
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


# =========================================================
# ECONOMIA JARVIS
# =========================================================

class EconomiaJARVIS:

    """
    Motor de dados econômicos do JARVIS.

    Consulta dados públicos do Banco Central via SGS
    e mantém cache local para evitar consultas excessivas.
    """

    BCB_URL = (
        "https://api.bcb.gov.br/dados/serie/"
        "bcdata.sgs.{codigo}/dados"
    )

    CACHE_HORAS = 6

    SERIES = {
        "selic": 432,
        "ipca": 433,
        "dolar_ptax": 1
    }

    # =====================================================
    # INICIALIZAÇÃO
    # =====================================================

    def __init__(
        self,
        base_dir=None
    ):

        self.base_dir = (
            base_dir
            or
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        self.cache_dir = os.path.join(
            self.base_dir,
            "jarvis_cache"
        )

        os.makedirs(
            self.cache_dir,
            exist_ok=True
        )

    # =====================================================
    # CAMINHO DO CACHE
    # =====================================================

    def _cache_path(
        self,
        nome
    ):

        return os.path.join(
            self.cache_dir,
            f"{nome}.json"
        )

    # =====================================================
    # LER CACHE
    # =====================================================

    def _ler_cache(
        self,
        nome
    ):

        caminho = self._cache_path(
            nome
        )

        if not os.path.exists(
            caminho
        ):

            return None

        try:

            idade = (
                datetime.now().timestamp()
                -
                os.path.getmtime(
                    caminho
                )
            )

            if idade > (
                self.CACHE_HORAS * 3600
            ):

                return None

            with open(
                caminho,
                "r",
                encoding="utf-8"
            ) as arquivo:

                dados = json.load(
                    arquivo
                )

            if isinstance(
                dados,
                list
            ):

                return dados

        except (
            OSError,
            json.JSONDecodeError,
            TypeError
        ):

            return None

        return None

    # =====================================================
    # SALVAR CACHE
    # =====================================================

    def _salvar_cache(
        self,
        nome,
        dados
    ):

        try:

            with open(
                self._cache_path(nome),
                "w",
                encoding="utf-8"
            ) as arquivo:

                json.dump(
                    dados,
                    arquivo,
                    ensure_ascii=False,
                    indent=2
                )

        except (
            OSError,
            TypeError
        ):

            pass

    # =====================================================
    # CONVERTER NÚMERO
    # =====================================================

    @staticmethod
    def _converter_numero(
        valor
    ):

        try:

            texto = str(
                valor
            ).strip()

            texto = texto.replace(
                ",",
                "."
            )

            return float(
                texto
            )

        except (
            ValueError,
            TypeError
        ):

            return None

    # =====================================================
    # BUSCAR SÉRIE
    # =====================================================

    def buscar_serie(
        self,
        nome,
        ultimos=12,
        ignorar_cache=False
    ):

        if nome not in self.SERIES:

            raise ValueError(
                f"Série econômica desconhecida: {nome}"
            )

        if not ignorar_cache:

            cache = self._ler_cache(
                nome
            )

            if cache:

                return cache

        codigo = self.SERIES[
            nome
        ]

        url = (
            f"{self.BCB_URL.format(codigo=codigo)}"
            f"/ultimos/{int(ultimos)}"
            f"?formato=json"
        )

        requisicao = Request(
            url,
            headers={
                "User-Agent": "CJARVIS/1.0"
            }
        )

        try:

            with urlopen(
                requisicao,
                timeout=12
            ) as resposta:

                conteudo = (
                    resposta
                    .read()
                    .decode(
                        "utf-8"
                    )
                )

            dados = json.loads(
                conteudo
            )

            if not isinstance(
                dados,
                list
            ):

                return []

            self._salvar_cache(
                nome,
                dados
            )

            return dados

        except (
            HTTPError,
            URLError,
            TimeoutError,
            OSError,
            json.JSONDecodeError
        ):

            return []

    # =====================================================
    # ÚLTIMO REGISTRO
    # =====================================================

    def ultimo(
        self,
        nome
    ):

        dados = self.buscar_serie(
            nome,
            ultimos=12
        )

        if not dados:

            return None

        dados_validos = []

        for item in dados:

            if not isinstance(
                item,
                dict
            ):

                continue

            numero = (
                self._converter_numero(
                    item.get(
                        "valor"
                    )
                )
            )

            data = item.get(
                "data"
            )

            if numero is None or not data:

                continue

            dados_validos.append(
                {
                    "data": data,
                    "valor": numero
                }
            )

        if not dados_validos:

            return None

        dados_validos.sort(
            key=lambda item:
            item["data"]
        )

        return dados_validos[-1]

    # =====================================================
    # INDICADORES
    # =====================================================

    def indicadores(
        self,
        atualizar=False
    ):

        resultado = {}

        for nome in self.SERIES:

            dados = self.buscar_serie(
                nome,
                ultimos=12,
                ignorar_cache=atualizar
            )

            validos = []

            for item in dados:

                if not isinstance(
                    item,
                    dict
                ):

                    continue

                numero = (
                    self._converter_numero(
                        item.get(
                            "valor"
                        )
                    )
                )

                data = item.get(
                    "data"
                )

                if (
                    numero is None
                    or
                    not data
                ):

                    continue

                validos.append(
                    {
                        "data": data,
                        "valor": numero
                    }
                )

            validos.sort(
                key=lambda item:
                item["data"]
            )

            ultimo = (
                validos[-1]
                if validos
                else
                None
            )

            resultado[nome] = {
                "ultimo": ultimo,
                "historico": validos
            }

        resultado[
            "atualizado_em"
        ] = datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        )

        return resultado

    # =====================================================
    # ANÁLISE DO CENÁRIO
    # =====================================================

    def analisar_cenario(
        self,
        atualizar=False
    ):

        dados = self.indicadores(
            atualizar=atualizar
        )

        mensagens = []

        selic = (
            dados[
                "selic"
            ][
                "ultimo"
            ]
        )

        ipca = (
            dados[
                "ipca"
            ][
                "ultimo"
            ]
        )

        dolar = (
            dados[
                "dolar_ptax"
            ][
                "ultimo"
            ]
        )

        # =====================================================
        # SELIC
        # =====================================================

        if selic:

            valor = selic[
                "valor"
            ]

            if valor >= 12:

                mensagens.append(
                    "Juros básicos elevados. "
                    "A renda fixa merece atenção, "
                    "mas prazo, liquidez e tributação "
                    "precisam ser comparados."
                )

            elif valor <= 8:

                mensagens.append(
                    "A Selic está relativamente baixa. "
                    "Vale ampliar a análise de diversificação "
                    "e do prêmio de risco."
                )

            else:

                mensagens.append(
                    "A Selic está em uma faixa intermediária. "
                    "Compare retorno líquido, prazo e risco."
                )

        # =====================================================
        # IPCA
        # =====================================================

        if ipca:

            valor = ipca[
                "valor"
            ]

            mensagens.append(
                f"Último IPCA mensal disponível: "
                f"{valor:.2f}%."
            )

        # =====================================================
        # DÓLAR
        # =====================================================

        if dolar:

            mensagens.append(
                f"Último dólar PTAX de venda disponível: "
                f"R$ {dolar['valor']:.4f}."
            )

        # =====================================================
        # SEM DADOS
        # =====================================================

        if not mensagens:

            mensagens.append(
                "Os indicadores oficiais "
                "não puderam ser atualizados agora."
            )

        return {
            "indicadores": dados,
            "mensagens": mensagens,
            "atualizado_em": (
                dados[
                    "atualizado_em"
                ]
            )
        }

    # =====================================================
    # RESUMO PARA O DASHBOARD
    # =====================================================

    def resumo_dashboard(
        self,
        atualizar=False
    ):

        analise = self.analisar_cenario(
            atualizar=atualizar
        )

        indicadores = analise[
            "indicadores"
        ]

        selic = (
            indicadores[
                "selic"
            ][
                "ultimo"
            ]
        )

        ipca = (
            indicadores[
                "ipca"
            ][
                "ultimo"
            ]
        )

        dolar = (
            indicadores[
                "dolar_ptax"
            ][
                "ultimo"
            ]
        )

        return {
            "selic": (
                selic["valor"]
                if selic
                else
                None
            ),

            "ipca": (
                ipca["valor"]
                if ipca
                else
                None
            ),

            "dolar": (
                dolar["valor"]
                if dolar
                else
                None
            ),

            "atualizado_em": (
                analise[
                    "atualizado_em"
                ]
            ),

            "mensagens": (
                analise[
                    "mensagens"
                ]
            )
        }