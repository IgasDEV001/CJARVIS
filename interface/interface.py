import os
import json
import calendar
from datetime import date


# =========================================================
# DIRETÓRIO RAIZ DO PROJETO
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# =========================================================
# MATPLOTLIB
# =========================================================

os.environ["MPLCONFIGDIR"] = os.path.join(
    BASE_DIR,
    "matplotlib_config"
)

os.environ["MPL_IGNORE_SYSTEM_FONTS"] = "1"


# =========================================================
# CONFIGURAÇÕES
# =========================================================

ARQUIVO_CONFIG = os.path.join(
    BASE_DIR,
    "data",
    "jarvis_config.json"
)


# =========================================================
# IMPORTS INTERNOS
# =========================================================

from core.banco import BancoDados
from core.cerebro import CerebroFinanceiro

from economia.economia import EconomiaJARVIS

from investimentos.investimentos import InvestimentosJARVIS


try:
    from ia.jarvis_ia import JarvisIA
except ImportError:
    JarvisIA = None


try:
    from ia.jarvis_worker import JarvisWorker
except ImportError:
    JarvisWorker = None


try:
    from economia.economia_worker import EconomiaWorker
except ImportError:
    EconomiaWorker = None


# =========================================================
# PYSIDE6
# =========================================================

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QStackedWidget,
    QDialog,
    QLineEdit,
    QMessageBox,
    QComboBox,
    QDateEdit,
    QProgressBar,
    QScrollArea
)

from PySide6.QtCore import (
    Qt,
    QDate,
    QThread
)

from PySide6.QtGui import (
    QFont
)


# =========================================================
# JANELA PRINCIPAL
# =========================================================

