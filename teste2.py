import psycopg2
import pyECLAT
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from pyECLAT import ECLAT
from pyECLAT import Example1

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


#print (df_eventos.head(10))


dados = Example1().get()
#print(dados)

df_eventos['tem_palavra'] = 1

# Criar uma tabela de ocorrências (transações)
transactions = df_eventos.pivot_table(index='id_evento', columns='palavra', values='tem_palavra', fill_value=0)
# Onde 4 é o número de palavras que você deseja em cada transação

#print(transactions)

# formatar para o algoritmo eclat
transactions = transactions.map(lambda x: 1 if x == 1 else 0)

#print(transactions)#


# transformar transactions em booleano

transactions = transactions.astype(bool)

#print(transactions)
# Aplicar o algoritmo Apriori
associacao = apriori(transactions, min_support=0.05, use_colnames=True)
#print(associacao.sort_values(by='support', ascending=False).head(15))

regras = association_rules(associacao, metric="lift", min_threshold=1.0)

print(regras.sort_values(by='support', ascending=False).head(15))








