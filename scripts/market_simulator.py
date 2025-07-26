"""
D&D 5e Financial Market Simulator - Enhanced Version
===================================================

Simulatore di mercato azionario che utilizza i risultati degli analyzer MongoDB e Neo4j
esistenti per calcolare prezzi delle azioni delle classi D&D usando modelli finanziari reali:
- CAPM (Capital Asset Pricing Model)
- Market Capitalization Model  
- Dividend Yield Model
- P/E Ratio (Price-to-Earnings)
"""

import json
import random
import math
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import sys
import os

# Import degli analyzer esistenti
try:
    from mongodb_analyzer import DNDDataAnalyzer
    from neo4j_analyzer import DNDGraphAnalyzer
    import pymongo
    from neo4j import GraphDatabase
    print("✅ Successfully imported analyzer modules")
except ImportError as e:
    print(f"❌ Error importing analyzer modules: {e}")
    print("💡 Make sure mongodb_analyzer.py and neo4j_analyzer.py are in the same directory")
    sys.exit(1)

@dataclass
class ClassFinancialMetrics:
    """Metriche finanziarie per una classe D&D"""
    # Dati base dalla classe
    name: str
    symbol: str
    
    # Metriche derivate dagli analyzer MongoDB
    power_score: float
    survivability_score: float
    versatility_score: float
    specialization_ratio: float
    overall_performance: float
    
    # Metriche di rete (Neo4j)
    centrality_score: float
    bridge_connections: int
    network_influence: float
    synergy_partnerships: int
    
    # Metriche finanziarie calcolate
    beta: float
    risk_free_rate: float
    market_risk_premium: float
    base_stock_price: float
    outstanding_shares: int
    market_cap: float
    annual_dividends: float
    dividend_yield: float
    earnings_per_share: float
    pe_ratio: float
    
    # Dati di mercato
    current_price: float
    daily_change: float
    daily_change_percent: float
    volume: int
    price_history: List[Dict]
    market_sentiment: str
    analyst_rating: str

