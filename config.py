#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo de configuração para o Steam Scraper
Aqui você pode ajustar parâmetros como delays, limites e configurações
"""

# Configurações de Rate Limiting
DELAY_MIN = 1.0          # Delay mínimo entre requisições (segundos)
DELAY_MAX = 3.0          # Delay máximo entre requisições (segundos)
MAX_REQUESTS_PER_MINUTE = 20  # Máximo de requisições por minuto

# Configurações de Busca
DEFAULT_MAX_RESULTS = 50      # Número padrão de resultados por busca
MAX_POPULAR_GAMES = 20        # Máximo de jogos populares para coletar

# Configurações de Headers HTTP
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

# Configurações de Timeout
REQUEST_TIMEOUT = 30          # Timeout para requisições HTTP (segundos)
CONNECTION_TIMEOUT = 10       # Timeout para conexão (segundos)

# Configurações de Retry
MAX_RETRIES = 3               # Máximo de tentativas para uma requisição
RETRY_DELAY = 5               # Delay entre tentativas (segundos)

# Configurações de Exportação
DEFAULT_CSV_ENCODING = 'utf-8-sig'  # Encoding padrão para CSV
DEFAULT_JSON_INDENT = 2              # Indentação padrão para JSON

# Configurações de Logging
LOG_LEVEL = 'INFO'            # Nível de log (DEBUG, INFO, WARNING, ERROR)
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Configurações de Steam
STEAM_BASE_URL = 'https://store.steampowered.com'
STEAM_SEARCH_URL = 'https://store.steampowered.com/search/'
STEAM_CATEGORIES = {
    'action': 998,
    'rpg': 998,
    'strategy': 998,
    'adventure': 998,
    'simulation': 998,
    'sports': 998,
    'racing': 998,
    'indie': 998,
}

# Configurações de Reviews
REVIEW_THRESHOLDS = {
    'very_positive': 0.8,     # 80%+ de reviews positivas
    'positive': 0.6,           # 60%+ de reviews positivas
    'mixed': 0.4,              # 40%+ de reviews positivas
    'negative': 0.2,           # 20%+ de reviews positivas
    'very_negative': 0.0,     # Menos de 20% de reviews positivas
}

# Configurações de Filtros
MIN_REVIEWS_FOR_RATING = 10   # Mínimo de reviews para calcular rating
MIN_PRICE_FILTER = 0.0        # Preço mínimo para filtrar jogos
MAX_PRICE_FILTER = 999.99     # Preço máximo para filtrar jogos

# Configurações de Cache
ENABLE_CACHE = True            # Habilitar cache de requisições
CACHE_DURATION = 3600         # Duração do cache em segundos (1 hora)
CACHE_DIR = './cache'         # Diretório para arquivos de cache

# Configurações de Proxy (opcional)
USE_PROXY = False             # Usar proxy para requisições
PROXY_LIST = [                # Lista de proxies (se USE_PROXY = True)
    # 'http://proxy1:port',
    # 'http://proxy2:port',
]

# Configurações de User-Agent
USER_AGENT_ROTATION = True    # Rotacionar User-Agents automaticamente
CUSTOM_USER_AGENTS = [        # User-Agents customizados (se USER_AGENT_ROTATION = False)
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
]

# Configurações de Debug
DEBUG_MODE = False             # Modo debug (mais logs e informações)
SAVE_HTML_RESPONSES = False   # Salvar respostas HTML para debug
HTML_DEBUG_DIR = './debug_html'  # Diretório para HTML de debug

# Configurações de Performance
ENABLE_MULTITHREADING = False  # Habilitar multithreading (experimental)
MAX_THREADS = 4               # Máximo de threads para scraping paralelo
THREAD_DELAY = 0.5            # Delay entre threads (segundos)

# Configurações de Validação
VALIDATE_DATA = True           # Validar dados extraídos
MIN_NAME_LENGTH = 2           # Comprimento mínimo para nome do jogo
MAX_NAME_LENGTH = 200         # Comprimento máximo para nome do jogo

# Configurações de Backup
AUTO_BACKUP = True            # Backup automático dos dados
BACKUP_INTERVAL = 300         # Intervalo de backup em segundos (5 minutos)
BACKUP_DIR = './backups'      # Diretório para backups

# Configurações de Notificação
ENABLE_NOTIFICATIONS = False  # Habilitar notificações (email, Discord, etc.)
NOTIFICATION_EMAIL = ''       # Email para notificações
NOTIFICATION_WEBHOOK = ''     # Webhook para notificações

# Configurações de Limpeza
AUTO_CLEANUP = True           # Limpeza automática de arquivos temporários
CLEANUP_INTERVAL = 86400      # Intervalo de limpeza em segundos (24 horas)
MAX_LOG_AGE = 604800          # Idade máxima dos logs em segundos (7 dias)
MAX_CACHE_AGE = 2592000       # Idade máxima do cache em segundos (30 dias)
