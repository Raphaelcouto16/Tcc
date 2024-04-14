import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import psycopg2

# Função para adicionar informações adicionais ao evento
def adicionar_informacoes_adicionais(df_eventos):
    df_eventos['Período da atividade'] = ''
    df_eventos['Horários'] = ''
    df_eventos['Período de inscrição'] = ''
    df_eventos['Investimento'] = ''
    
    df_eventos['Sobre'] = ''
    df_eventos['Objetivos'] = ''
    df_eventos['Programação'] = ''
    df_eventos['Pré-requisitos'] = ''
    df_eventos['Ministrante'] = ''
    df_eventos['Promoção'] = ''
    df_eventos['Apoio'] = ''
    
    df_eventos['Local'] = ''
    df_eventos['Certificado'] = ''
    df_eventos['Competências'] = ''
    
    conn = psycopg2.connect(
    dbname="projetotcc",
    user="projetotcc",
    password="TryTiR@1309927",
    host="179.188.16.157"
    )
    cur = conn.cursor()

    for index, evento in df_eventos.iterrows():
        # Acessar o link do evento
        link = evento['Link']
        response = requests.get(link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            panel_div = soup.find('div', class_='panel')

            if panel_div:
                # Iterar sobre as divs dentro da div "panel"
                for div_info in panel_div.find_all('div', class_='group-info-panel'):
                    title_tag = div_info.find('small', class_='title')
                    values = div_info.find_all('small')
                    if values:
                        if title_tag is not None and title_tag.string == 'Horários' and len(values) >= 2:
                            value_tag = (values[1].string + ' até ' + values[2].string) if len(values) > 2 else None  
                        else:
                            value_tag = values[1].string if len(values) > 1 else None
                    else:
                        value_tag = None

                    if title_tag and value_tag:
                        title = title_tag.string
                        value = value_tag

                        if title == 'Período da atividade':
                            df_eventos.at[index, 'Período da atividade'] = value
                        elif title == 'Horários':
                            df_eventos.at[index, 'Horários'] = value
                        elif title == 'Período de inscrição':
                            df_eventos.at[index, 'Período de inscrição'] = value
                        elif title == 'Investimento':
                            df_eventos.at[index, 'Investimento'] = value
                        
                        print(f'PAINEL {title} adicionada  com o valor {value}.')
                        
            # achar dados na seção de descrição do curso
            
            section_div =  soup.find('section', class_='course-description')
            
            if section_div:
                print('SEÇÃO DE DESCRIÇÃO ENCONTRADA')
                
                for div_info in section_div.find_all('div', class_='block-course'):
                    title_tag = div_info.find('h4', class_='title-block')
                    value_tag = div_info.find('p') 
                    print('CHEGOU NO FOR')
                    if title_tag and value_tag:
                        title = title_tag.string
                        value = value_tag.string
                        print('ENTRO NO IF')

                        if title == 'Sobre':
                            df_eventos.at[index, 'Sobre'] = value
                        elif title == 'Objetivos':
                            df_eventos.at[index, 'Objetivos'] = value
                        elif title == 'Programação':
                            df_eventos.at[index, 'Programação'] = value
                        elif title == 'Pré-requisitos':
                            df_eventos.at[index, 'Pré-requisitos'] = value
                        elif title == 'Sobre o(a) ministrante/palestrante':
                            df_eventos.at[index, 'Ministrante'] = value
                        elif title == 'Promoção':
                            df_eventos.at[index, 'Promoção'] = value
                        elif title == 'Apoio':
                            df_eventos.at[index, 'Apoio'] = value                        
                        print(f'SECTION {title} adicionada  com o valor {value}.')
                    

            
            
            local_tag = soup.find('div', class_='text-extra').find(lambda tag: tag.name == 'small' and tag.text == 'Local')
            # local_tag = soup.find('div', class_='text-extra').find('small', text='Local')
            local = local_tag.find_next('span').text if local_tag else 'Não encontrado'
            
            certificado_tag = soup.find('div', class_='text-extra').find('small', text='Certificado')
            certificado = certificado_tag.find_next('span').text if certificado_tag else 'Não encontrado'
            
            competencias_tag = soup.find('div', class_='text-extra').find('small', text='Competências')
            competencias = ', '.join([c.text for c in competencias_tag.find_all('small')]) if competencias_tag else 'Não encontrado'
            
            # Adicionar as informações ao DataFrame
            
           # df_eventos.at[index, 'Pré-requisitos'] = pre_requisitos
            df_eventos.at[index, 'Local'] = local
            #df_eventos.at[index, 'Período da atividade'] = periodo_atividade
            #df_eventos.at[index, 'Horários'] = horarios
            #df_eventos.at[index, 'Período de inscrição'] = periodo_inscricao
            #df_eventos.at[index, 'Investimento'] = investimento
            df_eventos.at[index, 'Certificado'] = certificado
            df_eventos.at[index, 'Competências'] =  competencias
            
            print(f'Informações adicionais do evento {evento["Nome do Evento"]} adicionadas.')
            
            cur.execute("""
                INSERT INTO eventos (link, nome_do_evento, periodo_da_atividade, horarios, periodo_de_inscricao, investimento, sobre, objetivos, programacao, pre_requisitos, ministrante, promocao, apoio, local, certificado, competencias)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                evento['Link'][:255].strip(),
                evento['Nome do Evento'][:255].strip(),
                df_eventos.at[index, 'Período da atividade'][:255].strip(),
                df_eventos.at[index, 'Horários'][:255].strip(),
                df_eventos.at[index, 'Período de inscrição'][:255].strip(),
                df_eventos.at[index, 'Investimento'][:100].strip(),
                df_eventos.at[index, 'Sobre'],
                df_eventos.at[index, 'Objetivos'],
                df_eventos.at[index, 'Programação'],
                df_eventos.at[index, 'Pré-requisitos'],
                df_eventos.at[index, 'Ministrante'],
                df_eventos.at[index, 'Promoção'],
                df_eventos.at[index, 'Apoio'],
                df_eventos.at[index, 'Local'][:255],
                df_eventos.at[index, 'Certificado'][:100],
                df_eventos.at[index, 'Competências'][:255]
            ))
            print(f'Informações do evento {evento["Nome do Evento"]} adicionadas ao banco de dados.')
            # Commit para salvar as alterações
            conn.commit()
            
            
            
            # esperar 1 segundo para não sobrecarregar o site
            time.sleep(2)
       
    # Fechar a conexão com o banco de dados
    conn.close()
    return df_eventos

# Ler o arquivo CSV com os eventos
df_eventos = pd.read_csv('eventos_universidade.csv')

# Adicionar informações adicionais aos eventos
df_eventos_com_info_adicionais = adicionar_informacoes_adicionais(df_eventos)

# Salvar os eventos atualizados em um novo arquivo CSV
df_eventos_com_info_adicionais.to_csv('eventos_universidade_com_info.csv', index=False)

print('Informações adicionais adicionadas e salvas no arquivo eventos_universidade_com_info.csv.')