class AdvancedDnDMarketSimulator:
    """
    Simulatore che integra analisi MongoDB e Neo4j
    con modelli finanziari realistici
    """
    
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017/", 
                 neo4j_uri: str = "bolt://localhost:7687", 
                 neo4j_user: str = "neo4j", 
                 neo4j_password: str = "admin123"):
        
        # Parametri di mercato globali
        self.risk_free_rate = 0.025  # Tasso risk-free al 2.5%
        self.market_risk_premium = 0.08  # Premio di rischio mercato 8%
        self.base_share_count = 1000000  # Numero base di azioni
        self.market_volatility = 0.12  # Volatilità mercato 12%
        
        # Parametri connessione
        self.mongo_uri = mongo_uri
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        
        # Dati dagli analyzer
        self.mongodb_results = {}
        self.neo4j_results = {}
        self.class_stocks = {}
        
        # Analyzer instances
        self.mongodb_analyzer = None
        self.neo4j_analyzer = None
        
        # Indici di mercato
        self.market_indices = {
            'DND_500': {'value': 100.0, 'change': 0.0},
            'CASTER_INDEX': {'value': 100.0, 'change': 0.0},
            'MARTIAL_INDEX': {'value': 100.0, 'change': 0.0}
        }

    def initialize_analyzers(self):
        """Inizializza gli analyzer MongoDB e Neo4j"""
        print("🔄 Initializing analyzers...")
        
        try:
            # MongoDB Analyzer
            mongo_client = pymongo.MongoClient(self.mongo_uri)
            mongo_db = mongo_client['HeroNomics']
            self.mongodb_analyzer = DNDDataAnalyzer(mongo_db)
            print("✅ MongoDB analyzer initialized")
            
            # Neo4j Analyzer
            self.neo4j_analyzer = DNDGraphAnalyzer(
                uri=self.neo4j_uri,
                user=self.neo4j_user,
                password=self.neo4j_password,
                database="heronomics"
            )
            print("✅ Neo4j analyzer initialized")
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing analyzers: {e}")
            return False

    def run_mongodb_analysis(self) -> Dict:
        """Esegue le analisi MongoDB usando l'analyzer esistente"""
        print("🔍 Running MongoDB analysis...")
        
        if not self.mongodb_analyzer:
            print("❌ MongoDB analyzer not initialized")
            return {}
        
        try:
            # Cattura risultati dalle analisi esistenti
            results = {}
            
            # 1. CLASS POWER METRICS
            print("  📊 Analyzing class power metrics...")
            
            # Esegui l'analisi esistente e cattura i risultati
            # Modifichiamo temporaneamente il metodo per restituire i dati
            original_method = self.mongodb_analyzer.analyze_class_power_metrics
            
            def capture_power_metrics():
                """Versione modificata che cattura i risultati"""
                pipeline = [
                    {"$lookup": {
                        "from": "spells",
                        "localField": "name",
                        "foreignField": "classes.name",
                        "as": "class_spells"
                    }},
                    {"$addFields": {
                        "total_spells": {"$size": "$class_spells"},
                        "unique_spells": {
                            "$size": {
                                "$filter": {
                                    "input": "$class_spells",
                                    "cond": {"$eq": [{"$size": "$$this.classes"}, 1]}
                                }
                            }
                        },
                        "high_level_spells": {
                            "$size": {
                                "$filter": {
                                    "input": "$class_spells",
                                    "cond": {"$gte": ["$$this.level", 6]}
                                }
                            }
                        },
                        "damage_spells": {
                            "$size": {
                                "$filter": {
                                    "input": "$class_spells",
                                    "cond": {"$ne": ["$$this.damage", None]}
                                }
                            }
                        },
                        "utility_spells": {
                            "$size": {
                                "$filter": {
                                    "input": "$class_spells",
                                    "cond": {"$eq": ["$$this.damage", None]}
                                }
                            }
                        },
                        "proficiency_count": {"$size": {"$ifNull": ["$proficiencies", []]}},
                        "saving_throw_count": {"$size": {"$ifNull": ["$saving_throws", []]}},
                        "base_survivability": "$hit_die"
                    }},
                    {"$addFields": {
                        "power_score": {
                            "$add": [
                                {"$multiply": ["$damage_spells", 1.5]},
                                {"$multiply": ["$high_level_spells", 2.0]},
                                {"$multiply": ["$unique_spells", 1.2]}
                            ]
                        },
                        "survivability_score": {
                            "$add": [
                                {"$multiply": ["$hit_die", 3]},
                                {"$multiply": ["$saving_throw_count", 2]},
                                {"$multiply": ["$proficiency_count", 0.5]}
                            ]
                        },
                        "versatility_score": {
                            "$add": [
                                {"$multiply": ["$utility_spells", 1.0]},
                                {"$multiply": ["$proficiency_count", 1.5]},
                                {"$multiply": [{"$divide": ["$total_spells", 10]}, 1.0]}
                            ]
                        },
                        "specialization_ratio": {
                            "$cond": [
                                {"$gt": ["$total_spells", 0]},
                                {"$divide": ["$unique_spells", "$total_spells"]},
                                0
                            ]
                        }
                    }},
                    {"$addFields": {
                        "overall_performance": {
                            "$add": [
                                {"$multiply": ["$power_score", 0.4]},
                                {"$multiply": ["$survivability_score", 0.3]},
                                {"$multiply": ["$versatility_score", 0.3]}
                            ]
                        }
                    }},
                    {"$sort": {"overall_performance": -1}}
                ]
                
                return list(self.mongodb_analyzer.db.classes.aggregate(pipeline))
            
            class_power_results = capture_power_metrics()
            
            # Organizza i risultati per classe
            class_metrics = {}
            for class_data in class_power_results:
                name = class_data["name"]
                class_metrics[name] = {
                    'power_score': class_data.get("power_score", 0),
                    'survivability_score': class_data.get("survivability_score", 0),
                    'versatility_score': class_data.get("versatility_score", 0),
                    'specialization_ratio': class_data.get("specialization_ratio", 0),
                    'overall_performance': class_data.get("overall_performance", 0),
                    'total_spells': class_data.get("total_spells", 0),
                    'hit_die': class_data.get("hit_die", 6),
                    'proficiency_count': class_data.get("proficiency_count", 0),
                    'saving_throw_count': class_data.get("saving_throw_count", 0)
                }
            
            results['class_power_metrics'] = class_metrics
            
            # 2. RESOURCE DEPENDENCIES
            print("  🔗 Analyzing resource dependencies...")
            
            dependency_pipeline = [
                {"$lookup": {
                    "from": "spells",
                    "localField": "name",
                    "foreignField": "classes.name",
                    "as": "class_spells"
                }},
                {"$addFields": {
                    "material_dependent_spells": {
                        "$size": {
                            "$filter": {
                                "input": "$class_spells",
                                "cond": {"$in": ["M", {"$ifNull": ["$$this.components", []]}]}
                            }
                        }
                    },
                    "concentration_spells": {
                        "$size": {
                            "$filter": {
                                "input": "$class_spells",
                                "cond": {"$eq": ["$$this.concentration", True]}
                            }
                        }
                    },
                    "total_spells": {"$size": "$class_spells"}
                }},
                {"$addFields": {
                    "resource_efficiency": {
                        "$cond": [
                            {"$gt": ["$total_spells", 0]},
                            {"$subtract": [1, {"$divide": ["$material_dependent_spells", "$total_spells"]}]},
                            1
                        ]
                    },
                    "concentration_dependency": {
                        "$cond": [
                            {"$gt": ["$total_spells", 0]},
                            {"$divide": ["$concentration_spells", "$total_spells"]},
                            0
                        ]
                    }
                }}
            ]
            
            dependency_results = list(self.mongodb_analyzer.db.classes.aggregate(dependency_pipeline))
            
            # Aggiungi dependency metrics ai risultati esistenti
            for dep_data in dependency_results:
                name = dep_data["name"]
                if name in class_metrics:
                    class_metrics[name].update({
                        'resource_efficiency': dep_data.get("resource_efficiency", 1.0),
                        'concentration_dependency': dep_data.get("concentration_dependency", 0.0),
                        'material_dependent_spells': dep_data.get("material_dependent_spells", 0)
                    })
            
            self.mongodb_results = results
            print(f"✅ MongoDB analysis complete: {len(class_metrics)} classes analyzed")
            return results
            
        except Exception as e:
            print(f"❌ Error in MongoDB analysis: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def run_neo4j_analysis(self) -> Dict:
        """Esegue le analisi Neo4j usando l'analyzer esistente"""
        print("🔍 Running Neo4j network analysis...")
        
        if not self.neo4j_analyzer:
            print("❌ Neo4j analyzer not initialized")
            return {}
        
        try:
            results = {}
            
            # 1. CENTRALITY ANALYSIS
            print("  📊 Analyzing network centrality...")
            
            with self.neo4j_analyzer.driver.session() as session:
                # Degree Centrality - classi con più spell
                class_centrality = session.run("""
                    MATCH (c:Class)-[:CAN_CAST]->(s:Spell)
                    WITH c, count(s) as spell_count
                    ORDER BY spell_count DESC
                    RETURN c.name as class_name, spell_count,
                           round(spell_count * 1.0 / 319 * 100, 2) as network_influence
                """).data()
                
                # Bridge Analysis - spell che collegano classi diverse
                bridge_analysis = session.run("""
                    MATCH (c1:Class)-[:CAN_CAST]->(s:Spell)<-[:CAN_CAST]-(c2:Class)
                    WHERE c1.name < c2.name
                    WITH c1.name as class1, c2.name as class2, count(s) as shared_spells
                    MATCH (c:Class {name: class1})
                    WITH c, count(*) as bridge_connections
                    RETURN c.name as class_name, bridge_connections
                    UNION
                    MATCH (c1:Class)-[:CAN_CAST]->(s:Spell)<-[:CAN_CAST]-(c2:Class)
                    WHERE c1.name < c2.name
                    WITH c1.name as class1, c2.name as class2, count(s) as shared_spells
                    MATCH (c:Class {name: class2})
                    WITH c, count(*) as bridge_connections
                    RETURN c.name as class_name, bridge_connections
                """).data()
                
                # Synergy Analysis
                synergy_analysis = session.run("""
                    MATCH (c1:Class)-[:CAN_CAST]->(s:Spell)<-[:CAN_CAST]-(c2:Class)
                    WHERE c1.name <> c2.name
                    WITH c1, count(DISTINCT c2) as synergy_partners
                    RETURN c1.name as class_name, synergy_partners
                """).data()
            
            # Organizza i risultati di rete
            network_metrics = {}
            
            # Processa centrality
            for item in class_centrality:
                name = item['class_name']
                network_metrics[name] = {
                    'centrality_score': item['spell_count'] / 100.0,  # Normalizzato
                    'network_influence': item['network_influence'],
                    'bridge_connections': 0,
                    'synergy_partnerships': 0
                }
            
            # Processa bridge connections
            bridge_dict = {}
            for item in bridge_analysis:
                name = item['class_name']
                if name in bridge_dict:
                    bridge_dict[name] += item['bridge_connections']
                else:
                    bridge_dict[name] = item['bridge_connections']
            
            for name, bridges in bridge_dict.items():
                if name in network_metrics:
                    network_metrics[name]['bridge_connections'] = bridges
            
            # Processa synergy partnerships
            for item in synergy_analysis:
                name = item['class_name']
                if name in network_metrics:
                    network_metrics[name]['synergy_partnerships'] = item['synergy_partners']
            
            results['network_metrics'] = network_metrics
            
            self.neo4j_results = results
            print(f"✅ Neo4j analysis complete: {len(network_metrics)} classes analyzed")
            return results
            
        except Exception as e:
            print(f"❌ Error in Neo4j analysis: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def calculate_beta(self, class_name: str) -> float:
        """
        Calcola il Beta usando le metriche di potere e volatilità della classe
        Beta = (Variabilità della classe / Variabilità del mercato) * Correlazione
        Formula deterministica basata sui dati reali
        """
        if class_name not in self.mongodb_results.get('class_power_metrics', {}):
            return 1.0  # Beta neutro se non ci sono dati
        
        metrics = self.mongodb_results['class_power_metrics'][class_name]
        network_data = self.neo4j_results.get('network_metrics', {}).get(class_name, {})
        
        # Calcola variabilità basata su specialization ratio (più alto = più volatile)
        specialization = metrics.get('specialization_ratio', 0.5)
        
        # Calcola stabilità da versatility e survivability (più alto = meno volatile)
        versatility = metrics.get('versatility_score', 0) / 50.0  # Normalizza
        survivability = metrics.get('survivability_score', 0) / 40.0  # Normalizza
        
        # Network influence (più connessa = meno volatile)
        network_influence = network_data.get('network_influence', 0) / 25.0  # Normalizza
        
        # Formula deterministica per Beta
        # Beta = 1.0 + specialization_effect - stability_effect
        specialization_effect = specialization * 1.5  # Range 0-1.5
        stability_effect = (versatility + survivability + network_influence) / 3 * 0.8  # Range 0-0.8
        
        beta = 1.0 + specialization_effect - stability_effect
        
        # Normalizza Beta tra 0.3 e 2.5
        beta = max(0.3, min(2.5, beta))
        
        return round(beta, 3)

    def calculate_outstanding_shares(self, class_name: str) -> int:
        """
        Calcola le azioni in circolazione basate su popolarità/accessibilità
        """
        base_shares = self.base_share_count
        
        # MongoDB metrics
        mongodb_data = self.mongodb_results.get('class_power_metrics', {}).get(class_name, {})
        hit_die = mongodb_data.get('hit_die', 6)
        total_spells = mongodb_data.get('total_spells', 0)
        
        # Neo4j network metrics
        network_data = self.neo4j_results.get('network_metrics', {}).get(class_name, {})
        network_influence = network_data.get('network_influence', 0)
        synergy_partnerships = network_data.get('synergy_partnerships', 0)
        
        # Fattore accessibilità (classi più semplici = più azioni)
        accessibility_factor = (hit_die / 12.0) + (total_spells / 100.0)
        
        # Fattore popolarità di rete
        popularity_factor = (network_influence / 25.0) + (synergy_partnerships / 10.0)
        
        # Calcola shares totali
        total_factor = 1.0 + accessibility_factor + popularity_factor
        outstanding_shares = int(base_shares * total_factor)
        
        return max(500000, min(5000000, outstanding_shares))

    def calculate_capm_price(self, class_name: str) -> float:
        """
        Calcola il prezzo base usando CAPM
        Stock Price = Risk-Free Rate + Beta × (Market Risk Premium)
        Poi lo scala per ottenere prezzi realistici
        """
        beta = self.calculate_beta(class_name)
        
        # CAPM formula
        expected_return = self.risk_free_rate + beta * self.market_risk_premium
        
        # Converti return in prezzo base (scaling factor)
        base_price = 50.0 + (expected_return * 1000)
        
        # Aggiungi fattori di performance
        mongodb_data = self.mongodb_results.get('class_power_metrics', {}).get(class_name, {})
        performance_multiplier = 1.0 + (mongodb_data.get('overall_performance', 0) / 100.0)
        
        final_price = base_price * performance_multiplier
        
        return round(final_price, 2)

    def calculate_earnings_per_share(self, class_name: str) -> float:
        """
        Calcola EPS basato sull'efficacia complessiva della classe
        """
        mongodb_data = self.mongodb_results.get('class_power_metrics', {}).get(class_name, {})
        network_data = self.neo4j_results.get('network_metrics', {}).get(class_name, {})
        
        # "Earnings" basati su performance e efficienza
        power_earnings = mongodb_data.get('power_score', 0) * 0.1
        survival_earnings = mongodb_data.get('survivability_score', 0) * 0.08
        utility_earnings = mongodb_data.get('versatility_score', 0) * 0.06
        network_earnings = network_data.get('network_influence', 0) * 0.05
        
        total_earnings = power_earnings + survival_earnings + utility_earnings + network_earnings
        
        # Dividi per outstanding shares (in milioni)
        outstanding_shares_millions = self.calculate_outstanding_shares(class_name) / 1000000
        eps = total_earnings / outstanding_shares_millions
        
        return round(eps, 2)

    def calculate_annual_dividends(self, class_name: str) -> float:
        """
        Calcola dividendi annuali basati sui benefici costanti della classe
        """
        mongodb_data = self.mongodb_results.get('class_power_metrics', {}).get(class_name, {})
        
        # Dividendi basati su stabilità e utility
        base_dividend = mongodb_data.get('survivability_score', 0) * 0.02
        utility_dividend = mongodb_data.get('versatility_score', 0) * 0.015
        resource_efficiency = mongodb_data.get('resource_efficiency', 1.0)
        
        # Classi più efficienti pagano dividendi più alti
        total_dividend = (base_dividend + utility_dividend) * resource_efficiency
        
        return round(total_dividend, 2)

    def generate_price_history(self, base_price: float, beta: float, class_name: str, days: int = 30) -> List[Dict]:
        """
        Genera storico prezzi deterministico basato sulle metriche della classe
        No randomizzazione - tutto basato sui dati reali
        """
        history = []
        
        # Ottieni metriche per calcoli deterministici
        mongodb_data = self.mongodb_results.get('class_power_metrics', {}).get(class_name, {})
        network_data = self.neo4j_results.get('network_metrics', {}).get(class_name, {})
        
        # Parametri deterministici basati sui dati
        overall_performance = mongodb_data.get('overall_performance', 0)
        specialization_ratio = mongodb_data.get('specialization_ratio', 0)
        network_influence = network_data.get('network_influence', 0)
        
        # Trend deterministico basato sulla performance
        # Classi migliori hanno trend leggermente positivo
        daily_trend = (overall_performance - 25) / 10000  # Range appross. -0.0025 to +0.0025
        
        # Volatilità basata su specialization e beta
        daily_volatility = (specialization_ratio * beta * 0.01)  # Range 0-0.025 circa
        
        current_price = base_price
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            
            # Movimento deterministico basato su:
            # 1. Trend generale della classe
            # 2. Pattern ciclico basato sul giorno (simula cicli di mercato)
            # 3. Volatilità basata sulle caratteristiche della classe
            
            # Componente trend
            trend_component = daily_trend
            
            # Componente ciclica deterministica (simula cicli di mercato)
            cycle_component = math.sin(2 * math.pi * i / 7) * daily_volatility * 0.5  # Ciclo settimanale
            
            # Componente di volatilità deterministico basato su caratteristiche classe
            # Usa hash del nome per creare "pseudo-randomness" deterministica
            seed_value = hash(class_name + str(i)) % 10000 / 10000  # 0-1
            volatility_component = (seed_value - 0.5) * daily_volatility * 2
            
            # Movimento totale
            price_change = trend_component + cycle_component + volatility_component
            current_price *= (1 + price_change)
            
            # Evita prezzi troppo estremi
            current_price = max(base_price * 0.7, min(base_price * 1.4, current_price))
            
            # Volume deterministico basato su network influence e performance
            base_volume = 30000
            volume_multiplier = 1.0 + (network_influence / 50.0) + (overall_performance / 200.0)
            # Variazione volume deterministica
            volume_variation = math.sin(2 * math.pi * i / 5) * 0.3  # Ciclo di 5 giorni
            volume = int(base_volume * volume_multiplier * (1 + volume_variation))
            volume = max(10000, volume)
            
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "price": round(current_price, 2),
                "volume": volume
            })
        
        return history

    def determine_market_sentiment(self, metrics: Dict) -> str:
        """Determina il sentiment di mercato basato sui dati reali"""
        overall_performance = metrics.get('overall_performance', 0)
        versatility_score = metrics.get('versatility_score', 0)
        power_score = metrics.get('power_score', 0)
        
        # Calcola sentiment score combinato
        sentiment_score = (overall_performance * 0.5) + (versatility_score * 0.3) + (power_score * 0.2)
        
        if sentiment_score >= 35:
            return "Bullish"
        elif sentiment_score >= 25:
            return "Neutral"
        else:
            return "Bearish"

    def determine_analyst_rating(self, financial_metrics: Dict, class_data: Dict) -> str:
        """Determina il rating degli analisti basato sui dati reali"""
        pe_ratio = financial_metrics.get('pe_ratio', 15)
        dividend_yield = financial_metrics.get('dividend_yield', 0)
        overall_performance = class_data.get('overall_performance', 0)
        resource_efficiency = class_data.get('resource_efficiency', 1.0)
        
        # Score composito per rating
        rating_score = 0
        
        # Valuation factors
        if pe_ratio < 12:
            rating_score += 2
        elif pe_ratio < 18:
            rating_score += 1
        elif pe_ratio > 25:
            rating_score -= 1
        
        # Dividend factors  
        if dividend_yield > 4:
            rating_score += 2
        elif dividend_yield > 2:
            rating_score += 1
        
        # Performance factors
        if overall_performance > 30:
            rating_score += 2
        elif overall_performance > 25:
            rating_score += 1
        elif overall_performance < 15:
            rating_score -= 1
        
        # Efficiency factors
        if resource_efficiency > 0.8:
            rating_score += 1
        elif resource_efficiency < 0.5:
            rating_score -= 1
        
        # Determina rating finale
        if rating_score >= 5:
            return "Strong Buy"
        elif rating_score >= 3:
            return "Buy"
        elif rating_score >= 1:
            return "Hold"
        elif rating_score >= -1:
            return "Weak Hold"
        else:
            return "Sell"

    def create_class_stock(self, class_name: str) -> Optional[ClassFinancialMetrics]:
        """Crea un oggetto ClassFinancialMetrics completo"""
        if class_name not in self.mongodb_results.get('class_power_metrics', {}):
            return None
        
        # Dati MongoDB
        mongodb_data = self.mongodb_results['class_power_metrics'][class_name]
        
        # Dati Neo4j
        network_data = self.neo4j_results.get('network_metrics', {}).get(class_name, {
            'centrality_score': 0.5,
            'bridge_connections': 0,
            'network_influence': 0,
            'synergy_partnerships': 0
        })
        
        # Calcoli finanziari
        beta = self.calculate_beta(class_name)
        base_price = self.calculate_capm_price(class_name)
        outstanding_shares = self.calculate_outstanding_shares(class_name)
        annual_dividends = self.calculate_annual_dividends(class_name)
        eps = self.calculate_earnings_per_share(class_name)
        
        # Metriche derivate
        market_cap = base_price * outstanding_shares
        dividend_yield = (annual_dividends / base_price) * 100 if base_price > 0 else 0
        pe_ratio = base_price / eps if eps > 0 else 0
        
        # Genera storico prezzi deterministico
        price_history = self.generate_price_history(base_price, beta, class_name)
        current_price = price_history[-1]['price']
        previous_price = price_history[-2]['price'] if len(price_history) > 1 else current_price
        
        # Calcola variazioni giornaliere
        daily_change = current_price - previous_price
        daily_change_percent = (daily_change / previous_price) * 100 if previous_price > 0 else 0
        
        # Volume giornaliero deterministico
        volume = price_history[-1]['volume']
        
        # Sentiment e rating basati sui dati reali
        market_sentiment = self.determine_market_sentiment(mongodb_data)
        analyst_rating = self.determine_analyst_rating({
            'pe_ratio': pe_ratio,
            'dividend_yield': dividend_yield
        }, mongodb_data)
        
        return ClassFinancialMetrics(
            name=class_name,
            symbol=class_name[:3].upper(),
            
            # MongoDB metrics
            power_score=mongodb_data.get('power_score', 0),
            survivability_score=mongodb_data.get('survivability_score', 0),
            versatility_score=mongodb_data.get('versatility_score', 0),
            specialization_ratio=mongodb_data.get('specialization_ratio', 0),
            overall_performance=mongodb_data.get('overall_performance', 0),
            
            # Neo4j metrics
            centrality_score=network_data['centrality_score'],
            bridge_connections=network_data['bridge_connections'],
            network_influence=network_data['network_influence'],
            synergy_partnerships=network_data['synergy_partnerships'],
            
            # Financial metrics
            beta=beta,
            risk_free_rate=self.risk_free_rate,
            market_risk_premium=self.market_risk_premium,
            base_stock_price=base_price,
            outstanding_shares=outstanding_shares,
            market_cap=market_cap,
            annual_dividends=annual_dividends,
            dividend_yield=dividend_yield,
            earnings_per_share=eps,
            pe_ratio=pe_ratio,
            
            # Market data
            current_price=current_price,
            daily_change=daily_change,
            daily_change_percent=daily_change_percent,
            volume=volume,
            price_history=price_history,
            market_sentiment=market_sentiment,
            analyst_rating=analyst_rating
        )

    def calculate_market_indices(self):
        """Calcola gli indici di mercato in modo deterministico"""
        if not self.class_stocks:
            return
        
        all_stocks = list(self.class_stocks.values())
        
        # DND_500 - Indice generale (weighted by market cap)
        total_market_cap = sum(stock.market_cap for stock in all_stocks)
        weighted_change = sum(
            (stock.market_cap / total_market_cap) * stock.daily_change_percent 
            for stock in all_stocks
        ) if total_market_cap > 0 else 0
        
        self.market_indices['DND_500']['change'] = round(weighted_change, 2)
        self.market_indices['DND_500']['value'] = round(
            100.0 * (1 + weighted_change / 100), 2
        )
        
        # CASTER_INDEX - Classi magiche
        caster_classes = ['Wizard', 'Sorcerer', 'Warlock', 'Bard', 'Cleric', 'Druid']
        caster_stocks = [stock for stock in all_stocks if stock.name in caster_classes]
        
        if caster_stocks:
            caster_market_cap = sum(stock.market_cap for stock in caster_stocks)
            caster_weighted_change = sum(
                (stock.market_cap / caster_market_cap) * stock.daily_change_percent 
                for stock in caster_stocks
            ) if caster_market_cap > 0 else 0
            
            self.market_indices['CASTER_INDEX']['change'] = round(caster_weighted_change, 2)
            self.market_indices['CASTER_INDEX']['value'] = round(
                100.0 * (1 + caster_weighted_change / 100), 2
            )
        
        # MARTIAL_INDEX - Classi marziali
        martial_classes = ['Fighter', 'Barbarian', 'Ranger', 'Paladin', 'Rogue', 'Monk']
        martial_stocks = [stock for stock in all_stocks if stock.name in martial_classes]
        
        if martial_stocks:
            martial_market_cap = sum(stock.market_cap for stock in martial_stocks)
            martial_weighted_change = sum(
                (stock.market_cap / martial_market_cap) * stock.daily_change_percent 
                for stock in martial_stocks
            ) if martial_market_cap > 0 else 0
            
            self.market_indices['MARTIAL_INDEX']['change'] = round(martial_weighted_change, 2)
            self.market_indices['MARTIAL_INDEX']['value'] = round(
                100.0 * (1 + martial_weighted_change / 100), 2
            )

    def generate_market_news(self, stock: ClassFinancialMetrics) -> List[str]:
        """Genera notizie di mercato basate sulle metriche reali"""
        news_items = []
        
        # News basate su performance
        if stock.daily_change_percent > 5:
            news_items.append(f"{stock.name} Corp surges {stock.daily_change_percent:.1f}% on strong quarterly performance metrics")
        elif stock.daily_change_percent < -5:
            news_items.append(f"{stock.symbol} falls {abs(stock.daily_change_percent):.1f}% amid concerns over class balance updates")
        
        # News basate su PE ratio
        if stock.pe_ratio > 25:
            news_items.append(f"Analysts question {stock.name}'s high valuation with P/E ratio at {stock.pe_ratio:.1f}")
        elif stock.pe_ratio < 10:
            news_items.append(f"{stock.symbol} trading at attractive valuation, P/E ratio of {stock.pe_ratio:.1f}")
        
        # News basate su dividend yield
        if stock.dividend_yield > 4:
            news_items.append(f"{stock.name} offers attractive {stock.dividend_yield:.1f}% dividend yield for income investors")
        
        # News basate su network metrics
        if stock.synergy_partnerships > 8:
            news_items.append(f"{stock.name} benefits from strong multiclass synergy partnerships ({stock.synergy_partnerships} active)")
        
        # News basate su beta
        if stock.beta > 2.0:
            news_items.append(f"Volatility warning: {stock.symbol} shows high beta of {stock.beta}, suitable for risk-tolerant investors")
        elif stock.beta < 0.5:
            news_items.append(f"{stock.name} offers defensive characteristics with low beta of {stock.beta}")
        
        return news_items[:3]  # Massimo 3 news per stock

    def create_market_report(self) -> Dict:
        """Crea un report completo del mercato con analisi finanziarie"""
        if not self.class_stocks:
            return {}
        
        stocks = list(self.class_stocks.values())
        
        # Market summary
        total_stocks = len(stocks)
        gainers = [s for s in stocks if s.daily_change > 0]
        losers = [s for s in stocks if s.daily_change < 0]
        unchanged = total_stocks - len(gainers) - len(losers)
        
        # Top performers
        top_performer = max(stocks, key=lambda x: x.daily_change_percent)
        worst_performer = min(stocks, key=lambda x: x.daily_change_percent)
        
        # Valuation metrics
        avg_pe = np.mean([s.pe_ratio for s in stocks if s.pe_ratio > 0])
        avg_dividend_yield = np.mean([s.dividend_yield for s in stocks])
        total_market_cap = sum(s.market_cap for s in stocks)
        
        # Risk metrics
        avg_beta = np.mean([s.beta for s in stocks])
        high_beta_stocks = [s for s in stocks if s.beta > 1.5]
        low_beta_stocks = [s for s in stocks if s.beta < 0.8]
        
        # Sector analysis
        caster_stocks = [s for s in stocks if s.name in ['Wizard', 'Sorcerer', 'Warlock', 'Bard', 'Cleric', 'Druid']]
        martial_stocks = [s for s in stocks if s.name in ['Fighter', 'Barbarian', 'Ranger', 'Paladin', 'Rogue', 'Monk']]
        
        caster_avg_return = np.mean([s.daily_change_percent for s in caster_stocks]) if caster_stocks else 0
        martial_avg_return = np.mean([s.daily_change_percent for s in martial_stocks]) if martial_stocks else 0
        
        return {
            "market_summary": {
                "total_stocks": total_stocks,
                "gainers": len(gainers),
                "losers": len(losers),
                "unchanged": unchanged,
                "total_market_cap": f"${total_market_cap:,.0f}",
                "avg_pe_ratio": round(avg_pe, 1),
                "avg_dividend_yield": f"{avg_dividend_yield:.2f}%",
                "avg_beta": round(avg_beta, 2)
            },
            "market_indices": self.market_indices,
            "top_performer": {
                "name": top_performer.name,
                "symbol": top_performer.symbol,
                "change_percent": top_performer.daily_change_percent,
                "price": top_performer.current_price,
                "volume": top_performer.volume,
                "market_cap": f"${top_performer.market_cap:,.0f}"
            },
            "worst_performer": {
                "name": worst_performer.name,
                "symbol": worst_performer.symbol,
                "change_percent": worst_performer.daily_change_percent,
                "price": worst_performer.current_price,
                "volume": worst_performer.volume,
                "market_cap": f"${worst_performer.market_cap:,.0f}"
            },
            "sector_performance": {
                "caster_avg_return": f"{caster_avg_return:.1f}%",
                "martial_avg_return": f"{martial_avg_return:.1f}%",
                "caster_count": len(caster_stocks),
                "martial_count": len(martial_stocks)
            },
            "risk_analysis": {
                "high_beta_count": len(high_beta_stocks),
                "low_beta_count": len(low_beta_stocks),
                "high_beta_stocks": [{"name": s.name, "beta": s.beta} for s in high_beta_stocks[:3]],
                "defensive_stocks": [{"name": s.name, "beta": s.beta} for s in low_beta_stocks[:3]]
            },
            "valuation_insights": {
                "undervalued_stocks": [
                    {"name": s.name, "pe": s.pe_ratio, "dividend_yield": f"{s.dividend_yield:.1f}%"} 
                    for s in sorted(stocks, key=lambda x: x.pe_ratio)[:3] if s.pe_ratio > 0
                ],
                "high_dividend_stocks": [
                    {"name": s.name, "dividend_yield": f"{s.dividend_yield:.1f}%", "price": s.current_price}
                    for s in sorted(stocks, key=lambda x: x.dividend_yield, reverse=True)[:3]
                ]
            },
            "generated_at": datetime.now().isoformat()
        }

    def save_market_data(self) -> bool:
        """Salva tutti i dati di mercato in formato JSON"""
        try:
            # Crea directory se non esiste
            os.makedirs('market_data', exist_ok=True)
            
            # Converti stocks in formato serializzabile
            stocks_data = {}
            for symbol, stock in self.class_stocks.items():
                stock_dict = asdict(stock)
                
                # Aggiungi news generate
                stock_dict['market_news'] = self.generate_market_news(stock)
                
                stocks_data[symbol] = stock_dict
            
            # Salva stocks dettagliati
            with open('market_data/financial_stocks.json', 'w') as f:
                json.dump(stocks_data, f, indent=2, default=str)
            print("💾 Saved: marked_data/financial_stocks.json")
            
            # Salva market report
            market_report = self.create_market_report()
            with open('market_data/market_report.json', 'w') as f:
                json.dump(market_report, f, indent=2, default=str)
            print("💾 Saved: market_data/market_report.json")
            
            # Salva summary per dashboard
            summary_data = {
                "last_updated": datetime.now().isoformat(),
                "market_indices": self.market_indices,
                "stock_count": len(self.class_stocks),
                "top_stocks": [
                    {
                        "name": stock.name,
                        "symbol": stock.symbol,
                        "price": stock.current_price,
                        "change": stock.daily_change_percent,
                        "market_cap": stock.market_cap,
                        "pe_ratio": stock.pe_ratio,
                        "dividend_yield": stock.dividend_yield
                    }
                    for stock in sorted(self.class_stocks.values(), 
                                      key=lambda x: x.daily_change_percent, reverse=True)[:5]
                ]
            }
            
            with open('market_data/market_summary.json', 'w') as f:
                json.dump(summary_data, f, indent=2, default=str)
            print("💾 Saved: market_data/market_summary.json")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving market data: {e}")
            import traceback
            traceback.print_exc()
            return False

    def print_market_overview(self):
        """Stampa una panoramica del mercato"""
        if not self.class_stocks:
            print("❌ No market data available")
            return
        
        print("\n" + "="*80)
        print("🏛️  D&D ADVENTURER'S STOCK EXCHANGE - MARKET OVERVIEW")
        print("="*80)
        
        # Market indices
        print("\n📊 MARKET INDICES:")
        for index_name, data in self.market_indices.items():
            change_emoji = "📈" if data['change'] >= 0 else "📉"
            print(f"  {index_name}: {data['value']:.2f} {change_emoji} {data['change']:+.2f}%")
        
        # Top performers
        sorted_stocks = sorted(self.class_stocks.values(), key=lambda x: x.daily_change_percent, reverse=True)
        
        print(f"\n🏆 TOP 5 PERFORMING STOCKS:")
        print(f"{'Symbol':<6} {'Name':<10} {'Price':<8} {'Change':<8} {'Volume':<10} {'P/E':<6} {'Div%':<6}")
        print("-" * 65)
        
        for stock in sorted_stocks[:5]:
            change_emoji = "📈" if stock.daily_change_percent >= 0 else "📉"
            print(f"{stock.symbol:<6} {stock.name:<10} ${stock.current_price:<7.2f} "
                  f"{change_emoji}{stock.daily_change_percent:+5.1f}% {stock.volume:<10,} "
                  f"{stock.pe_ratio:<6.1f} {stock.dividend_yield:<6.1f}%")
        
        print(f"\n📉 WORST 3 PERFORMING STOCKS:")
        for stock in sorted_stocks[-3:]:
            change_emoji = "📉"
            print(f"{stock.symbol:<6} {stock.name:<10} ${stock.current_price:<7.2f} "
                  f"{change_emoji}{stock.daily_change_percent:+5.1f}% {stock.volume:<10,} "
                  f"{stock.pe_ratio:<6.1f} {stock.dividend_yield:<6.1f}%")
        
        # Market stats
        total_market_cap = sum(s.market_cap for s in self.class_stocks.values())
        avg_pe = np.mean([s.pe_ratio for s in self.class_stocks.values() if s.pe_ratio > 0])
        avg_dividend = np.mean([s.dividend_yield for s in self.class_stocks.values()])
        
        print(f"\n💰 MARKET STATISTICS:")
        print(f"  Total Market Cap: ${total_market_cap:,.0f}")
        print(f"  Average P/E Ratio: {avg_pe:.1f}")
        print(f"  Average Dividend Yield: {avg_dividend:.2f}%")
        print(f"  Number of Stocks: {len(self.class_stocks)}")

    def run_simulation(self) -> bool:
        """Esegue la simulazione completa del mercato"""
        print("🏛️  === D&D ADVENTURER'S STOCK EXCHANGE - FINANCIAL MARKET SIMULATOR ===")
        print("📈 Using CAPM, Market Cap, Dividend Yield, and P/E Ratio models")
        
        # 1. Inizializza analyzer
        if not self.initialize_analyzers():
            return False
        
        # 2. Esegui analisi MongoDB
        if not self.run_mongodb_analysis():
            print("❌ Failed to run MongoDB analysis")
            return False
        
        # 3. Esegui analisi Neo4j
        if not self.run_neo4j_analysis():
            print("❌ Failed to run Neo4j analysis")
            return False
        
        # 4. Crea stocks per ogni classe
        print("\n📈 Creating financial instruments...")
        
        class_names = list(self.mongodb_results.get('class_power_metrics', {}).keys())
        successful_stocks = 0
        
        for class_name in class_names:
            try:
                stock = self.create_class_stock(class_name)
                if stock:
                    self.class_stocks[stock.symbol] = stock
                    successful_stocks += 1
                    print(f"✅ Created: {stock.symbol} - {stock.name} "
                          f"(${stock.current_price:.2f}, β={stock.beta:.2f}, P/E={stock.pe_ratio:.1f})")
            except Exception as e:
                print(f"⚠️  Failed to create stock for {class_name}: {e}")
        
        if successful_stocks == 0:
            print("❌ No stocks created successfully")
            return False
        
        # 5. Calcola indici di mercato
        print(f"\n📊 Calculating market indices...")
        self.calculate_market_indices()
        
        # 6. Salva tutti i dati
        print(f"\n💾 Saving market data...")
        if not self.save_market_data():
            return False
        
        # 7. Mostra panoramica
        self.print_market_overview()
        
        print(f"\n🎯 Financial market simulation completed!")
        print(f"💡 Created {successful_stocks} stocks using real D&D data and financial models")
        print(f"📂 Data saved in /data/ directory for dashboard visualization")
        
        return True

# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    """Funzione principale"""
    print("D&D 5e Financial Market Simulator")
    print("=================================")
    
    # Parametri di connessione (modifica se necessario)
    simulator = AdvancedDnDMarketSimulator(
        mongo_uri="mongodb://localhost:27017/",
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="admin123"
    )
    
    # Esegui simulazione
    success = simulator.run_simulation()
    
    if success:
        print("\n✅ Simulation completed successfully!")
        print("📊 Check data/financial_stocks.json for detailed stock data")
        print("📈 Check data/market_report.json for market analysis")
        print("📂 Check data/market_summary.json for dashboard data")
    else:
        print("\n❌ Simulation failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())