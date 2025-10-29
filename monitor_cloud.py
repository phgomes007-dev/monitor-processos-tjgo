name: Monitor de Processos TJGO

on:
  schedule:
    - cron: '0 12 * * *'
    - cron: '0 18 * * *'
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
    - name: 📥 Baixar código
      uses: actions/checkout@v3
    - name: 🐍 Configurar Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: 📦 Instalar dependências
      run: pip install -r requirements.txt
    - name: 🚀 Executar monitor
      run: python monitor_cloud.py
    - name: ✅ Finalizado
      run: echo "Monitoramento executado com sucesso!"
