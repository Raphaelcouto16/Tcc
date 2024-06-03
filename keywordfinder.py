import psycopg2

def insert_keywords(course_id, keywords):
    conn = psycopg2.connect(
        dbname="projetotcc",
        user="projetotcc",
        password="TryTiR@1309927",
        host="179.188.16.157"
    )
    cur = conn.cursor()
    
    for keyword in keywords:
        # Verificar se a palavra-chave já existe
        cur.execute("SELECT id_palavra FROM public.palavras_chave WHERE palavra = %s", (keyword,))
        result = cur.fetchone()
        
        if result:
            id_palavra = result[0]
        else:
            cur.execute("INSERT INTO public.palavras_chave (palavra) VALUES (%s) RETURNING id_palavra", (keyword,))
            id_palavra = cur.fetchone()[0]
        
        # Inserir na tabela intermediária
        cur.execute("INSERT INTO public.curso_palavra_chave (id_curso, id_palavra) VALUES (%s, %s)", (course_id, id_palavra))
    
    conn.commit()
    cur.close()
    conn.close()

keywords = [
    "Segurança de Redes",
    "Criptografia",
    "Cibersegurança",
    "Firewall",
    "Controle de Acesso",
    "Auditoria de Sistemas",
    "Análise de Vulnerabilidades",
    "Pen Testing",
    "Segurança da Informação",
    "Gestão de Riscos",
    "Política de Segurança",
    "Engenharia Social",
    "Segurança em Nuvem",
    "Proteção de Dados",
    "Segurança de Aplicações",
    "Forense Digital",
    "Backup e Recuperação",
    "Monitoramento de Segurança",
    "Certificação de Segurança",
    "Normas de Segurança"
]

insert_keywords(1409, keywords)
