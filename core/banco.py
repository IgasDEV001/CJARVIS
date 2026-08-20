import sqlite3
import os


class BancoDados:

    def __init__(self):

        # =====================================================
        # CONFIGURAR PASTA DO BANCO DE DADOS
        # =====================================================

        # O banco será salvo na pasta AppData do usuário.
        # Isso evita problemas de permissão quando o CJARVIS
        # estiver instalado em uma pasta protegida do Windows.

        pasta_dados = os.path.join(
            os.environ["APPDATA"],
            "CJARVIS"
        )

        # Criar a pasta automaticamente caso ela não exista
        os.makedirs(
            pasta_dados,
            exist_ok=True
        )

        # Caminho completo do banco de dados
        caminho_banco = os.path.join(
            pasta_dados,
            "jarvis.db"
        )

        # Conectar ao banco
        self.conexao = sqlite3.connect(
            caminho_banco
        )

        self.criar_tabelas()

    # =====================================================
    # CRIAR TABELAS
    # =====================================================

    def criar_tabelas(self):

        cursor = self.conexao.cursor()

        # =================================================
        # TABELA DE TRANSACOES
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                tipo TEXT NOT NULL,

                descricao TEXT NOT NULL,

                categoria TEXT NOT NULL,

                valor REAL NOT NULL,

                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # =================================================
        # TABELA DE METAS
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metas (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                nome TEXT NOT NULL,

                objetivo REAL NOT NULL,

                guardado REAL NOT NULL DEFAULT 0,

                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conexao.commit()

    # =====================================================
    # ADICIONAR TRANSACAO
    # =====================================================

    def adicionar_transacao(
        self,
        tipo,
        descricao,
        categoria,
        valor,
        data=None
    ):

        cursor = self.conexao.cursor()

        if data:

            cursor.execute("""
                INSERT INTO transacoes
                (
                    tipo,
                    descricao,
                    categoria,
                    valor,
                    data
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                tipo,
                descricao,
                categoria,
                valor,
                data
            ))

        else:

            cursor.execute("""
                INSERT INTO transacoes
                (
                    tipo,
                    descricao,
                    categoria,
                    valor
                )
                VALUES (?, ?, ?, ?)
            """, (
                tipo,
                descricao,
                categoria,
                valor
            ))

        self.conexao.commit()

        return cursor.lastrowid

    # =====================================================
    # BUSCAR TODAS AS TRANSACOES
    # =====================================================

    def buscar_transacoes(self):

        cursor = self.conexao.cursor()

        cursor.execute("""
            SELECT
                id,
                tipo,
                descricao,
                categoria,
                valor,
                data

            FROM transacoes

            ORDER BY id DESC
        """)

        return cursor.fetchall()

    # =====================================================
    # BUSCAR TRANSACOES POR MES
    # =====================================================

    def buscar_transacoes_mes(
        self,
        ano,
        mes
    ):

        cursor = self.conexao.cursor()

        prefixo = (
            f"{ano:04d}-{mes:02d}"
        )

        cursor.execute("""
            SELECT
                id,
                tipo,
                descricao,
                categoria,
                valor,
                data

            FROM transacoes

            WHERE data LIKE ?

            ORDER BY id DESC
        """, (
            prefixo + "%",
        ))

        return cursor.fetchall()

    # =====================================================
    # EDITAR TRANSACAO
    # =====================================================

    def editar_transacao(
        self,
        id_transacao,
        tipo,
        descricao,
        categoria,
        valor,
        data
    ):

        cursor = self.conexao.cursor()

        cursor.execute("""
            UPDATE transacoes

            SET
                tipo = ?,
                descricao = ?,
                categoria = ?,
                valor = ?,
                data = ?

            WHERE id = ?
        """, (
            tipo,
            descricao,
            categoria,
            valor,
            data,
            id_transacao
        ))

        self.conexao.commit()

    # =====================================================
    # EXCLUIR TRANSACAO
    # =====================================================

    def excluir_transacao(
        self,
        id_transacao
    ):

        cursor = self.conexao.cursor()

        cursor.execute("""
            DELETE FROM transacoes

            WHERE id = ?
        """, (
            id_transacao,
        ))

        self.conexao.commit()

    # =====================================================
    # ADICIONAR META
    # =====================================================

    def adicionar_meta(
        self,
        nome,
        objetivo,
        guardado
    ):

        cursor = self.conexao.cursor()

        cursor.execute("""
            INSERT INTO metas
            (
                nome,
                objetivo,
                guardado
            )

            VALUES (?, ?, ?)
        """, (
            nome,
            objetivo,
            guardado
        ))

        self.conexao.commit()

        return cursor.lastrowid

    # =====================================================
    # BUSCAR METAS
    # =====================================================

    def buscar_metas(self):

        cursor = self.conexao.cursor()

        cursor.execute("""
            SELECT
                id,
                nome,
                objetivo,
                guardado,
                data

            FROM metas

            ORDER BY id DESC
        """)

        return cursor.fetchall()

    # =====================================================
    # EDITAR META
    # =====================================================

    def editar_meta(
        self,
        id_meta,
        nome,
        objetivo,
        guardado
    ):

        cursor = self.conexao.cursor()

        cursor.execute("""
            UPDATE metas

            SET
                nome = ?,
                objetivo = ?,
                guardado = ?

            WHERE id = ?
        """, (
            nome,
            objetivo,
            guardado,
            id_meta
        ))

        self.conexao.commit()

    # =====================================================
    # EXCLUIR META
    # =====================================================

    def excluir_meta(
        self,
        id_meta
    ):

        cursor = self.conexao.cursor()

        cursor.execute("""
            DELETE FROM metas

            WHERE id = ?
        """, (
            id_meta,
        ))

        self.conexao.commit()

    # =====================================================
    # FECHAR BANCO
    # =====================================================

    def fechar(self):

        self.conexao.close()