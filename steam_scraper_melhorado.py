#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Steam Scraper Melhorado - Captura todas as informações incluindo reviews
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
import json
import re
from datetime import datetime

class SteamScraperMelhorado:
    def __init__(self):
        self.base_url = "https://store.steampowered.com"
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def get_random_delay(self):
        """Delay aleatório para evitar bloqueios"""
        delay = random.uniform(2, 4)
        time.sleep(delay)
        
    def get_game_by_app_id(self, app_id):
        """Obtém informações completas de um jogo pelo App ID"""
        try:
            print(f"📖 Obtendo informações do App ID: {app_id}")
            
            # PRIMEIRA TENTATIVA: API da Steam (mais confiável)
            print("🔄 Tentando via API da Steam...")
            game_info = self._get_game_via_api_direct(app_id)
            
            if game_info and game_info['nome'] != 'N/A':
                print(f"✅ Informações obtidas via API para: {game_info['nome']}")
                return game_info
            
            # SEGUNDA TENTATIVA: Scraping tradicional
            print("🔄 Tentando via scraping tradicional...")
            game_url = f"{self.base_url}/app/{app_id}/"
            print(f"🔗 URL: {game_url}")
            
            self.get_random_delay()
            response = self.session.get(game_url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Verifica se é página de agecheck
                if self._is_agecheck_page(soup):
                    print("🔞 Página de verificação de idade detectada. Tentando contornar...")
                    
                    # Tenta contornar o agecheck
                    response = self._bypass_agecheck(app_id)
                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                    else:
                        print("❌ Não foi possível contornar o agecheck")
                        return None
                
                # DEBUG: Salvar HTML para análise
                self._debug_save_html(soup, app_id)
                
                game_info = self.extract_game_info_completo(soup, app_id)
                
                if game_info and game_info['nome'] != 'N/A':
                    print(f"✅ Informações obtidas via scraping para: {game_info['nome']}")
                    return game_info
                else:
                    print(f"❌ Scraping falhou, retornando dados da API")
                    return self._get_game_via_api_direct(app_id)
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                print("🔄 Retornando dados da API como fallback...")
                return self._get_game_via_api_direct(app_id)
                
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            print("🔄 Tentando API como último recurso...")
            return self._get_game_via_api_direct(app_id)
    
    def extract_game_info_completo(self, soup, app_id):
        """Extrai TODAS as informações do jogo da Steam"""
        try:
            game_info = {
                'app_id': app_id,
                'nome': 'N/A',
                'generos': [],
                'generos_principais': [],
                'data_lancamento': 'N/A',
                'publisher': 'N/A',
                'developer': 'N/A',
                'franchise': 'N/A',
                'serie': 'N/A',
                'preco': 'N/A',
                'descricao': 'N/A',
                'tags': [],
                'reviews': {
                    'overall': 'N/A',
                    'total_reviews': 0,
                    'recentes': 'N/A',
                    'recentes_count': 0,
                    'pt_br': 'N/A',
                    'pt_br_count': 0
                },
                'url_steam': f"https://store.steampowered.com/app/{app_id}/"
            }
            
            # 1. NOME DO JOGO - MÉTODO MELHORADO
            name_selectors = [
                'div.apphub_AppName',
                'h1.pageheader',
                'h1.apphub_AppName',
                'div.apphub_AppName',
                'h1.app_title',
                'div.app_title',
                'h1.title',
                'div.title',
                'h1',
                'title'
            ]
            
            for selector in name_selectors:
                name_element = soup.select_one(selector)
                if name_element:
                    game_info['nome'] = name_element.get_text(strip=True)
                    break
            
            # 2. GÊNEROS - MÉTODO MELHORADO
            self.extract_genres_melhorado(soup, game_info)
            
            # 3. PREÇO
            price_selectors = [
                'div.game_purchase_price',
                'div.price',
                'div.discount_final_price',
                'div.discount_original_price'
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    game_info['preco'] = price_element.get_text(strip=True)
                    break
            
            # 4. DESCRIÇÃO
            desc_selectors = [
                'div.game_description_snippet',
                'div.description',
                'div.apphub_AppName'
            ]
            
            for selector in desc_selectors:
                desc_element = soup.select_one(selector)
                if desc_element:
                    game_info['descricao'] = desc_element.get_text(strip=True)
                    break
            
            # 5. TAGS
            tag_elements = soup.find_all('a', class_='app_tag')
            for tag in tag_elements:
                tag_text = tag.get_text(strip=True)
                if tag_text and len(tag_text) > 1:
                    game_info['tags'].append(tag_text)
            
            # 6. REVIEWS - MÉTODO MELHORADO
            self.extract_reviews_melhorado(soup, game_info)
            
            # DEBUG: Mostra o que foi capturado
            if game_info['reviews']['overall'] == 'N/A':
                self.debug_reviews_extraction(soup)
            
            # 7. PUBLISHER, DEVELOPER E FRANCHISE - MÉTODO MELHORADO
            self.extract_publisher_developer_franchise_melhorado(soup, game_info)
            
            # 8. DATA DE LANÇAMENTO - MÉTODO MELHORADO
            self.extract_release_date_melhorado(soup, game_info)
            
            return game_info
            
        except Exception as e:
            print(f"Erro ao extrair informações: {e}")
            return None
    
    def extract_genres_melhorado(self, soup, game_info):
        """Extrai gêneros de forma mais organizada"""
        try:
            # Método 1: Tags de gênero da Steam
            genre_elements = (
                soup.find_all('a', class_='app_tag') or
                soup.find_all('a', class_='tag') or
                soup.find_all('span', class_='app_tag') or
                soup.find_all('div', class_='app_tag')
            )
            all_genres = []
            
            for genre in genre_elements:
                genre_text = genre.get_text(strip=True)
                if genre_text and len(genre_text) > 1:
                    all_genres.append(genre_text)
            
            # Método 2: Procura por texto específico de gêneros
            all_text = soup.get_text()
            genre_patterns = [
                r'gênero[:\s]+([^\n\r]+)',
                r'genre[:\s]+([^\n\r]+)',
                r'categoria[:\s]+([^\n\r]+)',
                r'category[:\s]+([^\n\r]+)'
            ]
            
            for pattern in genre_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    genre_text = match.group(1).strip()
                    # Separa gêneros por vírgula ou ponto
                    genres_split = re.split(r'[,\.]', genre_text)
                    for genre in genres_split:
                        genre_clean = genre.strip()
                        if genre_clean and genre_clean not in all_genres:
                            all_genres.append(genre_clean)
                    break
            
            # Organiza gêneros por prioridade
            generos_principais = []
            generos_secundarios = []
            
            # Gêneros principais (mais importantes)
            generos_importantes = [
                'Ação', 'Aventura', 'RPG', 'Estratégia', 'Simulação', 'Esporte',
                'Corrida', 'Tiro', 'Luta', 'Plataforma', 'Puzzle', 'Indie',
                'Casual', 'Multijogador', 'Um Jogador', 'Cooperativo'
            ]
            
            for genre in all_genres:
                if any(importante.lower() in genre.lower() for importante in generos_importantes):
                    generos_principais.append(genre)
                else:
                    generos_secundarios.append(genre)
            
            # Remove duplicatas e organiza
            generos_principais = list(dict.fromkeys(generos_principais))  # Remove duplicatas mantendo ordem
            generos_secundarios = list(dict.fromkeys(generos_secundarios))
            
            # Combina todos os gêneros
            game_info['generos'] = generos_principais + generos_secundarios
            game_info['generos_principais'] = generos_principais
            
        except Exception as e:
            print(f"Erro ao extrair gêneros: {e}")
    
    def extract_publisher_developer_franchise_melhorado(self, soup, game_info):
        """Extrai publisher, developer e franchise de forma mais precisa"""
        try:
            # Método 1: Procura por tabelas de informações
            info_tables = soup.find_all('table')
            for table in info_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        if 'developer' in key or 'desenvolvedor' in key:
                            game_info['developer'] = value
                        elif 'publisher' in key or 'distribuidora' in key:
                            game_info['publisher'] = value
                        elif 'franchise' in key or 'série' in key or 'series' in key:
                            game_info['franchise'] = value
                            game_info['serie'] = value  # Alias para série
            
            # Método 2: Procura por texto específico
            all_text = soup.get_text()
            
            # Developer
            dev_patterns = [
                r'desenvolvedor[:\s]+([^\n\r]+)',
                r'developer[:\s]+([^\n\r]+)',
                r'desenvolvido\s+por[:\s]+([^\n\r]+)'
            ]
            
            for pattern in dev_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match and game_info['developer'] == 'N/A':
                    game_info['developer'] = match.group(1).strip()
                    break
            
            # Publisher
            pub_patterns = [
                r'distribuidora[:\s]+([^\n\r]+)',
                r'publisher[:\s]+([^\n\r]+)',
                r'publicado\s+por[:\s]+([^\n\r]+)'
            ]
            
            for pattern in pub_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match and game_info['publisher'] == 'N/A':
                    game_info['publisher'] = match.group(1).strip()
                    break
            
            # Franchise/Série
            franchise_patterns = [
                r'série[:\s]+([^\n\r]+)',
                r'franchise[:\s]+([^\n\r]+)',
                r'series[:\s]+([^\n\r]+)',
                r'franquia[:\s]+([^\n\r]+)'
            ]
            
            for pattern in franchise_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match and game_info['franchise'] == 'N/A':
                    franchise_text = match.group(1).strip()
                    game_info['franchise'] = franchise_text
                    game_info['serie'] = franchise_text
                    break
            
            # Método 3: Procura por links de franchise/série
            franchise_links = soup.find_all('a', href=re.compile(r'franchise|series|série'))
            if franchise_links:
                for link in franchise_links:
                    link_text = link.get_text(strip=True)
                    if link_text and link_text != 'N/A':
                        game_info['franchise'] = link_text
                        game_info['serie'] = link_text
                        break
                        
        except Exception as e:
            print(f"Erro ao extrair publisher/developer/franchise: {e}")
    
    def extract_release_date_melhorado(self, soup, game_info):
        """Extrai data de lançamento de forma mais precisa"""
        try:
            # Método 1: Procura por elementos específicos
            date_selectors = [
                'div.release_date',
                'div.date',
                'span.release_date',
                'span.date'
            ]
            
            for selector in date_selectors:
                date_element = soup.select_one(selector)
                if date_element:
                    date_text = date_element.get_text(strip=True)
                    if date_text and date_text != 'N/A':
                        # Limpa o texto da data
                        clean_date = self.clean_date_text(date_text)
                        game_info['data_lancamento'] = clean_date
                        return
            
            # Método 2: Procura por padrões de data no texto
            all_text = soup.get_text()
            date_patterns = [
                r'(\d{1,2}/\w+/\d{4})',  # 30/jan./2025
                r'(\d{1,2}\s+\w+\s+\d{4})',  # 30 jan 2025
                r'(\d{1,2}\.\s+\w+\s+\d{4})',  # 30. jan 2025
                r'lançamento[:\s]+([^\n\r]+)',  # lançamento: 30/jan./2025
                r'release[:\s]+([^\n\r]+)',  # release: 30/jan./2025
                r'data[:\s]+([^\n\r]+)'  # data: 30/jan./2025
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    date_text = match.group(1).strip()
                    if date_text and date_text != 'N/A':
                        clean_date = self.clean_date_text(date_text)
                        game_info['data_lancamento'] = clean_date
                        break
                        
        except Exception as e:
            print(f"Erro ao extrair data de lançamento: {e}")
    
    def clean_date_text(self, date_text):
        """Limpa e formata o texto da data"""
        try:
            # Remove prefixos desnecessários
            date_text = re.sub(r'^data\s+de\s+lançamento\s*:\s*', '', date_text, flags=re.IGNORECASE)
            date_text = re.sub(r'^lançamento\s*:\s*', '', date_text, flags=re.IGNORECASE)
            date_text = re.sub(r'^release\s*:\s*', '', date_text, flags=re.IGNORECASE)
            date_text = re.sub(r'^data\s*:\s*', '', date_text, flags=re.IGNORECASE)
            
            # Remove espaços extras
            date_text = date_text.strip()
            
            return date_text
        except:
            return date_text
    
    def extract_reviews_melhorado(self, soup, game_info):
        """Extrai informações de reviews de forma mais precisa"""
        try:
            # Método 1: Procura por elementos específicos de review da Steam
            review_selectors = [
                'div.user_reviews_summary_row',
                'div.review_summary',
                'div.review_breakdown'
            ]
            
            for selector in review_selectors:
                review_elements = soup.find_all('div', class_=selector)
                if review_elements:
                    break
            
            # Se não encontrou, procura por qualquer div que contenha "análise"
            if not review_elements:
                review_elements = soup.find_all('div', string=re.compile(r'análise|review', re.IGNORECASE))
            
            # Método 2: Procura por texto específico de reviews
            all_text = soup.get_text()
            
            # Reviews Gerais (todas as línguas)
            global_patterns = [
                r'(\d+(?:\.\d+)*)\s*análise\(s\)\s+em\s+todos\s+os\s+idiomas\s*\(([^)]+)\)',
                r'(\d+(?:\.\d+)*)\s*review\(s\)\s+in\s+all\s+languages\s*\(([^)]+)\)',
                r'(\d+(?:\.\d+)*)\s*análise\(s\)\s*\(([^)]+)\)'
            ]
            
            for pattern in global_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    count = int(match.group(1).replace('.', ''))
                    sentiment = match.group(2).strip()
                    game_info['reviews']['total_reviews'] = count
                    game_info['reviews']['overall'] = sentiment
                    break
            
            # Reviews em Português (PT-BR)
            ptbr_patterns = [
                r'(\d+(?:\.\d+)*)\s*análise\(s\)\s+em\s+Português\s*\(Brasil\)\s*\(([^)]+)\)',
                r'(\d+(?:\.\d+)*)\s*análise\(s\)\s+em\s+PT-BR\s*\(([^)]+)\)',
                r'(\d+(?:\.\d+)*)\s*análise\(s\)\s*em\s+Português[^)]*\(([^)]+)\)'
            ]
            
            for pattern in ptbr_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    count = int(match.group(1).replace('.', ''))
                    sentiment = match.group(2).strip()
                    game_info['reviews']['pt_br_count'] = count
                    game_info['reviews']['pt_br'] = sentiment
                    break
            
            # Reviews Recentes
            recent_patterns = [
                r'(\d+(?:\.\d+)*)\s*análise\(s\)\s+recentes\s*\(([^)]+)\)',
                r'(\d+(?:\.\d+)*)\s*recent\s+review\(s\)\s*\(([^)]+)\)',
                r'(\d+(?:\.\d+)*)\s*análise\(s\)\s*\(([^)]+)\)\s*recentes'
            ]
            
            for pattern in recent_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    count = int(match.group(1).replace('.', ''))
                    sentiment = match.group(2).strip()
                    game_info['reviews']['recentes_count'] = count
                    game_info['reviews']['recentes'] = sentiment
                    break
            
            # Método 3: Procura por padrões mais genéricos
            if game_info['reviews']['overall'] == 'N/A':
                # Procura por "Bem positivas" ou similar
                sentiment_patterns = [
                    r'(\d+(?:\.\d+)*)\s*análise\(s\)[^)]*\(([^)]+)\)',
                    r'([^)]+)\s*\((\d+(?:\.\d+)*)\s*análise\(s\)\)'
                ]
                
                for pattern in sentiment_patterns:
                    match = re.search(pattern, all_text, re.IGNORECASE)
                    if match:
                        if match.group(1).replace('.', '').isdigit():
                            count = int(match.group(1).replace('.', ''))
                            sentiment = match.group(2).strip()
                        else:
                            sentiment = match.group(1).strip()
                            count = int(match.group(2).replace('.', ''))
                        
                        if game_info['reviews']['total_reviews'] == 0:
                            game_info['reviews']['total_reviews'] = count
                            game_info['reviews']['overall'] = sentiment
                        break
            
            # Método 4: Procura por elementos HTML específicos
            # Procura por divs que contenham números e sentimentos
            review_divs = soup.find_all('div', string=re.compile(r'\d+.*positiv|negativ|mista', re.IGNORECASE))
            
            for div in review_divs:
                text = div.get_text(strip=True)
                
                # Reviews recentes
                if 'recente' in text.lower() or 'recent' in text.lower():
                    count_match = re.search(r'(\d+(?:\.\d+)*)', text)
                    sentiment_match = re.search(r'(muito\s+positiv|positiv|mista|negativ)', text, re.IGNORECASE)
                    
                    if count_match and sentiment_match:
                        count = int(count_match.group(1).replace('.', ''))
                        sentiment = sentiment_match.group(1).title()
                        
                        if game_info['reviews']['recentes'] == 'N/A':
                            game_info['reviews']['recentes_count'] = count
                            game_info['reviews']['recentes'] = sentiment
                
                # Reviews PT-BR
                elif 'português' in text.lower() or 'pt-br' in text.lower():
                    count_match = re.search(r'(\d+(?:\.\d+)*)', text)
                    sentiment_match = re.search(r'(bem\s+positiv|positiv|mista|negativ)', text, re.IGNORECASE)
                    
                    if count_match and sentiment_match:
                        count = int(count_match.group(1).replace('.', ''))
                        sentiment = sentiment_match.group(1).title()
                        
                        if game_info['reviews']['pt_br'] == 'N/A':
                            game_info['reviews']['pt_br_count'] = count
                            game_info['reviews']['pt_br'] = sentiment
                        
        except Exception as e:
            print(f"Erro ao extrair reviews: {e}")
    
    def debug_reviews_extraction(self, soup):
        """Função de debug para ver o que está sendo capturado"""
        try:
            print("\n🔍 DEBUG: Analisando HTML para reviews...")
            
            # Procura por todos os textos que contenham "análise"
            all_text = soup.get_text()
            analysis_matches = re.findall(r'(\d+(?:\.\d+)*)\s*análise\(s\)[^)]*\(([^)]+)\)', all_text, re.IGNORECASE)
            
            if analysis_matches:
                print(f"✅ Encontrados {len(analysis_matches)} padrões de análise:")
                for i, (count, sentiment) in enumerate(analysis_matches, 1):
                    print(f"   {i}. {count} análises - {sentiment}")
            else:
                print("❌ Nenhum padrão de análise encontrado")
            
            # Procura por divs específicos
            review_divs = soup.find_all('div', class_=re.compile(r'review|análise', re.IGNORECASE))
            print(f"\n📊 Divs de review encontradas: {len(review_divs)}")
            
            for i, div in enumerate(review_divs[:5], 1):
                text = div.get_text(strip=True)
                if text and len(text) > 10:
                    print(f"   {i}. {text[:100]}...")
            
        except Exception as e:
            print(f"Erro no debug: {e}")
    
    def search_games(self, query, max_results=10):
        """Busca jogos na Steam por nome com múltiplas estratégias"""
        try:
            print(f"🔍 Buscando '{query}' na Steam...")
            
            # Estratégia 1: API de sugestões da Steam
            games = self._search_via_suggest_api(query, max_results)
            
            # Estratégia 2: Se não encontrou, tenta busca tradicional
            if not games:
                games = self._search_via_store_search(query, max_results)
            
            # Estratégia 3: Se ainda não encontrou, tenta busca por termos modificados
            if not games:
                games = self._search_with_modified_terms(query, max_results)
            
            if games:
                print(f"✅ Encontrados {len(games)} jogos")
            else:
                print("❌ Nenhum jogo encontrado.")
                self._show_search_tips(query)
            
            return games
            
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            return []
    
    def _search_via_suggest_api(self, query, max_results):
        """Busca usando a API de sugestões da Steam"""
        try:
            # API de sugestões da Steam
            suggest_url = "https://store.steampowered.com/search/suggest"
            params = {
                'term': query,
                'f': 'games',
                'cc': 'BR',
                'l': 'portuguese'
            }
            
            self.get_random_delay()
            response = self.session.get(suggest_url, params=params, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            game_matches = soup.find_all('a', class_='match')
            
            games = []
            for match in game_matches[:max_results]:
                try:
                    # Nome
                    name_elem = match.find('div', class_='match_name')
                    name = name_elem.get_text(strip=True) if name_elem else 'N/A'
                    
                    # App ID
                    href = match.get('href', '')
                    app_id = 'N/A'
                    if '/app/' in href:
                        app_id_match = re.search(r'/app/(\d+)/', href)
                        if app_id_match:
                            app_id = app_id_match.group(1)
                    
                    # Preço
                    price_elem = match.find('div', class_='match_price')
                    price = price_elem.get_text(strip=True) if price_elem else 'Grátis'
                    
                    if name != 'N/A' and app_id != 'N/A':
                        games.append({
                            'nome': name,
                            'app_id': app_id,
                            'preco': price,
                            'data_lancamento': 'N/A',
                            'url': href
                        })
                        
                except Exception as e:
                    continue
            
            return games
            
        except Exception as e:
            return []
    
    def _search_via_store_search(self, query, max_results):
        """Busca tradicional na loja Steam"""
        try:
            search_url = "https://store.steampowered.com/search/"
            params = {
                'term': query,
                'category1': '998',  # Games
                'l': 'portuguese',
                'cc': 'BR'
            }
            
            self.get_random_delay()
            response = self.session.get(search_url, params=params, timeout=15)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Procura por diferentes seletores de resultado
            game_containers = (
                soup.find_all('a', class_='search_result_row') or
                soup.find_all('div', class_='search_result_row') or
                soup.find_all('a', {'data-ds-appid': True})
            )
            
            games = []
            for container in game_containers[:max_results]:
                try:
                    # Nome do jogo
                    name_elem = (
                        container.find('span', class_='title') or
                        container.find('div', class_='title') or
                        container.find('h4')
                    )
                    name = name_elem.get_text(strip=True) if name_elem else 'N/A'
                    
                    # App ID
                    app_id = 'N/A'
                    # Método 1: data-ds-appid
                    if container.get('data-ds-appid'):
                        app_id = container.get('data-ds-appid')
                    # Método 2: href
                    else:
                        href = container.get('href', '')
                        if '/app/' in href:
                            app_id_match = re.search(r'/app/(\d+)/', href)
                            if app_id_match:
                                app_id = app_id_match.group(1)
                    
                    # Preço
                    price_elem = (
                        container.find('div', class_='search_price') or
                        container.find('div', class_='discount_final_price') or
                        container.find('span', class_='price')
                    )
                    price = price_elem.get_text(strip=True) if price_elem else 'N/A'
                    
                    # Data de lançamento
                    release_elem = container.find('div', class_='search_released')
                    release_date = release_elem.get_text(strip=True) if release_elem else 'N/A'
                    
                    if name != 'N/A' and app_id != 'N/A':
                        games.append({
                            'nome': name,
                            'app_id': app_id,
                            'preco': price,
                            'data_lancamento': release_date,
                            'url': f"https://store.steampowered.com/app/{app_id}/"
                        })
                        
                except Exception as e:
                    continue
            
            return games
            
        except Exception as e:
            return []
    
    def _search_with_modified_terms(self, query, max_results):
        """Tenta busca com termos modificados"""
        try:
            # Lista de variações do termo de busca
            search_variations = [
                query.replace(" ", ""),  # Sem espaços
                query.replace(":", ""),  # Sem dois pontos
                query.split()[0] if " " in query else query,  # Primeira palavra
                query.lower(),  # Minúsculo
                query.upper(),  # Maiúsculo
                query.replace("2077", ""),  # Remove números comuns
                query.replace("'s", ""),  # Remove apóstrofes
            ]
            
            # Remove duplicatas mantendo ordem
            search_variations = list(dict.fromkeys(search_variations))
            
            for variation in search_variations[:3]:  # Testa apenas 3 variações
                if variation != query and len(variation) > 2:
                    print(f"🔄 Tentando variação: '{variation}'")
                    games = self._search_via_suggest_api(variation, max_results)
                    if games:
                        return games
                    
                    # Pequeno delay entre tentativas
                    time.sleep(0.5)
            
            return []
            
        except Exception as e:
            return []
    
    def _is_agecheck_page(self, soup):
        """Verifica se a página é de verificação de idade"""
        try:
            # Verifica por elementos específicos do agecheck
            page_text = soup.get_text().lower()
            
            agecheck_indicators = [
                'agecheck' in page_text,
                'verificação de idade' in page_text,
                'verification' in page_text,
                soup.find('div', class_='agecheck'),
                soup.find('form', action=lambda x: x and 'agecheck' in x),
                soup.find('input', {'name': 'ageDay'}),
                soup.find('input', {'name': 'ageMonth'}),
                soup.find('input', {'name': 'ageYear'}),
                soup.find('title', string=lambda x: x and 'agecheck' in x.lower())
            ]
            
            # Verifica se a página tem conteúdo real do jogo
            game_content_indicators = [
                soup.find('div', class_='apphub_AppName'),
                soup.find('div', class_='game_purchase_price'),
                soup.find('div', class_='app_tag'),
                soup.find('div', class_='game_description_snippet')
            ]
            
            has_agecheck = any(agecheck_indicators)
            has_game_content = any(game_content_indicators)
            
            return has_agecheck and not has_game_content
            
        except Exception as e:
            return False
    
    def _bypass_agecheck(self, app_id):
        """Tenta contornar a verificação de idade"""
        try:
            print("🔄 Tentando contornar agecheck...")
            
            # Método 1: Usa a API da Steam para obter dados
            print("🔄 Tentando API da Steam...")
            api_response = self._get_game_via_api(app_id)
            if api_response:
                return api_response
            
            # Método 2: Simula que o usuário é maior de idade
            agecheck_url = f"{self.base_url}/agecheckset/app/{app_id}/"
            
            # Dados para simular idade (18+ anos)
            age_data = {
                'ageDay': '1',
                'ageMonth': '1', 
                'ageYear': '1990'
            }
            
            # Headers específicos para agecheck
            agecheck_headers = {
                'User-Agent': self.session.headers['User-Agent'],
                'Referer': f"{self.base_url}/app/{app_id}/",
                'Origin': self.base_url,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Faz POST para o agecheck
            response = self.session.post(agecheck_url, data=age_data, headers=agecheck_headers, timeout=30)
            
            if response.status_code == 200:
                print("✅ Agecheck contornado com sucesso!")
                
                # Pequeno delay para processar
                time.sleep(1)
                
                # Agora faz GET para a página real com cookies
                game_url = f"{self.base_url}/app/{app_id}/"
                return self.session.get(game_url, timeout=30)
            else:
                print(f"❌ Falha no agecheck: {response.status_code}")
                
                # Método alternativo: tenta com cookies diretos
                print("🔄 Tentando método alternativo...")
                return self._bypass_agecheck_alternative(app_id)
                
        except Exception as e:
            print(f"❌ Erro ao contornar agecheck: {e}")
            return None
    
    def _get_game_via_api_direct(self, app_id):
        """Obtém dados do jogo diretamente via API da Steam"""
        try:
            print("🔄 Usando API da Steam...")
            
            # API de detalhes da Steam
            api_url = "https://store.steampowered.com/api/appdetails"
            params = {
                'appids': app_id,
                'cc': 'BR',
                'l': 'portuguese'
            }
            
            headers = {
                'User-Agent': self.session.headers['User-Agent'],
                'Accept': 'application/json',
                'Referer': f"{self.base_url}/app/{app_id}/"
            }
            
            response = self.session.get(api_url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data and str(app_id) in data and data[str(app_id)]['success']:
                    game_data = data[str(app_id)]['data']
                    print("✅ Dados obtidos via API!")
                    
                    # Converte dados da API diretamente para game_info
                    return self._convert_api_data_to_game_info(game_data, app_id)
                else:
                    print("❌ API retornou dados inválidos")
                    return self._create_empty_game_info(app_id)
            else:
                print(f"❌ Erro na API: {response.status_code}")
                return self._create_empty_game_info(app_id)
                
        except Exception as e:
            print(f"❌ Erro na API: {e}")
            return self._create_empty_game_info(app_id)
    
    def _convert_api_data_to_game_info(self, game_data, app_id):
        """Converte dados da API diretamente para game_info"""
        try:
            game_info = {
                'app_id': app_id,
                'nome': game_data.get('name', 'N/A'),
                'generos': [],
                'generos_principais': [],
                'data_lancamento': game_data.get('release_date', {}).get('date', 'N/A'),
                'publisher': ', '.join(game_data.get('publishers', ['N/A'])),
                'developer': ', '.join(game_data.get('developers', ['N/A'])),
                'franchise': game_data.get('franchise', 'N/A'),
                'serie': game_data.get('series', 'N/A'),
                'preco': game_data.get('price_overview', {}).get('final_formatted', 'N/A'),
                'descricao': self._clean_html_description(game_data.get('detailed_description', 'N/A')),
                'tags': [],
                'reviews': {
                    'overall': 'N/A',
                    'total_reviews': 0,
                    'recentes': 'N/A',
                    'recentes_count': 0,
                    'pt_br': 'N/A',
                    'pt_br_count': 0
                },
                'url_steam': f"https://store.steampowered.com/app/{app_id}/"
            }
            
            # Extrai gêneros
            genres = game_data.get('genres', [])
            for genre in genres:
                genre_name = genre.get('description', '')
                if genre_name:
                    game_info['generos'].append(genre_name)
            
            # Organiza gêneros principais
            generos_importantes = [
                'Ação', 'Aventura', 'RPG', 'Estratégia', 'Simulação', 'Esporte',
                'Corrida', 'Tiro', 'Luta', 'Plataforma', 'Puzzle', 'Indie',
                'Casual', 'Multijogador', 'Um Jogador', 'Cooperativo'
            ]
            
            for genre in game_info['generos']:
                if any(importante.lower() in genre.lower() for importante in generos_importantes):
                    game_info['generos_principais'].append(genre)
            
            # Extrai tags
            tags = game_data.get('tags', [])
            for tag in tags:
                tag_name = tag.get('name', '')
                if tag_name:
                    game_info['tags'].append(tag_name)
            
            # Extrai reviews se disponível
            if 'metacritic' in game_data:
                metacritic = game_data['metacritic']
                if metacritic and 'score' in metacritic:
                    score = metacritic['score']
                    if score >= 80:
                        game_info['reviews']['overall'] = 'Muito Positivas'
                    elif score >= 70:
                        game_info['reviews']['overall'] = 'Positivas'
                    elif score >= 50:
                        game_info['reviews']['overall'] = 'Mistas'
                    else:
                        game_info['reviews']['overall'] = 'Negativas'
            
            # Extrai reviews da Steam se disponível
            if 'steam_appid' in game_data:
                # Tenta obter reviews via API separada
                reviews_data = self._get_reviews_via_api(app_id)
                if reviews_data:
                    game_info['reviews'].update(reviews_data)
            
            # Extrai tags de categorias também
            categories = game_data.get('categories', [])
            for category in categories:
                category_name = category.get('description', '')
                if category_name and category_name not in game_info['tags']:
                    game_info['tags'].append(category_name)
            
            return game_info
            
        except Exception as e:
            print(f"❌ Erro ao converter dados da API: {e}")
            return self._create_empty_game_info(app_id)
    
    def _get_reviews_via_api(self, app_id):
        """Obtém reviews via API da Steam"""
        try:
            # API de reviews da Steam
            reviews_url = f"https://store.steampowered.com/appreviews/{app_id}"
            params = {
                'json': 1,
                'filter': 'summary',
                'language': 'portuguese',
                'cc': 'BR'
            }
            
            headers = {
                'User-Agent': self.session.headers['User-Agent'],
                'Accept': 'application/json'
            }
            
            response = self.session.get(reviews_url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data and 'success' in data and data['success'] == 1:
                    query_summary = data.get('query_summary', {})
                    
                    reviews_info = {
                        'overall': 'N/A',
                        'total_reviews': query_summary.get('total_reviews', 0),
                        'recentes': 'N/A',
                        'recentes_count': 0,
                        'pt_br': 'N/A',
                        'pt_br_count': 0
                    }
                    
                    # Determina sentimento geral
                    total_positive = query_summary.get('total_positive', 0)
                    total_reviews = query_summary.get('total_reviews', 0)
                    
                    if total_reviews > 0:
                        positive_percentage = (total_positive / total_reviews) * 100
                        
                        if positive_percentage >= 90:
                            reviews_info['overall'] = 'Muito Positivas'
                        elif positive_percentage >= 80:
                            reviews_info['overall'] = 'Positivas'
                        elif positive_percentage >= 70:
                            reviews_info['overall'] = 'Bem Positivas'
                        elif positive_percentage >= 50:
                            reviews_info['overall'] = 'Mistas'
                        else:
                            reviews_info['overall'] = 'Negativas'
                    
                    # Reviews recentes
                    recent_reviews = data.get('reviews', [])
                    if recent_reviews:
                        recent_positive = sum(1 for r in recent_reviews if r.get('voted_up', False))
                        recent_total = len(recent_reviews)
                        
                        if recent_total > 0:
                            recent_percentage = (recent_positive / recent_total) * 100
                            
                            if recent_percentage >= 90:
                                reviews_info['recentes'] = 'Muito Positivas'
                            elif recent_percentage >= 80:
                                reviews_info['recentes'] = 'Positivas'
                            elif recent_percentage >= 70:
                                reviews_info['recentes'] = 'Bem Positivas'
                            elif recent_percentage >= 50:
                                reviews_info['recentes'] = 'Mistas'
                            else:
                                reviews_info['recentes'] = 'Negativas'
                            
                            reviews_info['recentes_count'] = recent_total
                    
                    # Reviews PT-BR (mesmo que geral por enquanto)
                    reviews_info['pt_br'] = reviews_info['overall']
                    reviews_info['pt_br_count'] = reviews_info['total_reviews']
                    
                    return reviews_info
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao obter reviews: {e}")
            return None
    
    def _clean_html_description(self, html_text):
        """Remove tags HTML e limpa a descrição"""
        try:
            if not html_text or html_text == 'N/A':
                return 'N/A'
            
            # Remove tags HTML básicas
            import re
            
            # Remove tags HTML
            clean_text = re.sub(r'<[^>]+>', '', html_text)
            
            # Remove múltiplos espaços em branco
            clean_text = re.sub(r'\s+', ' ', clean_text)
            
            # Remove quebras de linha extras
            clean_text = clean_text.replace('\n', ' ').replace('\r', ' ')
            
            # Remove espaços no início e fim
            clean_text = clean_text.strip()
            
            # Limita o tamanho da descrição
            if len(clean_text) > 500:
                clean_text = clean_text[:500] + "..."
            
            return clean_text
            
        except Exception as e:
            print(f"❌ Erro ao limpar descrição: {e}")
            return html_text
    
    def _create_empty_game_info(self, app_id):
        """Cria estrutura vazia de game_info"""
        return {
            'app_id': app_id,
            'nome': 'N/A',
            'generos': [],
            'generos_principais': [],
            'data_lancamento': 'N/A',
            'publisher': 'N/A',
            'developer': 'N/A',
            'franchise': 'N/A',
            'serie': 'N/A',
            'preco': 'N/A',
            'descricao': 'N/A',
            'tags': [],
            'reviews': {
                'overall': 'N/A',
                'total_reviews': 0,
                'recentes': 'N/A',
                'recentes_count': 0,
                'pt_br': 'N/A',
                'pt_br_count': 0
            },
            'url_steam': f"https://store.steampowered.com/app/{app_id}/"
        }
    
    def _bypass_agecheck_alternative(self, app_id):
        """Método alternativo para contornar agecheck"""
        try:
            # Define cookies diretamente para simular idade
            age_cookies = {
                f'agecheck_{app_id}': '1',
                'mature_content': '1',
                'age_verified': '1'
            }
            
            # Atualiza cookies da sessão
            for cookie_name, cookie_value in age_cookies.items():
                self.session.cookies.set(cookie_name, cookie_value, domain='.steampowered.com')
            
            # Tenta acessar a página novamente
            game_url = f"{self.base_url}/app/{app_id}/"
            return self.session.get(game_url, timeout=30)
            
        except Exception as e:
            print(f"❌ Método alternativo falhou: {e}")
            return None
    
    def _debug_save_html(self, soup, app_id):
        """Salva o HTML para debug"""
        try:
            debug_filename = f"debug_{app_id}.html"
            with open(debug_filename, 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))
            print(f"🔍 HTML salvo em: {debug_filename}")
        except Exception as e:
            print(f"Erro ao salvar HTML: {e}")
    
    def _show_search_tips(self, query):
        """Mostra dicas de busca para o usuário"""
        print("\n💡 DICAS DE BUSCA:")
        print("   • Tente termos mais simples: 'Spider', 'Counter', 'Cyberpunk'")
        print("   • Use nomes em inglês: 'Call of Duty' em vez de 'Call of Duty'")
        print("   • Tente apenas a primeira palavra do título")
        print("   • Se souber o App ID, use a opção 1 do menu")
        
        # Exemplos específicos baseados na busca
        if "cyberpunk" in query.lower():
            print("   • Para Cyberpunk 2077, tente: 'cyberpunk' ou App ID: 1091500")
        elif "spider" in query.lower():
            print("   • Para Spider-Man, tente: 'spider' ou App ID: 2651280")
        elif "call" in query.lower() or "duty" in query.lower():
            print("   • Para Call of Duty, tente: 'call duty' ou busque por App ID")
        elif "gta" in query.lower() or "theft" in query.lower():
            print("   • Para GTA, tente: 'grand theft auto' ou App ID específico")
    
    def save_to_json(self, games_data, filename=None):
        """Salva dados em JSON"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"steam_games_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(games_data, f, ensure_ascii=False, indent=2)
            print(f"✅ Dados salvos em {filename}")
        except Exception as e:
            print(f"❌ Erro ao salvar JSON: {e}")
    
    def save_to_csv(self, games_data, filename=None):
        """Salva dados em CSV"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"steam_games_{timestamp}.csv"
        
        try:
            import csv
            if not games_data:
                print("Nenhum dado para salvar!")
                return
            
            # Obter todas as chaves possíveis
            all_keys = set()
            for game in games_data:
                if isinstance(game, dict):
                    all_keys.update(game.keys())
            
            headers = sorted(list(all_keys))
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                
                for game in games_data:
                    if isinstance(game, dict):
                        row = {}
                        for key in headers:
                            value = game.get(key, '')
                            if isinstance(value, (list, dict)):
                                row[key] = str(value)
                            else:
                                row[key] = value
                        writer.writerow(row)
            
            print(f"✅ Dados salvos em {filename}")
        except Exception as e:
            print(f"❌ Erro ao salvar CSV: {e}")

def main():
    """Função principal"""
    print("🚀 STEAM SCRAPER MELHORADO")
    print("=" * 50)
    print("✨ Agora captura: Reviews, Data, Developer, Publisher!")
    
    scraper = SteamScraperMelhorado()
    
    while True:
        print("\nEscolha uma opção:")
        print("1. 🔍 Buscar jogo por App ID")
        print("2. 🔍 Buscar jogos por nome")
        print("3. ❌ Sair")
        
        opcao = input("\nOpção (1-3): ").strip()
        
        if opcao == "1":
            app_id = input("Digite o App ID: ").strip()
            if app_id:
                game_info = scraper.get_game_by_app_id(app_id)
                if game_info:
                    print(f"\n🎯 INFORMAÇÕES COMPLETAS:")
                    print("=" * 50)
                    
                    # Informações principais
                    print(f"📱 App ID: {game_info['app_id']}")
                    print(f"🎮 Nome: {game_info['nome']}")
                    print(f"💰 Preço: {game_info['preco']}")
                    print(f"📅 Data de Lançamento: {game_info['data_lancamento']}")
                    print(f"👨‍💻 Developer: {game_info['developer']}")
                    print(f"🏢 Publisher: {game_info['publisher']}")
                    print(f"🎬 Franchise/Série: {game_info['franchise']}")
                    
                    # Reviews
                    reviews = game_info['reviews']
                    print(f"\n📊 REVIEWS:")
                    print(f"   Geral: {reviews['overall']} ({reviews['total_reviews']} análises)")
                    print(f"   Recentes: {reviews['recentes']} ({reviews['recentes_count']} análises)")
                    print(f"   PT-BR: {reviews['pt_br']} ({reviews['pt_br_count']} análises)")
                    
                    # Gêneros organizados
                    print(f"\n🎭 GÊNEROS:")
                    if game_info['generos_principais']:
                        print(f"   Principais: {', '.join(game_info['generos_principais'])}")
                    if len(game_info['generos']) > len(game_info['generos_principais']):
                        outros_generos = game_info['generos'][len(game_info['generos_principais']):]
                        print(f"   Outros: {', '.join(outros_generos[:8])}...")
                    print(f"   Total: {len(game_info['generos'])} gêneros")
                    
                    # Tags
                    print(f"\n🏷️  Tags ({len(game_info['tags'])}): {', '.join(game_info['tags'][:5])}...")
                    
                    # Salvar dados
                    salvar = input("\n💾 Salvar dados? (s/n): ").strip().lower()
                    if salvar in ['s', 'sim', 'y', 'yes']:
                        scraper.save_to_json([game_info], f"jogo_{app_id}.json")
                        scraper.save_to_csv([game_info], f"jogo_{app_id}.csv")
        
        elif opcao == "2":
            query = input("Digite o nome do jogo: ").strip()
            if query:
                games = scraper.search_games(query, max_results=5)
                if games:
                    print(f"\n📋 Resultados:")
                    for i, game in enumerate(games, 1):
                        print(f"{i}. {game['nome']} (ID: {game['app_id']}) - {game['preco']}")
                    
                    # Opção para detalhes
                    escolha = input(f"\nEscolha um jogo (1-{len(games)}) para ver detalhes, ou 0 para voltar: ").strip()
                    try:
                        escolha = int(escolha)
                        if 1 <= escolha <= len(games):
                            selected_game = games[escolha - 1]
                            if selected_game['app_id'] != 'N/A':
                                details = scraper.get_game_by_app_id(selected_game['app_id'])
                                if details:
                                    print(f"\n🎯 DETALHES COMPLETOS:")
                                    for key, value in details.items():
                                        print(f"   {key}: {value}")
                                    
                                    # Salvar
                                    salvar = input("\n💾 Salvar dados? (s/n): ").strip().lower()
                                    if salvar in ['s', 'sim', 'y', 'yes']:
                                        scraper.save_to_json([details], f"jogo_{selected_game['app_id']}.json")
                                        scraper.save_to_csv([details], f"jogo_{selected_game['app_id']}.csv")
                    except ValueError:
                        print("❌ Escolha inválida!")
        
        elif opcao == "3":
            print("👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida! Escolha 1, 2 ou 3.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
