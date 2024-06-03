import psycopg2
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

# Função para conectar ao banco de dados
def connect_db():
    return psycopg2.connect(
        dbname="projetotcc",
        user="projetotcc",
        password="TryTiR@1309927",
        host="179.188.16.157"
    )

# Função para obter dados de alunos e suas palavras-chave
def get_aluno_palavras_chaves(cur):
    query = """
    SELECT a.id_aluno, p.palavra
    FROM public.alunos a
    JOIN public.aluno_palavras_chaves apc ON a.id_aluno = apc.id_aluno
    JOIN public.palavras_chave p ON apc.id_palavra = p.id_palavra
    """
    cur.execute(query)
    return cur.fetchall()

# Função para obter dados de eventos e suas palavras-chave
def get_evento_palavras_chaves(cur):
    query = """
    SELECT e.id_evento, p.palavra
    FROM public.eventos e
    JOIN public.evento_palavras_chaves epc ON e.id_evento = epc.id_evento
    JOIN public.palavras_chave p ON epc.id_palavra = p.id_palavra
    """
    cur.execute(query)
    return cur.fetchall()

# Conectar ao banco de dados e obter dados
conn = connect_db()
cur = conn.cursor()

aluno_palavras = get_aluno_palavras_chaves(cur)
evento_palavras = get_evento_palavras_chaves(cur)

cur.close()
conn.close()

# Converter dados para DataFrame
df_alunos = pd.DataFrame(aluno_palavras, columns=['id_aluno', 'palavra'])
df_eventos = pd.DataFrame(evento_palavras, columns=['id_evento', 'palavra'])

# Criar uma matriz de presença de palavras para alunos
aluno_word_matrix = df_alunos.pivot_table(index='id_aluno', columns='palavra', aggfunc=len, fill_value=0)

# Criar uma matriz de presença de palavras para eventos
evento_word_matrix = df_eventos.pivot_table(index='id_evento', columns='palavra', aggfunc=len, fill_value=0)

# Preencher valores NaN com False
aluno_word_matrix.fillna(False, inplace=True)
evento_word_matrix.fillna(False, inplace=True)

# Converter para booleanos (True e False)
aluno_word_matrix = aluno_word_matrix.astype(bool)
evento_word_matrix = evento_word_matrix.astype(bool)

# Combinar matrizes de alunos e eventos para encontrar associações
combined_matrix = aluno_word_matrix._append(evento_word_matrix, ignore_index=False)

# Aplicar o algoritmo Apriori
frequent_itemsets = apriori(combined_matrix, min_support=0.01, use_colnames=True)
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)

# Filtrar regras relevantes para recomendar eventos a alunos
recomendacoes = rules[rules['consequents'].apply(lambda x: any(i in evento_word_matrix.index for i in x))]

# Conectar novamente ao banco de dados para inserir recomendações
conn = connect_db()
cur = conn.cursor()

for _, row in recomendacoes.iterrows():
    consequents = row['consequents']
    for evento_id in consequents:
        if evento_id in evento_word_matrix.index:
            antecedents = row['antecedents']
            for aluno_id in antecedents:
                if aluno_id in aluno_word_matrix.index:
                    cur.execute("INSERT INTO public.alunos_eventos (id_aluno, id_evento) VALUES (%s, %s)", (aluno_id, evento_id))
                    conn.commit()

cur.close()
conn.close()
