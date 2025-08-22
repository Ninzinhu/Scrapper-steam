# 🚀 Steam Scraper - Versão Melhorada

Um scraper robusto para extrair informações detalhadas de jogos da Steam, incluindo reviews, gêneros organizados, franchise/série e muito mais!

## ✨ **Funcionalidades Principais**

- 🔍 **Busca por App ID** - Extrai dados completos de qualquer jogo
- 🔍 **Busca por nome** - Encontra jogos e mostra detalhes
- 📊 **Reviews completos** - Captura reviews gerais, recentes e em PT-BR
- 🎭 **Gêneros organizados** - Separa gêneros principais dos secundários
- 🎬 **Franchise/Série** - Identifica jogos que fazem parte de séries
- 💾 **Exportação** - Salva dados em JSON e CSV
- 🛡️ **Anti-bloqueio** - Headers realistas e delays inteligentes

## 📁 **Estrutura do Projeto**

```
Scrapper-steam/
├── steam_scraper_melhorado.py  # 🎯 SCRAPER PRINCIPAL
├── requirements.txt             # 📦 Dependências
├── config.py                   # ⚙️ Configurações
├── install.bat                 # 🪟 Instalação Windows
├── install.sh                  # 🐧 Instalação Linux/Mac
└── README.md                   # 📖 Documentação
```

## 🚀 **Instalação Rápida**

### **Windows:**

```bash
install.bat
```

### **Linux/Mac:**

```bash
chmod +x install.sh
./install.sh
```

### **Manual:**

```bash
pip install -r requirements.txt
```

## 🎮 **Como Usar**

### **1. Executar o Scraper:**

```bash
python steam_scraper_melhorado.py
```

### **2. Menu de Opções:**

- **Opção 1**: Buscar jogo por App ID
- **Opção 2**: Buscar jogos por nome
- **Opção 3**: Sair

### **3. Exemplo de Uso:**

```bash
# Buscar Counter-Strike 2
App ID: 730

# Buscar por nome
Nome: "Spider-Man"
```

## 📊 **Dados Extraídos**

### **Informações Básicas:**

- Nome do jogo
- App ID
- Preço
- Data de lançamento
- Developer
- Publisher

### **Reviews Detalhados:**

- **Geral**: Todas as línguas
- **Recentes**: Últimas análises
- **PT-BR**: Reviews em português

### **Gêneros Organizados:**

- **Principais**: Ação, RPG, Estratégia, etc.
- **Outros**: Gêneros secundários
- **Total**: Contagem completa

### **Informações Extras:**

- Franchise/Série
- Tags
- Descrição
- URL da Steam

## ⚙️ **Configurações**

O arquivo `config.py` permite personalizar:

- Delays entre requisições
- Headers HTTP
- Timeouts
- Configurações de exportação

## 🛠️ **Tecnologias**

- **Python 3.7+**
- **BeautifulSoup4** - Parsing HTML
- **Requests** - Requisições HTTP
- **Fake UserAgent** - Headers realistas
- **Regex** - Extração de dados

## 🔧 **Solução de Problemas**

### **Erro de Conexão:**

- Verifique sua conexão com a internet
- A Steam pode estar temporariamente indisponível

### **Dados Incompletos:**

- Alguns jogos podem não ter todas as informações
- Tente novamente em alguns minutos

### **Rate Limiting:**

- O scraper já inclui delays automáticos
- Se persistir, aumente os delays no `config.py`

## 📝 **Exemplo de Saída**

```json
{
  "app_id": "730",
  "nome": "Counter-Strike 2",
  "generos_principais": ["Tiro em Primeira Pessoa", "Multijogador"],
  "data_lancamento": "21/ago./2012",
  "publisher": "Valve",
  "developer": "Valve",
  "franchise": "Counter-Strike",
  "reviews": {
    "overall": "Muito positivas",
    "total_reviews": 8975290,
    "pt_br": "Muito positivas",
    "pt_br_count": 498762
  }
}
```

## 🤝 **Contribuições**

Sinta-se à vontade para:

- Reportar bugs
- Sugerir melhorias
- Contribuir com código

## 📄 **Licença**

Este projeto é para uso educacional e pessoal. Respeite os termos de uso da Steam.

---

**🎯 Scraper otimizado e funcional para extrair dados completos da Steam!**
