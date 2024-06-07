import pandas as pd
import psycopg2
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense

# Conexão com o banco de dados PostgreSQL
conn = psycopg2.connect(
    dbname="projetotcc",
    user="projetotcc",
    password="TryTiR@1309927",
    host="179.188.16.157"
)

# Carregar eventos_df da tabela de eventos do banco de dados
eventos_df = pd.read_sql_query('SELECT nome_do_evento, area, sobre FROM eventos', conn)

# Carregar cursos_df da tabela de cursos do banco de dados
cursos_df = pd.read_sql_query('SELECT nome FROM cursos', conn)


# Combine eventos_df and cursos_df using merge
eventos_df = eventos_df.merge(cursos_df, left_on='nome_do_evento', right_on='nome')

# Pré-processamento dos dados
tokenizer = Tokenizer()
tokenizer.fit_on_texts(eventos_df['sobre'])
X = tokenizer.texts_to_sequences(eventos_df['sobre'])
X = pad_sequences(X)

y = pd.get_dummies(eventos_df['nome']).values

# Dividir os dados em conjuntos de treinamento e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Construir o modelo
model = Sequential()
model.add(Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=128, input_length=X.shape[1]))
model.add(LSTM(units=128))
model.add(Dense(units=y.shape[1], activation='softmax'))

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Treinar o modelo
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

# Avaliar o modelo
loss, accuracy = model.evaluate(X_test, y_test)
print(f'Acurácia do modelo: {accuracy}')

# Predição
novo_evento = ["Workshop de Python"]
novo_evento_seq = tokenizer.texts_to_sequences(novo_evento)
novo_evento_seq = pad_sequences(novo_evento_seq, maxlen=X.shape[1])
predicao = model.predict(novo_evento_seq)
print(f'O curso predito para o evento "{novo_evento[0]}" é: {eventos_df.columns[predicao.argmax() + 1]}')