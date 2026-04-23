import json
import os
import smtplib
import urllib.request
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def handler(event: dict, context) -> dict:
    """Отправка заявки с сайта Led Media на почту и в Telegram"""

    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }

    body = json.loads(event.get('body', '{}'))
    name = body.get('name', '').strip()
    phone = body.get('phone', '').strip()
    message = body.get('message', '').strip()

    if not name or not phone:
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Имя и телефон обязательны'})
        }

    email_text = f"""
Новая заявка с сайта Led Media

Имя: {name}
Телефон: {phone}
Сообщение: {message or 'не указано'}
    """.strip()

    # Отправка на email
    smtp_password = os.environ.get('SMTP_PASSWORD', '')
    if smtp_password:
        try:
            msg = MIMEMultipart()
            msg['From'] = 'led-media42@mail.ru'
            msg['To'] = 'led-media42@mail.ru'
            msg['Subject'] = f'Новая заявка с сайта: {name}'
            msg.attach(MIMEText(email_text, 'plain', 'utf-8'))

            with smtplib.SMTP_SSL('smtp.mail.ru', 465) as server:
                server.login('led-media42@mail.ru', smtp_password)
                server.sendmail('led-media42@mail.ru', 'led-media42@mail.ru', msg.as_string())
        except Exception as e:
            print(f'Email error: {e}')

    # Отправка в Telegram
    tg_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    tg_chat = os.environ.get('TELEGRAM_CHAT_ID', '')
    if tg_token and tg_chat:
        try:
            tg_text = (
                f"📣 *Новая заявка с сайта Led Media*\n\n"
                f"👤 *Имя:* {name}\n"
                f"📞 *Телефон:* {phone}\n"
                f"💬 *Сообщение:* {message or 'не указано'}"
            )
            tg_data = json.dumps({
                'chat_id': tg_chat,
                'text': tg_text,
                'parse_mode': 'Markdown'
            }).encode('utf-8')
            req = urllib.request.Request(
                f'https://api.telegram.org/bot{tg_token}/sendMessage',
                data=tg_data,
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            print(f'Telegram error: {e}')

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'success': True})
    }
