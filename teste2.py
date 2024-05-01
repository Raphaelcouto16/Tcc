import pandas as pd
import psycopg2
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

# Carregar dados do banco de dados
conn = psycopg2.connect(
    dbname="projetotcc",
    user="projetotcc",
    password="TryTiR@1309927",
    host="179.188.16.157"
)

eventos_df = pd.read_sql_query('SELECT nome_do_evento, area, sobre FROM eventos', conn)
cursos_df = pd.read_sql_query('SELECT nome, area FROM cursos', conn)

# Combinar os dataframes
df = pd.merge(eventos_df, cursos_df, how='inner', on='area')

# Codificar variáveis categóricas
le = LabelEncoder()
df['nome_do_evento_encoded'] = le.fit_transform(df['nome_do_evento'])
df['nome_curso_encoded'] = le.fit_transform(df['nome'])

# Dividir conjunto de dados em treinamento e teste
X = df[['nome_do_evento_encoded', 'area_encoded']] # características
y = df['nome_curso_encoded'] # alvo

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Treinar modelo
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Avaliar modelo
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Predição
# Suponha que você tenha um novo evento
novo_evento = pd.DataFrame({'nome_do_evento_encoded': [X_test.iloc[0]['nome_do_evento_encoded']], 'area_encoded': [X_test.iloc[0]['area_encoded']]})

# Predizer curso associado ao novo evento
predicao = model.predict(novo_evento)
nome_curso_predito = le.inverse_transform(predicao)
print("Curso associado ao novo evento:", nome_curso_predito)
