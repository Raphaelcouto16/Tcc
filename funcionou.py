import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Conectar ao banco de dados PostgreSQL
def connect_db():
    conn = psycopg2.connect(
        dbname="projetotcc",
        user="projetotcc",
        password="TryTiR@1309927",
        host="179.188.16.157"
    )
    return conn

# Extrair dados do banco de dados
def extract_data(conn):
    query_alunos = "SELECT * FROM public.alunos"
    query_aluno_palavras_chaves = "SELECT * FROM public.aluno_palavras_chaves"
    query_evento_palavras_chaves = "SELECT * FROM public.evento_palavras_chaves"
    query_palavras_chave = "SELECT * FROM public.palavras_chave"
    
    
    

    df_alunos = pd.read_sql(query_alunos, conn)
    df_aluno_palavras_chaves = pd.read_sql(query_aluno_palavras_chaves, conn)
    df_evento_palavras_chaves = pd.read_sql(query_evento_palavras_chaves, conn)
    df_palavras_chave = pd.read_sql(query_palavras_chave, conn)
    
    return df_alunos, df_aluno_palavras_chaves, df_evento_palavras_chaves, df_palavras_chave

# Pré-processar dados
def preprocess_data(df_alunos, df_aluno_palavras_chaves, df_evento_palavras_chaves, df_palavras_chave):
    aluno_keywords = df_aluno_palavras_chaves.merge(df_palavras_chave, left_on='id_palavra', right_on='id_palavra')
    evento_keywords = df_evento_palavras_chaves.merge(df_palavras_chave, left_on='id_palavra', right_on='id_palavra')
    
    aluno_keywords_agg = aluno_keywords.groupby('id_aluno')['palavra'].apply(lambda x: ' '.join(x)).reset_index()
    evento_keywords_agg = evento_keywords.groupby('id_evento')['palavra'].apply(lambda x: ' '.join(x)).reset_index()
    
    return aluno_keywords_agg, evento_keywords_agg

# Treinar modelo e fazer recomendações
def recommend_events(aluno_keywords_agg, evento_keywords_agg):
    vectorizer = CountVectorizer()
    
    aluno_vectors = vectorizer.fit_transform(aluno_keywords_agg['palavra'])
    evento_vectors = vectorizer.transform(evento_keywords_agg['palavra'])
    
    similarities = cosine_similarity(aluno_vectors, evento_vectors)
    
    recommendations = []
    for aluno_idx in range(similarities.shape[0]):
        event_indices = similarities[aluno_idx].argsort()[-5:][::-1]  # Top 5 eventos
        for event_idx in event_indices:
            recommendations.append((
                int(aluno_keywords_agg.iloc[aluno_idx]['id_aluno']), 
                int(evento_keywords_agg.iloc[event_idx]['id_evento'])
            ))
    
    return recommendations

# Inserir recomendações na tabela alunos_eventos
def insert_recommendations(conn, recommendations):
    insert_query = "INSERT INTO public.alunos_eventos (id_aluno, id_evento) VALUES %s"
    cursor = conn.cursor()
    execute_values(cursor, insert_query, recommendations)
    conn.commit()

# Função principal
def main():
    conn = connect_db()
    df_alunos, df_aluno_palavras_chaves, df_evento_palavras_chaves, df_palavras_chave = extract_data(conn)
    aluno_keywords_agg, evento_keywords_agg = preprocess_data(df_alunos, df_aluno_palavras_chaves, df_evento_palavras_chaves, df_palavras_chave)
    recommendations = recommend_events(aluno_keywords_agg, evento_keywords_agg)
    insert_recommendations(conn, recommendations)
    conn.close()

if __name__ == "__main__":
    main()


#comentario de varias linhas

# Este script Python é usado para conectar a um banco de dados PostgreSQL, extrair dados, processá-los, treinar um modelo de recomendação e, finalmente, inserir as recomendações de volta no banco de dados.

# O script começa importando as bibliotecas necessárias. Ele usa psycopg2 para conectar ao banco de dados PostgreSQL, pandas e numpy para manipulação de dados, CountVectorizer do sklearn para converter texto em vetores e cosine_similarity do sklearn para calcular a similaridade entre vetores.

# A função connect_db é usada para estabelecer uma conexão com o banco de dados PostgreSQL. Ela retorna a conexão estabelecida.

# A função extract_data é usada para extrair dados do banco de dados. Ela executa várias consultas SQL para extrair dados de diferentes tabelas e armazena os resultados em DataFrames do pandas.

# A função preprocess_data é usada para pré-processar os dados extraídos. Ela mescla os DataFrames com base em IDs comuns e agrupa as palavras-chave por aluno e evento.

# A função recommend_events é usada para treinar o modelo de recomendação e fazer recomendações. Ela converte as palavras-chave em vetores usando CountVectorizer, calcula a similaridade entre os vetores de alunos e eventos usando cosine_similarity e, em seguida, seleciona os 5 principais eventos para cada aluno.

# A função insert_recommendations é usada para inserir as recomendações de volta no banco de dados. Ela executa uma consulta SQL de inserção para adicionar as recomendações à tabela alunos_eventos.

# Finalmente, a função main é usada para orquestrar todo o processo. Ela chama todas as funções acima na ordem correta e fecha a conexão com o banco de dados no final.

# O script é executado se o nome do arquivo é o ponto de entrada do programa, ou seja, se o script é executado diretamente e não importado como um módulo.
