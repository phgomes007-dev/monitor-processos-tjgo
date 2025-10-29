cd ~/desktop/monitor-processos-tjgo
cat > monitor_cloud.py << 'EOF'
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
        chrome_options.add_argument("--headless")
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
    
    def tentar_encontrar_campo(self):
        """Tenta diferentes seletores para encontrar o campo de busca"""
        seletores = [
            (By.NAME, "numeroProcesso"),
            (By.ID, "numeroProcesso"),
            (By.CSS_SELECTOR, "input[name='numeroProcesso']"),
            (By.CSS_SELECTOR, "input[placeholder*='processo']"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.CSS_SELECTOR, "input"),
            (By.XPATH, "//input[contains(@name, 'processo')]"),
            (By.XPATH, "//input[contains(@placeholder, 'processo')]")
        ]
        
        for by, seletor in seletores:
            try:
                print(f"🔍 Tentando seletor: {by}='{seletor}'")
                elemento = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((by, seletor))
                )
                print(f"✅ Campo encontrado com: {by}='{seletor}'")
                return elemento
            except:
                continue
        
        # Se não encontrou, mostrar página para debug
        print("❌ Nenhum seletor funcionou. HTML da página:")
        print(self.driver.page_source[:1000])  # Primeiros 1000 chars
        return None
    
    def consultar_processo(self, numero_processo):
        """Faz consulta REAL no Projudi TJGO - Versão melhorada"""
        try:
            print(f"🔍 Consultando processo REAL: {numero_processo}")
            
            # 1. Acessar o Projudi
            print("🌐 Acessando Projudi TJGO...")
            self.driver.get("https://projudi.tjgo.jus.br/Projudi/")
            time.sleep(5)  # Mais tempo para carregar
            
            print(f"📄 Página carregada: {self.driver.title}")
            print(f"🔗 URL atual: {self.driver.current_url}")
            
            # 2. Tentar encontrar campo de busca
            campo_busca = self.tentar_encontrar_campo()
            if not campo_busca:
                return {"status": "ERRO", "detalhes": "Campo de busca não encontrado"}
            
            # 3. Preencher campo
            print("⌨️ Preenchendo número do processo...")
            campo_busca.clear()
            campo_busca.send_keys(numero_processo)
            time.sleep(2)
            
            # 4. Tentar enviar formulário
            print("🔎 Enviando busca...")
            try:
                from selenium.webdriver.common.keys import Keys
                campo_busca.send_keys(Keys.RETURN)
                print("✅ Busca enviada com Enter")
            except Exception as e:
                print(f"❌ Erro ao enviar com Enter: {e}")
                return {"status": "ERRO", "detalhes": f"Erro ao enviar busca: {e}"}
            
            # 5. Aguardar resultados
            print("⏳ Aguardando resultados...")
            time.sleep(5)
            
            print(f"🔗 Nova URL: {self.driver.current_url}")
            pagina_texto = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            
            print("📊 Analisando resultado...")
            
            # 6. Analisar resultado
            if "nenhum processo encontrado" in pagina_texto:
                return {"status": "NÃO ENCONTRADO", "detalhes": "Processo não existe no sistema"}
            
            if "processo não localizado" in pagina_texto:
                return {"status": "NÃO LOCALIZADO", "detalhes": "Processo não foi localizado"}
            
            if numero_processo.replace('.', '').replace('-', '') in self.driver.page_source.replace('.', '').replace('-', ''):
                return {
                    "status": "ENCONTRADO", 
                    "detalhes": "Processo localizado no Projudi",
                    "consulta": datetime.now().strftime('%d/%m/%Y %H:%M')
                }
            else:
                return {"status": "INDETERMINADO", "detalhes": "Não foi possível confirmar"}
                
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
    
    print(f"📊 Resultado final: {resultado}")
    
    # Preparar mensagem
    mensagem = f"🔍 <b>CONSULTA REAL PROJUDI</b>\n\n"
    mensagem += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    mensagem += f"⚡ GitHub Actions + Selenium\n\n"
    mensagem += f"<b>Processo:</b> {processo}\n"
    mensagem += f"<b>Status:</b> {resultado['status']}\n"
    mensagem += f"<b>Detalhes:</b> {resultado['detalhes']}\n"
    
    mensagem += f"\n🏁 <i>Fase 1 - Consulta básica</i>"
    
    # Enviar para Telegram
    if telegram.enviar_mensagem(mensagem):
        print("✅✅✅ RESULTADO ENVIADO PARA TELEGRAM!")
    else:
        print("❌❌❌ FALHA NO ENVIO")
    
    consulta.close()
    
except Exception as e:
    print(f"❌❌❌ ERRO CRÍTICO: {e}")
    try:
        telegram = TelegramCloud()
        erro_msg = f"🚨 <b>ERRO NA CONSULTA</b>\n\nErro: {str(e)}\n\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        telegram.enviar_mensagem(erro_msg)
    except:
        pass

print("=== CONSULTA REAL FINALIZADA ===")
EOF

git add monitor_cloud.py
git commit -m "Fase 1: Melhorar busca de elementos com múltiplos seletores"
git push