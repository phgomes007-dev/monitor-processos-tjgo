import json
import logging
import random
import requests
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# 🔒 DADOS SEGUROS
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
        except Exception as e:
            print(f"❌ Erro Telegram: {e}")
            return False

class ConsultaProjudi:
    def __init__(self):
        self.setup_driver()
    
    def setup_driver(self):
        """Configura o navegador Chrome"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Executa em background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
    
    def consultar_processo(self, numero_processo):
        """Faz consulta REAL no Projudi TJGO"""
        try:
            print(f"🔍 Consultando processo REAL: {numero_processo}")
            
            # Acessar o Projudi
            self.driver.get("https://projudi.tjgo.jus.br/Projudi/")
            time.sleep(3)
            
            # Localizar campo de busca
            campo_busca = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "numeroProcesso"))
            )
            
            # Preencher número do processo
            campo_busca.clear()
            campo_busca.send_keys(numero_processo)
            time.sleep(2)
            
            # Clicar em buscar (tentar diferentes seletores)
            botoes_busca = [
                "input[type='submit']",
                "button[type='submit']", 
                "input[value*='Buscar']",
                "input[value*='buscar']"
            ]
            
            for seletor in botoes_busca:
                try:
                    botao = self.driver.find_element(By.CSS_SELECTOR, seletor)
                    botao.click()
                    break
                except:
                    continue
            
            # Aguardar resultados
            time.sleep(5)
            
            # Verificar se encontrou o processo
            pagina_html = self.driver.page_source
            
            if "nenhum processo encontrado" in pagina_html.lower():
                return {"status": "NÃO ENCONTRADO", "error": "Processo não localizado"}
            
            if "processo não localizado" in pagina_html.lower():
                return {"status": "NÃO LOCALIZADO", "error": "Processo não existe"}
            
            # Extrair dados básicos (implementar parsing mais sofisticado depois)
            if numero_processo.replace('.', '').replace('-', '') in pagina_html.replace('.', '').replace('-', ''):
                return {
                    "status": "ENCONTRADO",
                    "numero": numero_processo,
                    "detalhes": "Processo localizado no sistema",
                    "consulta": datetime.now().isoformat(),
                    "html_length": len(pagina_html)  # Para debug
                }
            else:
                return {"status": "INDETERMINADO", "error": "Não foi possível extrair dados"}
                
        except Exception as e:
            return {"status": "ERRO", "error": str(e)}
        finally:
            self.driver.quit()
    
    def extrair_dados_detalhados(self, html):
        """Extrai dados específicos do HTML (implementar depois)"""
        # TODO: Implementar parsing com BeautifulSoup
        return {"detalhes": "Em desenvolvimento"}

class MonitorCloud:
    def __init__(self):
        self.telegram = TelegramCloud()
        self.consulta = ConsultaProjudi()
    
    def executar(self):
        print("=== MONITOR CLOUD INICIADO ===")
        
        mensagem = f"🔍 <b>Consulta REAL Projudi</b>\n\n"
        mensagem += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        mensagem += f"📋 Processos: {len(CONFIG['processos'])}\n"
        mensagem += f"⚡ GitHub Actions\n\n"
        
        for processo in CONFIG["processos"]:
            print(f"Consultando: {processo}")
            resultado = self.consulta.consultar_processo(processo)
            
            mensagem += f"<b>{processo}</b>\n"
            mensagem += f"Status: {resultado.get('status', 'N/A')}\n"
            
            if resultado.get('error'):
                mensagem += f"Erro: {resultado['error']}\n"
            elif resultado.get('detalhes'):
                mensagem += f"Detalhes: {resultado['detalhes']}\n"
            
            mensagem += f"HTML: {resultado.get('html_length', 0)} chars\n\n"
        
        mensagem += f"🏁 <i>Consulta real concluída</i>"
        
        # Enviar para Telegram
        if self.telegram.enviar_mensagem(mensagem):
            print("✅ Relatório enviado para Telegram!")
        else:
            print("❌ Falha no envio")
        
        print("=== MONITOR CLOUD FINALIZADO ===")

if __name__ == "__main__":
    monitor = MonitorCloud()
    monitor.executar()