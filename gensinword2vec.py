import psycopg2
import pandas as pd
import gensim.downloader as api
from fuzzywuzzy import fuzz

# Carregar vetores de palavras pré-treinados (Word2Vec)
modelo_word2vec = api.load('word2vec-google-news-300')

# Carregar dados do banco de dados
conn = psycopg2.connect(
    dbname="projetotcc",
    user="projetotcc",
    password="TryTiR@1309927",
    host="179.188.16.157"
)

eventos_df = pd.read_sql_query('SELECT nome_do_evento, area, sobre FROM eventos', conn)
cursos_df = pd.read_sql_query('SELECT nome, area FROM cursos', conn)

# Defina a limiar de similaridade
limiar_similaridade = 0.7  # Você pode ajustar esse valor conforme necessário

# Para cada evento, encontrar cursos associados com similaridade de palavras
for index, evento in eventos_df.iterrows():
    nome_evento = evento['nome_do_evento']
    area_evento = evento['area']

    # Filtrar cursos com a mesma área do evento
    cursos_area_evento = cursos_df[cursos_df["area"] == area_evento]

    # Calcular similaridade de palavras entre o nome do evento e o nome dos cursos
    for index, curso in cursos_area_evento.iterrows():
        nome_curso = curso['nome']
        try:
            similaridade = modelo_word2vec.similarity(nome_evento, nome_curso)

            # Se a similaridade for maior que o limiar, considere o curso associado ao evento
            if similaridade >= limiar_similaridade:
                print(f"O evento '{nome_evento}' está associado ao curso '{nome_curso}' (similaridade: {similaridade})")
        except KeyError:
            pass  # Se uma palavra não estiver presente no modelo Word2Vec, Keyerror será levantado