class JanelaPrincipal(QMainWindow):

    def __init__(self):

        super().__init__()

        # =====================================================
        # BANCO
        # =====================================================

        self.banco = BancoDados()

        # =====================================================
        # CONFIGURAÇÕES
        # =====================================================

        self.configuracoes = (
            self.carregar_configuracoes()
        )

        # =====================================================
        # DADOS
        # =====================================================

        self.transacoes = []
        self.metas = []

        self.total_receitas = 0.0
        self.total_despesas = 0.0
        self.saldo_atual = 0.0

        # =====================================================
        # CÉREBRO
        # =====================================================

        self.cerebro = None

        try:

            self.cerebro = CerebroFinanceiro(
                transacoes=[],
                metas=[],
                configuracoes=self.configuracoes
            )

        except Exception:

            try:
                self.cerebro = CerebroFinanceiro()

            except Exception as erro:

                print(
                    "ERRO AO INICIAR CÉREBRO:",
                    erro
                )

        # =====================================================
        # ECONOMIA
        # =====================================================

        self.economia = None

        try:

            self.economia = EconomiaJARVIS(
                BASE_DIR
            )

        except Exception:

            try:
                self.economia = EconomiaJARVIS()

            except Exception as erro:

                print(
                    "ERRO AO INICIAR ECONOMIA:",
                    erro
                )

        # =====================================================
        # INVESTIMENTOS
        # =====================================================

        self.investimentos = None

        try:

            self.investimentos = (
                InvestimentosJARVIS(
                    cerebro=self.cerebro,
                    economia=self.economia
                )
            )

        except Exception:

            try:
                self.investimentos = (
                    InvestimentosJARVIS()
                )

            except Exception as erro:

                print(
                    "ERRO AO INICIAR INVESTIMENTOS:",
                    erro
                )

        # =====================================================
        # IA
        # =====================================================

        self.jarvis_ia = None

        if JarvisIA is not None:

            try:
                self.jarvis_ia = JarvisIA()

            except Exception as erro:

                print(
                    "ERRO AO INICIAR IA DO JARVIS:",
                    erro
                )

        # =====================================================
        # THREAD IA
        # =====================================================

        self.thread_jarvis = None
        self.worker_jarvis = None
        self.chat_processando = False

        # =====================================================
        # THREAD ECONOMIA
        # =====================================================

        self.thread_economia = None
        self.worker_economia = None
        self.economia_processando = False

        # =====================================================
        # JANELA
        # =====================================================

        self.setWindowTitle(
            "JARVIS Financeiro"
        )

        self.setMinimumSize(
            1200,
            750
        )

        self.resize(
            1400,
            850
        )

        # =====================================================
        # DASHBOARD
        # =====================================================

        self.ano_dashboard = (
            QDate.currentDate().year()
        )

        self.mes_dashboard = (
            QDate.currentDate().month()
        )

        self.transacoes_dashboard = []

        self.total_receitas_dashboard = 0.0
        self.total_despesas_dashboard = 0.0
        self.saldo_dashboard = 0.0

        # =====================================================
        # COMPARAÇÃO
        # =====================================================

        self.receitas_mes_anterior = 0.0
        self.despesas_mes_anterior = 0.0
        self.saldo_mes_anterior = 0.0

        # =====================================================
        # PROJEÇÃO
        # =====================================================

        self.dias_mes_projecao = 0
        self.dias_passados_projecao = 0
        self.dias_restantes_projecao = 0

        self.media_diaria_despesas = 0.0
        self.despesa_projetada = 0.0
        self.saldo_projetado = 0.0
        self.percentual_despesa_projetada = 0.0

        self.status_projecao = "NORMAL"

        # =====================================================
        # RELATÓRIOS
        # =====================================================

        self.relatorios_inicializados = False

        self.ano_relatorio = (
            QDate.currentDate().year()
        )

        self.mes_relatorio = (
            QDate.currentDate().month()
        )

        self.transacoes_relatorio = []

        self.total_receitas_relatorio = 0.0
        self.total_despesas_relatorio = 0.0
        self.saldo_relatorio = 0.0

        # =====================================================
        # MENU
        # =====================================================

        self.botoes_menu = []

        # =====================================================
        # INTERFACE
        # =====================================================

        self.criar_interface()

        # =====================================================
        # DADOS
        # =====================================================

        self.carregar_dados()
        self.carregar_metas()
        self.atualizar_cerebro()
        self.carregar_configuracoes_na_interface()

        # =====================================================
        # MENU INICIAL
        # =====================================================

        self.marcar_menu_ativo(0)

    # =========================================================
    # CONFIGURAÇÕES PADRÃO
    # =========================================================

    def configuracoes_padrao(self):

        return {
            "tema": "JARVIS Dark",
            "animacoes": "Ativados",
            "alertas": "Ativados",
            "sensibilidade_alertas": "Normal",
            "moeda": "BRL - Real brasileiro",
            "reserva": "20%",
            "inteligencia": "Normal",
            "mensagens": "Ativadas"
        }

    # =========================================================
    # CARREGAR CONFIGURAÇÕES
    # =========================================================

    def carregar_configuracoes(self):

        padrao = self.configuracoes_padrao()

        os.makedirs(
            os.path.join(
                BASE_DIR,
                "data"
            ),
            exist_ok=True
        )

        if not os.path.exists(
            ARQUIVO_CONFIG
        ):

            return padrao

        try:

            with open(
                ARQUIVO_CONFIG,
                "r",
                encoding="utf-8"
            ) as arquivo:

                dados = json.load(
                    arquivo
                )

            if not isinstance(
                dados,
                dict
            ):

                return padrao

            for chave, valor in padrao.items():

                if chave not in dados:

                    dados[chave] = valor

            return dados

        except (
            json.JSONDecodeError,
            OSError,
            TypeError
        ):

            return padrao

    # =========================================================
    # SALVAR CONFIGURAÇÕES
    # =========================================================

    def salvar_arquivo_configuracoes(self):

        try:

            os.makedirs(
                os.path.join(
                    BASE_DIR,
                    "data"
                ),
                exist_ok=True
            )

            with open(
                ARQUIVO_CONFIG,
                "w",
                encoding="utf-8"
            ) as arquivo:

                json.dump(
                    self.configuracoes,
                    arquivo,
                    ensure_ascii=False,
                    indent=4
                )

            return True

        except (
            OSError,
            TypeError
        ):

            return False

    # =========================================================
    # ATUALIZAR CÉREBRO
    # =========================================================

    def atualizar_cerebro(self):

        if self.cerebro is None:

            return

        try:

            self.cerebro.atualizar_dados(
                transacoes=self.transacoes,
                metas=self.metas,
                configuracoes=self.configuracoes
            )

        except Exception as erro:

            print(
                "ERRO AO ATUALIZAR CÉREBRO:",
                erro
            )

    # =========================================================
    # INTERFACE
    # =========================================================

    def criar_interface(self):

        central = QWidget()

        central.setObjectName(
            "central_principal"
        )

        central.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        self.setCentralWidget(
            central
        )

        layout_principal = QHBoxLayout(
            central
        )

        layout_principal.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout_principal.setSpacing(
            0
        )

        self.menu = self.criar_menu()

        self.paginas = QStackedWidget()

        self.pagina_dashboard = (
            self.criar_dashboard()
        )

        self.pagina_financas = (
            self.criar_financas()
        )

        self.pagina_relatorios = (
            self.criar_relatorios()
        )

        self.pagina_metas = (
            self.criar_metas()
        )

        self.pagina_economia = (
            self.criar_economia()
        )

        self.pagina_configuracoes = (
            self.criar_configuracoes()
        )

        self.paginas.addWidget(
            self.pagina_dashboard
        )

        self.paginas.addWidget(
            self.pagina_financas
        )

        self.paginas.addWidget(
            self.pagina_relatorios
        )

        self.paginas.addWidget(
            self.pagina_metas
        )

        self.paginas.addWidget(
            self.pagina_economia
        )

        self.paginas.addWidget(
            self.pagina_configuracoes
        )

        layout_principal.addWidget(
            self.menu
        )

        layout_principal.addWidget(
            self.paginas
        )

        self.aplicar_tema()

    # =========================================================
    # MENU
    # =========================================================

    def criar_menu(self):

        menu = QFrame()

        menu.setObjectName(
            "menu"
        )

        menu.setFixedWidth(
            245
        )

        layout = QVBoxLayout(
            menu
        )

        layout.setContentsMargins(
            16,
            25,
            16,
            18
        )

        layout.setSpacing(5)

        logo = QLabel(
            "J.A.R.V.I.S"
        )

        logo.setObjectName(
            "logo_jarvis"
        )

        logo.setFont(
            QFont(
                "Arial",
                25,
                QFont.Bold
            )
        )

        logo.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            logo
        )

        subtitulo = QLabel(
            "FINANCIAL SYSTEM"
        )

        subtitulo.setObjectName(
            "subtitulo_jarvis"
        )

        subtitulo.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            subtitulo
        )

        layout.addSpacing(35)

        self.criar_botao_menu(
            "◉",
            "Dashboard",
            0,
            layout
        )

        self.criar_botao_menu(
            "💰",
            "Finanças",
            1,
            layout
        )

        self.criar_botao_menu(
            "📊",
            "Relatórios",
            2,
            layout
        )

        self.criar_botao_menu(
            "🎯",
            "Metas",
            3,
            layout
        )

        self.criar_botao_menu(
            "📈",
            "Economia",
            4,
            layout
        )

        layout.addSpacing(14)

        divisor = QFrame()

        divisor.setFrameShape(
            QFrame.HLine
        )

        divisor.setObjectName(
            "divisor_menu"
        )

        layout.addWidget(
            divisor
        )

        layout.addSpacing(10)

        self.criar_botao_menu(
            "⚙",
            "Configurações",
            5,
            layout
        )

        layout.addStretch()

        status = QFrame()

        status.setObjectName(
            "status_box"
        )

        status_layout = QVBoxLayout(
            status
        )

        status_layout.setContentsMargins(
            12,
            10,
            12,
            10
        )

        online = QLabel(
            "●  SISTEMA ONLINE"
        )

        online.setObjectName(
            "status_online"
        )

        status_layout.addWidget(
            online
        )

        info = QLabel(
            "JARVIS FINANCE CORE"
        )

        info.setObjectName(
            "status_info"
        )

        status_layout.addWidget(
            info
        )

        layout.addWidget(
            status
        )

        return menu

    # =========================================================
    # BOTÃO MENU
    # =========================================================

    def criar_botao_menu(
        self,
        icone,
        texto,
        indice,
        layout
    ):

        botao = QPushButton(
            f"{icone}   {texto}"
        )

        botao.setObjectName(
            "menu_button"
        )

        botao.setMinimumHeight(
            44
        )

        botao.clicked.connect(
            lambda checked=False,
            i=indice:
            self.mudar_pagina(i)
        )

        self.botoes_menu.append(
            botao
        )

        layout.addWidget(
            botao
        )

    # =========================================================
    # MENU ATIVO
    # =========================================================

    def marcar_menu_ativo(
        self,
        indice
    ):

        for numero, botao in enumerate(
            self.botoes_menu
        ):

            if numero == indice:

                botao.setObjectName(
                    "menu_button_active"
                )

            else:

                botao.setObjectName(
                    "menu_button"
                )

            botao.style().unpolish(
                botao
            )

            botao.style().polish(
                botao
            )

            botao.update()

    # =========================================================
    # MUDAR PÁGINA
    # =========================================================

    def mudar_pagina(
        self,
        pagina
    ):

        self.paginas.setCurrentIndex(
            pagina
        )

        self.marcar_menu_ativo(
            pagina
        )

        if pagina == 0:

            self.atualizar_dashboard()

        elif pagina == 2:

            self.inicializar_relatorios()

        elif pagina == 3:

            self.atualizar_metas()

        elif pagina == 4:

            self.atualizar_economia()

    # =========================================================
    # TEMA
    # =========================================================

    def aplicar_tema(self):

        tema = self.configuracoes.get(
            "tema",
            "JARVIS Dark"
        )

        paletas = {
            "JARVIS Dark": {
                "fundo_1": "#03060b", "fundo_2": "#081622",
                "menu_1": "#080d15", "menu_2": "#09111b",
                "painel": "#0d1723", "painel_2": "#0a1b2a",
                "card": "#0e1824", "campo": "#080f17",
                "botao": "#17283a", "borda": "#1a2d3e"
            },
            "JARVIS Deep": {
                "fundo_1": "#02040a", "fundo_2": "#040b14",
                "menu_1": "#050910", "menu_2": "#060d16",
                "painel": "#080e16", "painel_2": "#07131d",
                "card": "#0a111a", "campo": "#050a10",
                "botao": "#111d2a", "borda": "#172738"
            },
            "JARVIS Minimal": {
                "fundo_1": "#071018", "fundo_2": "#0a131d",
                "menu_1": "#071019", "menu_2": "#09141e",
                "painel": "#101a24", "painel_2": "#0d1b25",
                "card": "#121e29", "campo": "#0b141d",
                "botao": "#1a2a39", "borda": "#253949"
            },
            "JARVIS Blue": {
                "fundo_1": "#03101f", "fundo_2": "#062744",
                "menu_1": "#04172b", "menu_2": "#06213a",
                "painel": "#0a2945", "painel_2": "#0b3557",
                "card": "#0d3150", "campo": "#061c31",
                "botao": "#12466d", "borda": "#1d5d89"
            },
            "JARVIS Purple": {
                "fundo_1": "#0b0618", "fundo_2": "#241044",
                "menu_1": "#100821", "menu_2": "#1b0d35",
                "painel": "#251444", "painel_2": "#311a55",
                "card": "#2b174b", "campo": "#150b27",
                "botao": "#48226d", "borda": "#673694"
            },
            "JARVIS Green": {
                "fundo_1": "#03120b", "fundo_2": "#073522",
                "menu_1": "#041b11", "menu_2": "#06291a",
                "painel": "#0a3823", "painel_2": "#0d472c",
                "card": "#0c4027", "campo": "#062319",
                "botao": "#155c39", "borda": "#20754a"
            },
            "JARVIS Red": {
                "fundo_1": "#170405", "fundo_2": "#3b0b0f",
                "menu_1": "#200609", "menu_2": "#31090d",
                "painel": "#421014", "painel_2": "#51151a",
                "card": "#491217", "campo": "#26080b",
                "botao": "#681c23", "borda": "#8a2a32"
            },
            "JARVIS Orange": {
                "fundo_1": "#180b02", "fundo_2": "#3b1d05",
                "menu_1": "#211003", "menu_2": "#311604",
                "painel": "#442207", "painel_2": "#542b09",
                "card": "#4b2608", "campo": "#291404",
                "botao": "#69370b", "borda": "#8a4b12"
            },
            "JARVIS Pink": {
                "fundo_1": "#180511", "fundo_2": "#3b0d2b",
                "menu_1": "#220816", "menu_2": "#310b21",
                "painel": "#45112f", "painel_2": "#55153a",
                "card": "#4d1235", "campo": "#280917",
                "botao": "#6d1b4d", "borda": "#8d2b67"
            },
            "JARVIS Cyan": {
                "fundo_1": "#021417", "fundo_2": "#06363b",
                "menu_1": "#031c20", "menu_2": "#052a30",
                "painel": "#0a3b40", "painel_2": "#0d4b50",
                "card": "#0c4449", "campo": "#05262a",
                "botao": "#11636a", "borda": "#1c7c84"
            },
            "JARVIS White": {
                "fundo_1": "#f4f6f8", "fundo_2": "#ffffff",
                "menu_1": "#e8edf2", "menu_2": "#f7f9fb",
                "painel": "#ffffff", "painel_2": "#f3f6f8",
                "card": "#ffffff", "campo": "#eef2f5",
                "botao": "#dce3e9", "borda": "#c7d0d8"
            }
        }

        paleta = paletas.get(tema, paletas["JARVIS Dark"])
        fundo_1 = paleta["fundo_1"]
        fundo_2 = paleta["fundo_2"]
        menu_1 = paleta["menu_1"]
        menu_2 = paleta["menu_2"]

        css = f"""
            QMainWindow {{
                background-color: {fundo_1};
            }}

            QWidget {{
                color: #e7edf5;
                font-family: "Segoe UI";
                background-color: transparent;
            }}

            QWidget#central_principal {{
                background: qlineargradient(
                    x1: 0,
                    y1: 0,
                    x2: 1,
                    y2: 1,
                    stop: 0 {fundo_1},
                    stop: 0.5 {fundo_2},
                    stop: 1 #04080f
                );
            }}

            QStackedWidget {{
                background-color: transparent;
                border: none;
            }}

            QFrame#menu {{
                background: qlineargradient(
                    x1: 0,
                    y1: 0,
                    x2: 0,
                    y2: 1,
                    stop: 0 {menu_1},
                    stop: 1 {menu_2}
                );
                border-right: 1px solid #183045;
            }}

            #logo_jarvis {{
                color: #69dcff;
                background-color: transparent;
                font-size: 25px;
                font-weight: bold;
            }}

            #subtitulo_jarvis {{
                color: #526a82;
                background-color: transparent;
                font-size: 9px;
                font-weight: bold;
            }}

            #divisor_menu {{
                color: #152536;
            }}

            QPushButton#menu_button {{
                background-color: transparent;
                color: #8397ad;
                border: 1px solid transparent;
                border-radius: 10px;
                padding: 11px 12px;
                text-align: left;
                font-size: 14px;
            }}

            QPushButton#menu_button:hover {{
                background-color: #0e1b29;
                color: #eef8ff;
                border: 1px solid #1b3a52;
            }}

            QPushButton#menu_button_active {{
                background-color: #0c273b;
                color: #96eaff;
                border: 1px solid #22749a;
                border-left: 3px solid #55d7ff;
                border-radius: 10px;
                padding: 11px 12px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
            }}

            QFrame#status_box {{
                background-color: #09141f;
                border: 1px solid #173b54;
                border-radius: 10px;
            }}

            #status_online {{
                color: #4ade80;
                background-color: transparent;
                font-size: 10px;
                font-weight: bold;
            }}

            #status_info {{
                color: #526b83;
                background-color: transparent;
                font-size: 9px;
            }}

            QFrame#system_bar {{
                background-color: #08131f;
                border: 1px solid #17384e;
                border-radius: 12px;
            }}

            QLabel#system_label {{
                color: #60778d;
                background-color: transparent;
                font-size: 8px;
                font-weight: bold;
            }}

            QLabel#system_value {{
                color: #8fe8ff;
                background-color: transparent;
                font-size: 10px;
                font-weight: bold;
            }}

            QLabel#system_value_green {{
                color: #4ade80;
                background-color: transparent;
                font-size: 10px;
                font-weight: bold;
            }}

            #titulo_pagina {{
                color: #f4f9ff;
                background-color: transparent;
                font-size: 30px;
                font-weight: bold;
            }}

            #subtitulo_pagina {{
                color: #60768d;
                background-color: transparent;
                font-size: 13px;
            }}

            #titulo_painel {{
                color: #eef7ff;
                background-color: transparent;
                font-size: 17px;
                font-weight: bold;
            }}

            QFrame#painel {{
                background-color: #0d1723;
                border: 1px solid #1a2d3e;
                border-radius: 16px;
            }}

            QFrame#painel_jarvis {{
                background-color: #0a1b2a;
                border: 1px solid #1b6e94;
                border-radius: 18px;
            }}

            QFrame#painel_economia {{
                background-color: #081822;
                border: 1px solid #1d566f;
                border-radius: 16px;
            }}

            #titulo_jarvis {{
                color: #70ddff;
                background-color: transparent;
                font-size: 19px;
                font-weight: bold;
            }}

            #mensagem_jarvis {{
                color: #d9f5ff;
                background-color: transparent;
                font-size: 14px;
            }}

            #jarvis_meta {{
                color: #59738c;
                background-color: transparent;
                font-size: 8px;
                font-weight: bold;
            }}

            #jarvis_status {{
                color: #4ade80;
                background-color: transparent;
                font-size: 9px;
                font-weight: bold;
            }}

            QLabel#economia_valor {{
                color: #8fe8ff;
                background-color: transparent;
                font-size: 24px;
                font-weight: bold;
            }}

            QLabel#economia_label {{
                color: #6d849a;
                background-color: transparent;
                font-size: 10px;
                font-weight: bold;
            }}

            QLabel#economia_texto {{
                color: #c8d6e4;
                background-color: transparent;
                font-size: 13px;
            }}

            QFrame#painel_alertas {{
                background-color: #0b141e;
                border: 1px solid #214257;
                border-radius: 16px;
            }}

            QLabel#alerta_normal {{
                color: #c8d6e4;
                background-color: transparent;
                font-size: 13px;
            }}

            QLabel#alerta_atencao {{
                color: #f4c95d;
                background-color: transparent;
                font-size: 13px;
                font-weight: bold;
            }}

            QLabel#alerta_critico {{
                color: #ff7373;
                background-color: transparent;
                font-size: 13px;
                font-weight: bold;
            }}

            QLabel#alerta_sucesso {{
                color: #63e6be;
                background-color: transparent;
                font-size: 13px;
                font-weight: bold;
            }}

            QFrame#painel_projecao {{
                background-color: #0a1824;
                border: 1px solid #28506a;
                border-radius: 16px;
            }}

            QLabel#projecao_titulo {{
                color: #8fe8ff;
                background-color: transparent;
                font-size: 17px;
                font-weight: bold;
            }}

            QLabel#projecao_label {{
                color: #61778b;
                background-color: transparent;
                font-size: 9px;
                font-weight: bold;
            }}

            QLabel#projecao_valor {{
                color: #eef8ff;
                background-color: transparent;
                font-size: 20px;
                font-weight: bold;
            }}

            QLabel#projecao_status_normal {{
                color: #63e6be;
                background-color: transparent;
                font-size: 13px;
                font-weight: bold;
            }}

            QLabel#projecao_status_atencao {{
                color: #f4c95d;
                background-color: transparent;
                font-size: 13px;
                font-weight: bold;
            }}

            QLabel#projecao_status_critico {{
                color: #ff7373;
                background-color: transparent;
                font-size: 13px;
                font-weight: bold;
            }}

            QFrame#card_financeiro {{
                background-color: #0e1824;
                border: 1px solid #1b2e40;
                border-radius: 16px;
            }}

            QFrame#card_saldo {{
                background-color: #0a202b;
                border: 1px solid #207093;
                border-radius: 16px;
            }}

            #titulo_card {{
                color: #627991;
                background-color: transparent;
                font-size: 10px;
                font-weight: bold;
            }}

            #valor_card {{
                color: #f7fbff;
                background-color: transparent;
                font-size: 27px;
                font-weight: bold;
            }}

            #valor_saldo_card {{
                color: #8fe8ff;
                background-color: transparent;
                font-size: 29px;
                font-weight: bold;
            }}

            #descricao_card {{
                color: #526981;
                background-color: transparent;
                font-size: 11px;
            }}

            QLineEdit,
            QDateEdit {{
                background-color: #080f17;
                color: #e5eef6;
                border: 1px solid #263e53;
                border-radius: 8px;
                padding: 10px;
            }}

            QLineEdit:focus,
            QDateEdit:focus {{
                border: 1px solid #42bfe9;
            }}

            QComboBox {{
                background-color: #0c1621;
                color: #d2dfeb;
                border: 1px solid #294155;
                border-radius: 9px;
                padding: 8px 12px;
                min-height: 18px;
            }}

            QComboBox:hover {{
                border: 1px solid #367d9f;
            }}

            QComboBox:focus {{
                border: 1px solid #4fc3f7;
            }}

            QComboBox QAbstractItemView {{
                background-color: #0c1621;
                color: #e8f1f8;
                border: 1px solid #294155;
                selection-background-color: #16364d;
            }}

            QTableWidget {{
                background-color: #080f17;
                color: #d9e5ef;
                border: 1px solid #1b2e40;
                border-radius: 12px;
                gridline-color: #142536;
                selection-background-color: #112a40;
                alternate-background-color: #0a131d;
            }}

            QTableWidget::item {{
                padding: 8px;
            }}

            QHeaderView::section {{
                background-color: #0e1925;
                color: #8297ad;
                border: none;
                padding: 10px;
                font-weight: bold;
            }}

            QProgressBar {{
                background-color: #172330;
                border: none;
                border-radius: 6px;
                height: 12px;
                text-align: center;
                color: #e7f0f6;
            }}

            QProgressBar::chunk {{
                background-color: #18b7a7;
                border-radius: 6px;
            }}

            QScrollArea {{
                background-color: transparent;
                border: none;
            }}

            QScrollBar:vertical {{
                background-color: #070c13;
                width: 9px;
            }}

            QScrollBar::handle:vertical {{
                background-color: #27445b;
                border-radius: 4px;
                min-height: 40px;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QPushButton {{
                background-color: #17283a;
                color: #dce8f2;
                border: 1px solid #294258;
                border-radius: 8px;
                padding: 10px 14px;
            }}

            QPushButton:hover {{
                background-color: #1a354c;
                border: 1px solid #3b6d90;
            }}

            QPushButton:pressed {{
                background-color: #0d1925;
            }}

            QPushButton:disabled {{
                color: #607384;
                background-color: #101b26;
                border: 1px solid #1c2b37;
            }}

            QDialog,
            QMessageBox {{
                background-color: #0c1520;
            }}
            """

        substituicoes = {
            "#0d1723": paleta["painel"],
            "#0a1b2a": paleta["painel_2"],
            "#0e1824": paleta["card"],
            "#080f17": paleta["campo"],
            "#0c1621": paleta["campo"],
            "#17283a": paleta["botao"],
            "#1a2d3e": paleta["borda"],
            "#1b2e40": paleta["borda"]
        }

        for original, novo in substituicoes.items():
            css = css.replace(original, novo)

        if tema == "JARVIS White":
            css += f"""

            /* =====================================================
               JARVIS WHITE
               ===================================================== */

            QMainWindow {{
                background-color: #f4f6f8;
            }}

            QWidget {{
                color: #17212b;
            }}

            QWidget#central_principal {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f4f6f8,
                    stop: 0.5 #ffffff,
                    stop: 1 #eef2f5
                );
            }}

            QFrame#menu {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e8edf2,
                    stop: 1 #f7f9fb
                );
                border-right: 1px solid #c7d0d8;
            }}

            #logo_jarvis {{ color: #087ea4; }}
            #subtitulo_jarvis {{ color: #65727d; }}
            #divisor_menu {{ color: #c7d0d8; background-color: #c7d0d8; }}

            QPushButton#menu_button {{
                color: #4f5d68;
                background-color: transparent;
            }}

            QPushButton#menu_button:hover {{
                background-color: #e2e7eb;
                color: #17212b;
                border: 1px solid #c7d0d8;
            }}

            QPushButton#menu_button_active {{
                background-color: #d8edf3;
                color: #056783;
                border: 1px solid #8fbfce;
                border-left: 3px solid #087ea4;
            }}

            QFrame#status_box,
            QFrame#system_bar {{
                background-color: #f3f6f8;
                border: 1px solid #c7d0d8;
            }}

            #status_online,
            QLabel#system_value_green,
            #jarvis_status,
            QLabel#alerta_sucesso,
            QLabel#projecao_status_normal {{
                color: #16845b;
            }}

            #status_info,
            QLabel#system_label,
            #subtitulo_pagina,
            QLabel#economia_label,
            #jarvis_meta,
            #titulo_card,
            #descricao_card,
            QLabel#projecao_label {{
                color: #65727d;
            }}

            QLabel#system_value,
            #titulo_jarvis,
            QLabel#economia_valor,
            QLabel#projecao_titulo,
            #valor_saldo_card {{
                color: #087ea4;
            }}

            #titulo_pagina,
            #titulo_painel,
            #mensagem_jarvis,
            QLabel#economia_texto,
            QLabel#projecao_valor,
            #valor_card {{
                color: #17212b;
            }}

            QFrame#painel,
            QFrame#painel_jarvis,
            QFrame#painel_economia,
            QFrame#painel_alertas,
            QFrame#painel_projecao,
            QFrame#card_financeiro {{
                background-color: #ffffff;
                border-color: #c7d0d8;
            }}

            QFrame#painel_jarvis,
            QFrame#card_saldo {{
                background-color: #f3f6f8;
                border-color: #8fbfce;
            }}

            QLabel#alerta_normal,
            QLabel#alerta_atencao,
            QLabel#alerta_critico,
            QLabel#alerta_sucesso {{
                background-color: transparent;
            }}

            QLabel#alerta_normal {{ color: #25313b; }}
            QLabel#alerta_atencao {{ color: #a66a00; }}
            QLabel#alerta_critico {{ color: #c0392b; }}
            QLabel#alerta_sucesso {{ color: #16845b; }}

            QLabel#projecao_status_atencao {{ color: #a66a00; }}
            QLabel#projecao_status_critico {{ color: #c0392b; }}

            QLineEdit,
            QDateEdit,
            QComboBox {{
                background-color: #eef2f5;
                color: #17212b;
                border: 1px solid #c7d0d8;
            }}

            QLineEdit:focus,
            QDateEdit:focus,
            QComboBox:focus {{
                border: 1px solid #087ea4;
            }}

            QComboBox QAbstractItemView {{
                background-color: #ffffff;
                color: #17212b;
                border: 1px solid #c7d0d8;
                selection-background-color: #d8edf3;
                selection-color: #17212b;
            }}

            QTableWidget {{
                background-color: #ffffff;
                color: #17212b;
                border: 1px solid #c7d0d8;
                gridline-color: #d7dee4;
                selection-background-color: #d8edf3;
                selection-color: #17212b;
                alternate-background-color: #f8fafb;
            }}

            QHeaderView::section {{
                background-color: #e8edf2;
                color: #4f5d68;
                border: none;
            }}

            QProgressBar {{
                background-color: #dce3e9;
                color: #17212b;
            }}

            QProgressBar::chunk {{
                background-color: #087ea4;
            }}

            QScrollBar:vertical {{
                background-color: #eef2f5;
            }}

            QScrollBar::handle:vertical {{
                background-color: #c7d0d8;
            }}

            QPushButton {{
                background-color: #dce3e9;
                color: #17212b;
                border: 1px solid #c7d0d8;
            }}

            QPushButton:hover {{
                background-color: #d8edf3;
                color: #056783;
                border: 1px solid #8fbfce;
            }}

            QPushButton:pressed {{
                background-color: #cfd8de;
            }}

            QPushButton:disabled {{
                color: #8a969f;
                background-color: #eef2f5;
                border: 1px solid #d7dee4;
            }}

            QDialog,
            QMessageBox {{
                background-color: #ffffff;
                color: #17212b;
            }}

            QMessageBox QLabel {{
                color: #17212b;
            }}
            """

        self.setStyleSheet(css)

    # =========================================================
    # SYSTEM BAR
    # =========================================================

    def criar_system_bar(self):

        bar = QFrame()

        bar.setObjectName(
            "system_bar"
        )

        layout = QHBoxLayout(
            bar
        )

        layout.setContentsMargins(
            14,
            8,
            14,
            8
        )

        layout.setSpacing(
            18
        )

        sistemas = [
            ("CORE", "ONLINE", "green"),
            ("DATABASE", "SQLITE", "blue"),
            ("ENGINE", "ACTIVE", "blue"),
            ("SECURITY", "LOCAL", "blue")
        ]

        for titulo, valor, tipo in sistemas:

            coluna = QVBoxLayout()

            coluna.setSpacing(0)

            label_titulo = QLabel(
                titulo
            )

            label_titulo.setObjectName(
                "system_label"
            )

            coluna.addWidget(
                label_titulo
            )

            label_valor = QLabel(
                valor
            )

            label_valor.setObjectName(
                "system_value_green"
                if tipo == "green"
                else "system_value"
            )

            coluna.addWidget(
                label_valor
            )

            layout.addLayout(
                coluna
            )

        layout.addStretch()

        return bar

    # =========================================================
    # CARD
    # =========================================================

    def criar_card(
        self,
        titulo,
        valor,
        descricao,
        tipo=None
    ):

        card = QFrame()

        card.setObjectName(
            "card_saldo"
            if tipo == "saldo"
            else "card_financeiro"
        )

        card.setMinimumHeight(
            135
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            20,
            18,
            20,
            18
        )

        titulo_label = QLabel(
            titulo
        )

        titulo_label.setObjectName(
            "titulo_card"
        )

        layout.addWidget(
            titulo_label
        )

        layout.addSpacing(10)

        valor_label = QLabel(
            valor
        )

        valor_label.setObjectName(
            "valor_saldo_card"
            if tipo == "saldo"
            else "valor_card"
        )

        layout.addWidget(
            valor_label
        )

        layout.addSpacing(4)

        descricao_label = QLabel(
            descricao
        )

        descricao_label.setObjectName(
            "descricao_card"
        )

        layout.addWidget(
            descricao_label
        )

        return card

    # =========================================================
    # ATUALIZAR CARD
    # =========================================================

    def atualizar_card(
        self,
        card,
        novo_valor
    ):

        if card is None:
            return

        layout = card.layout()

        if layout is None:
            return

        item = layout.itemAt(2)

        if item is None:
            return

        widget = item.widget()

        if widget:

            widget.setText(
                str(
                    novo_valor
                )
            )

    # =========================================================
    # DASHBOARD
    # =========================================================

    def criar_dashboard(self):

        pagina = QWidget()

        layout_externo = QVBoxLayout(
            pagina
        )

        layout_externo.setContentsMargins(
            0,
            0,
            0,
            0
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        scroll.setFrameShape(
            QFrame.NoFrame
        )

        conteudo = QWidget()

        layout = QVBoxLayout(
            conteudo
        )

        layout.setContentsMargins(
            35,
            28,
            35,
            40
        )

        layout.setSpacing(16)

        cabecalho = QHBoxLayout()

        titulo = QLabel(
            "Dashboard"
        )

        titulo.setObjectName(
            "titulo_pagina"
        )

        cabecalho.addWidget(
            titulo
        )

        cabecalho.addStretch()

        cabecalho.addWidget(
            QLabel("📅")
        )

        self.combo_mes_dashboard = QComboBox()

        meses = [
            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro"
        ]

        for numero, nome in enumerate(
            meses,
            1
        ):

            self.combo_mes_dashboard.addItem(
                f"{nome} {self.ano_dashboard}",
                numero
            )

        self.combo_mes_dashboard.setCurrentIndex(
            self.mes_dashboard - 1
        )

        self.combo_mes_dashboard.setFixedWidth(
            155
        )

        cabecalho.addWidget(
            self.combo_mes_dashboard
        )

        layout.addLayout(
            cabecalho
        )

        subtitulo = QLabel(
            "Visão geral inteligente da sua vida financeira."
        )

        subtitulo.setObjectName(
            "subtitulo_pagina"
        )

        layout.addWidget(
            subtitulo
        )

        layout.addWidget(
            self.criar_system_bar()
        )

        cards = QHBoxLayout()

        self.card_saldo = self.criar_card(
            "SALDO DO MÊS",
            "R$ 0,00",
            "Resultado",
            "saldo"
        )

        self.card_receitas = self.criar_card(
            "RECEITAS",
            "R$ 0,00",
            "Entradas"
        )

        self.card_despesas = self.criar_card(
            "DESPESAS",
            "R$ 0,00",
            "Saídas"
        )

        cards.addWidget(
            self.card_saldo
        )

        cards.addWidget(
            self.card_receitas
        )

        cards.addWidget(
            self.card_despesas
        )

        layout.addLayout(
            cards
        )

        # =====================================================
        # JARVIS
        # =====================================================

        painel_jarvis = QFrame()

        painel_jarvis.setObjectName(
            "painel_jarvis"
        )

        jarvis_layout = QVBoxLayout(
            painel_jarvis
        )

        topo = QHBoxLayout()

        titulo_jarvis = QLabel(
            "🤖  JARVIS"
        )

        titulo_jarvis.setObjectName(
            "titulo_jarvis"
        )

        topo.addWidget(
            titulo_jarvis
        )

        topo.addStretch()

        status = QLabel(
            "● CORE ONLINE"
        )

        status.setObjectName(
            "jarvis_status"
        )

        topo.addWidget(
            status
        )

        jarvis_layout.addLayout(
            topo
        )

        self.mensagem_jarvis = QLabel(
            "Aguardando dados..."
        )

        self.mensagem_jarvis.setObjectName(
            "mensagem_jarvis"
        )

        self.mensagem_jarvis.setWordWrap(
            True
        )

        jarvis_layout.addWidget(
            self.mensagem_jarvis
        )

        meta = QLabel(
            "FINANCE CORE • ANALYSIS ACTIVE • LOCAL PROCESSING"
        )

        meta.setObjectName(
            "jarvis_meta"
        )

        jarvis_layout.addWidget(
            meta
        )

        layout.addWidget(
            painel_jarvis
        )

        # =====================================================
        # PROJEÇÃO
        # =====================================================

        painel_projecao = QFrame()

        painel_projecao.setObjectName(
            "painel_projecao"
        )

        layout_projecao = QVBoxLayout(
            painel_projecao
        )

        topo_projecao = QHBoxLayout()

        titulo_projecao = QLabel(
            "🔮  Projeção Financeira"
        )

        titulo_projecao.setObjectName(
            "projecao_titulo"
        )

        topo_projecao.addWidget(
            titulo_projecao
        )

        topo_projecao.addStretch()

        self.status_projecao_label = QLabel(
            "ANALISANDO..."
        )

        self.status_projecao_label.setObjectName(
            "projecao_status_normal"
        )

        topo_projecao.addWidget(
            self.status_projecao_label
        )

        layout_projecao.addLayout(
            topo_projecao
        )

        linha_projecao = QHBoxLayout()

        blocos = [
            (
                "MÉDIA DIÁRIA",
                "valor_media_projecao"
            ),
            (
                "DESPESA PROJETADA",
                "valor_despesa_projecao"
            ),
            (
                "SALDO PROJETADO",
                "valor_saldo_projecao"
            )
        ]

        for titulo_bloco, atributo in blocos:

            bloco = QVBoxLayout()

            label = QLabel(
                titulo_bloco
            )

            label.setObjectName(
                "projecao_label"
            )

            bloco.addWidget(
                label
            )

            valor = QLabel(
                "R$ 0,00"
            )

            valor.setObjectName(
                "projecao_valor"
            )

            setattr(
                self,
                atributo,
                valor
            )

            bloco.addWidget(
                valor
            )

            linha_projecao.addLayout(
                bloco
            )

        layout_projecao.addLayout(
            linha_projecao
        )

        self.texto_projecao = QLabel(
            "Aguardando dados suficientes."
        )

        self.texto_projecao.setWordWrap(
            True
        )

        layout_projecao.addWidget(
            self.texto_projecao
        )

        layout.addWidget(
            painel_projecao
        )

        # =====================================================
        # ALERTAS
        # =====================================================

        painel_alertas = QFrame()

        painel_alertas.setObjectName(
            "painel_alertas"
        )

        layout_alertas = QVBoxLayout(
            painel_alertas
        )

        topo_alertas = QHBoxLayout()

        titulo_alertas = QLabel(
            "🚨  Alertas do JARVIS"
        )

        titulo_alertas.setObjectName(
            "titulo_painel"
        )

        topo_alertas.addWidget(
            titulo_alertas
        )

        topo_alertas.addStretch()

        status_alertas = QLabel(
            "MONITORAMENTO ATIVO"
        )

        status_alertas.setObjectName(
            "jarvis_status"
        )

        topo_alertas.addWidget(
            status_alertas
        )

        layout_alertas.addLayout(
            topo_alertas
        )

        self.texto_alertas = QLabel(
            "Analisando..."
        )

        self.texto_alertas.setWordWrap(
            True
        )

        layout_alertas.addWidget(
            self.texto_alertas
        )

        layout.addWidget(
            painel_alertas
        )

        # =====================================================
        # INTELIGÊNCIA
        # =====================================================

        linha_inferior = QHBoxLayout()

        painel_inteligencia = QFrame()

        painel_inteligencia.setObjectName(
            "painel"
        )

        layout_inteligencia = QVBoxLayout(
            painel_inteligencia
        )

        titulo_inteligencia = QLabel(
            "🧠  Central de Inteligência"
        )

        titulo_inteligencia.setObjectName(
            "titulo_painel"
        )

        layout_inteligencia.addWidget(
            titulo_inteligencia
        )

        self.texto_inteligencia = QLabel(
            "Aguardando análise..."
        )

        self.texto_inteligencia.setWordWrap(
            True
        )

        layout_inteligencia.addWidget(
            self.texto_inteligencia
        )

        linha_inferior.addWidget(
            painel_inteligencia
        )

        # =====================================================
        # PLANO
        # =====================================================

        painel_plano = QFrame()

        painel_plano.setObjectName(
            "painel"
        )

        layout_plano = QVBoxLayout(
            painel_plano
        )

        titulo_plano = QLabel(
            "📋  Plano do JARVIS"
        )

        titulo_plano.setObjectName(
            "titulo_painel"
        )

        layout_plano.addWidget(
            titulo_plano
        )

        self.texto_plano = QLabel(
            "Calculando..."
        )

        self.texto_plano.setWordWrap(
            True
        )

        layout_plano.addWidget(
            self.texto_plano
        )

        linha_inferior.addWidget(
            painel_plano
        )

        layout.addLayout(
            linha_inferior
        )

        # =====================================================
        # COMPARAÇÃO
        # =====================================================

        painel_comparacao = QFrame()

        painel_comparacao.setObjectName(
            "painel"
        )

        layout_comparacao = QVBoxLayout(
            painel_comparacao
        )

        titulo_comparacao = QLabel(
            "📈  Comparação com o mês anterior"
        )

        titulo_comparacao.setObjectName(
            "titulo_painel"
        )

        layout_comparacao.addWidget(
            titulo_comparacao
        )

        self.texto_comparacao = QLabel(
            "Calculando..."
        )

        self.texto_comparacao.setWordWrap(
            True
        )

        layout_comparacao.addWidget(
            self.texto_comparacao
        )

        layout.addWidget(
            painel_comparacao
        )

        scroll.setWidget(
            conteudo
        )

        layout_externo.addWidget(
            scroll
        )

        self.combo_mes_dashboard.currentIndexChanged.connect(
            lambda index:
            self.atualizar_dashboard()
        )

        return pagina

    # =========================================================
    # CARREGAR DASHBOARD
    # =========================================================

    def carregar_dashboard_mes(self):

        mes = (
            self.combo_mes_dashboard.currentData()
        )

        if mes is None:
            return

        self.mes_dashboard = int(
            mes
        )

        dados = (
            self.banco.buscar_transacoes_mes(
                self.ano_dashboard,
                self.mes_dashboard
            )
        )

        self.transacoes_dashboard = []

        self.total_receitas_dashboard = 0.0
        self.total_despesas_dashboard = 0.0

        for transacao in dados:

            data = transacao[5]

            if data:
                data = data[:10]

            self.transacoes_dashboard.append({
                "id": transacao[0],
                "tipo": transacao[1],
                "descricao": transacao[2],
                "categoria": transacao[3],
                "valor": transacao[4],
                "data": data
            })

            if transacao[1] == "receita":

                self.total_receitas_dashboard += (
                    transacao[4]
                )

            else:

                self.total_despesas_dashboard += (
                    transacao[4]
                )

        self.saldo_dashboard = (
            self.total_receitas_dashboard
            -
            self.total_despesas_dashboard
        )

    # =========================================================
    # MÊS ANTERIOR
    # =========================================================

    def carregar_mes_anterior(self):

        mes_atual = self.mes_dashboard
        ano_atual = self.ano_dashboard

        if mes_atual == 1:

            mes_anterior = 12
            ano_anterior = ano_atual - 1

        else:

            mes_anterior = mes_atual - 1
            ano_anterior = ano_atual

        dados = (
            self.banco.buscar_transacoes_mes(
                ano_anterior,
                mes_anterior
            )
        )

        self.receitas_mes_anterior = 0.0
        self.despesas_mes_anterior = 0.0

        for transacao in dados:

            if transacao[1] == "receita":

                self.receitas_mes_anterior += (
                    transacao[4]
                )

            else:

                self.despesas_mes_anterior += (
                    transacao[4]
                )

        self.saldo_mes_anterior = (
            self.receitas_mes_anterior
            -
            self.despesas_mes_anterior
        )

    # =========================================================
    # PROJEÇÃO
    # =========================================================

    def calcular_projecao_financeira(self):

        hoje = date.today()

        self.dias_mes_projecao = (
            calendar.monthrange(
                self.ano_dashboard,
                self.mes_dashboard
            )[1]
        )

        if (
            self.ano_dashboard == hoje.year
            and
            self.mes_dashboard == hoje.month
        ):

            self.dias_passados_projecao = max(
                1,
                hoje.day
            )

            self.dias_restantes_projecao = max(
                0,
                self.dias_mes_projecao
                -
                hoje.day
            )

            despesas_realizadas = 0.0
            receitas_realizadas = 0.0
            receitas_futuras = 0.0

            for transacao in (
                self.transacoes_dashboard
            ):

                data_texto = str(
                    transacao.get(
                        "data",
                        ""
                    )
                )

                try:

                    data_transacao = (
                        date.fromisoformat(
                            data_texto[:10]
                        )
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    continue

                valor = float(
                    transacao.get(
                        "valor",
                        0
                    )
                )

                tipo = transacao.get(
                    "tipo"
                )

                if tipo == "despesa":

                    if data_transacao <= hoje:

                        despesas_realizadas += valor

                elif tipo == "receita":

                    if data_transacao <= hoje:

                        receitas_realizadas += valor

                    else:

                        receitas_futuras += valor

            if despesas_realizadas > 0:

                self.media_diaria_despesas = (
                    despesas_realizadas
                    /
                    self.dias_passados_projecao
                )

            else:

                self.media_diaria_despesas = 0.0

            gasto_futuro = (
                self.media_diaria_despesas
                *
                self.dias_restantes_projecao
            )

            self.despesa_projetada = (
                despesas_realizadas
                +
                gasto_futuro
            )

            receita_projetada = (
                receitas_realizadas
                +
                receitas_futuras
            )

            self.saldo_projetado = (
                receita_projetada
                -
                self.despesa_projetada
            )

        elif (
            self.ano_dashboard > hoje.year
            or
            (
                self.ano_dashboard == hoje.year
                and
                self.mes_dashboard > hoje.month
            )
        ):

            self.dias_passados_projecao = 0

            self.dias_restantes_projecao = (
                self.dias_mes_projecao
            )

            self.media_diaria_despesas = 0.0

            self.despesa_projetada = (
                self.total_despesas_dashboard
            )

            self.saldo_projetado = (
                self.total_receitas_dashboard
                -
                self.total_despesas_dashboard
            )

        else:

            self.dias_passados_projecao = (
                self.dias_mes_projecao
            )

            self.dias_restantes_projecao = 0

            self.media_diaria_despesas = (
                self.total_despesas_dashboard
                /
                max(
                    1,
                    self.dias_mes_projecao
                )
            )

            self.despesa_projetada = (
                self.total_despesas_dashboard
            )

            self.saldo_projetado = (
                self.total_receitas_dashboard
                -
                self.total_despesas_dashboard
            )

        if self.total_receitas_dashboard > 0:

            self.percentual_despesa_projetada = (
                self.despesa_projetada
                /
                self.total_receitas_dashboard
            ) * 100

        else:

            self.percentual_despesa_projetada = 0.0

        if self.saldo_projetado < 0:

            self.status_projecao = "CRITICO"

        elif (
            self.percentual_despesa_projetada >= 75
        ):

            self.status_projecao = "ATENCAO"

        else:

            self.status_projecao = "NORMAL"

    # =========================================================
    # VISUAL PROJEÇÃO
    # =========================================================

    def atualizar_projecao_visual(self):

        self.calcular_projecao_financeira()

        self.valor_media_projecao.setText(
            self.formatar_dinheiro(
                self.media_diaria_despesas
            )
        )

        self.valor_despesa_projecao.setText(
            self.formatar_dinheiro(
                self.despesa_projetada
            )
        )

        self.valor_saldo_projecao.setText(
            self.formatar_dinheiro(
                self.saldo_projetado
            )
        )

        if self.status_projecao == "CRITICO":

            self.status_projecao_label.setText(
                "🔴 RISCO CRÍTICO"
            )

        elif self.status_projecao == "ATENCAO":

            self.status_projecao_label.setText(
                "🟡 ATENÇÃO"
            )

        else:

            self.status_projecao_label.setText(
                "🟢 SOB CONTROLE"
            )

        if self.saldo_projetado < 0:

            mensagem = (
                "Mantendo o ritmo atual de gastos, "
                "a projeção indica saldo negativo."
            )

        elif self.status_projecao == "ATENCAO":

            mensagem = (
                "Seu ritmo atual de despesas exige atenção."
            )

        else:

            mensagem = (
                "Mantendo o ritmo atual, sua projeção "
                "permanece positiva."
            )

        if self.dias_restantes_projecao > 0:

            mensagem += (
                f" Restam "
                f"{self.dias_restantes_projecao} "
                "dia(s) no período."
            )

        self.texto_projecao.setText(
            mensagem
        )

    # =========================================================
    # DASHBOARD
    # =========================================================

    def atualizar_dashboard(self):

        self.carregar_dashboard_mes()

        self.atualizar_card(
            self.card_saldo,
            self.formatar_dinheiro(
                self.saldo_dashboard
            )
        )

        self.atualizar_card(
            self.card_receitas,
            self.formatar_dinheiro(
                self.total_receitas_dashboard
            )
        )

        self.atualizar_card(
            self.card_despesas,
            self.formatar_dinheiro(
                self.total_despesas_dashboard
            )
        )

        self.atualizar_projecao_visual()

        mensagens_ativas = (
            self.configuracoes.get(
                "mensagens",
                "Ativadas"
            )
            ==
            "Ativadas"
        )

        if mensagens_ativas:

            if self.saldo_dashboard > 0:

                self.mensagem_jarvis.setText(
                    "Seu saldo está positivo em "
                    f"{self.formatar_dinheiro(self.saldo_dashboard)}. "
                    "O JARVIS está monitorando suas finanças."
                )

            elif self.saldo_dashboard < 0:

                self.mensagem_jarvis.setText(
                    "ATENÇÃO: suas despesas ultrapassaram "
                    "suas receitas em "
                    f"{self.formatar_dinheiro(abs(self.saldo_dashboard))}."
                )

            else:

                self.mensagem_jarvis.setText(
                    "Ainda não existem movimentações "
                    "suficientes para análise."
                )

        else:

            self.mensagem_jarvis.setText(
                "Mensagens inteligentes desativadas."
            )

        insights = (
            self.gerar_inteligencia_dashboard()
        )

        texto_inteligencia = ""

        for insight in insights:

            texto_inteligencia += (
                "• "
                +
                insight
                +
                "\n\n"
            )

        self.texto_inteligencia.setText(
            texto_inteligencia
        )

        self.texto_plano.setText(
            self.gerar_plano_dashboard()
        )

        comparacao = (
            self.gerar_comparacao_mensal()
        )

        texto_comparacao = ""

        for item in comparacao:

            texto_comparacao += (
                "• "
                +
                item
                +
                "\n\n"
            )

        self.texto_comparacao.setText(
            texto_comparacao
        )

        self.atualizar_alertas_dashboard()

    # =========================================================
    # ALERTAS
    # =========================================================

    def gerar_alertas_dashboard(self):

        habilitado = (
            self.configuracoes.get(
                "alertas",
                "Ativados"
            )
            ==
            "Ativados"
        )

        if not habilitado:

            return [
                (
                    "normal",
                    "ℹ️ Monitoramento de alertas "
                    "desativado nas configurações."
                )
            ]

        alertas = []

        if (
            self.total_receitas_dashboard == 0
            and
            self.total_despesas_dashboard == 0
        ):

            return [
                (
                    "normal",
                    "ℹ️ Nenhuma movimentação encontrada."
                ),
                (
                    "normal",
                    "💡 Cadastre receitas e despesas "
                    "para ativar o monitoramento."
                )
            ]

        if self.saldo_dashboard < 0:

            alertas.append(
                (
                    "critico",
                    "🔴 Suas despesas já ultrapassaram "
                    "suas receitas."
                )
            )

        sensibilidade = (
            self.configuracoes.get(
                "sensibilidade_alertas",
                "Normal"
            )
        )

        if sensibilidade == "Baixa":

            limite_atencao = 90

        elif sensibilidade == "Alta":

            limite_atencao = 65

        else:

            limite_atencao = 75

        if self.saldo_projetado < 0:

            alertas.append(
                (
                    "critico",
                    "🔴 A projeção indica possível "
                    "saldo negativo no fechamento."
                )
            )

        elif (
            self.percentual_despesa_projetada >= 100
        ):

            alertas.append(
                (
                    "critico",
                    "🔴 A projeção indica "
                    "comprometimento total da receita."
                )
            )

        elif (
            self.percentual_despesa_projetada
            >=
            limite_atencao
        ):

            alertas.append(
                (
                    "atencao",
                    f"🟡 Os gastos projetados representam "
                    f"{self.percentual_despesa_projetada:.1f}% "
                    "da receita."
                )
            )

        percentual_atual = 0.0

        if self.total_receitas_dashboard > 0:

            percentual_atual = (
                self.total_despesas_dashboard
                /
                self.total_receitas_dashboard
            ) * 100

        if percentual_atual >= 100:

            alertas.append(
                (
                    "critico",
                    f"🔴 Você já comprometeu "
                    f"{percentual_atual:.1f}% da sua receita."
                )
            )

        elif percentual_atual >= 90:

            alertas.append(
                (
                    "atencao",
                    f"🟠 {percentual_atual:.1f}% da sua "
                    "receita já está comprometida."
                )
            )

        categorias = {}

        for transacao in self.transacoes_dashboard:

            if transacao["tipo"] != "despesa":
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

        if categorias:

            maior_categoria = max(
                categorias,
                key=categorias.get
            )

            maior_valor = (
                categorias[
                    maior_categoria
                ]
            )

            alertas.append(
                (
                    "normal",
                    f"🔎 Maior categoria: "
                    f"{maior_categoria}, "
                    f"{self.formatar_dinheiro(maior_valor)}."
                )
            )

        if self.saldo_dashboard > 0:

            dias = max(
                1,
                self.dias_restantes_projecao
            )

            reserva = (
                self.obter_percentual_reserva()
            )

            disponivel = (
                self.saldo_dashboard
                -
                (
                    self.saldo_dashboard
                    *
                    reserva
                )
            )

            limite = (
                disponivel
                /
                dias
            )

            if limite > 0:

                alertas.append(
                    (
                        "normal",
                        f"💡 Limite diário sugerido: "
                        f"{self.formatar_dinheiro(limite)}."
                    )
                )

        if not alertas:

            alertas.append(
                (
                    "sucesso",
                    "🟢 Nenhum alerta importante."
                )
            )

        return alertas

    # =========================================================
    # ATUALIZAR ALERTAS
    # =========================================================

    def atualizar_alertas_dashboard(self):

        alertas = (
            self.gerar_alertas_dashboard()
        )

        texto = ""

        critico = False
        atencao = False

        for tipo, mensagem in alertas:

            texto += (
                "• "
                +
                mensagem
                +
                "\n\n"
            )

            if tipo == "critico":
                critico = True

            elif tipo == "atencao":
                atencao = True

        self.texto_alertas.setText(
            texto
        )

        if critico:

            self.texto_alertas.setObjectName(
                "alerta_critico"
            )

        elif atencao:

            self.texto_alertas.setObjectName(
                "alerta_atencao"
            )

        else:

            self.texto_alertas.setObjectName(
                "alerta_normal"
            )

        self.texto_alertas.style().unpolish(
            self.texto_alertas
        )

        self.texto_alertas.style().polish(
            self.texto_alertas
        )

        self.texto_alertas.update()

    # =========================================================
    # INTELIGÊNCIA
    # =========================================================

    def gerar_inteligencia_dashboard(self):

        mensagens = []

        if (
            self.total_receitas_dashboard == 0
            and
            self.total_despesas_dashboard == 0
        ):

            return [
                "Não encontrei movimentações para "
                "o mês selecionado.",
                "Cadastre uma receita ou despesa "
                "para iniciar a análise."
            ]

        if self.saldo_dashboard < 0:

            mensagens.append(
                "Você gastou mais do que recebeu."
            )

        else:

            mensagens.append(
                f"Seu saldo atual é "
                f"{self.formatar_dinheiro(self.saldo_dashboard)}."
            )

        if self.total_receitas_dashboard > 0:

            percentual = (
                self.total_despesas_dashboard
                /
                self.total_receitas_dashboard
            ) * 100

            mensagens.append(
                f"{percentual:.1f}% da sua receita "
                "foi utilizada."
            )

        categorias = {}

        for transacao in self.transacoes_dashboard:

            if transacao["tipo"] != "despesa":
                continue

            categoria = transacao["categoria"]

            categorias[categoria] = (
                categorias.get(
                    categoria,
                    0.0
                )
                +
                transacao["valor"]
            )

        if categorias:

            maior_categoria = max(
                categorias,
                key=categorias.get
            )

            mensagens.append(
                f"Maior categoria: "
                f"{maior_categoria}, "
                f"{self.formatar_dinheiro(categorias[maior_categoria])}."
            )

        if self.saldo_projetado < 0:

            mensagens.append(
                "A projeção indica risco de saldo negativo."
            )

        else:

            mensagens.append(
                f"Saldo projetado: "
                f"{self.formatar_dinheiro(self.saldo_projetado)}."
            )

        nivel = (
            self.configuracoes.get(
                "inteligencia",
                "Normal"
            )
        )

        if nivel in (
            "Normal",
            "Avançado"
        ):

            mensagens.append(
                f"Média diária de despesas: "
                f"{self.formatar_dinheiro(self.media_diaria_despesas)}."
            )

        if nivel == "Avançado":

            mensagens.append(
                f"Despesa projetada: "
                f"{self.formatar_dinheiro(self.despesa_projetada)}."
            )

        return mensagens

    # =========================================================
    # PLANO
    # =========================================================

    def gerar_plano_dashboard(self):

        if self.saldo_dashboard <= 0:

            return (
                "O saldo atual está em "
                f"{self.formatar_dinheiro(self.saldo_dashboard)}.\n\n"
                "O foco deve ser equilibrar "
                "entradas e saídas."
            )

        dias = max(
            1,
            self.dias_restantes_projecao
        )

        reserva = (
            self.saldo_dashboard
            *
            self.obter_percentual_reserva()
        )

        disponivel = (
            self.saldo_dashboard
            -
            reserva
        )

        limite = (
            disponivel
            /
            dias
        )

        return (
            f"Saldo atual: "
            f"{self.formatar_dinheiro(self.saldo_dashboard)}.\n\n"
            f"Reserva sugerida: "
            f"{self.formatar_dinheiro(reserva)}.\n\n"
            f"Valor disponível: "
            f"{self.formatar_dinheiro(disponivel)}.\n\n"
            f"Limite diário: "
            f"{self.formatar_dinheiro(limite)}."
        )

    # =========================================================
    # COMPARAÇÃO
    # =========================================================

    def gerar_comparacao_mensal(self):

        self.carregar_mes_anterior()

        mensagens = []

        def variacao(
            atual,
            anterior
        ):

            if anterior == 0:

                if atual == 0:
                    return 0

                return None

            return (
                (
                    atual
                    -
                    anterior
                )
                /
                abs(anterior)
            ) * 100

        receitas = variacao(
            self.total_receitas_dashboard,
            self.receitas_mes_anterior
        )

        despesas = variacao(
            self.total_despesas_dashboard,
            self.despesas_mes_anterior
        )

        if receitas is None:

            mensagens.append(
                "Receitas: sem base anterior."
            )

        elif receitas > 0:

            mensagens.append(
                f"Receitas: ↑ {receitas:.1f}%."
            )

        elif receitas < 0:

            mensagens.append(
                f"Receitas: ↓ {abs(receitas):.1f}%."
            )

        else:

            mensagens.append(
                "Receitas: sem alteração."
            )

        if despesas is None:

            mensagens.append(
                "Despesas: sem base anterior."
            )

        elif despesas > 0:

            mensagens.append(
                f"Despesas: ↑ {despesas:.1f}%."
            )

        elif despesas < 0:

            mensagens.append(
                f"Despesas: ↓ {abs(despesas):.1f}%."
            )

        else:

            mensagens.append(
                "Despesas: sem alteração."
            )

        diferenca = (
            self.saldo_dashboard
            -
            self.saldo_mes_anterior
        )

        if diferenca > 0:

            mensagens.append(
                f"Saldo: ↑ "
                f"{self.formatar_dinheiro(diferenca)}."
            )

        elif diferenca < 0:

            mensagens.append(
                f"Saldo: ↓ "
                f"{self.formatar_dinheiro(abs(diferenca))}."
            )

        else:

            mensagens.append(
                "Saldo: sem alteração."
            )

        return mensagens

    # =========================================================
    # FINANÇAS
    # =========================================================

    def criar_financas(self):

        pagina = QWidget()

        layout = QVBoxLayout(
            pagina
        )

        layout.setContentsMargins(
            24,
            24,
            24,
            24
        )

        titulo = QLabel(
            "Finanças"
        )

        titulo.setObjectName(
            "titulo_pagina"
        )

        layout.addWidget(
            titulo
        )

        descricao = QLabel(
            "Gerencie suas receitas e despesas."
        )

        descricao.setObjectName(
            "subtitulo_pagina"
        )

        layout.addWidget(
            descricao
        )

        layout.addSpacing(18)

        layout.addWidget(
            self.criar_system_bar()
        )

        layout.addSpacing(14)

        botoes = QHBoxLayout()

        botao_receita = QPushButton(
            "Nova Receita"
        )

        botao_despesa = QPushButton(
            "Nova Despesa"
        )

        botoes.addWidget(
            botao_receita
        )

        botoes.addWidget(
            botao_despesa
        )

        botoes.addStretch()

        layout.addLayout(
            botoes
        )

        painel = QFrame()

        painel.setObjectName(
            "painel"
        )

        painel_layout = QVBoxLayout(
            painel
        )

        titulo_tabela = QLabel(
            "Transações"
        )

        titulo_tabela.setObjectName(
            "titulo_painel"
        )

        painel_layout.addWidget(
            titulo_tabela
        )

        self.tabela = QTableWidget()

        self.tabela.setColumnCount(
            7
        )

        self.tabela.setHorizontalHeaderLabels([
            "ID",
            "Tipo",
            "Descrição",
            "Categoria",
            "Valor",
            "Data",
            "Ações"
        ])

        self.tabela.setAlternatingRowColors(
            True
        )

        self.tabela.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.tabela.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.tabela.verticalHeader().setVisible(
            False
        )

        header = (
            self.tabela.horizontalHeader()
        )

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            5,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            6,
            QHeaderView.Fixed
        )

        self.tabela.setColumnWidth(
            6,
            180
        )

        painel_layout.addWidget(
            self.tabela
        )

        layout.addWidget(
            painel
        )

        self.label_saldo_financas = QLabel(
            "Saldo atual: R$ 0,00"
        )

        self.label_saldo_financas.setFont(
            QFont(
                "Arial",
                19,
                QFont.Bold
            )
        )

        layout.addWidget(
            self.label_saldo_financas
        )

        layout.addStretch()

        botao_receita.clicked.connect(
            lambda checked=False:
            self.abrir_cadastro(
                "receita"
            )
        )

        botao_despesa.clicked.connect(
            lambda checked=False:
            self.abrir_cadastro(
                "despesa"
            )
        )

        return pagina

    # =========================================================
    # TABELA
    # =========================================================

    def atualizar_tabela(self):

        self.tabela.setRowCount(
            len(
                self.transacoes
            )
        )

        for linha, transacao in enumerate(
            self.transacoes
        ):

            valores = [
                str(
                    transacao["id"]
                ),
                (
                    "Receita"
                    if transacao["tipo"] == "receita"
                    else
                    "Despesa"
                ),
                transacao["descricao"],
                transacao["categoria"],
                self.formatar_dinheiro(
                    transacao["valor"]
                ),
                transacao["data"]
            ]

            data_obj = QDate.fromString(
                transacao["data"],
                "yyyy-MM-dd"
            )

            if data_obj.isValid():

                valores[5] = (
                    data_obj.toString(
                        "dd/MM/yyyy"
                    )
                )

            for coluna, valor in enumerate(
                valores
            ):

                item = QTableWidgetItem(
                    str(
                        valor
                    )
                )

                if coluna in (
                    0,
                    1,
                    4,
                    5
                ):

                    item.setTextAlignment(
                        Qt.AlignCenter
                        |
                        Qt.AlignVCenter
                    )

                else:

                    item.setTextAlignment(
                        Qt.AlignVCenter
                    )

                self.tabela.setItem(
                    linha,
                    coluna,
                    item
                )

            widget_acoes = QWidget()

            layout_acoes = QHBoxLayout(
                widget_acoes
            )

            layout_acoes.setContentsMargins(
                5,
                4,
                5,
                4
            )

            layout_acoes.setSpacing(6)

            editar = QPushButton(
                "Editar"
            )

            excluir = QPushButton(
                "Excluir"
            )

            editar.setFixedSize(
                72,
                32
            )

            excluir.setFixedSize(
                72,
                32
            )

            layout_acoes.addWidget(
                editar
            )

            layout_acoes.addWidget(
                excluir
            )

            editar.clicked.connect(
                lambda checked=False,
                t=transacao:
                self.abrir_cadastro(
                    t["tipo"],
                    t
                )
            )

            excluir.clicked.connect(
                lambda checked=False,
                tid=transacao["id"]:
                self.excluir_transacao(
                    tid
                )
            )

            self.tabela.setCellWidget(
                linha,
                6,
                widget_acoes
            )

            self.tabela.setRowHeight(
                linha,
                52
            )

    # =========================================================
    # CADASTRO
    # =========================================================

    def abrir_cadastro(
        self,
        tipo,
        transacao=None
    ):

        janela = QDialog(
            self
        )

        editando = (
            transacao is not None
        )

        if tipo == "receita":

            titulo = (
                "Editar Receita"
                if editando
                else
                "Nova Receita"
            )

        else:

            titulo = (
                "Editar Despesa"
                if editando
                else
                "Nova Despesa"
            )

        janela.setWindowTitle(
            titulo
        )

        janela.setMinimumWidth(
            420
        )

        layout = QVBoxLayout(
            janela
        )

        label_titulo = QLabel(
            titulo
        )

        label_titulo.setFont(
            QFont(
                "Arial",
                20,
                QFont.Bold
            )
        )

        layout.addWidget(
            label_titulo
        )

        descricao = QLineEdit()

        descricao.setPlaceholderText(
            "Descrição"
        )

        layout.addWidget(
            descricao
        )

        categoria = QComboBox()

        categoria.addItems([
            "Alimentação",
            "Transporte",
            "Moradia",
            "Educação",
            "Saúde",
            "Lazer",
            "Salário",
            "Investimentos",
            "Contas",
            "Compras",
            "Outros"
        ])

        layout.addWidget(
            categoria
        )

        valor = QLineEdit()

        valor.setPlaceholderText(
            "Valor"
        )

        layout.addWidget(
            valor
        )

        data = QDateEdit()

        data.setCalendarPopup(
            True
        )

        data.setDate(
            QDate.currentDate()
        )

        data.setDisplayFormat(
            "dd/MM/yyyy"
        )

        layout.addWidget(
            data
        )

        if editando:

            descricao.setText(
                transacao["descricao"]
            )

            categoria.setCurrentText(
                transacao["categoria"]
            )

            valor.setText(
                str(
                    transacao["valor"]
                )
            )

            data_obj = QDate.fromString(
                transacao["data"],
                "yyyy-MM-dd"
            )

            if data_obj.isValid():

                data.setDate(
                    data_obj
                )

        salvar = QPushButton(
            "Salvar"
        )

        layout.addWidget(
            salvar
        )

        if editando:

            salvar.clicked.connect(
                lambda checked=False:
                self.editar_transacao(
                    transacao["id"],
                    tipo,
                    descricao.text(),
                    categoria.currentText(),
                    valor.text(),
                    data.date().toString(
                        "yyyy-MM-dd"
                    ),
                    janela
                )
            )

        else:

            salvar.clicked.connect(
                lambda checked=False:
                self.salvar_transacao(
                    tipo,
                    descricao.text(),
                    categoria.currentText(),
                    valor.text(),
                    data.date().toString(
                        "yyyy-MM-dd"
                    ),
                    janela
                )
            )

        janela.exec()

    # =========================================================
    # SALVAR TRANSAÇÃO
    # =========================================================

    def salvar_transacao(
        self,
        tipo,
        descricao,
        categoria,
        valor,
        data,
        janela
    ):

        descricao = descricao.strip()

        if not descricao:

            QMessageBox.warning(
                self,
                "Atenção",
                "Digite uma descrição."
            )

            return

        try:

            valor = self.converter_valor(
                valor
            )

        except ValueError:

            QMessageBox.warning(
                self,
                "Valor inválido",
                "Digite um valor válido."
            )

            return

        if valor <= 0:

            QMessageBox.warning(
                self,
                "Valor inválido",
                "O valor deve ser maior que zero."
            )

            return

        id_transacao = (
            self.banco.adicionar_transacao(
                tipo,
                descricao,
                categoria,
                valor,
                data
            )
        )

        self.transacoes.insert(
            0,
            {
                "id": id_transacao,
                "tipo": tipo,
                "descricao": descricao,
                "categoria": categoria,
                "valor": valor,
                "data": data
            }
        )

        self.recalcular_totais()
        self.atualizar_tabela()
        self.atualizar_cerebro()
        self.atualizar_dashboard()

        if self.relatorios_inicializados:

            self.atualizar_relatorios()

        janela.accept()

    # =========================================================
    # EDITAR TRANSAÇÃO
    # =========================================================

    def editar_transacao(
        self,
        id_transacao,
        tipo,
        descricao,
        categoria,
        valor,
        data,
        janela
    ):

        descricao = descricao.strip()

        if not descricao:

            QMessageBox.warning(
                self,
                "Atenção",
                "Digite uma descrição."
            )

            return

        try:

            valor = self.converter_valor(
                valor
            )

        except ValueError:

            QMessageBox.warning(
                self,
                "Valor inválido",
                "Digite um valor válido."
            )

            return

        if valor <= 0:

            QMessageBox.warning(
                self,
                "Valor inválido",
                "O valor deve ser maior que zero."
            )

            return

        self.banco.editar_transacao(
            id_transacao,
            tipo,
            descricao,
            categoria,
            valor,
            data
        )

        for transacao in self.transacoes:

            if transacao["id"] == id_transacao:

                transacao["tipo"] = tipo
                transacao["descricao"] = descricao
                transacao["categoria"] = categoria
                transacao["valor"] = valor
                transacao["data"] = data

                break

        self.recalcular_totais()
        self.atualizar_tabela()
        self.atualizar_cerebro()
        self.atualizar_dashboard()

        if self.relatorios_inicializados:

            self.atualizar_relatorios()

        janela.accept()

    # =========================================================
    # EXCLUIR TRANSAÇÃO
    # =========================================================

    def excluir_transacao(
        self,
        id_transacao
    ):

        resposta = QMessageBox.question(
            self,
            "Excluir transação",
            "Tem certeza que deseja excluir esta transação?"
        )

        if resposta != QMessageBox.Yes:

            return

        self.banco.excluir_transacao(
            id_transacao
        )

        self.transacoes = [
            transacao
            for transacao in self.transacoes
            if transacao["id"] != id_transacao
        ]

        self.recalcular_totais()
        self.atualizar_tabela()
        self.atualizar_cerebro()
        self.atualizar_dashboard()

        if self.relatorios_inicializados:

            self.atualizar_relatorios()

    # =========================================================
    # RECALCULAR TOTAIS
    # =========================================================

    def recalcular_totais(self):

        self.total_receitas = 0.0
        self.total_despesas = 0.0

        for transacao in self.transacoes:

            if transacao["tipo"] == "receita":

                self.total_receitas += (
                    transacao["valor"]
                )

            else:

                self.total_despesas += (
                    transacao["valor"]
                )

        self.saldo_atual = (
            self.total_receitas
            -
            self.total_despesas
        )

        if hasattr(
            self,
            "label_saldo_financas"
        ):

            self.label_saldo_financas.setText(
                f"Saldo atual: "
                f"{self.formatar_dinheiro(self.saldo_atual)}"
            )

    # =========================================================
    # CARREGAR DADOS
    # =========================================================

    def carregar_dados(self):

        dados = (
            self.banco.buscar_transacoes()
        )

        self.transacoes = []

        for transacao in dados:

            data = transacao[5]

            if data:

                data = data[:10]

            else:

                data = (
                    QDate.currentDate()
                    .toString(
                        "yyyy-MM-dd"
                    )
                )

            self.transacoes.append({
                "id": transacao[0],
                "tipo": transacao[1],
                "descricao": transacao[2],
                "categoria": transacao[3],
                "valor": transacao[4],
                "data": data
            })

        self.recalcular_totais()
        self.atualizar_tabela()
        self.atualizar_dashboard()

    # =========================================================
    # METAS
    # =========================================================

    def criar_metas(self):

        pagina = QWidget()

        layout = QVBoxLayout(
            pagina
        )

        layout.setContentsMargins(
            30,
            25,
            30,
            25
        )

        cabecalho = QHBoxLayout()

        titulo = QLabel(
            "Metas financeiras"
        )

        titulo.setObjectName(
            "titulo_pagina"
        )

        cabecalho.addWidget(
            titulo
        )

        cabecalho.addStretch()

        nova_meta = QPushButton(
            "Nova Meta"
        )

        cabecalho.addWidget(
            nova_meta
        )

        layout.addLayout(
            cabecalho
        )

        descricao = QLabel(
            "Defina objetivos e acompanhe seu progresso."
        )

        descricao.setObjectName(
            "subtitulo_pagina"
        )

        layout.addWidget(
            descricao
        )

        layout.addWidget(
            self.criar_system_bar()
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.container_metas = QWidget()

        self.layout_metas = QVBoxLayout(
            self.container_metas
        )

        self.layout_metas.setSpacing(12)

        scroll.setWidget(
            self.container_metas
        )

        layout.addWidget(
            scroll
        )

        nova_meta.clicked.connect(
            lambda checked=False:
            self.abrir_cadastro_meta()
        )

        return pagina

    # =========================================================
    # CARREGAR METAS
    # =========================================================

    def carregar_metas(self):

        dados = (
            self.banco.buscar_metas()
        )

        self.metas = []

        for meta in dados:

            self.metas.append({
                "id": meta[0],
                "nome": meta[1],
                "objetivo": meta[2],
                "guardado": meta[3],
                "data": meta[4]
            })

        self.atualizar_metas()

    # =========================================================
    # ATUALIZAR METAS
    # =========================================================

    def atualizar_metas(self):

        while self.layout_metas.count():

            item = self.layout_metas.takeAt(
                0
            )

            widget = item.widget()

            if widget:

                widget.deleteLater()

        if not self.metas:

            vazio = QFrame()

            vazio.setObjectName(
                "painel"
            )

            layout = QVBoxLayout(
                vazio
            )

            mensagem = QLabel(
                "Nenhuma meta cadastrada.\n\n"
                "Clique em 'Nova Meta'."
            )

            mensagem.setAlignment(
                Qt.AlignCenter
            )

            layout.addWidget(
                mensagem
            )

            self.layout_metas.addWidget(
                vazio
            )

            return

        for meta in self.metas:

            painel = QFrame()

            painel.setObjectName(
                "painel"
            )

            layout = QVBoxLayout(
                painel
            )

            topo = QHBoxLayout()

            nome = QLabel(
                meta["nome"]
            )

            nome.setFont(
                QFont(
                    "Arial",
                    18,
                    QFont.Bold
                )
            )

            topo.addWidget(
                nome
            )

            topo.addStretch()

            editar = QPushButton(
                "Editar"
            )

            excluir = QPushButton(
                "Excluir"
            )

            topo.addWidget(
                editar
            )

            topo.addWidget(
                excluir
            )

            layout.addLayout(
                topo
            )

            objetivo = meta["objetivo"]
            guardado = meta["guardado"]

            percentual = 0

            if objetivo > 0:

                percentual = int(
                    (
                        guardado
                        /
                        objetivo
                    )
                    *
                    100
                )

            percentual = min(
                percentual,
                100
            )

            texto = QLabel(
                f"Guardado: "
                f"{self.formatar_dinheiro(guardado)} "
                f"de "
                f"{self.formatar_dinheiro(objetivo)} "
                f"({percentual}%)"
            )

            layout.addWidget(
                texto
            )

            progresso = QProgressBar()

            progresso.setValue(
                percentual
            )

            progresso.setFormat(
                f"{percentual}%"
            )

            layout.addWidget(
                progresso
            )

            editar.clicked.connect(
                lambda checked=False,
                m=meta:
                self.abrir_cadastro_meta(m)
            )

            excluir.clicked.connect(
                lambda checked=False,
                mid=meta["id"]:
                self.excluir_meta(mid)
            )

            self.layout_metas.addWidget(
                painel
            )

    # =========================================================
    # CADASTRO META
    # =========================================================

    def abrir_cadastro_meta(
        self,
        meta=None
    ):

        janela = QDialog(
            self
        )

        editando = (
            meta is not None
        )

        janela.setWindowTitle(
            "Editar Meta"
            if editando
            else
            "Nova Meta"
        )

        janela.setMinimumWidth(
            420
        )

        layout = QVBoxLayout(
            janela
        )

        nome = QLineEdit()

        nome.setPlaceholderText(
            "Nome da meta"
        )

        layout.addWidget(
            nome
        )

        objetivo = QLineEdit()

        objetivo.setPlaceholderText(
            "Valor objetivo"
        )

        layout.addWidget(
            objetivo
        )

        guardado = QLineEdit()

        guardado.setPlaceholderText(
            "Valor já guardado"
        )

        layout.addWidget(
            guardado
        )

        if editando:

            nome.setText(
                meta["nome"]
            )

            objetivo.setText(
                str(
                    meta["objetivo"]
                )
            )

            guardado.setText(
                str(
                    meta["guardado"]
                )
            )

        salvar = QPushButton(
            "Salvar"
        )

        layout.addWidget(
            salvar
        )

        if editando:

            salvar.clicked.connect(
                lambda checked=False:
                self.editar_meta(
                    meta["id"],
                    nome.text(),
                    objetivo.text(),
                    guardado.text(),
                    janela
                )
            )

        else:

            salvar.clicked.connect(
                lambda checked=False:
                self.salvar_meta(
                    nome.text(),
                    objetivo.text(),
                    guardado.text(),
                    janela
                )
            )

        janela.exec()

    # =========================================================
    # SALVAR META
    # =========================================================

    def salvar_meta(
        self,
        nome,
        objetivo,
        guardado,
        janela
    ):

        nome = nome.strip()

        try:

            objetivo = self.converter_valor(
                objetivo
            )

            guardado = self.converter_valor(
                guardado
            )

        except ValueError:

            QMessageBox.warning(
                self,
                "Erro",
                "Digite valores válidos."
            )

            return

        if not nome or objetivo <= 0:

            QMessageBox.warning(
                self,
                "Erro",
                "Preencha a meta corretamente."
            )

            return

        if guardado < 0 or guardado > objetivo:

            QMessageBox.warning(
                self,
                "Erro",
                "Valor guardado inválido."
            )

            return

        id_meta = (
            self.banco.adicionar_meta(
                nome,
                objetivo,
                guardado
            )
        )

        self.metas.insert(
            0,
            {
                "id": id_meta,
                "nome": nome,
                "objetivo": objetivo,
                "guardado": guardado,
                "data": ""
            }
        )

        self.atualizar_metas()
        self.atualizar_cerebro()
        self.atualizar_dashboard()

        janela.accept()

    # =========================================================
    # EDITAR META
    # =========================================================

    def editar_meta(
        self,
        id_meta,
        nome,
        objetivo,
        guardado,
        janela
    ):

        try:

            objetivo = self.converter_valor(
                objetivo
            )

            guardado = self.converter_valor(
                guardado
            )

        except ValueError:

            QMessageBox.warning(
                self,
                "Erro",
                "Digite valores válidos."
            )

            return

        if (
            not nome.strip()
            or
            objetivo <= 0
            or
            guardado < 0
            or
            guardado > objetivo
        ):

            QMessageBox.warning(
                self,
                "Erro",
                "Dados da meta inválidos."
            )

            return

        self.banco.editar_meta(
            id_meta,
            nome.strip(),
            objetivo,
            guardado
        )

        for meta in self.metas:

            if meta["id"] == id_meta:

                meta["nome"] = nome.strip()
                meta["objetivo"] = objetivo
                meta["guardado"] = guardado

                break

        self.atualizar_metas()
        self.atualizar_cerebro()
        self.atualizar_dashboard()

        janela.accept()

    # =========================================================
    # EXCLUIR META
    # =========================================================

    def excluir_meta(
        self,
        id_meta
    ):

        resposta = QMessageBox.question(
            self,
            "Excluir meta",
            "Tem certeza que deseja excluir esta meta?"
        )

        if resposta != QMessageBox.Yes:

            return

        self.banco.excluir_meta(
            id_meta
        )

        self.metas = [
            meta
            for meta in self.metas
            if meta["id"] != id_meta
        ]

        self.atualizar_metas()
        self.atualizar_cerebro()
        self.atualizar_dashboard()

    # =========================================================
    # RELATÓRIOS
    # =========================================================

    def criar_relatorios(self):

        pagina = QWidget()

        layout = QVBoxLayout(
            pagina
        )

        layout.setContentsMargins(
            30,
            25,
            30,
            25
        )

        titulo = QLabel(
            "Relatórios"
        )

        titulo.setObjectName(
            "titulo_pagina"
        )

        layout.addWidget(
            titulo
        )

        descricao = QLabel(
            "Análise visual das suas receitas e despesas."
        )

        descricao.setObjectName(
            "subtitulo_pagina"
        )

        layout.addWidget(
            descricao
        )

        layout.addWidget(
            self.criar_system_bar()
        )

        painel = QFrame()

        painel.setObjectName(
            "painel"
        )

        painel_layout = QVBoxLayout(
            painel
        )

        mensagem = QLabel(
            "Selecione Relatórios para carregar "
            "a análise financeira."
        )

        mensagem.setAlignment(
            Qt.AlignCenter
        )

        painel_layout.addWidget(
            mensagem
        )

        layout.addWidget(
            painel
        )

        layout.addStretch()

        return pagina

    # =========================================================
    # RELATÓRIOS REAL
    # =========================================================

    def inicializar_relatorios(self):

        if self.relatorios_inicializados:

            self.atualizar_relatorios()

            return

        from matplotlib.backends.backend_qtagg import (
            FigureCanvasQTAgg
        )

        from matplotlib.figure import Figure

        class GraficoCanvas(
            FigureCanvasQTAgg
        ):

            def __init__(self):

                self.figura = Figure(
                    figsize=(5, 3),
                    dpi=100
                )

                self.eixo = (
                    self.figura.add_subplot(
                        111
                    )
                )

                super().__init__(
                    self.figura
                )

        pagina = QWidget()

        layout = QVBoxLayout(
            pagina
        )

        layout.setContentsMargins(
            30,
            25,
            30,
            25
        )

        cabecalho = QHBoxLayout()

        titulo = QLabel(
            "Relatórios"
        )

        titulo.setObjectName(
            "titulo_pagina"
        )

        cabecalho.addWidget(
            titulo
        )

        cabecalho.addStretch()

        atualizar = QPushButton(
            "Atualizar"
        )

        cabecalho.addWidget(
            atualizar
        )

        layout.addLayout(
            cabecalho
        )

        layout.addWidget(
            QLabel(
                "Análise visual das suas finanças."
            )
        )

        layout.addWidget(
            self.criar_system_bar()
        )

        filtro = QHBoxLayout()

        filtro.addWidget(
            QLabel(
                "📅 Período:"
            )
        )

        self.combo_mes_relatorio = QComboBox()

        meses = [
            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro"
        ]

        for numero, nome in enumerate(
            meses,
            1
        ):

            self.combo_mes_relatorio.addItem(
                f"{nome} {self.ano_relatorio}",
                numero
            )

        self.combo_mes_relatorio.setCurrentIndex(
            self.mes_relatorio - 1
        )

        filtro.addWidget(
            self.combo_mes_relatorio
        )

        filtro.addStretch()

        layout.addLayout(
            filtro
        )

        resumo = QHBoxLayout()

        self.label_relatorio_receitas = (
            self.criar_card(
                "RECEITAS",
                "R$ 0,00",
                "Total do mês"
            )
        )

        self.label_relatorio_despesas = (
            self.criar_card(
                "DESPESAS",
                "R$ 0,00",
                "Total do mês"
            )
        )

        self.label_relatorio_saldo = (
            self.criar_card(
                "SALDO",
                "R$ 0,00",
                "Resultado",
                "saldo"
            )
        )

        resumo.addWidget(
            self.label_relatorio_receitas
        )

        resumo.addWidget(
            self.label_relatorio_despesas
        )

        resumo.addWidget(
            self.label_relatorio_saldo
        )

        layout.addLayout(
            resumo
        )

        graficos = QHBoxLayout()

        painel1 = QFrame()

        painel1.setObjectName(
            "painel"
        )

        layout1 = QVBoxLayout(
            painel1
        )

        layout1.addWidget(
            QLabel(
                "Receitas x Despesas"
            )
        )

        self.grafico_totais = (
            GraficoCanvas()
        )

        layout1.addWidget(
            self.grafico_totais
        )

        graficos.addWidget(
            painel1
        )

        painel2 = QFrame()

        painel2.setObjectName(
            "painel"
        )

        layout2 = QVBoxLayout(
            painel2
        )

        layout2.addWidget(
            QLabel(
                "Gastos por categoria"
            )
        )

        self.grafico_categorias = (
            GraficoCanvas()
        )

        layout2.addWidget(
            self.grafico_categorias
        )

        graficos.addWidget(
            painel2
        )

        layout.addLayout(
            graficos
        )

        self.combo_mes_relatorio.currentIndexChanged.connect(
            lambda index:
            self.atualizar_relatorios()
        )

        atualizar.clicked.connect(
            lambda checked=False:
            self.atualizar_relatorios()
        )

        antiga = (
            self.paginas.widget(2)
        )

        self.paginas.removeWidget(
            antiga
        )

        antiga.deleteLater()

        self.paginas.insertWidget(
            2,
            pagina
        )

        self.paginas.setCurrentIndex(
            2
        )

        self.relatorios_inicializados = True

        self.atualizar_relatorios()

    # =========================================================
    # CARREGAR RELATÓRIO
    # =========================================================

    def carregar_relatorio_mes(self):

        mes = (
            self.combo_mes_relatorio.currentData()
        )

        if mes is None:

            return

        self.mes_relatorio = int(
            mes
        )

        dados = (
            self.banco.buscar_transacoes_mes(
                self.ano_relatorio,
                self.mes_relatorio
            )
        )

        self.transacoes_relatorio = []

        self.total_receitas_relatorio = 0.0
        self.total_despesas_relatorio = 0.0

        for transacao in dados:

            self.transacoes_relatorio.append({
                "id": transacao[0],
                "tipo": transacao[1],
                "descricao": transacao[2],
                "categoria": transacao[3],
                "valor": transacao[4],
                "data": transacao[5]
            })

            if transacao[1] == "receita":

                self.total_receitas_relatorio += (
                    transacao[4]
                )

            else:

                self.total_despesas_relatorio += (
                    transacao[4]
                )

        self.saldo_relatorio = (
            self.total_receitas_relatorio
            -
            self.total_despesas_relatorio
        )

    # =========================================================
    # ATUALIZAR RELATÓRIOS
    # =========================================================

    def atualizar_relatorios(self):

        if not self.relatorios_inicializados:

            return

        self.carregar_relatorio_mes()

        self.atualizar_card(
            self.label_relatorio_receitas,
            self.formatar_dinheiro(
                self.total_receitas_relatorio
            )
        )

        self.atualizar_card(
            self.label_relatorio_despesas,
            self.formatar_dinheiro(
                self.total_despesas_relatorio
            )
        )

        self.atualizar_card(
            self.label_relatorio_saldo,
            self.formatar_dinheiro(
                self.saldo_relatorio
            )
        )

        eixo = self.grafico_totais.eixo

        eixo.clear()

        eixo.bar(
            [
                "Receitas",
                "Despesas"
            ],
            [
                self.total_receitas_relatorio,
                self.total_despesas_relatorio
            ]
        )

        eixo.set_title(
            "Visão geral do mês"
        )

        eixo.grid(
            axis="y",
            alpha=0.2
        )

        self.grafico_totais.figura.tight_layout()

        self.grafico_totais.draw()

        eixo = self.grafico_categorias.eixo

        eixo.clear()

        categorias = {}

        for transacao in self.transacoes_relatorio:

            if transacao["tipo"] != "despesa":

                continue

            categoria = transacao["categoria"]

            categorias[categoria] = (
                categorias.get(
                    categoria,
                    0.0
                )
                +
                transacao["valor"]
            )

        if categorias:

            eixo.barh(
                list(
                    categorias.keys()
                ),
                list(
                    categorias.values()
                )
            )

            eixo.set_title(
                "Gastos por categoria"
            )

        else:

            eixo.text(
                0.5,
                0.5,
                "Nenhuma despesa cadastrada",
                ha="center",
                va="center"
            )

            eixo.set_xticks([])
            eixo.set_yticks([])

        self.grafico_categorias.figura.tight_layout()

        self.grafico_categorias.draw()

    # =========================================================
    # ECONOMIA
    # =========================================================

    def criar_economia(self):

        pagina = QWidget()

        layout_externo = QVBoxLayout(
            pagina
        )

        layout_externo.setContentsMargins(
            30,
            25,
            30,
            25
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        scroll.setFrameShape(
            QFrame.NoFrame
        )

        conteudo = QWidget()

        layout = QVBoxLayout(
            conteudo
        )

        layout.setContentsMargins(
            5,
            5,
            15,
            30
        )

        layout.setSpacing(16)

        titulo = QLabel(
            "Economia & Investimentos"
        )

        titulo.setObjectName(
            "titulo_pagina"
        )

        layout.addWidget(
            titulo
        )

        descricao = QLabel(
            "Acompanhe o cenário econômico e converse com o JARVIS."
        )

        descricao.setObjectName(
            "subtitulo_pagina"
        )

        layout.addWidget(
            descricao
        )

        layout.addWidget(
            self.criar_system_bar()
        )

        # =====================================================
        # RADAR ECONÔMICO
        # =====================================================

        painel_radar = QFrame()

        painel_radar.setObjectName(
            "painel_economia"
        )

        layout_radar = QVBoxLayout(
            painel_radar
        )

        topo_radar = QHBoxLayout()

        titulo_radar = QLabel(
            "📡  JARVIS MARKET RADAR"
        )

        titulo_radar.setObjectName(
            "titulo_jarvis"
        )

        topo_radar.addWidget(
            titulo_radar
        )

        topo_radar.addStretch()

        self.botao_atualizar_economia = QPushButton(
            "🔄 Atualizar mercado"
        )

        topo_radar.addWidget(
            self.botao_atualizar_economia
        )

        layout_radar.addLayout(
            topo_radar
        )

        linha_indicadores = QHBoxLayout()

        for nome, atributo in [
            ("SELIC", "label_economia_selic"),
            ("IPCA MENSAL", "label_economia_ipca"),
            ("DÓLAR PTAX", "label_economia_dolar")
        ]:

            bloco = QVBoxLayout()

            label = QLabel(
                nome
            )

            label.setObjectName(
                "economia_label"
            )

            bloco.addWidget(
                label
            )

            valor = QLabel(
                "--"
            )

            valor.setObjectName(
                "economia_valor"
            )

            setattr(
                self,
                atributo,
                valor
            )

            bloco.addWidget(
                valor
            )

            linha_indicadores.addLayout(
                bloco
            )

        layout_radar.addLayout(
            linha_indicadores
        )

        self.label_economia_atualizacao = QLabel(
            "Aguardando atualização..."
        )

        self.label_economia_atualizacao.setObjectName(
            "economia_label"
        )

        layout_radar.addWidget(
            self.label_economia_atualizacao
        )

        self.texto_cenario_economia = QLabel(
            "Aguardando análise econômica..."
        )

        self.texto_cenario_economia.setObjectName(
            "economia_texto"
        )

        self.texto_cenario_economia.setWordWrap(
            True
        )

        layout_radar.addWidget(
            self.texto_cenario_economia
        )

        layout.addWidget(
            painel_radar
        )

        # =====================================================
        # CHAT
        # =====================================================

        painel_chat = QFrame()

        painel_chat.setObjectName(
            "painel_jarvis"
        )

        layout_chat = QVBoxLayout(
            painel_chat
        )

        topo_chat = QHBoxLayout()

        titulo_chat = QLabel(
            "🤖  Pergunte ao JARVIS"
        )

        titulo_chat.setObjectName(
            "titulo_jarvis"
        )

        topo_chat.addWidget(
            titulo_chat
        )

        topo_chat.addStretch()

        self.label_status_ia = QLabel(
            "● IA LOCAL"
        )

        self.label_status_ia.setObjectName(
            "jarvis_status"
        )

        topo_chat.addWidget(
            self.label_status_ia
        )

        botao_limpar_chat = QPushButton(
            "🗑 Limpar conversa"
        )

        topo_chat.addWidget(
            botao_limpar_chat
        )

        layout_chat.addLayout(
            topo_chat
        )

        self.chat_historico_visual = QLabel(
            "🤖 JARVIS:\n\n"
            "Estou pronto para conversar."
        )

        self.chat_historico_visual.setObjectName(
            "mensagem_jarvis"
        )

        self.chat_historico_visual.setWordWrap(
            True
        )

        self.chat_historico_visual.setAlignment(
            Qt.AlignTop
        )

        self.chat_historico_visual.setMinimumHeight(
            180
        )

        layout_chat.addWidget(
            self.chat_historico_visual
        )

        linha_chat = QHBoxLayout()

        self.input_pergunta_jarvis = QLineEdit()

        self.input_pergunta_jarvis.setPlaceholderText(
            "Digite qualquer pergunta para o JARVIS..."
        )

        linha_chat.addWidget(
            self.input_pergunta_jarvis
        )

        self.botao_perguntar_jarvis = QPushButton(
            "🧠 Perguntar"
        )

        self.botao_perguntar_jarvis.setMinimumWidth(
            130
        )

        linha_chat.addWidget(
            self.botao_perguntar_jarvis
        )

        layout_chat.addLayout(
            linha_chat
        )

        layout.addWidget(
            painel_chat
        )

        # =====================================================
        # PERFIL
        # =====================================================

        painel_perfil = QFrame()

        painel_perfil.setObjectName(
            "painel"
        )

        layout_perfil = QVBoxLayout(
            painel_perfil
        )

        titulo_perfil = QLabel(
            "🧭  Perfil para análise"
        )

        titulo_perfil.setObjectName(
            "titulo_painel"
        )

        layout_perfil.addWidget(
            titulo_perfil
        )

        linha_perfil = QHBoxLayout()

        linha_perfil.addWidget(
            QLabel("Perfil:")
        )

        self.combo_perfil_investidor = QComboBox()

        self.combo_perfil_investidor.addItems([
            "Conservador",
            "Moderado",
            "Arrojado"
        ])

        linha_perfil.addWidget(
            self.combo_perfil_investidor
        )

        linha_perfil.addWidget(
            QLabel("Horizonte:")
        )

        self.combo_horizonte_investidor = QComboBox()

        self.combo_horizonte_investidor.addItems([
            "Curto prazo",
            "Médio prazo",
            "Longo prazo"
        ])

        linha_perfil.addWidget(
            self.combo_horizonte_investidor
        )

        linha_perfil.addWidget(
            QLabel("Reserva:")
        )

        self.combo_reserva_investidor = QComboBox()

        self.combo_reserva_investidor.addItems([
            "Ainda estou construindo",
            "Já tenho reserva"
        ])

        linha_perfil.addWidget(
            self.combo_reserva_investidor
        )

        layout_perfil.addLayout(
            linha_perfil
        )

        layout.addWidget(
            painel_perfil
        )

        # =====================================================
        # INVESTIMENTOS
        # =====================================================

        painel_investimento = QFrame()

        painel_investimento.setObjectName(
            "painel"
        )

        layout_investimento = QVBoxLayout(
            painel_investimento
        )

        titulo_investimento = QLabel(
            "💰  Análise de investimento"
        )

        titulo_investimento.setObjectName(
            "titulo_painel"
        )

        layout_investimento.addWidget(
            titulo_investimento
        )

        linha_valor = QHBoxLayout()

        linha_valor.addWidget(
            QLabel(
                "Valor disponível:"
            )
        )

        self.input_valor_investimento = QLineEdit()

        self.input_valor_investimento.setPlaceholderText(
            "Ex.: 500,00"
        )

        linha_valor.addWidget(
            self.input_valor_investimento
        )

        self.botao_analisar_investimento = QPushButton(
            "🧠 Analisar"
        )

        linha_valor.addWidget(
            self.botao_analisar_investimento
        )

        layout_investimento.addLayout(
            linha_valor
        )

        self.texto_analise_investimento = QLabel(
            "Informe um valor para o JARVIS analisar."
        )

        self.texto_analise_investimento.setObjectName(
            "economia_texto"
        )

        self.texto_analise_investimento.setWordWrap(
            True
        )

        layout_investimento.addWidget(
            self.texto_analise_investimento
        )

        layout.addWidget(
            painel_investimento
        )

        layout.addStretch()

        scroll.setWidget(
            conteudo
        )

        layout_externo.addWidget(
            scroll
        )

        # =====================================================
        # EVENTOS
        # =====================================================

        self.botao_atualizar_economia.clicked.connect(
            self.atualizar_economia
        )

        botao_limpar_chat.clicked.connect(
            self.limpar_conversa_jarvis
        )

        self.botao_perguntar_jarvis.clicked.connect(
            self.perguntar_ao_jarvis
        )

        self.input_pergunta_jarvis.returnPressed.connect(
            self.perguntar_ao_jarvis
        )

        self.botao_analisar_investimento.clicked.connect(
            self.analisar_investimento
        )

        self.atualizar_status_ia()

        return pagina

    # =========================================================
    # STATUS IA
    # =========================================================

    def atualizar_status_ia(self):

        if (
            self.jarvis_ia is None
            or
            JarvisWorker is None
        ):

            self.label_status_ia.setText(
                "● IA OFFLINE"
            )

        else:

            self.label_status_ia.setText(
                "● IA LOCAL"
            )

    # =========================================================
    # CONTEXTO IA
    # =========================================================

    def criar_contexto_ia(self):

        perfil = "--"
        horizonte = "--"
        reserva = "--"

        try:

            perfil = (
                self.combo_perfil_investidor.currentText()
            )

            horizonte = (
                self.combo_horizonte_investidor.currentText()
            )

            reserva = (
                self.combo_reserva_investidor.currentText()
            )

        except Exception:

            pass

        return f"""
DADOS FINANCEIROS ATUAIS

Saldo geral:
{self.formatar_dinheiro(self.saldo_atual)}

Receitas totais:
{self.formatar_dinheiro(self.total_receitas)}

Despesas totais:
{self.formatar_dinheiro(self.total_despesas)}

Saldo do mês:
{self.formatar_dinheiro(self.saldo_dashboard)}

Receitas do mês:
{self.formatar_dinheiro(self.total_receitas_dashboard)}

Despesas do mês:
{self.formatar_dinheiro(self.total_despesas_dashboard)}

Saldo projetado:
{self.formatar_dinheiro(self.saldo_projetado)}

Despesa projetada:
{self.formatar_dinheiro(self.despesa_projetada)}

Média diária:
{self.formatar_dinheiro(self.media_diaria_despesas)}

Percentual projetado:
{self.percentual_despesa_projetada:.1f}%

Reserva configurada:
{self.configuracoes.get("reserva", "20%")}

Perfil:
{perfil}

Horizonte:
{horizonte}

Reserva de emergência:
{reserva}

Nível de inteligência:
{self.configuracoes.get("inteligencia", "Normal")}

Quantidade de transações:
{len(self.transacoes)}

Quantidade de metas:
{len(self.metas)}
"""

    # =========================================================
    # CHAT
    # =========================================================

    def perguntar_ao_jarvis(self):

        if self.chat_processando:
            return

        pergunta = (
            self.input_pergunta_jarvis
            .text()
            .strip()
        )

        if not pergunta:
            return

        if (
            self.jarvis_ia is None
            or
            JarvisWorker is None
        ):

            self.chat_historico_visual.setText(
                "🤖 JARVIS:\n\n"
                "A IA local não está disponível."
            )

            return

        self.chat_processando = True

        self.input_pergunta_jarvis.setEnabled(
            False
        )

        self.botao_perguntar_jarvis.setEnabled(
            False
        )

        self.label_status_ia.setText(
            "● PROCESSANDO"
        )

        contexto = (
            self.criar_contexto_ia()
        )

        texto_atual = (
            self.chat_historico_visual.text()
        )

        self.chat_historico_visual.setText(
            texto_atual
            +
            "\n\n"
            +
            "👤 Você:\n"
            +
            pergunta
            +
            "\n\n"
            +
            "🤖 JARVIS:\n"
            +
            "Processando..."
        )

        self.thread_jarvis = QThread(
            self
        )

        try:

            self.worker_jarvis = JarvisWorker(
                pergunta,
                contexto
            )

        except Exception as erro:

            self.chat_processando = False

            self.input_pergunta_jarvis.setEnabled(
                True
            )

            self.botao_perguntar_jarvis.setEnabled(
                True
            )

            self.label_status_ia.setText(
                "● IA OFFLINE"
            )

            self.chat_historico_visual.setText(
                "🤖 JARVIS:\n\n"
                "Erro ao iniciar IA:\n\n"
                +
                str(erro)
            )

            self.thread_jarvis.deleteLater()

            self.thread_jarvis = None

            return

        self.worker_jarvis.moveToThread(
            self.thread_jarvis
        )

        self.thread_jarvis.started.connect(
            self.worker_jarvis.executar
        )

        self.worker_jarvis.resposta_pronta.connect(
            self.janela_resposta_jarvis
        )

        self.worker_jarvis.erro.connect(
            self.janela_erro_jarvis
        )

        self.worker_jarvis.finalizado.connect(
            self.finalizar_thread_jarvis
        )

        self.worker_jarvis.finalizado.connect(
            self.thread_jarvis.quit
        )

        self.thread_jarvis.finished.connect(
            self.worker_jarvis.deleteLater
        )

        self.thread_jarvis.finished.connect(
            self.thread_jarvis.deleteLater
        )

        self.thread_jarvis.finished.connect(
            self.limpar_referencias_thread_jarvis
        )

        self.thread_jarvis.start()

    # =========================================================
    # RESPOSTA IA
    # =========================================================

    def janela_resposta_jarvis(
        self,
        resposta
    ):

        if self.jarvis_ia is None:
            return

        try:

            if self.worker_jarvis is not None:

                self.jarvis_ia.historico = list(
                    self.worker_jarvis.ia.historico
                )

        except Exception as erro:

            print(
                "ERRO AO TRANSFERIR MEMÓRIA:",
                erro
            )

        texto = ""

        for mensagem in (
            self.jarvis_ia.historico
        ):

            if mensagem.get(
                "role"
            ) == "user":

                texto += (
                    "👤 Você:\n"
                    +
                    str(
                        mensagem.get(
                            "content",
                            ""
                        )
                    )
                    +
                    "\n\n"
                )

            elif mensagem.get(
                "role"
            ) == "assistant":

                texto += (
                    "🤖 JARVIS:\n"
                    +
                    str(
                        mensagem.get(
                            "content",
                            ""
                        )
                    )
                    +
                    "\n\n"
                )

        if not texto:

            texto = (
                "🤖 JARVIS:\n"
                +
                str(
                    resposta
                )
            )

        self.chat_historico_visual.setText(
            texto
        )

        self.label_status_ia.setText(
            "● IA LOCAL"
        )

    # =========================================================
    # ERRO IA
    # =========================================================

    def janela_erro_jarvis(
        self,
        erro
    ):

        print(
            "ERRO AO PERGUNTAR AO JARVIS:",
            erro
        )

        texto = (
            self.chat_historico_visual.text()
        )

        texto = texto.replace(
            "Processando...",
            "Não consegui concluir a resposta."
        )

        texto += (
            "\n\nDetalhe técnico:\n"
            +
            str(
                erro
            )
        )

        self.chat_historico_visual.setText(
            texto
        )

        self.label_status_ia.setText(
            "● IA LOCAL"
        )

    # =========================================================
    # FINALIZAR THREAD IA
    # =========================================================

    def finalizar_thread_jarvis(self):

        self.chat_processando = False

        self.input_pergunta_jarvis.setEnabled(
            True
        )

        self.botao_perguntar_jarvis.setEnabled(
            True
        )

        self.input_pergunta_jarvis.clear()

        self.input_pergunta_jarvis.setFocus()

        self.label_status_ia.setText(
            "● IA LOCAL"
        )

    # =========================================================
    # LIMPAR REFERÊNCIAS IA
    # =========================================================

    def limpar_referencias_thread_jarvis(self):

        self.thread_jarvis = None
        self.worker_jarvis = None

    # =========================================================
    # LIMPAR CONVERSA
    # =========================================================

    def limpar_conversa_jarvis(self):

        if self.chat_processando:

            QMessageBox.information(
                self,
                "JARVIS",
                "Aguarde a resposta atual terminar."
            )

            return

        if self.jarvis_ia is None:

            return

        resposta = QMessageBox.question(
            self,
            "Limpar conversa",
            "Deseja apagar a memória da conversa?"
        )

        if resposta != QMessageBox.Yes:

            return

        self.jarvis_ia.limpar_historico()

        self.chat_historico_visual.setText(
            "🤖 JARVIS:\n\n"
            "Memória da conversa limpa.\n"
            "Estou pronto para uma nova conversa."
        )

        self.input_pergunta_jarvis.clear()

        self.input_pergunta_jarvis.setFocus()

    # =========================================================
    # ECONOMIA
    # =========================================================

    def atualizar_economia(self):

        if self.economia_processando:
            return

        if EconomiaWorker is None:

            self.texto_cenario_economia.setText(
                "O arquivo economia_worker.py "
                "não foi encontrado."
            )

            return

        self.economia_processando = True

        self.botao_atualizar_economia.setEnabled(
            False
        )

        self.botao_atualizar_economia.setText(
            "⏳ Atualizando..."
        )

        self.label_economia_atualizacao.setText(
            "Consultando dados econômicos..."
        )

        self.texto_cenario_economia.setText(
            "📡 JARVIS está consultando "
            "os dados econômicos.\n\n"
            "A interface continua disponível."
        )

        self.thread_economia = QThread(
            self
        )

        try:

            self.worker_economia = EconomiaWorker(
                BASE_DIR
            )

        except Exception as erro:

            self.economia_processando = False

            self.botao_atualizar_economia.setEnabled(
                True
            )

            self.botao_atualizar_economia.setText(
                "🔄 Atualizar mercado"
            )

            self.texto_cenario_economia.setText(
                "Erro ao iniciar módulo de economia:\n\n"
                +
                str(erro)
            )

            self.thread_economia.deleteLater()

            self.thread_economia = None

            return

        self.worker_economia.moveToThread(
            self.thread_economia
        )

        self.thread_economia.started.connect(
            self.worker_economia.executar
        )

        self.worker_economia.dados_prontos.connect(
            self.economia_dados_recebidos
        )

        self.worker_economia.erro.connect(
            self.economia_erro
        )

        self.worker_economia.finalizado.connect(
            self.finalizar_thread_economia
        )

        self.worker_economia.finalizado.connect(
            self.thread_economia.quit
        )

        self.thread_economia.finished.connect(
            self.worker_economia.deleteLater
        )

        self.thread_economia.finished.connect(
            self.thread_economia.deleteLater
        )

        self.thread_economia.finished.connect(
            self.limpar_referencias_thread_economia
        )

        self.thread_economia.start()

    # =========================================================
    # DADOS ECONÔMICOS
    # =========================================================

    def economia_dados_recebidos(
        self,
        dados
    ):

        try:

            selic = dados.get("selic")
            ipca = dados.get("ipca")
            dolar = dados.get("dolar")

            if selic is not None:

                try:

                    self.label_economia_selic.setText(
                        f"{float(selic):.2f}%"
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    self.label_economia_selic.setText(
                        str(selic)
                    )

            else:

                self.label_economia_selic.setText(
                    "--"
                )

            if ipca is not None:

                try:

                    self.label_economia_ipca.setText(
                        f"{float(ipca):.2f}%"
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    self.label_economia_ipca.setText(
                        str(ipca)
                    )

            else:

                self.label_economia_ipca.setText(
                    "--"
                )

            if dolar is not None:

                try:

                    self.label_economia_dolar.setText(
                        f"R$ {float(dolar):.4f}"
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    self.label_economia_dolar.setText(
                        str(dolar)
                    )

            else:

                self.label_economia_dolar.setText(
                    "--"
                )

            atualizado = dados.get(
                "atualizado_em",
                "--"
            )

            self.label_economia_atualizacao.setText(
                f"Última atualização: {atualizado}"
            )

            mensagens = dados.get(
                "mensagens",
                []
            )

            texto = ""

            if isinstance(
                mensagens,
                list
            ):

                for mensagem in mensagens:

                    texto += (
                        "• "
                        +
                        str(mensagem)
                        +
                        "\n\n"
                    )

            elif mensagens:

                texto = str(
                    mensagens
                )

            if not texto:

                texto = (
                    "Os dados econômicos foram "
                    "atualizados, mas não há "
                    "análise textual disponível."
                )

            self.texto_cenario_economia.setText(
                texto
            )

        except Exception as erro:

            print(
                "ERRO AO PROCESSAR ECONOMIA:",
                erro
            )

            self.texto_cenario_economia.setText(
                "Os dados foram recebidos, "
                "mas ocorreu um erro ao "
                "atualizar a tela."
            )

    # =========================================================
    # ERRO ECONOMIA
    # =========================================================

    def economia_erro(
        self,
        erro
    ):

        print(
            "ERRO AO ATUALIZAR ECONOMIA:",
            erro
        )

        self.label_economia_atualizacao.setText(
            "Falha na atualização."
        )

        self.texto_cenario_economia.setText(
            "⚠ Não foi possível atualizar "
            "os dados econômicos agora.\n\n"
            "Verifique a conexão com a internet "
            "e tente novamente."
        )

    # =========================================================
    # FINALIZAR ECONOMIA
    # =========================================================

    def finalizar_thread_economia(self):

        self.economia_processando = False

        if hasattr(
            self,
            "botao_atualizar_economia"
        ):

            self.botao_atualizar_economia.setEnabled(
                True
            )

            self.botao_atualizar_economia.setText(
                "🔄 Atualizar mercado"
            )

    # =========================================================
    # LIMPAR REFERÊNCIAS ECONOMIA
    # =========================================================

    def limpar_referencias_thread_economia(self):

        self.thread_economia = None
        self.worker_economia = None

    # =========================================================
    # INVESTIMENTOS
    # =========================================================

    def analisar_investimento(self):

        texto = (
            self.input_valor_investimento
            .text()
            .strip()
        )

        try:

            valor = self.converter_valor(
                texto
            )

        except ValueError:

            self.texto_analise_investimento.setText(
                "Digite um valor válido."
            )

            return

        if valor <= 0:

            self.texto_analise_investimento.setText(
                "Digite um valor maior que zero."
            )

            return

        if self.investimentos is None:

            self.texto_analise_investimento.setText(
                "O módulo de investimentos "
                "não está disponível."
            )

            return

        perfil = (
            self.combo_perfil_investidor.currentText()
        )

        horizonte = (
            self.combo_horizonte_investidor.currentText()
        )

        reserva_pronta = (
            self.combo_reserva_investidor.currentText()
            ==
            "Já tenho reserva"
        )

        try:

            analise = (
                self.investimentos
                .sugerir_alocacao_educacional(
                    valor=valor,
                    perfil=perfil,
                    horizonte=horizonte,
                    reserva_pronta=reserva_pronta
                )
            )

            texto_resultado = (
                "🤖 JARVIS\n\n"
                f"Perfil: {analise['perfil']}\n"
                f"Horizonte: "
                f"{analise.get('horizonte', horizonte)}\n\n"
                f"Prioridade: "
                f"{analise['prioridade']}\n\n"
            )

            texto_resultado += (
                analise["motivo"]
                +
                "\n\n"
            )

            texto_resultado += (
                "Alternativas para estudo:\n"
            )

            for item in analise[
                "distribuicao"
            ]:

                texto_resultado += (
                    f"• {item['categoria']}: "
                    f"{item['percentual']}% "
                    f"= "
                    f"{self.formatar_dinheiro(item['valor'])}\n"
                )

                exemplos = item.get(
                    "exemplos",
                    []
                )

                if exemplos:

                    texto_resultado += (
                        "  Exemplos: "
                        +
                        ", ".join(
                            exemplos
                        )
                        +
                        "\n"
                    )

            texto_resultado += (
                "\n⚠ Análise educacional. "
                "Não representa garantia de retorno."
            )

            self.texto_analise_investimento.setText(
                texto_resultado
            )

        except Exception as erro:

            print(
                "ERRO AO ANALISAR INVESTIMENTO:",
                erro
            )

            self.texto_analise_investimento.setText(
                "Não consegui realizar a análise.\n\n"
                f"Detalhe técnico: {erro}"
            )

    # =========================================================
    # CONFIGURAÇÕES
    # =========================================================

    def criar_configuracoes(self):

        pagina = QWidget()

        layout_externo = QVBoxLayout(
            pagina
        )

        layout_externo.setContentsMargins(
            30,
            25,
            30,
            25
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        scroll.setFrameShape(
            QFrame.NoFrame
        )

        conteudo = QWidget()

        layout = QVBoxLayout(
            conteudo
        )

        layout.setContentsMargins(
            5,
            5,
            15,
            30
        )

        layout.setSpacing(16)

        titulo = QLabel(
            "Configurações"
        )

        titulo.setObjectName(
            "titulo_pagina"
        )

        layout.addWidget(
            titulo
        )

        descricao = QLabel(
            "Personalize o comportamento e a aparência do JARVIS."
        )

        descricao.setObjectName(
            "subtitulo_pagina"
        )

        layout.addWidget(
            descricao
        )

        layout.addWidget(
            self.criar_system_bar()
        )

        # =====================================================
        # APARÊNCIA
        # =====================================================

        painel_aparencia = QFrame()

        painel_aparencia.setObjectName(
            "painel"
        )

        layout_aparencia = QVBoxLayout(
            painel_aparencia
        )

        titulo_aparencia = QLabel(
            "🎨  Aparência"
        )

        titulo_aparencia.setObjectName(
            "titulo_painel"
        )

        layout_aparencia.addWidget(
            titulo_aparencia
        )

        self.combo_tema = QComboBox()

        self.combo_tema.addItems([
            "JARVIS Dark",
            "JARVIS Deep",
            "JARVIS Minimal",
            "JARVIS Blue",
            "JARVIS Purple",
            "JARVIS Green",
            "JARVIS Red",
            "JARVIS Orange",
            "JARVIS Pink",
            "JARVIS Cyan",
            "JARVIS White"
        ])

        self.combo_tema.setFixedWidth(
            200
        )

        linha = QHBoxLayout()

        coluna = QVBoxLayout()

        label = QLabel(
            "Tema visual"
        )

        label.setStyleSheet(
            "font-size: 13px; font-weight: bold;"
        )

        desc = QLabel(
            "Define o estilo visual do JARVIS."
        )

        desc.setObjectName(
            "subtitulo_pagina"
        )

        coluna.addWidget(
            label
        )

        coluna.addWidget(
            desc
        )

        linha.addLayout(
            coluna
        )

        linha.addStretch()

        linha.addWidget(
            self.combo_tema
        )

        layout_aparencia.addLayout(
            linha
        )

        self.combo_animacoes = QComboBox()

        self.combo_animacoes.addItems([
            "Ativados",
            "Desativados"
        ])

        self.combo_animacoes.setFixedWidth(
            200
        )

        linha = QHBoxLayout()

        coluna = QVBoxLayout()

        label = QLabel(
            "Efeitos visuais"
        )

        label.setStyleSheet(
            "font-size: 13px; font-weight: bold;"
        )

        desc = QLabel(
            "Ativa efeitos visuais da interface."
        )

        desc.setObjectName(
            "subtitulo_pagina"
        )

        coluna.addWidget(
            label
        )

        coluna.addWidget(
            desc
        )

        linha.addLayout(
            coluna
        )

        linha.addStretch()

        linha.addWidget(
            self.combo_animacoes
        )

        layout_aparencia.addLayout(
            linha
        )

        layout.addWidget(
            painel_aparencia
        )

        # =====================================================
        # ALERTAS
        # =====================================================

        painel_alertas = QFrame()

        painel_alertas.setObjectName(
            "painel"
        )

        layout_alertas = QVBoxLayout(
            painel_alertas
        )

        titulo_alertas = QLabel(
            "🚨  Alertas e Monitoramento"
        )

        titulo_alertas.setObjectName(
            "titulo_painel"
        )

        layout_alertas.addWidget(
            titulo_alertas
        )

        self.combo_alertas = QComboBox()

        self.combo_alertas.addItems([
            "Ativados",
            "Desativados"
        ])

        self.combo_alertas.setFixedWidth(
            200
        )

        linha = QHBoxLayout()

        coluna = QVBoxLayout()

        label = QLabel(
            "Monitoramento automático"
        )

        label.setStyleSheet(
            "font-size: 13px; font-weight: bold;"
        )

        desc = QLabel(
            "Ativa ou desativa o sistema de alertas."
        )

        desc.setObjectName(
            "subtitulo_pagina"
        )

        coluna.addWidget(
            label
        )

        coluna.addWidget(
            desc
        )

        linha.addLayout(
            coluna
        )

        linha.addStretch()

        linha.addWidget(
            self.combo_alertas
        )

        layout_alertas.addLayout(
            linha
        )

        self.combo_sensibilidade = QComboBox()

        self.combo_sensibilidade.addItems([
            "Baixa",
            "Normal",
            "Alta"
        ])

        self.combo_sensibilidade.setFixedWidth(
            200
        )

        linha = QHBoxLayout()

        coluna = QVBoxLayout()

        label = QLabel(
            "Sensibilidade dos alertas"
        )

        label.setStyleSheet(
            "font-size: 13px; font-weight: bold;"
        )

        desc = QLabel(
            "Define quando o JARVIS deve chamar sua atenção."
        )

        desc.setObjectName(
            "subtitulo_pagina"
        )

        coluna.addWidget(
            label
        )

        coluna.addWidget(
            desc
        )

        linha.addLayout(
            coluna
        )

        linha.addStretch()

        linha.addWidget(
            self.combo_sensibilidade
        )

        layout_alertas.addLayout(
            linha
        )

        layout.addWidget(
            painel_alertas
        )

        # =====================================================
        # FINANCEIRO
        # =====================================================

        painel_financeiro = QFrame()

        painel_financeiro.setObjectName(
            "painel"
        )

        layout_financeiro = QVBoxLayout(
            painel_financeiro
        )

        titulo_financeiro = QLabel(
            "💰  Configurações Financeiras"
        )

        titulo_financeiro.setObjectName(
            "titulo_painel"
        )

        layout_financeiro.addWidget(
            titulo_financeiro
        )

        self.combo_moeda = QComboBox()

        self.combo_moeda.addItems([
            "BRL - Real brasileiro",
            "USD - Dólar",
            "EUR - Euro"
        ])

        self.combo_moeda.setFixedWidth(
            220
        )

        linha = QHBoxLayout()

        coluna = QVBoxLayout()

        label = QLabel(
            "Moeda principal"
        )

        label.setStyleSheet(
            "font-size: 13px; font-weight: bold;"
        )

        desc = QLabel(
            "Moeda utilizada nos cálculos."
        )

        desc.setObjectName(
            "subtitulo_pagina"
        )

        coluna.addWidget(
            label
        )

        coluna.addWidget(
            desc
        )

        linha.addLayout(
            coluna
        )

        linha.addStretch()

        linha.addWidget(
            self.combo_moeda
        )

        layout_financeiro.addLayout(
            linha
        )

        self.combo_reserva = QComboBox()

        self.combo_reserva.addItems([
            "10%",
            "15%",
            "20%",
            "25%",
            "30%"
        ])

        self.combo_reserva.setFixedWidth(
            200
        )

        linha = QHBoxLayout()

        coluna = QVBoxLayout()

        label = QLabel(
            "Reserva financeira"
        )

        label.setStyleSheet(
            "font-size: 13px; font-weight: bold;"
        )

        desc = QLabel(
            "Percentual do saldo recomendado para preservar."
        )

        desc.setObjectName(
            "subtitulo_pagina"
        )

        coluna.addWidget(
            label
        )

        coluna.addWidget(
            desc
        )

        linha.addLayout(
            coluna
        )

        linha.addStretch()

        linha.addWidget(
            self.combo_reserva
        )

        layout_financeiro.addLayout(
            linha
        )

        layout.addWidget(
            painel_financeiro
        )

        # =====================================================
        # JARVIS
        # =====================================================

        painel_jarvis_config = QFrame()

        painel_jarvis_config.setObjectName(
            "painel_jarvis"
        )

        layout_jarvis = QVBoxLayout(
            painel_jarvis_config
        )

        titulo_jarvis = QLabel(
            "🤖  Personalidade do JARVIS"
        )

        titulo_jarvis.setObjectName(
            "titulo_jarvis"
        )

        layout_jarvis.addWidget(
            titulo_jarvis
        )

        self.combo_inteligencia = QComboBox()

        self.combo_inteligencia.addItems([
            "Básico",
            "Normal",
            "Avançado"
        ])

        self.combo_inteligencia.setFixedWidth(
            200
        )

        linha = QHBoxLayout()

        coluna = QVBoxLayout()

        label = QLabel(
            "Nível de análise"
        )

        label.setStyleSheet(
            "font-size: 13px; font-weight: bold;"
        )

        desc = QLabel(
            "Define a quantidade de informações analisadas."
        )

        desc.setObjectName(
            "subtitulo_pagina"
        )

        coluna.addWidget(
            label
        )

        coluna.addWidget(
            desc
        )

        linha.addLayout(
            coluna
        )

        linha.addStretch()

        linha.addWidget(
            self.combo_inteligencia
        )

        layout_jarvis.addLayout(
            linha
        )

        self.combo_mensagens = QComboBox()

        self.combo_mensagens.addItems([
            "Ativadas",
            "Desativadas"
        ])

        self.combo_mensagens.setFixedWidth(
            200
        )

        linha = QHBoxLayout()

        coluna = QVBoxLayout()

        label = QLabel(
            "Mensagens inteligentes"
        )

        label.setStyleSheet(
            "font-size: 13px; font-weight: bold;"
        )

        desc = QLabel(
            "Exibe recomendações personalizadas no Dashboard."
        )

        desc.setObjectName(
            "subtitulo_pagina"
        )

        coluna.addWidget(
            label
        )

        coluna.addWidget(
            desc
        )

        linha.addLayout(
            coluna
        )

        linha.addStretch()

        linha.addWidget(
            self.combo_mensagens
        )

        layout_jarvis.addLayout(
            linha
        )

        layout.addWidget(
            painel_jarvis_config
        )

        # =====================================================
        # SISTEMA
        # =====================================================

        painel_sistema = QFrame()

        painel_sistema.setObjectName(
            "painel"
        )

        layout_sistema = QVBoxLayout(
            painel_sistema
        )

        titulo_sistema = QLabel(
            "🔧  Sistema"
        )

        titulo_sistema.setObjectName(
            "titulo_painel"
        )

        layout_sistema.addWidget(
            titulo_sistema
        )

        informacoes = QLabel(
            "JARVIS Finance Core\n"
            "Interface gráfica: PySide6\n"
            "Banco de dados: SQLite\n"
            "Gráficos: Matplotlib\n"
            "Economia: EconomiaJARVIS\n"
            "Investimentos: InvestimentosJARVIS\n"
            "IA: Ollama Local\n"
            "Chat: QThread\n"
            "Economia: QThread\n"
            "Modo: Local"
        )

        layout_sistema.addWidget(
            informacoes
        )

        restaurar = QPushButton(
            "♻ Restaurar configurações"
        )

        restaurar.setMinimumHeight(
            40
        )

        layout_sistema.addWidget(
            restaurar
        )

        restaurar.clicked.connect(
            self.restaurar_configuracoes
        )

        layout.addWidget(
            painel_sistema
        )

        # =====================================================
        # SALVAR
        # =====================================================

        botoes_final = QHBoxLayout()

        botoes_final.addStretch()

        salvar = QPushButton(
            "💾 Salvar configurações"
        )

        salvar.setMinimumSize(
            220,
            44
        )

        botoes_final.addWidget(
            salvar
        )

        layout.addLayout(
            botoes_final
        )

        salvar.clicked.connect(
            self.salvar_configuracoes
        )

        layout.addStretch()

        scroll.setWidget(
            conteudo
        )

        layout_externo.addWidget(
            scroll
        )

        self.conectar_configuracoes_tempo_real()

        return pagina

    # =========================================================
    # CONFIGURAÇÕES TEMPO REAL
    # =========================================================

    def conectar_configuracoes_tempo_real(self):

        self.combo_tema.currentTextChanged.connect(
            self.aplicar_configuracao_tempo_real
        )

        self.combo_animacoes.currentTextChanged.connect(
            self.aplicar_configuracao_tempo_real
        )

        self.combo_alertas.currentTextChanged.connect(
            self.aplicar_configuracao_tempo_real
        )

        self.combo_sensibilidade.currentTextChanged.connect(
            self.aplicar_configuracao_tempo_real
        )

        self.combo_moeda.currentTextChanged.connect(
            self.aplicar_configuracao_tempo_real
        )

        self.combo_reserva.currentTextChanged.connect(
            self.aplicar_configuracao_tempo_real
        )

        self.combo_inteligencia.currentTextChanged.connect(
            self.aplicar_configuracao_tempo_real
        )

        self.combo_mensagens.currentTextChanged.connect(
            self.aplicar_configuracao_tempo_real
        )

    # =========================================================
    # APLICAR CONFIGURAÇÕES
    # =========================================================

    def aplicar_configuracao_tempo_real(self):

        if not hasattr(
            self,
            "combo_tema"
        ):

            return

        self.configuracoes["tema"] = (
            self.combo_tema.currentText()
        )

        self.configuracoes["animacoes"] = (
            self.combo_animacoes.currentText()
        )

        self.configuracoes["alertas"] = (
            self.combo_alertas.currentText()
        )

        self.configuracoes[
            "sensibilidade_alertas"
        ] = (
            self.combo_sensibilidade.currentText()
        )

        self.configuracoes["moeda"] = (
            self.combo_moeda.currentText()
        )

        self.configuracoes["reserva"] = (
            self.combo_reserva.currentText()
        )

        self.configuracoes["inteligencia"] = (
            self.combo_inteligencia.currentText()
        )

        self.configuracoes["mensagens"] = (
            self.combo_mensagens.currentText()
        )

        self.atualizar_cerebro()
        self.aplicar_tema()

        try:
            self.atualizar_dashboard()
        except Exception:
            pass

        try:

            if self.relatorios_inicializados:
                self.atualizar_relatorios()

        except Exception:
            pass

        self.salvar_arquivo_configuracoes()

    # =========================================================
    # CARREGAR CONFIGURAÇÕES NA INTERFACE
    # =========================================================

    def carregar_configuracoes_na_interface(self):

        if not hasattr(
            self,
            "combo_tema"
        ):

            return

        combos = [
            self.combo_tema,
            self.combo_animacoes,
            self.combo_alertas,
            self.combo_sensibilidade,
            self.combo_moeda,
            self.combo_reserva,
            self.combo_inteligencia,
            self.combo_mensagens
        ]

        for combo in combos:
            combo.blockSignals(True)

        self.combo_tema.setCurrentText(
            self.configuracoes.get(
                "tema",
                "JARVIS Dark"
            )
        )

        self.combo_animacoes.setCurrentText(
            self.configuracoes.get(
                "animacoes",
                "Ativados"
            )
        )

        self.combo_alertas.setCurrentText(
            self.configuracoes.get(
                "alertas",
                "Ativados"
            )
        )

        self.combo_sensibilidade.setCurrentText(
            self.configuracoes.get(
                "sensibilidade_alertas",
                "Normal"
            )
        )

        self.combo_moeda.setCurrentText(
            self.configuracoes.get(
                "moeda",
                "BRL - Real brasileiro"
            )
        )

        self.combo_reserva.setCurrentText(
            self.configuracoes.get(
                "reserva",
                "20%"
            )
        )

        self.combo_inteligencia.setCurrentText(
            self.configuracoes.get(
                "inteligencia",
                "Normal"
            )
        )

        self.combo_mensagens.setCurrentText(
            self.configuracoes.get(
                "mensagens",
                "Ativadas"
            )
        )

        for combo in combos:
            combo.blockSignals(False)

        self.atualizar_cerebro()

    # =========================================================
    # SALVAR CONFIGURAÇÕES
    # =========================================================

    def salvar_configuracoes(self):

        self.aplicar_configuracao_tempo_real()

        QMessageBox.information(
            self,
            "JARVIS",
            "⚙ Configurações salvas com sucesso."
        )

    # =========================================================
    # RESTAURAR CONFIGURAÇÕES
    # =========================================================

    def restaurar_configuracoes(self):

        resposta = QMessageBox.question(
            self,
            "Restaurar configurações",
            "Deseja restaurar as configurações padrão?"
        )

        if resposta != QMessageBox.Yes:
            return

        self.configuracoes = (
            self.configuracoes_padrao()
        )

        self.carregar_configuracoes_na_interface()
        self.atualizar_cerebro()
        self.aplicar_tema()
        self.atualizar_dashboard()
        self.salvar_arquivo_configuracoes()

        QMessageBox.information(
            self,
            "JARVIS",
            "Configurações restauradas."
        )

    # =========================================================
    # RESERVA
    # =========================================================

    def obter_percentual_reserva(self):

        valor = (
            self.configuracoes.get(
                "reserva",
                "20%"
            )
        )

        try:

            numero = float(
                str(
                    valor
                ).replace(
                    "%",
                    ""
                )
            )

            return numero / 100

        except (
            ValueError,
            TypeError
        ):

            return 0.20

    # =========================================================
    # FORMATAR DINHEIRO
    # =========================================================

    def formatar_dinheiro(
        self,
        valor
    ):

        moeda = (
            self.configuracoes.get(
                "moeda",
                "BRL - Real brasileiro"
            )
        )

        if moeda.startswith(
            "USD"
        ):

            simbolo = "$"

        elif moeda.startswith(
            "EUR"
        ):

            simbolo = "€"

        else:

            simbolo = "R$"

        try:

            valor = float(
                valor
            )

        except (
            ValueError,
            TypeError
        ):

            valor = 0.0

        return (
            f"{simbolo} {valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    # =========================================================
    # CONVERTER VALOR
    # =========================================================

    def converter_valor(
        self,
        valor
    ):

        valor = str(
            valor
        )

        valor = valor.replace(
            "R$",
            ""
        )

        valor = valor.replace(
            "$",
            ""
        )

        valor = valor.replace(
            "€",
            ""
        )

        valor = valor.replace(
            " ",
            ""
        )

        if "," in valor:

            valor = valor.replace(
                ".",
                ""
            )

            valor = valor.replace(
                ",",
                "."
            )

        return float(
            valor
        )

    # =========================================================
    # FECHAR
    # =========================================================

    def closeEvent(
        self,
        event
    ):

        try:

            if (
                self.thread_jarvis is not None
                and
                self.thread_jarvis.isRunning()
            ):

                self.thread_jarvis.quit()

                self.thread_jarvis.wait(
                    1000
                )

        except Exception:

            pass

        try:

            if (
                self.thread_economia is not None
                and
                self.thread_economia.isRunning()
            ):

                self.thread_economia.quit()

                self.thread_economia.wait(
                    1000
                )

        except Exception:

            pass

        try:

            self.aplicar_configuracao_tempo_real()

        except Exception:

            pass

        try:

            self.banco.fechar()

        except Exception:

            pass

        event.accept()