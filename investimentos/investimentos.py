# =========================================================
# JARVIS - MÓDULO DE INVESTIMENTOS
# =========================================================

class InvestimentosJARVIS:

    def __init__(
        self,
        cerebro=None,
        economia=None
    ):

        self.cerebro = cerebro
        self.economia = economia

    # =====================================================
    # ANÁLISE EDUCACIONAL
    # =====================================================

    def sugerir_alocacao_educacional(
        self,
        valor,
        perfil="Moderado",
        horizonte="Médio prazo",
        reserva_pronta=False
    ):

        valor = float(valor)

        if valor <= 0:

            raise ValueError(
                "O valor para análise deve ser maior que zero."
            )

        # =================================================
        # PERFIL CONSERVADOR
        # =================================================

        if perfil == "Conservador":

            if horizonte == "Curto prazo":

                distribuicao = [
                    {
                        "categoria": "Reserva de liquidez",
                        "percentual": 70,
                        "valor": valor * 0.70,
                        "exemplos": [
                            "Tesouro Selic",
                            "CDB com liquidez diária"
                        ]
                    },
                    {
                        "categoria": "Renda fixa",
                        "percentual": 30,
                        "valor": valor * 0.30,
                        "exemplos": [
                            "CDB",
                            "LCI/LCA",
                            "Tesouro Direto"
                        ]
                    }
                ]

            elif horizonte == "Médio prazo":

                distribuicao = [
                    {
                        "categoria": "Renda fixa pós-fixada",
                        "percentual": 50,
                        "valor": valor * 0.50,
                        "exemplos": [
                            "CDB",
                            "Tesouro Selic"
                        ]
                    },
                    {
                        "categoria": "Renda fixa indexada à inflação",
                        "percentual": 30,
                        "valor": valor * 0.30,
                        "exemplos": [
                            "Tesouro IPCA+"
                        ]
                    },
                    {
                        "categoria": "Liquidez",
                        "percentual": 20,
                        "valor": valor * 0.20,
                        "exemplos": [
                            "CDB com liquidez diária"
                        ]
                    }
                ]

            else:

                distribuicao = [
                    {
                        "categoria": "Renda fixa",
                        "percentual": 40,
                        "valor": valor * 0.40,
                        "exemplos": [
                            "Tesouro Direto",
                            "CDB"
                        ]
                    },
                    {
                        "categoria": "Inflação",
                        "percentual": 35,
                        "valor": valor * 0.35,
                        "exemplos": [
                            "Tesouro IPCA+"
                        ]
                    },
                    {
                        "categoria": "Renda variável diversificada",
                        "percentual": 15,
                        "valor": valor * 0.15,
                        "exemplos": [
                            "ETFs amplos"
                        ]
                    },
                    {
                        "categoria": "Liquidez",
                        "percentual": 10,
                        "valor": valor * 0.10,
                        "exemplos": [
                            "CDB com liquidez diária"
                        ]
                    }
                ]

            prioridade = (
                "Preservação de capital e liquidez"
            )

            motivo = (
                "Para um perfil conservador, o JARVIS "
                "prioriza instrumentos de menor volatilidade, "
                "liquidez e proteção do patrimônio."
            )

        # =================================================
        # PERFIL MODERADO
        # =================================================

        elif perfil == "Moderado":

            if horizonte == "Curto prazo":

                distribuicao = [
                    {
                        "categoria": "Liquidez",
                        "percentual": 55,
                        "valor": valor * 0.55,
                        "exemplos": [
                            "Tesouro Selic",
                            "CDB com liquidez diária"
                        ]
                    },
                    {
                        "categoria": "Renda fixa",
                        "percentual": 30,
                        "valor": valor * 0.30,
                        "exemplos": [
                            "CDB",
                            "LCI/LCA"
                        ]
                    },
                    {
                        "categoria": "Renda variável",
                        "percentual": 15,
                        "valor": valor * 0.15,
                        "exemplos": [
                            "ETFs diversificados"
                        ]
                    }
                ]

            elif horizonte == "Médio prazo":

                distribuicao = [
                    {
                        "categoria": "Renda fixa",
                        "percentual": 40,
                        "valor": valor * 0.40,
                        "exemplos": [
                            "CDB",
                            "Tesouro Selic"
                        ]
                    },
                    {
                        "categoria": "Inflação",
                        "percentual": 25,
                        "valor": valor * 0.25,
                        "exemplos": [
                            "Tesouro IPCA+"
                        ]
                    },
                    {
                        "categoria": "Renda variável",
                        "percentual": 25,
                        "valor": valor * 0.25,
                        "exemplos": [
                            "ETFs",
                            "Fundos imobiliários"
                        ]
                    },
                    {
                        "categoria": "Liquidez",
                        "percentual": 10,
                        "valor": valor * 0.10,
                        "exemplos": [
                            "CDB com liquidez diária"
                        ]
                    }
                ]

            else:

                distribuicao = [
                    {
                        "categoria": "Renda fixa",
                        "percentual": 30,
                        "valor": valor * 0.30,
                        "exemplos": [
                            "Tesouro Direto",
                            "CDB"
                        ]
                    },
                    {
                        "categoria": "Inflação",
                        "percentual": 25,
                        "valor": valor * 0.25,
                        "exemplos": [
                            "Tesouro IPCA+"
                        ]
                    },
                    {
                        "categoria": "ETFs diversificados",
                        "percentual": 25,
                        "valor": valor * 0.25,
                        "exemplos": [
                            "ETFs de mercado amplo"
                        ]
                    },
                    {
                        "categoria": "Fundos imobiliários",
                        "percentual": 10,
                        "valor": valor * 0.10,
                        "exemplos": [
                            "FIIs diversificados"
                        ]
                    },
                    {
                        "categoria": "Liquidez",
                        "percentual": 10,
                        "valor": valor * 0.10,
                        "exemplos": [
                            "Tesouro Selic",
                            "CDB"
                        ]
                    }
                ]

            prioridade = (
                "Equilíbrio entre segurança e crescimento"
            )

            motivo = (
                "Para um perfil moderado, o JARVIS busca "
                "equilibrar renda fixa, proteção contra inflação "
                "e exposição controlada à renda variável."
            )

        # =================================================
        # PERFIL ARROJADO
        # =================================================

        elif perfil == "Arrojado":

            if horizonte == "Curto prazo":

                distribuicao = [
                    {
                        "categoria": "Liquidez",
                        "percentual": 45,
                        "valor": valor * 0.45,
                        "exemplos": [
                            "Tesouro Selic",
                            "CDB com liquidez diária"
                        ]
                    },
                    {
                        "categoria": "Renda variável",
                        "percentual": 35,
                        "valor": valor * 0.35,
                        "exemplos": [
                            "ETFs diversificados",
                            "Ações"
                        ]
                    },
                    {
                        "categoria": "FIIs",
                        "percentual": 20,
                        "valor": valor * 0.20,
                        "exemplos": [
                            "FIIs diversificados"
                        ]
                    }
                ]

            elif horizonte == "Médio prazo":

                distribuicao = [
                    {
                        "categoria": "Renda fixa",
                        "percentual": 25,
                        "valor": valor * 0.25,
                        "exemplos": [
                            "Tesouro Selic",
                            "CDB"
                        ]
                    },
                    {
                        "categoria": "ETFs",
                        "percentual": 30,
                        "valor": valor * 0.30,
                        "exemplos": [
                            "ETFs amplos",
                            "ETFs internacionais"
                        ]
                    },
                    {
                        "categoria": "Ações",
                        "percentual": 25,
                        "valor": valor * 0.25,
                        "exemplos": [
                            "Ações diversificadas"
                        ]
                    },
                    {
                        "categoria": "Fundos imobiliários",
                        "percentual": 20,
                        "valor": valor * 0.20,
                        "exemplos": [
                            "FIIs diversificados"
                        ]
                    }
                ]

            else:

                distribuicao = [
                    {
                        "categoria": "Renda fixa",
                        "percentual": 20,
                        "valor": valor * 0.20,
                        "exemplos": [
                            "Tesouro Direto",
                            "CDB"
                        ]
                    },
                    {
                        "categoria": "ETFs diversificados",
                        "percentual": 30,
                        "valor": valor * 0.30,
                        "exemplos": [
                            "ETFs de mercado amplo"
                        ]
                    },
                    {
                        "categoria": "Ações",
                        "percentual": 25,
                        "valor": valor * 0.25,
                        "exemplos": [
                            "Ações diversificadas"
                        ]
                    },
                    {
                        "categoria": "FIIs",
                        "percentual": 15,
                        "valor": valor * 0.15,
                        "exemplos": [
                            "FIIs diversificados"
                        ]
                    },
                    {
                        "categoria": "Exposição internacional",
                        "percentual": 10,
                        "valor": valor * 0.10,
                        "exemplos": [
                            "ETFs internacionais"
                        ]
                    }
                ]

            prioridade = (
                "Crescimento patrimonial no longo prazo"
            )

            motivo = (
                "Para um perfil arrojado e horizonte maior, "
                "o JARVIS considera uma exposição maior à renda "
                "variável, mantendo alguma diversificação em "
                "renda fixa."
            )

        else:

            raise ValueError(
                "Perfil de investimento inválido."
            )

        # =================================================
        # RESERVA DE EMERGÊNCIA
        # =================================================

        if not reserva_pronta:

            prioridade = (
                "Construção da reserva de emergência"
            )

            motivo = (
                "Antes de aumentar a exposição a investimentos "
                "de maior risco, o JARVIS recomenda estudar a "
                "formação de uma reserva de emergência com "
                "alta liquidez e baixo risco."
            )

        # =================================================
        # RESULTADO
        # =================================================

        return {
            "perfil": perfil,
            "horizonte": horizonte,
            "valor_analisado": valor,
            "prioridade": prioridade,
            "motivo": motivo,
            "distribuicao": distribuicao,
            "reserva_pronta": reserva_pronta
        }

    # =====================================================
    # ANÁLISE SIMPLES
    # =====================================================

    def analisar_valor(
        self,
        valor,
        perfil="Moderado"
    ):

        return self.sugerir_alocacao_educacional(
            valor=valor,
            perfil=perfil,
            horizonte="Médio prazo",
            reserva_pronta=False
        )