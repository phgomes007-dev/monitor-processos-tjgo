import json
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

print(f"=== CONSULTA REAL PROJUDI INICIADA ===")
print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

class TelegramCloud:
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
    
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

class ConsultaProjudiReal:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configura o navegador Chrome para GitHub Actions"""
        print("🖥️ Configurando navegador...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Executa em background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✅ Navegador configurado!")
        except Exception as e:
            print(f"❌ Erro ao configurar navegador: {e}")
            raise e
    
    def consultar_processo(self, numero_processo):
        """Faz consulta REAL no Projudi TJGO - FASE 1"""
        try:
            print(f"🔍 Consultando processo REAL: {numero_processo}")
            
            # 1. Acessar o Projudi
            print("🌐 Acessando Projudi TJGO...")
            self.driver.get("https://projudi.tjgo.jus.br/Projudi/")
            time.sleep(3)
            
            # 2. Localizar e preencher campo de busca
            print("⌨️ Preenchendo número do processo...")
            campo_busca = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.NAME, "numeroProcesso"))
            )
            campo_busca.clear()
            campo_busca.send_keys(numero_processo)
            time.sleep(2)
            
            # 3. Clicar em buscar
            print("🔎 Clicando em buscar...")
            botoes_busca = [
                "input[type='submit']",
                "button[type='submit']", 
                "input[value*='Buscar']",
                "input[value*='buscar']",
                ".btn",
                "button"
            ]
            
            botao_encontrado = False
            for seletor in botoes_busca:
                try:
                    botao = self.driver.find_element(By.CSS_SELECTOR, seletor)
                    botao.click()
                    botao_encontrado = True
                    print(f"✅ Botão encontrado: {seletor}")
                    break
                except:
                    continue
            
            if not botao_encontrado:
                # Tentar enviar formulário com Enter
                from selenium.webdriver.common.keys import Keys
                campo_busca.send_keys(Keys.RETURN)
                print("✅ Busca enviada com Enter")
            
            # 4. Aguardar e analisar resultados
            print("⏳ Aguardando resultados...")
            time.sleep(5)
            
            pagina_html = self.driver.page_source
            pagina_texto = self.driver.find_element(By.TAG_NAME, "body").text
            
            print(f"📄 Tamanho da página: {len(pagina_html)} caracteres")
            
            # 5. Analisar resultado
            if "nenhum processo encontrado" in pagina_texto.lower():
                return {"status": "NÃO ENCONTRADO", "detalhes": "Processo não existe no sistema"}
            
            if "processo não localizado" in pagina_texto.lower():
                return {"status": "NÃO LOCALIZADO", "detalhes": "Processo não foi localizado"}
            
            if numero_processo.replace('.', '').replace('-', '') in pagina_texto.replace('.', '').replace('-', ''):
                return {
                    "status": "ENCONTRADO", 
                    "detalhes": "Processo localizado no Projudi",
                    "consulta": datetime.now().strftime('%d/%m/%Y %H:%M'),
                    "pagina_tamanho": len(pagina_html)
                }
            else:
                return {"status": "INDETERMINADO", "detalhes": "Não foi possível confirmar se processo existe"}
                
        except Exception as e:
            return {"status": "ERRO", "detalhes": f"Erro técnico: {str(e)}"}
    
    def close(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
            print("🖥️ Navegador fechado")

# EXECUÇÃO PRINCIPAL
try:
    telegram = TelegramCloud()
    consulta = ConsultaProjudiReal()
    
    processo = "5650304-47.2025.8.09.0168"
    resultado = consulta.consultar_processo(processo)
    
    print(f"📊 Resultado: {resultado}")
    
    # Preparar mensagem para Telegram
    mensagem = f"🔍 <b>CONSULTA REAL PROJUDI</b>\n\n"
    mensagem += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    mensagem += f"⚡ GitHub Actions + Selenium\n\n"
    mensagem += f"<b>Processo:</b> {processo}\n"
    mensagem += f"<b>Status:</b> {resultado['status']}\n"
    mensagem += f"<b>Detalhes:</b> {resultado['detalhes']}\n"
    
    if resultado.get('pagina_tamanho'):
        mensagem += f"<b>Página:</b> {resultado['pagina_tamanho']} chars\n"
    
    mensagem += f"\n🏁 <i>Fase 1 - Consulta básica concluída</i>"
    
    # Enviar para Telegram
    if telegram.enviar_mensagem(mensagem):
        print("✅✅✅ CONSULTA REAL ENVIADA PARA TELEGRAM!")
    else:
        print("❌❌❌ FALHA NO ENVIO DO RESULTADO")
    
    consulta.close()
    
except Exception as e:
    print(f"❌❌❌ ERRO CRÍTICO: {e}")
    # Tentar enviar erro para Telegram
    try:
        telegram = TelegramCloud()
        erro_msg = f"🚨 <b>ERRO NA CONSULTA</b>\n\nErro: {str(e)}\n\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        telegram.enviar_mensagem(erro_msg)
    except:
        pass

print("=== CONSULTA REAL FINALIZADA ===")