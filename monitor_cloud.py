import json
import logging
import random
import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8309039392:AAHaX5biBX2nVQstAj1Bgic0jDFdQPLGaio')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '815852291')

CONFIG = {
    "telegram_token": TELEGRAM_TOKEN,
    "telegram_chat_id": TELEGRAM_CHAT_ID,
    "processos": ["5650304-47.2025.8.09.0168"]
}

class TelegramCloud:
    def __init__(self):
        self.token = CONFIG["telegram_token"]
        self.chat_id = CONFIG["telegram_chat_id"]
    
    def enviar_mensagem(self, texto):
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": texto,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except:
            return False

class MonitorCloud:
    def __init__(self):
        self.telegram = TelegramCloud()
    
    def simular_consulta(self, numero_processo):
        cenarios = [
            {"status": "EM ANDAMENTO", "movimentos": random.randint(3, 8)},
            {"status": "ARQUIVADO", "movimentos": random.randint(2, 5)},
            {"status": "JULGADO", "movimentos": random.randint(6, 10)}
        ]
        
        cenario = random.choice(cenarios)
        
        if random.random() < 0.6:
            cenario["movimentos"] += random.randint(1, 3)
            if random.random() < 0.4:
                cenario["status"] = random.choice(["EM ANDAMENTO", "ARQUIVADO", "JULGADO"])
        
        return {
            "status": cenario["status"],
            "movimentacoes": cenario["movimentos"],
            "consulta": datetime.now().isoformat()
        }
    
    def executar(self):
        print("=== MONITOR CLOUD INICIADO ===")
        
        mensagem = f"🔄 <b>Monitor Cloud Executando</b>\n\n"
        mensagem += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        mensagem += f"📋 Processos: {len(CONFIG['processos'])}\n"
        mensagem += f"⚡ GitHub Actions\n\n"
        
        for processo in CONFIG["processos"]:
            dados = self.simular_consulta(processo)
            
            if random.random() < 0.5:
                mensagem += f"🚨 <b>{processo}</b>\n"
                mensagem += f"   Status: {dados['status']}\n"
                mensagem += f"   Movimentações: {dados['movimentacoes']}\n\n"
            else:
                mensagem += f"✅ <b>{processo}</b> - Sem mudanças\n\n"
        
        mensagem += f"🏁 <i>Execução concluída</i>"
        
        if self.telegram.enviar_mensagem(mensagem):
            print("✅ Relatório enviado para Telegram!")
        else:
            print("❌ Falha no envio")
        
        print("=== MONITOR CLOUD FINALIZADO ===")

if __name__ == "__main__":
    monitor = MonitorCloud()
    monitor.executar()