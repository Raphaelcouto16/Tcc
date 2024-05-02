import pandas as pd
import psycopg2
from fuzzywuzzy import fuzz

# Conectar ao banco de dados
conn = psycopg2.connect(
    dbname="projetotcc",
    user="projetotcc",
    password="TryTiR@1309927",
    host="179.188.16.157"
)

# Carregar eventos_df da tabela de eventos do banco de dados
eventos_df = pd.read_sql_query('SELECT id_evento ,nome_do_evento, area, sobre FROM eventos', conn)

# Carregar cursos_df da tabela de cursos do banco de dados
cursos_df = pd.read_sql_query('SELECT id_curso, nome, area FROM cursos', conn)

# Defina a limiar de similaridade
limiar_similaridade = 55  # Você pode ajustar esse valor conforme necessário

#contadores de quantos eventos e cursos foram encontrados
eventos_nao_encontrados = 0
eventos_encontrados = 0

# Para cada evento, encontrar cursos associados com a quantidade de caracteres mais próximos ou iguais ao nome do evento
for index, evento in eventos_df.iterrows():
    nome_evento = evento['nome_do_evento']
    area_evento = evento['area']

    # Filtrar cursos com a quantidade de caracteres mais próximos ou iguais ao nome do evento
    cursos_filtrados = cursos_df[cursos_df["nome"].apply(lambda x: fuzz.partial_ratio(x, nome_evento)) >= limiar_similaridade]

    # Se houver cursos filtrados, imprima-os
    if not cursos_filtrados.empty:
        print(f"Cursos associados para o evento '{nome_evento}':")
        print(cursos_filtrados)
        # laço nos cursos filtrados e inserindo no banco o id do curso e do evento
        for id_curso, curso in cursos_filtrados.iterrows():
            cursor = conn.cursor()
            id_curso_real = curso['id_curso']  # Obtenha o ID real do curso
            print(id_curso_real)
            print(index)
            cursor.execute("INSERT INTO cursos_eventos (id_curso, id_evento) VALUES (%s, %s)", (id_curso_real, evento['id_evento']))
            conn.commit()
            cursor.close()
        eventos_encontrados += 1
    else:
        print(f"Não foram encontrados cursos associados para o evento '{nome_evento}' com quantidade de caracteres próximos ou iguais.")
        eventos_nao_encontrados += 1

print(f"\nTotal de eventos: {len(eventos_df)}")
print(f"Total de cursos: {len(cursos_df)}")
print(f"Total de eventos encontrados: {eventos_encontrados}")
print(f"Total de eventos não encontrados: {eventos_nao_encontrados}")

#calular porcetagem de eventos econtrados e não encontrados
porcentagem_eventos_encontrados = (eventos_encontrados / len(eventos_df)) * 100
porcentagem_eventos_nao_encontrados = (eventos_nao_encontrados/ len(eventos_df)) * 100
print(f"Porcentagem de eventos encontrados: {porcentagem_eventos_encontrados}%")
print(f"Porcentagem de eventos nao encontrados: {porcentagem_eventos_nao_encontrados}%")

#gravar cursos compativeis com eventos no banco de dados
#dados da tabela 
#cursos_eventos (
#	id_curso_evento serial4 NOT NULL,
#	id_curso int4 NULL,
#	id_evento int4 NULL,
#	CONSTRAINT crusos_eventos_pkey PRIMARY KEY (id_curso_evento)
#)

#monte uma consulta ligando eventos e cursos com a cursos_eventos em sql 
#SELECT * FROM eventos
#INNER JOIN cursos_eventos ON eventos.id_evento = cursos_eventos.id_evento
#INNER JOIN cursos ON cursos_eventos.id_curso = cursos.id_curso
#WHERE eventos.id_evento = 1
#ORDER BY cursos.nome ASC