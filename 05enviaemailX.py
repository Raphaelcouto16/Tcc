import psycopg2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

# Função para conectar ao banco de dados
def connect_db():
    return psycopg2.connect(
        dbname="projetotcc",
        user="projetotcc",
        password="TryTiR@1309927",
        host="179.188.16.157"
    )

# Função para obter dados dos alunos e eventos
def get_alunos_eventos(cur):
    query = """
    SELECT ae.id_aluno_evento, a.id_aluno, a.nome, a.email, e.nome_do_evento, e.link, e.area, e.periodo_da_atividade, e.horarios
    FROM public.alunos_eventos ae
    JOIN public.alunos a ON ae.id_aluno = a.id_aluno
    JOIN public.eventos e ON ae.id_evento = e.id_evento
    """
    cur.execute(query)
    return cur.fetchall()

# Função para enviar email
def send_email(to_email, subject, body):
    from_email = "tryti.contact@gmail.com"  # Substitua pelo seu email
    password = "tpam rwiv vibp yshq"  # Substitua pela sua senha

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Falha ao enviar email para {to_email}: {str(e)}")
        return False

# Função para registrar envio de email no banco de dados
def registrar_envio(cur, conn, id_aluno_evento, status):
    query = """
    INSERT INTO public.envio_email (id_aluno_evento, status_do_envio)
    VALUES (%s, %s)
    """
    cur.execute(query, (id_aluno_evento, status))
    conn.commit()

# Conectar ao banco de dados e obter dados
conn = connect_db()
cur = conn.cursor()

alunos_eventos = get_alunos_eventos(cur)

# Enviar emails e registrar envios
for ae in alunos_eventos:
    id_aluno_evento, id_aluno, nome, email, nome_do_evento, link, area, periodo_da_atividade, horarios = ae
    
    subject = f"Serviço de envio de email para {nome}"
    body = f"""
    Olá {nome},

    Temos o prazer de informar sobre um novo evento que pode ser do seu interesse:

    Nome do Evento: {nome_do_evento}
    Link: {link}
    Área: {area}
    Período da Atividade: {periodo_da_atividade}
    Horários: {horarios}

    Esperamos que você possa participar!

    Atenciosamente,
    Equipe de Eventos
    """
    
    #esperar 5 segundos
    time.sleep(5)

    if send_email(email, subject, body):
        registrar_envio(cur, conn, id_aluno_evento, "Enviado")
    else:
        registrar_envio(cur, conn, id_aluno_evento, "Falha ao Enviar")

cur.close()
conn.close()
