import pandas as pd
import psycopg2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
from sklearn.metrics.pairwise import cosine_similarity



# Conexão com o banco de dados PostgreSQL
conn = psycopg2.connect(
    dbname="projetotcc",
    user="projetotcc",
    password="TryTiR@1309927",
    host="179.188.16.157"
)

# Carregar eventos_df da tabela de eventos do banco de dados
eventos = pd.read_sql_query('SELECT nome_do_evento, area, sobre FROM eventos', conn)

# Carregar cursos_df da tabela de cursos do banco de dados
cursos = pd.read_sql_query('SELECT nome FROM cursos', conn)

# Preencher valores nulos com uma string vazia
eventos = eventos.fillna('')
cursos = cursos.fillna('')


def preprocess_text(text):
    # Converte o texto para minúsculas


    text = text.lower()
    
    # Remove pontuações
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenização
    tokens = word_tokenize(text)
    
    # Remoção de stopwords
    stop_words = set(stopwords.words('portuguese')) # Altere para o idioma desejado
    tokens = [word for word in tokens if word not in stop_words]
    
    # Lematização
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    
    # Reconstroi o texto a partir dos tokens
    processed_text = ' '.join(tokens)
    
    return processed_text

eventos = eventos.map(preprocess_text)
cursos = cursos.map(preprocess_text)

print (eventos)
print (cursos)

# Definindo um modelo de classificação
X_eventos = eventos  # Define the variable X_eventos with appropriate values

model = MLPClassifier()

# Treinando o modelo com os dados de eventos e cursos
model.fit(X_eventos, cursos)

# Fazendo a previsão dos cursos correspondentes aos eventos
cursos_correspondentes = model.predict(X_eventos)

# Imprimindo os cursos correspondentes aos eventos
for i, evento in enumerate(eventos):
    print(f"Evento: {evento} | Curso correspondente: {cursos_correspondentes[i]}")

            
            
