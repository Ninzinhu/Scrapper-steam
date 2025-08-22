#!/bin/bash

echo "========================================"
echo "    INSTALADOR DO STEAM SCRAPER"
echo "========================================"
echo

# Verifica se Python está instalado
echo "Verificando se Python está instalado..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "Python 3 encontrado!"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "Python encontrado!"
else
    echo "ERRO: Python não está instalado!"
    echo "Por favor, instale Python 3.8+ primeiro"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi

echo "Versão do Python:"
$PYTHON_CMD --version
echo

# Verifica se pip está instalado
echo "Verificando se pip está instalado..."
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "ERRO: pip não está instalado!"
    echo "Instalando pip..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install python3-pip -y
    elif command -v yum &> /dev/null; then
        sudo yum install python3-pip -y
    elif command -v brew &> /dev/null; then
        brew install python3
    else
        echo "Não foi possível instalar pip automaticamente"
        echo "Por favor, instale manualmente"
        exit 1
    fi
fi

# Determina o comando pip correto
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
else
    PIP_CMD="pip"
fi

echo "pip encontrado!"
echo

# Atualiza pip
echo "Atualizando pip..."
$PIP_CMD install --upgrade pip

# Instala dependências
echo "Instalando dependências..."
$PIP_CMD install -r requirements.txt

if [ $? -ne 0 ]; then
    echo
    echo "ERRO: Falha ao instalar dependências!"
    echo "Tente executar manualmente: $PIP_CMD install -r requirements.txt"
    exit 1
fi

echo
echo "========================================"
echo "    INSTALAÇÃO CONCLUÍDA!"
echo "========================================"
echo
echo "Para usar o scraper básico:"
echo "  $PYTHON_CMD exemplo_uso.py"
echo
echo "Para usar o scraper avançado:"
echo "  $PYTHON_CMD exemplo_avancado.py"
echo
echo "Para testar a instalação:"
echo "  $PYTHON_CMD teste_scraper.py"
echo
echo "🎉 Steam Scraper instalado com sucesso!"
