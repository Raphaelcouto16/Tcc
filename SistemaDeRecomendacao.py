import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Carregar os dados dos estudantes
estudantes = pd.read_csv('estudantes.csv')
eventos = pd.read_csv('eventos_universidade_com_info.csv')

# Suponha que 'eventos' seja um DataFrame com as informações dos eventos
# Vamos considerar as mesmas informações que usamos para os eventos (Sobre, Objetivos, Pré-requisitos)
eventos['Texto'] = eventos['Sobre'] + ' ' + eventos['Objetivos'] + ' ' + eventos['Pré-requisitos'] + ' ' + eventos['Área']

# Concatenar as áreas de interesse dos estudantes com as informações dos eventos
eventos['Texto'] = eventos['Texto'] + ' ' + eventos['Área']

# Criar uma matriz TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(eventos['Texto'].fillna(''))

# Função para recomendar eventos para um estudante
def recomendar_eventos_para_estudante(estudante_id, num_recomendacoes=5):
    # Obter as áreas de interesse do estudante
    areas_interesse_estudante = estudantes.loc[estudante_id, 'Áreas de Interesse']

    # Concatenar as áreas de interesse do estudante com as informações dos eventos
    areas_interesse_estudante_texto = ' '.join(areas_interesse_estudante.split(','))
    preferencias_estudante_texto = areas_interesse_estudante_texto + ' ' + estudantes.loc[estudante_id, 'Algo que Procura']
    preferencias_estudante_tfidf = vectorizer.transform([preferencias_estudante_texto])

    # Calcular a similaridade de cosseno entre as preferências do estudante e todos os eventos
    similaridade_com_estudante = cosine_similarity(preferencias_estudante_tfidf, tfidf_matrix).flatten()

    # Obter os índices dos eventos mais similares
    indices_recomendados = similaridade_com_estudante.argsort()[-num_recomendacoes:][::-1]

    # Retorna os eventos recomendados
    return eventos.iloc[indices_recomendados]

# Exemplo de recomendação para o estudante com ID 0
# Suponha que queremos recomendar 3 eventos para o estudante com ID 0
estudante_id = 2
num_recomendacoes = 3
eventos_recomendados = recomendar_eventos_para_estudante(estudante_id, num_recomendacoes)
print(eventos_recomendados[['Link', 'Nome do Evento', 'Área']])
