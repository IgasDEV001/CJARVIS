# =========================================================
# JARVIS FINANCIAL BRAIN
# =========================================================

from datetime import date
import calendar


class CerebroFinanceiro:

    def __init__(
        self,
        transacoes=None,
        metas=None,
        configuracoes=None
    ):

        self.transacoes = transacoes or []
        self.metas = metas or []
        self.configuracoes = configuracoes or {}

    # =====================================================
    # ATUALIZAR DADOS
    # =====================================================

    def atualizar_dados(
        self,
        transacoes=None,
        metas=None,
        configuracoes=None
    ):

        if transacoes is not None:
            self.transacoes = transacoes

        if metas is not None:
            self.metas = metas

        if configuracoes is not None:
            self.configuracoes = configuracoes

    # =====================================================
    # FILTRAR MÊS
    # =====================================================

    def filtrar_mes(
        self,
        ano,
        mes
    ):

        resultado = []

        for transacao in self.transacoes:

            data_texto = str(
                transacao.get(
                    "data",
                    ""
                )
            )

            if not data_texto:
                continue

            try:

                ano_data = int(
                    data_texto[:4]
                )

                mes_data = int(
                    data_texto[5:7]
                )

            except (
                ValueError,
                TypeError
            ):

                continue

            if (
                ano_data == ano
                and
                mes_data == mes
            ):

                resultado.append(
                    transacao
                )

        return resultado

    # =====================================================
    # RESUMO FINANCEIRO
    # =====================================================

    def calcular_resumo(
        self,
        ano,
        mes
    ):

        transacoes = self.filtrar_mes(
            ano,
            mes
        )

        receitas = 0.0
        despesas = 0.0

        for transacao in transacoes:

            valor = float(
                transacao.get(
                    "valor",
                    0
                )
            )

            if transacao.get("tipo") == "receita":

                receitas += valor

            elif transacao.get("tipo") == "despesa":

                despesas += valor

        saldo = (
            receitas
            -
            despesas
        )

        percentual = 0.0

        if receitas > 0:

            percentual = (
                despesas
                /
                receitas
            ) * 100

        return {
            "receitas": receitas,
            "despesas": despesas,
            "saldo": saldo,
            "percentual_despesas": percentual,
            "quantidade_transacoes": len(transacoes)
        }

    # =====================================================
    # CATEGORIAS
    # =====================================================

    def analisar_categorias(
        self,
        ano,
        mes
    ):

        transacoes = self.filtrar_mes(
            ano,
            mes
        )

        categorias = {}

        for transacao in transacoes:

            if transacao.get("tipo") != "despesa":
                continue

            categoria = transacao.get(
                "categoria",
                "Outros"
            )

            valor = float(
                transacao.get(
                    "valor",
                    0
                )
            )

            categorias[categoria] = (
                categorias.get(
                    categoria,
                    0.0
                )
                +
                valor
            )

        ordenadas = sorted(
            categorias.items(),
            key=lambda item: item[1],
            reverse=True
        )

        return ordenadas

    # =====================================================
    # MAIOR CATEGORIA
    # =====================================================

    def maior_categoria(
        self,
        ano,
        mes
    ):

        categorias = self.analisar_categorias(
            ano,
            mes
        )

        if not categorias:
            return None

        nome, valor = categorias[0]

        return {
            "nome": nome,
            "valor": valor
        }

    # =====================================================
    # MÉDIA DIÁRIA
    # =====================================================

    def media_diaria_despesas(
        self,
        ano,
        mes
    ):

        resumo = self.calcular_resumo(
            ano,
            mes
        )

        hoje = date.today()

        if (
            ano == hoje.year
            and
            mes == hoje.month
        ):

            dias = hoje.day

        else:

            dias = calendar.monthrange(
                ano,
                mes
            )[1]

        dias = max(
            1,
            dias
        )

        return (
            resumo["despesas"]
            /
            dias
        )

    # =====================================================
    # PREVISÃO
    # =====================================================

    def previsao_mes(
        self,
        ano,
        mes
    ):

        resumo = self.calcular_resumo(
            ano,
            mes
        )

        hoje = date.today()

        dias_mes = calendar.monthrange(
            ano,
            mes
        )[1]

        if (
            ano == hoje.year
            and
            mes == hoje.month
        ):

            dias_passados = max(
                1,
                hoje.day
            )

            dias_restantes = max(
                0,
                dias_mes
                -
                hoje.day
            )

        elif (
            ano > hoje.year
            or
            (
                ano == hoje.year
                and
                mes > hoje.month
            )
        ):

            dias_passados = 1
            dias_restantes = dias_mes - 1

        else:

            dias_passados = dias_mes
            dias_restantes = 0

        media = (
            resumo["despesas"]
            /
            max(
                1,
                dias_passados
            )
        )

        gastos_futuros = (
            media
            *
            dias_restantes
        )

        despesa_projetada = (
            resumo["despesas"]
            +
            gastos_futuros
        )

        saldo_projetado = (
            resumo["receitas"]
            -
            despesa_projetada
        )

        return {
            "media_diaria": media,
            "gastos_futuros": gastos_futuros,
            "despesa_projetada": despesa_projetada,
            "saldo_projetado": saldo_projetado,
            "dias_restantes": dias_restantes
        }

    # =====================================================
    # RESERVA
    # =====================================================

    def percentual_reserva(self):

        valor = self.configuracoes.get(
            "reserva",
            "20%"
        )

        try:

            valor = float(
                str(valor).replace(
                    "%",
                    ""
                )
            )

            return valor / 100

        except (
            ValueError,
            TypeError
        ):

            return 0.20

    # =====================================================
    # LIMITE DIÁRIO
    # =====================================================

    def limite_diario(
        self,
        ano,
        mes
    ):

        resumo = self.calcular_resumo(
            ano,
            mes
        )

        previsao = self.previsao_mes(
            ano,
            mes
        )

        saldo = resumo["saldo"]

        if saldo <= 0:

            return 0.0

        reserva = (
            saldo
            *
            self.percentual_reserva()
        )

        disponivel = (
            saldo
            -
            reserva
        )

        dias = max(
            1,
            previsao["dias_restantes"]
        )

        return (
            disponivel
            /
            dias
        )

    # =====================================================
    # METAS
    # =====================================================

    def analisar_metas(self):

        resultado = []

        for meta in self.metas:

            objetivo = float(
                meta.get(
                    "objetivo",
                    0
                )
            )

            guardado = float(
                meta.get(
                    "guardado",
                    0
                )
            )

            restante = max(
                0,
                objetivo
                -
                guardado
            )

            percentual = 0.0

            if objetivo > 0:

                percentual = (
                    guardado
                    /
                    objetivo
                ) * 100

            resultado.append({
                "nome": meta.get(
                    "nome",
                    "Meta"
                ),
                "objetivo": objetivo,
                "guardado": guardado,
                "restante": restante,
                "percentual": percentual
            })

        resultado.sort(
            key=lambda item: item["percentual"]
        )

        return resultado

    # =====================================================
    # SCORE FINANCEIRO
    # =====================================================

    def calcular_score(
        self,
        ano,
        mes
    ):

        resumo = self.calcular_resumo(
            ano,
            mes
        )

        score = 100

        # -----------------------------------------------
        # SALDO
        # -----------------------------------------------

        if resumo["saldo"] < 0:

            score -= 35

        elif resumo["saldo"] == 0:

            score -= 20

        # -----------------------------------------------
        # COMPROMETIMENTO DA RECEITA
        # -----------------------------------------------

        percentual = (
            resumo["percentual_despesas"]
        )

        if percentual >= 100:

            score -= 30

        elif percentual >= 90:

            score -= 20

        elif percentual >= 80:

            score -= 12

        elif percentual >= 70:

            score -= 6

        # -----------------------------------------------
        # METAS
        # -----------------------------------------------

        if self.metas:

            progresso_total = 0.0

            for meta in self.metas:

                objetivo = float(
                    meta.get(
                        "objetivo",
                        0
                    )
                )

                guardado = float(
                    meta.get(
                        "guardado",
                        0
                    )
                )

                if objetivo > 0:

                    progresso_total += (
                        guardado
                        /
                        objetivo
                    )

            media_metas = (
                progresso_total
                /
                len(self.metas)
            )

            if media_metas >= 0.75:

                score += 5

            elif media_metas < 0.25:

                score -= 8

        # -----------------------------------------------
        # LIMITES
        # -----------------------------------------------

        score = max(
            0,
            min(
                100,
                score
            )
        )

        if score >= 85:

            status = "EXCELENTE"

        elif score >= 70:

            status = "SAUDÁVEL"

        elif score >= 50:

            status = "ATENÇÃO"

        elif score >= 30:

            status = "RISCO"

        else:

            status = "CRÍTICO"

        return {
            "score": score,
            "status": status
        }

    # =====================================================
    # RECOMENDAÇÕES
    # =====================================================

    def gerar_recomendacoes(
        self,
        ano,
        mes
    ):

        resumo = self.calcular_resumo(
            ano,
            mes
        )

        previsao = self.previsao_mes(
            ano,
            mes
        )

        recomendacoes = []

        # -----------------------------------------------
        # SALDO
        # -----------------------------------------------

        if resumo["saldo"] < 0:

            recomendacoes.append({
                "nivel": "critico",
                "titulo": "Saldo negativo",
                "mensagem": (
                    "Suas despesas ultrapassaram "
                    "suas receitas neste período."
                )
            })

        # -----------------------------------------------
        # PROJEÇÃO
        # -----------------------------------------------

        if previsao["saldo_projetado"] < 0:

            recomendacoes.append({
                "nivel": "critico",
                "titulo": "Risco de saldo negativo",
                "mensagem": (
                    "Mantendo o ritmo atual de gastos, "
                    "a projeção indica saldo negativo."
                )
            })

        # -----------------------------------------------
        # RECEITA
        # -----------------------------------------------

        if resumo["receitas"] > 0:

            percentual = (
                resumo["percentual_despesas"]
            )

            if percentual >= 90:

                recomendacoes.append({
                    "nivel": "atencao",
                    "titulo": "Receita muito comprometida",
                    "mensagem": (
                        f"{percentual:.1f}% da sua receita "
                        "já está comprometida."
                    )
                })

            elif percentual <= 60:

                recomendacoes.append({
                    "nivel": "positivo",
                    "titulo": "Boa margem financeira",
                    "mensagem": (
                        "Seu nível atual de despesas "
                        "está relativamente controlado."
                    )
                })

        # -----------------------------------------------
        # MAIOR CATEGORIA
        # -----------------------------------------------

        categoria = self.maior_categoria(
            ano,
            mes
        )

        if categoria:

            percentual_categoria = 0.0

            if resumo["despesas"] > 0:

                percentual_categoria = (
                    categoria["valor"]
                    /
                    resumo["despesas"]
                ) * 100

            if percentual_categoria >= 40:

                recomendacoes.append({
                    "nivel": "atencao",
                    "titulo": "Concentração de gastos",
                    "mensagem": (
                        f"A categoria "
                        f"{categoria['nome']} "
                        f"representa "
                        f"{percentual_categoria:.1f}% "
                        "das suas despesas."
                    )
                })

        # -----------------------------------------------
        # LIMITE DIÁRIO
        # -----------------------------------------------

        limite = self.limite_diario(
            ano,
            mes
        )

        if limite > 0:

            recomendacoes.append({
                "nivel": "informacao",
                "titulo": "Limite diário",
                "mensagem": (
                    f"Seu limite diário recomendado é "
                    f"R$ {limite:,.2f}."
                )
            })

        # -----------------------------------------------
        # METAS
        # -----------------------------------------------

        metas = self.analisar_metas()

        if metas:

            meta = metas[0]

            if meta["percentual"] < 25:

                recomendacoes.append({
                    "nivel": "atencao",
                    "titulo": "Meta atrasada",
                    "mensagem": (
                        f"A meta "
                        f"{meta['nome']} "
                        "ainda possui pouco progresso."
                    )
                })

        # -----------------------------------------------
        # CASO NORMAL
        # -----------------------------------------------

        if not recomendacoes: 

            recomendacoes.append({
                "nivel": "positivo",
                "titulo": "Situação estável",
                "mensagem": (
                    "Não identifiquei nenhum problema "
                    "financeiro relevante neste momento."
                )
            })

        return recomendacoes

    # =====================================================
    # RESUMO PARA O JARVIS
    # =====================================================

    def gerar_diagnostico(
        self,
        ano,
        mes
    ):

        resumo = self.calcular_resumo(
            ano,
            mes
        )

        previsao = self.previsao_mes(
            ano,
            mes
        )

        score = self.calcular_score(
            ano,
            mes
        )

        categoria = self.maior_categoria(
            ano,
            mes
        )

        limite = self.limite_diario(
            ano,
            mes
        )

        diagnostico = {
            "resumo": resumo,
            "previsao": previsao,
            "score": score,
            "maior_categoria": categoria,
            "limite_diario": limite,
            "recomendacoes": self.gerar_recomendacoes(
                ano,
                mes
            )
        }

        return diagnostico

    # =====================================================
    # CHAT FINANCEIRO
    # =====================================================

    def responder(
        self,
        pergunta,
        ano,
        mes
    ):

        pergunta = (
            str(pergunta)
            .lower()
            .strip()
        )

        resumo = self.calcular_resumo(
            ano,
            mes
        )

        previsao = self.previsao_mes(
            ano,
            mes
        )

        categoria = self.maior_categoria(
            ano,
            mes
        )

        limite = self.limite_diario(
            ano,
            mes
        )

        # -------------------------------------------------
        # SALDO
        # -------------------------------------------------

        if (
            "saldo" in pergunta
            or
            "quanto tenho" in pergunta
        ):

            return (
                "Seu saldo atual é "
                f"R$ {resumo['saldo']:,.2f}."
            )

        # -------------------------------------------------
        # GASTOS
        # -------------------------------------------------

        if (
            "quanto gastei" in pergunta
            or
            "quanto estou gastando" in pergunta
            or
            "despesas" in pergunta
        ):

            return (
                "Até agora você gastou "
                f"R$ {resumo['despesas']:,.2f} "
                f"neste período."
            )

        # -------------------------------------------------
        # RECEITAS
        # -------------------------------------------------

        if (
            "receita" in pergunta
            or
            "quanto recebi" in pergunta
        ):

            return (
                "Suas receitas neste período "
                f"somam R$ {resumo['receitas']:,.2f}."
            )

        # -------------------------------------------------
        # LIMITE
        # -------------------------------------------------

        if (
            "quanto posso gastar" in pergunta
            or
            "limite" in pergunta
            or
            "posso gastar" in pergunta
        ):

            if limite <= 0:

                return (
                    "No momento, não recomendo "
                    "novos gastos. Seu saldo não "
                    "possui margem suficiente."
                )

            return (
                "Pelos dados atuais, seu limite "
                f"diário recomendado é "
                f"R$ {limite:,.2f}."
            )

        # -------------------------------------------------
        # PROJEÇÃO
        # -------------------------------------------------

        if (
            "previsão" in pergunta
            or
            "previsao" in pergunta
            or
            "fim do mês" in pergunta
            or
            "fim do mes" in pergunta
        ):

            return (
                "Mantendo seu ritmo atual, "
                "a projeção de saldo para o "
                f"fechamento é "
                f"R$ {previsao['saldo_projetado']:,.2f}."
            )

        # -------------------------------------------------
        # MAIOR GASTO
        # -------------------------------------------------

        if (
            "maior gasto" in pergunta
            or
            "onde gasto mais" in pergunta
            or
            "categoria" in pergunta
        ):

            if categoria is None:

                return (
                    "Ainda não encontrei despesas "
                    "suficientes para identificar "
                    "uma categoria dominante."
                )

            return (
                f"Sua maior categoria de gastos é "
                f"{categoria['nome']}, com "
                f"R$ {categoria['valor']:,.2f}."
            )

        # -------------------------------------------------
        # SCORE
        # -------------------------------------------------

        if (
            "score" in pergunta
            or
            "saúde financeira" in pergunta
            or
            "saude financeira" in pergunta
        ):

            score = self.calcular_score(
                ano,
                mes
            )

            return (
                f"Seu JARVIS Score é "
                f"{score['score']}/100. "
                f"Status: {score['status']}."
            )

        # -------------------------------------------------
        # RESPOSTA PADRÃO
        # -------------------------------------------------

        return (
            "Ainda não tenho uma resposta específica "
            "para essa pergunta. Tente perguntar sobre "
            "saldo, despesas, receitas, limite diário, "
            "previsão, maior gasto ou score."
        )