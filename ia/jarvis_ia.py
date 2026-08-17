import requests


class JarvisIA:

    def __init__(self):

        self.url = (
            "http://localhost:11434/api/chat"
        )

        self.modelo = "llama3.2:3b"

        self.historico = []

        self.system_prompt = """
Você é JARVIS, o assistente pessoal inteligente
do usuário.

Sua identidade é JARVIS.

Quando o usuário escrever:

Olá JARVIS
Oi JARVIS
Bom dia JARVIS
Boa tarde JARVIS
Boa noite JARVIS

ele está falando diretamente com você.

Não interprete "Ola Jarvis" como nome de uma pessoa.

PERSONALIDADE:

- inteligente
- educado
- profissional
- natural
- amigável
- objetivo
- elegante
- português brasileiro

Você pode conversar livremente.

Não fique limitado a palavras-chave.

CAPACIDADES:

- conversar normalmente
- responder perguntas
- explicar assuntos
- explicar economia
- explicar investimentos
- analisar finanças pessoais
- analisar despesas
- analisar receitas
- ajudar com metas
- criar planos
- comparar alternativas

FINANÇAS:

Use os dados fornecidos pelo sistema quando
eles forem relevantes.

Nunca invente números financeiros.

INVESTIMENTOS:

Nunca prometa lucro.

Explique risco, liquidez, prazo e custos.

CONVERSA:

Você pode conversar sobre assuntos gerais.

Se o usuário apenas cumprimentar,
responda naturalmente.

Você é o próprio JARVIS.
"""

    def limpar_historico(self):

        self.historico = []

    def quantidade_mensagens(self):

        return len(
            self.historico
        )

    def responder(
        self,
        pergunta,
        contexto=""
    ):

        pergunta = str(
            pergunta
        ).strip()

        if not pergunta:

            return (
                "Estou aguardando sua pergunta."
            )

        mensagens = [
            {
                "role": "system",
                "content":
                    self.system_prompt
                    +
                    "\n\nCONTEXTO FINANCEIRO:\n"
                    +
                    contexto
            }
        ]

        mensagens.extend(
            self.historico[-12:]
        )

        mensagens.append(
            {
                "role": "user",
                "content": pergunta
            }
        )

        resposta = requests.post(
            self.url,
            json={
                "model": self.modelo,
                "messages": mensagens,
                "stream": False
            },
            timeout=180
        )

        resposta.raise_for_status()

        dados = resposta.json()

        mensagem = (
            dados
            .get(
                "message",
                {}
            )
            .get(
                "content",
                ""
            )
        )

        if not mensagem:

            raise RuntimeError(
                "O Ollama não retornou uma resposta."
            )

        mensagem = mensagem.strip()

        self.historico.append(
            {
                "role": "user",
                "content": pergunta
            }
        )

        self.historico.append(
            {
                "role": "assistant",
                "content": mensagem
            }
        )

        self.historico = (
            self.historico[-12:]
        )

        return mensagem