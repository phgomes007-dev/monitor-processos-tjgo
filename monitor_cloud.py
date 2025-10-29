import json
import requests
import os
import time
from datetime import datetime

# 🔒 DADOS SEGUROS
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8309039392:AAHaX5biBX2nVQstAj1Bgic0jDFdQPLGaio')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '815852291')

print(f"=== MONITOR INICIADO ===")
print(f"Token: {TELEGRAM_TOKEN[:10]}...")
print(f"Chat ID: {TELEGRAM_CHAT_ID}")

class TelegramCloud:
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
    
    def enviar_mensagem(self, texto):
        try:
            print("📱 Tentando enviar para Telegram...")
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": texto,
                "parse_mode": "HTML"
            }
            print(f"URL: {url}")
            print(f"Chat ID: {self.chat_id}")
            
            response = requests.post(url, json=payload, timeout=10)
            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Erro Telegram: {e}")
            return False

# Teste direto
telegram = TelegramCloud()

mensagem = f"🔍 <b>Teste de Consulta</b>\n\n"
mensagem += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
mensagem += f"🔄 Sistema funcionando\n"
mensagem += f"⚡ GitHub Actions\n\n"
mensagem += f"📋 Processo: 5650304-47.2025.8.09.0168\n"
mensagem += f"🔧 Status: Em testes\n\n"
mensagem += f"🏁 <i>Teste concluído</i>"

if telegram.enviar_mensagem(mensagem):
    print("✅✅✅ MENSAGEM ENVIADA COM SUCESSO!")
else:
    print("❌❌❌ FALHA CRÍTICA NO ENVIO")

print("=== MONITOR FINALIZADO ===")