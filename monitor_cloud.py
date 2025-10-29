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
        """Configura o navegador Chrome"""
        print("🖥️ Configurando navegador...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✅ Navegador configurado!")
        except Exception as e:
            print(f"❌ Erro ao configurar navegador: {e}")
            raise e

    def testar_urls(self):
        """Testa diferentes URLs do Projudi"""
        urls = [
            "https://projudi.tjgo.jus.br/Projudi",
            "https://projudi.tjgo.jus.br",
            "https://projudi.tjgo.jus.br/Projudi/home.seam",
            "https://projudi.tjgo.jus.br/Projudi/buscas/ProcBusca.jsp",
            "https://esaj.tjgo.jus.br/projudi",
        ]
        
        for url in urls:
            try:
                print(f"🔗 Testando URL: {url}")
                self.driver.get(url)
                time.sleep(3)
                
                titulo = self.driver.title
                url_atual = self.driver.current_url
                print(f"   ✅ Carregou: {titulo}")
                print(f"   🔗 URL atual: {url_atual}")
                
                # Verificar se não é página de erro
                if "404" not in self.driver.page_source and "não encontrado" not in self.driver.page_source.lower():
                    print(f"   🎯 URL VÁLIDA ENCONTRADA: {url}")
                    return url
                    
            except Exception as e:
                print(f"   ❌ Erro em {url}: {e}")
        
        return None

    def consultar_processo(self, numero_processo):
        """Tenta consulta real com diferentes abordagens"""
        try:
            print(f"🔍 Consultando: {numero_processo}")
            
            # 1. Primeiro encontrar URL válida
            print("🌐 Procurando URL válida do Projudi...")
            url_valida = self.testar_urls()
            
            if not url_valida:
                return {"status": "ERRO", "detalhes": "Nenhuma URL do Projudi está funcionando"}
            
            print(f"🎯 Usando URL: {url_valida}")
            
            # 2. Tentar encontrar campo de busca na URL válida
            seletores = [
                (By.NAME, "numeroProcesso"),
                (By.ID, "numeroProcesso"), 
                (By.CSS_SELECTOR, "input[name*='processo']"),
                (By.CSS_SELECTOR, "input[placeholder*='processo']"),
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.XPATH, "//input[contains(@name, 'processo')]"),
            ]
            
            campo_encontrado = None
            for by, seletor in seletores:
                try:
                    campo = self.driver.find_element(by, seletor)
                    campo_encontrado = campo
                    print(f"✅ Campo encontrado: {seletor}")
                    break
                except:
                    continue
            
            if not campo_encontrado:
                return {"status": "ERRO", "detalhes": f"URL carrega mas campo não encontrado. Página: {self.driver.title}"}
            
            # 3. Fazer busca
            campo_encontrado.clear()
            campo_encontrado.send_keys(numero_processo)
            time.sleep(2)
            
            from selenium.webdriver.common.keys import Keys
            campo_encontrado.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # 4. Analisar resultado
            pagina_texto = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            
            if "nenhum processo encontrado" in pagina_texto:
                return {"status": "NÃO ENCONTRADO", "detalhes": "Processo não existe"}
            elif "processo não localizado" in pagina_texto:
                return {"status": "NÃO LOCALIZADO", "detalhes": "Processo não localizado"} 
            elif numero_processo.replace('.', '').replace('-', '') in self.driver.page_source.replace('.', '').replace('-', ''):
                return {"status": "ENCONTRADO", "detalhes": "Processo localizado no sistema"}
            else:
                return {"status": "INDETERMINADO", "detalhes": "Consulta realizada mas resultado incerto"}
                
        except Exception as e:
            return {"status": "ERRO", "detalhes": f"Erro durante consulta: {str(e)}"}
    
    def close(self):
        if self.driver:
            self.driver.quit()

# EXECUÇÃO PRINCIPAL COM FALLBACK
try:
    telegram = TelegramCloud()
    
    # Tentar consulta real
    consulta = ConsultaProjudiReal()
    processo = "5650304-47.2025.8.09.0168"
    resultado = consulta.consultar_processo(processo)
    consulta.close()
    
except Exception as e:
    print(f"❌ Erro na consulta real: {e}")
    # Fallback para simulação
    import random
    situacoes = ["EM ANDAMENTO", "ARQUIVADO", "JULGADO"]
    resultado = {
        "status": "SIMULAÇÃO", 
        "detalhes": f"Consulta real falhou. Situação simulada: {random.choice(situacoes)}",
        "fallback": True
    }

# Enviar resultado
mensagem = f"🔍 <b>CONSULTA PROJUDI</b>\n\n"
mensagem += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
mensagem += f"⚡ GitHub Actions\n\n"
mensagem += f"<b>Processo:</b> {processo}\n"
mensagem += f"<b>Status:</b> {resultado['status']}\n"
mensagem += f"<b>Detalhes:</b> {resultado['detalhes']}\n"

if resultado.get('fallback'):
    mensagem += f"\n⚠️ <i>Usando dados simulados temporariamente</i>"

mensagem += f"\n🏁 <i>Consulta concluída</i>"

if telegram.enviar_mensagem(mensagem):
    print("✅ Mensagem enviada!")
else:
    print("❌ Falha no envio")

print("=== CONSULTA FINALIZADA ===")