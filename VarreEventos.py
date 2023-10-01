import requests 
from bs4 import BeautifulSoup
import pandas as pd

def extrair_informacoes_eventos(url):
    # Fazer a requisição para o site
    response = requests.get(url)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code != 200:
        print(f"Falha ao acessar o site. Status code: {response.status_code}")
        return None

    # Parsing do HTML com BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontrar todos os elementos <a> com a classe "panel-courses"
    eventos = soup.find_all('a', class_='panel-courses')

    dados_eventos = []
    for evento in eventos:
        link = evento['href']
        nome_evento = evento.find('h4').text
        escola_e_area = evento.find_all('small', class_='school')
        escola = escola_e_area[0].text
        area = escola_e_area[1].text if len(escola_e_area) > 1 else 'Não especificada'
        duracao = evento.find('small', class_='time').text

        dados_eventos.append({
            'Link': link,
            'Nome do Evento': nome_evento,
            'Escola': escola,
            'Área': area,
            'Duração': duracao
        })

    return dados_eventos

# URL do site da universidade
url_universidade = 'https://unisinos.br/lab/cursos/'

# Extrair informações dos eventos
dados_eventos = extrair_informacoes_eventos(url_universidade)

# Verificar se há dados para armazenar
if dados_eventos:
    # Criar um DataFrame pandas
    df = pd.DataFrame(dados_eventos)

    # Salvar os dados em um arquivo CSV
    df.to_csv('eventos_universidade.csv', index=False)

    print('Dados salvos em eventos_universidade.csv.')
else:
    print('Nenhum dado encontrado para salvar.')
