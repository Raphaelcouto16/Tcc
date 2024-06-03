import psycopg2
import spacy
import re

# Carregar o modelo de linguagem do spaCy para português
nlp = spacy.load("pt_core_news_sm")

# Função para limpar e separar palavras-chave usando spaCy
def extrair_palavras(texto):
    doc = nlp(texto)
    palavras = set()
    for token in doc:
        # Incluir apenas palavras que não sejam stopwords, que não sejam pontuações e que sejam alfas
        if not token.is_stop and not token.is_punct and token.is_alpha:
            palavras.add(token.lemma_.lower())
    return palavras

# Conectar ao banco de dados
conn = psycopg2.connect(
    dbname="projetotcc",
    user="projetotcc",
    password="TryTiR@1309927",
    host="179.188.16.157"
)
cur = conn.cursor()

# Ler dados da tabela eventos
cur.execute("SELECT id_evento, nome_do_evento, sobre, objetivos, programacao, pre_requisitos FROM public.eventos")
eventos = cur.fetchall()

# Processar cada evento
for evento in eventos:
    id_evento = evento[0]
    textos = evento[1:]

    # Extrair palavras-chave
    palavras_chave = set()
    for texto in textos:
        if texto:
            palavras_chave.update(extrair_palavras(texto))

    # Verificar e inserir palavras-chave na tabela palavras_chave
    for palavra in palavras_chave:
        cur.execute("SELECT id_palavra FROM public.palavras_chave WHERE palavra = %s", (palavra,))
        resultado = cur.fetchone()
        if resultado:
            id_palavra = resultado[0]
        else:
            cur.execute("INSERT INTO public.palavras_chave (palavra) VALUES (%s) RETURNING id_palavra", (palavra,))
            id_palavra = cur.fetchone()[0]
            conn.commit()
        
        # Inserir na tabela evento_palavras_chaves
        cur.execute("INSERT INTO public.evento_palavras_chaves (id_evento, id_palavra) VALUES (%s, %s)", (id_evento, id_palavra))
        conn.commit()

# Fechar a conexão com o banco de dados
cur.close()
conn.close()
