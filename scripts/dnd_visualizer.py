import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import pymongo
from neo4j import GraphDatabase
import numpy as np
from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as mpatches
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

# Import analyzer classes
from mongodb_analyzer import DNDDataAnalyzer
from neo4j_analyzer import DNDGraphAnalyzer

class DNDEnhancedVisualizer:
    """
    Visualizzatore D&D che usa le funzioni degli analyzer esistenti
    """
    
    def __init__(self, 
                 mongo_uri="mongodb://localhost:27017/", 
                 mongo_db="HeroNomics",
                 neo4j_uri="bolt://localhost:7687", 
                 neo4j_user="neo4j", 
                 neo4j_password="admin123",
                 neo4j_database="heronomics"):
        
        self.output_dir = "site/dnd_images"
        self.ensure_output_dirs()
        
        # Setup databases
        self.setup_databases(mongo_uri, mongo_db, neo4j_uri, neo4j_user, neo4j_password, neo4j_database)
        
        # Inizializza gli analyzer
        self.mongo_analyzer = DNDDataAnalyzer(self.mongo_db) if self.mongo_db is not None else None
        self.neo4j_analyzer = DNDGraphAnalyzer(neo4j_uri, neo4j_user, neo4j_password, neo4j_database) if self.neo4j_driver is not None else None
        
        # Styling con colori pastello e background bianco
        self.setup_fancy_styling()

    def setup_databases(self, mongo_uri, mongo_db, neo4j_uri, neo4j_user, neo4j_password, neo4j_database):
        """Inizializza connessioni ai database"""
        try:
            # MongoDB connection
            self.mongo_client = pymongo.MongoClient(mongo_uri)
            self.mongo_db = self.mongo_client[mongo_db]
            print("✓ Connected to MongoDB")
            
            # Neo4j connection
            self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password), database=neo4j_database)
            print("✓ Connected to Neo4j")
            
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            self.mongo_client = None
            self.mongo_db = None
            self.neo4j_driver = None

    def setup_fancy_styling(self):
        """Setup styling moderno con sfondo bianco e colori pastello"""
        plt.style.use('default')
        sns.set_style("whitegrid")
        
        # Pastel color palettes - soft and fancy
        self.color_palettes = {
            'primary': ['#FFB6C1', '#98FB98', '#87CEEB', '#DDA0DD', '#F0E68C', '#FFA07A', '#20B2AA', '#FFE4B5'],
            'secondary': ['#F8BBD9', '#B5EAD7', '#C7CEEA', '#FFDAC1', '#E2F0CB', '#C1E1C5', '#FAD2E1', '#BEE1E6'],
            'network': ['#FF9999', '#66D9EF', '#C5E1A5', '#FFCC80', '#CE93D8', '#80DEEA', '#FFAB91', '#A5D6A7'],
            'gradient_pastels': ['#FF6B9D', '#C44569', '#F8B500', '#6C5CE7', '#00CEC9', '#55A3FF', '#FD79A8', '#FDCB6E'],
            'soft_blues': ['#E3F2FD', '#BBDEFB', '#90CAF9', '#64B5F6', '#42A5F5', '#2196F3'],
            'soft_pinks': ['#FCE4EC', '#F8BBD9', '#F48FB1', '#F06292', '#EC407A', '#E91E63'],
            'soft_greens': ['#E8F5E8', '#C8E6C9', '#A5D6A7', '#81C784', '#66BB6A', '#4CAF50']
        }
        
        # Parametri per matplotlib per lo stile
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white', 
            'axes.edgecolor': '#CCCCCC',
            'axes.linewidth': 1.2,
            'axes.labelcolor': '#333333',
            'text.color': '#333333',
            'xtick.color': '#666666',
            'ytick.color': '#666666', 
            'grid.color': '#E0E0E0',
            'grid.alpha': 0.7,
            'font.size': 11,
            'axes.titlesize': 16,
            'axes.labelsize': 12,
            'legend.fontsize': 10,
            'figure.titlesize': 18,
            'font.family': 'sans-serif',
            'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans']
        })

    def ensure_output_dirs(self):
        """Crea le directory di output"""
        os.makedirs(self.output_dir, exist_ok=True)

    # ==========================================
    # WRAPPER METHODS FOR ANALYZER FUNCTIONS
    # ==========================================
    
    def get_class_power_data_from_analyzer(self):
        """Ottiene dati usando l'analyzer MongoDB"""
        if self.mongo_analyzer is None:
            return []
        
        # Usa la pipeline esistente dal mongodb_analyzer
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
                        {"$multiply": [{"$subtract": ["$total_spells", "$damage_spells"]}, 1.0]},
                        {"$multiply": ["$proficiency_count", 1.5]}
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
        
        try:
            return list(self.mongo_analyzer.db.classes.aggregate(pipeline))
        except Exception as e:
            print(f"Error getting class power data: {e}")
            return []

    def get_spell_class_network_data(self):
        """Ottiene dati di rete dal Neo4j analyzer"""
        if self.neo4j_analyzer is None:
            return [], []
        
        with self.neo4j_analyzer.driver.session() as session:
            # Query per centralità (dal neo4j_analyzer)
            centrality_query = """
            MATCH (c:Class)-[:CAN_CAST]->(s:Spell)
            WITH c, count(s) as spell_count
            ORDER BY spell_count DESC
            RETURN c.name as class_name, spell_count,
                   round(spell_count * 1.0 / 319 * 100, 2) as network_influence
            LIMIT 12
            """
            
            centrality_data = session.run(centrality_query).data()
            
            # Query per network (dal neo4j_analyzer)  
            network_query = """
            MATCH (c1:Class)-[:CAN_CAST]->(s:Spell)<-[:CAN_CAST]-(c2:Class)
            WHERE c1.name < c2.name
            WITH c1, c2, count(s) as shared_spells
            WHERE shared_spells > 10
            RETURN c1.name as class1, c2.name as class2, shared_spells
            ORDER BY shared_spells DESC
            LIMIT 20
            """
            
            network_data = session.run(network_query).data()
            
        return centrality_data, network_data

    # ==========================================
    # MONGODB ANALYZER VISUALIZATIONS (6)
    # ==========================================

    def plot_1_class_power_metrics(self):
        """1. Class Power & Survivability Metrics"""
        print("📊 1. Generating Class Power Metrics...")
        
        data = self.get_class_power_data_from_analyzer()
        if not data:
            print("No class data available")
            return
        
        # Create visualization - Bubble Chart
        fig, ax = plt.subplots(figsize=(14, 10))
        fig.patch.set_facecolor('white')
        
        classes = [item['name'] for item in data[:10]]
        power_scores = [item['power_score'] for item in data[:10]]
        survival_scores = [item['survivability_score'] for item in data[:10]]
        versatility_scores = [item['versatility_score'] for item in data[:10]]
        
        # Fix color array length to match data points
        colors = self.color_palettes['gradient_pastels'][:len(classes)]
        if len(colors) < len(classes):
            colors = (colors * ((len(classes) // len(colors)) + 1))[:len(classes)]
        
        scatter = ax.scatter(power_scores, survival_scores, 
                           s=[v*8 for v in versatility_scores],
                           c=colors, alpha=0.7, edgecolors='white', linewidth=2)
        
        # Add labels
        for i, class_name in enumerate(classes):
            ax.annotate(class_name, (power_scores[i], survival_scores[i]),
                       xytext=(8, 8), textcoords='offset points',
                       fontsize=10, fontweight='bold', color='#333333',
                       bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.9, 
                               edgecolor='#CCCCCC'))
        
        ax.set_xlabel('Power Score (Offensive Capability)', fontsize=12, fontweight='bold', color='#444444')
        ax.set_ylabel('Survivability Score', fontsize=12, fontweight='bold', color='#444444')
        ax.set_title('D&D Class Performance Matrix\nBubble size = Versatility Score', 
                    fontsize=16, fontweight='bold', pad=20, color='#2C3E50')
        ax.grid(alpha=0.3, color='#DDDDDD')
        ax.set_facecolor('white')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "1_class_power_metrics.png"), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def plot_2_spell_rarity_distribution(self):
        """2. Spell Rarity Distribution"""
        print("📊 2. Generating Spell Rarity Distribution...")
        
        if self.mongo_analyzer is None:
            print("No MongoDB analyzer available")
            return
        
        # Simula l'analisi di rarità
        pipeline = [
            {"$addFields": {
                "class_access_count": {"$size": {"$ifNull": ["$classes", []]}},
                "spell_level": "$level"
            }},
            {"$addFields": {
                "rarity_category": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$class_access_count", 1]}, "then": "Exclusive"},
                            {"case": {"$eq": ["$class_access_count", 2]}, "then": "Rare"},
                            {"case": {"$lte": ["$class_access_count", 4]}, "then": "Uncommon"},
                            {"case": {"$lte": ["$class_access_count", 7]}, "then": "Common"}
                        ],
                        "default": "Ubiquitous"
                    }
                }
            }},
            {"$group": {
                "_id": "$rarity_category",
                "total_spells": {"$sum": 1}
            }},
            {"$sort": {"total_spells": -1}}
        ]
        
        try:
            data = list(self.mongo_analyzer.db.spells.aggregate(pipeline))
            if not data:
                print("No spell rarity data available")
                return
            
            fig, ax = plt.subplots(figsize=(12, 8))
            fig.patch.set_facecolor('white')
            
            rarity_names = [item['_id'] for item in data]
            rarity_counts = [item['total_spells'] for item in data]
            
            colors = self.color_palettes['soft_blues'][:len(rarity_names)]
            
            wedges, texts, autotexts = ax.pie(rarity_counts, labels=rarity_names, 
                                            colors=colors, autopct='%1.1f%%',
                                            startangle=90, explode=[0.05]*len(rarity_names))
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            ax.set_title('Spell Rarity Distribution\nMarket Share Analysis', 
                        fontsize=16, fontweight='bold', pad=20, color='#2C3E50')
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, "2_spell_rarity_distribution.png"), 
                       dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
        except Exception as e:
            print(f"Error in spell rarity analysis: {e}")

    def plot_3_school_market_dominance(self):
        """3. School Market Dominance"""
        print("📊 3. Generating School Market Dominance...")
        
        if self.mongo_analyzer is None:
            print("No MongoDB analyzer available")
            return
        
        # Simula l'analisi di dominanza delle scuole
        pipeline = [
            {"$match": {"school.name": {"$exists": True, "$ne": None}}},
            {"$group": {
                "_id": "$school.name",
                "total_spells": {"$sum": 1},
                "avg_level": {"$avg": "$level"}
            }},
            {"$sort": {"total_spells": -1}}
        ]
        
        try:
            data = list(self.mongo_analyzer.db.spells.aggregate(pipeline))
            if not data:
                print("No school market data available")
                return
            
            fig, ax = plt.subplots(figsize=(14, 8))
            fig.patch.set_facecolor('white')
            
            schools = [item['_id'] for item in data]
            spell_counts = [item['total_spells'] for item in data]
            avg_levels = [item['avg_level'] for item in data]
            
            colors = self.color_palettes['soft_greens'][:len(schools)]
            
            bars = ax.bar(schools, spell_counts, color=colors, alpha=0.8, 
                         edgecolor='white', linewidth=2)
            
            # Add value labels
            for bar, count in zip(bars, spell_counts):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                       str(count), ha='center', fontweight='bold', fontsize=10)
            
            ax.set_xlabel('Magic Schools', fontsize=12, fontweight='bold', color='#444444')
            ax.set_ylabel('Number of Spells', fontsize=12, fontweight='bold', color='#444444')
            ax.set_title('Magic School Market Dominance\nTotal Spells per School', 
                        fontsize=16, fontweight='bold', pad=20, color='#2C3E50')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(axis='y', alpha=0.3, color='#DDDDDD')
            ax.set_facecolor('white')
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, "3_school_market_dominance.png"), 
                       dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
        except Exception as e:
            print(f"Error in school market analysis: {e}")

    def plot_4_equipment_tiers(self):
        """4. Equipment Market Tiers"""
        print("📊 4. Generating Equipment Market Tiers...")
        
        if self.mongo_analyzer is None:
            print("No MongoDB analyzer available")
            return
        
        # Simula l'analisi dei tier di equipaggiamento
        pipeline = [
            {"$match": {"cost.quantity": {"$exists": True, "$ne": None}}},
            {"$addFields": {
                "cost_in_gp": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$cost.unit", "cp"]}, "then": {"$divide": ["$cost.quantity", 100]}},
                            {"case": {"$eq": ["$cost.unit", "sp"]}, "then": {"$divide": ["$cost.quantity", 10]}},
                            {"case": {"$eq": ["$cost.unit", "gp"]}, "then": "$cost.quantity"},
                            {"case": {"$eq": ["$cost.unit", "pp"]}, "then": {"$multiply": ["$cost.quantity", 10]}}
                        ],
                        "default": 0
                    }
                }
            }},
            {"$addFields": {
                "price_tier": {
                    "$switch": {
                        "branches": [
                            {"case": {"$lt": ["$cost_in_gp", 1]}, "then": "Budget"},
                            {"case": {"$lt": ["$cost_in_gp", 10]}, "then": "Economy"},
                            {"case": {"$lt": ["$cost_in_gp", 100]}, "then": "Standard"},
                            {"case": {"$lt": ["$cost_in_gp", 500]}, "then": "Premium"}
                        ],
                        "default": "Luxury"
                    }
                }
            }},
            {"$group": {
                "_id": "$price_tier",
                "item_count": {"$sum": 1},
                "avg_cost": {"$avg": "$cost_in_gp"}
            }},
            {"$sort": {"avg_cost": 1}}
        ]
        
        try:
            data = list(self.mongo_analyzer.db.equipment.aggregate(pipeline))
            if not data:
                print("No equipment tier data available")
                return
            
            fig, ax = plt.subplots(figsize=(12, 8))
            fig.patch.set_facecolor('white')
            
            tiers = [item['_id'] for item in data]
            counts = [item['item_count'] for item in data]
            
            colors = self.color_palettes['soft_pinks'][:len(tiers)]
            
            bars = ax.bar(tiers, counts, color=colors, alpha=0.8, 
                         edgecolor='white', linewidth=2)
            
            # Add value labels
            for bar, count in zip(bars, counts):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                       str(count), ha='center', fontweight='bold', fontsize=10)
            
            ax.set_xlabel('Price Tiers', fontsize=12, fontweight='bold', color='#444444')
            ax.set_ylabel('Number of Items', fontsize=12, fontweight='bold', color='#444444')
            ax.set_title('Equipment Market Tier Distribution\nItems by Price Category', 
                        fontsize=16, fontweight='bold', pad=20, color='#2C3E50')
            ax.grid(axis='y', alpha=0.3, color='#DDDDDD')
            ax.set_facecolor('white')
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, "4_equipment_tiers.png"), 
                       dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
        except Exception as e:
            print(f"Error in equipment tier analysis: {e}")

    def plot_5_racial_advantages(self):
        """5. Racial Competitive Advantages"""
        print("📊 5. Generating Racial Advantages...")
        
        if self.mongo_analyzer is None:
            print("No MongoDB analyzer available")
            return
        
        # Simula l'analisi dei vantaggi razziali
        pipeline = [
            {"$addFields": {
                "ability_bonus_count": {"$size": {"$ifNull": ["$ability_bonuses", []]}},
                "trait_count": {"$size": {"$ifNull": ["$traits", []]}},
                "language_count": {"$size": {"$ifNull": ["$languages", []]}},
                "speed": {"$ifNull": ["$speed", 30]}
            }},
            {"$addFields": {
                "advantage_score": {
                    "$add": [
                        {"$multiply": ["$ability_bonus_count", 2]},
                        {"$multiply": ["$trait_count", 1.5]},
                        {"$multiply": ["$language_count", 0.5]},
                        {"$divide": ["$speed", 10]}
                    ]
                }
            }},
            {"$sort": {"advantage_score": -1}},
            {"$limit": 15}
        ]
        
        try:
            data = list(self.mongo_analyzer.db.races.aggregate(pipeline))
            if not data:
                print("No racial advantage data available")
                return
            
            fig, ax = plt.subplots(figsize=(12, 8))
            fig.patch.set_facecolor('white')
            
            races = [item['name'] for item in data]
            scores = [item['advantage_score'] for item in data]
            
            colors = self.color_palettes['gradient_pastels'][:len(races)]
            
            bars = ax.barh(races, scores, color=colors, alpha=0.8, 
                          edgecolor='white', linewidth=2)
            
            # Add value labels
            for bar, score in zip(bars, scores):
                ax.text(score + 0.1, bar.get_y() + bar.get_height()/2,
                       f'{score:.1f}', va='center', fontweight='bold', fontsize=10)
            
            ax.set_xlabel('Advantage Score', fontsize=12, fontweight='bold', color='#444444')
            ax.set_ylabel('Races', fontsize=12, fontweight='bold', color='#444444')
            ax.set_title('Racial Competitive Advantages\nComposite Advantage Score', 
                        fontsize=16, fontweight='bold', pad=20, color='#2C3E50')
            ax.grid(axis='x', alpha=0.3, color='#DDDDDD')
            ax.set_facecolor('white')
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, "5_racial_advantages.png"), 
                       dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
        except Exception as e:
            print(f"Error in racial advantage analysis: {e}")

    def plot_6_spell_distribution_heatmap(self):
        """6. Spell Distribution Heatmap"""
        print("📊 6. Generating Spell Distribution Heatmap...")
        
        if self.mongo_analyzer is None:
            print("No MongoDB analyzer available")
            return
        
        # Simula l'analisi di distribuzione degli spell
        pipeline = [
            {"$unwind": "$classes"},
            {"$group": {
                "_id": {
                    "class": "$classes.name",
                    "level": "$level"
                },
                "spell_count": {"$sum": 1}
            }},
            {"$group": {
                "_id": "$_id.class",
                "level_distribution": {"$push": {
                    "level": "$_id.level",
                    "count": "$spell_count"
                }},
                "total_spells": {"$sum": "$spell_count"}
            }},
            {"$sort": {"total_spells": -1}},
            {"$limit": 8}
        ]
        
        try:
            data = list(self.mongo_analyzer.db.spells.aggregate(pipeline))
            if not data:
                print("No spell distribution data available")
                return
            
            # Prepare matrix for heatmap
            classes = [item['_id'] for item in data]
            max_level = 9
            
            matrix_data = []
            for class_data in data:
                row = [0] * (max_level + 1)  # Levels 0-9
                for level_info in class_data['level_distribution']:
                    level = level_info['level']
                    if 0 <= level <= max_level:
                        row[level] = level_info['count']
                matrix_data.append(row)
            
            matrix = np.array(matrix_data)
            
            fig, ax = plt.subplots(figsize=(14, 8))
            fig.patch.set_facecolor('white')
            
            # Custom pastel colormap
            colors = ['#FFFFFF', '#FFE5E5', '#FFCCCC', '#FFB3B3', '#FF9999', '#FF8080']
            from matplotlib.colors import LinearSegmentedColormap
            cmap = LinearSegmentedColormap.from_list('pastel_heat', colors, N=256)
            
            im = ax.imshow(matrix, cmap=cmap, aspect='auto', interpolation='bilinear')
            
            # Set ticks and labels
            ax.set_xticks(range(max_level + 1))
            ax.set_xticklabels([f'L{i}' if i > 0 else 'Cantrips' for i in range(max_level + 1)], 
                              fontsize=10, color='#444444')
            ax.set_yticks(range(len(classes)))
            ax.set_yticklabels(classes, fontsize=11, color='#444444')
            
            # Add text annotations
            for i in range(len(classes)):
                for j in range(max_level + 1):
                    value = matrix[i, j]
                    if value > 0:
                        text_color = '#333333' if value < matrix.max() * 0.6 else '#FFFFFF'
                        ax.text(j, i, str(int(value)), ha='center', va='center',
                               color=text_color, fontweight='bold', fontsize=9)
            
            ax.set_xlabel('Spell Level', fontsize=12, fontweight='bold', color='#444444')
            ax.set_ylabel('Classes', fontsize=12, fontweight='bold', color='#444444')
            ax.set_title('Class Spell Distribution Heatmap\nSpells by Level and Class', 
                        fontsize=16, fontweight='bold', pad=20, color='#2C3E50')
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.1)
            cbar.set_label('Number of Spells', rotation=270, labelpad=15, fontsize=12, color='#444444')
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, "6_spell_distribution_heatmap.png"), 
                       dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
        except Exception as e:
            print(f"Error in spell distribution analysis: {e}")

    # ==========================================
    # NEO4J ANALYZER VISUALIZATIONS (7)
    # ==========================================

    def plot_7_spell_class_network(self):
        """7. Spell-Class Network - solo PNG statico"""
        print("📊 7. Generating Spell-Class Network...")
        
        centrality_data, network_data = self.get_spell_class_network_data()
        if not centrality_data or not network_data:
            print("No network data available")
            return
        
        # Create static matplotlib network
        self._create_static_network_plot(centrality_data, network_data, "7_spell_class_network.png")

    def _create_static_network_plot(self, centrality_data, network_data, filename):
        """Crea una versione statica del network plot"""
        G = nx.Graph()
        
        # Add nodes
        for item in centrality_data:
            class_name = item['class_name']
            influence = item['network_influence']
            G.add_node(class_name, influence=influence)
        
        # Add edges
        for item in network_data:
            class1 = item['class1']
            class2 = item['class2']
            shared = item['shared_spells']
            if G.has_node(class1) and G.has_node(class2):
                G.add_edge(class1, class2, weight=shared)
        
        fig, ax = plt.subplots(figsize=(14, 10))
        fig.patch.set_facecolor('white')
        
        pos = nx.spring_layout(G, seed=42, k=2, iterations=50)
        
        # Draw edges
        edges = G.edges(data=True)
        for (u, v, d) in edges:
            weight = d['weight']
            width = max(1, weight / 10)
            alpha = min(0.9, 0.3 + (weight / 50) * 0.5)  # Ensure alpha is <= 1
            nx.draw_networkx_edges(G, pos, [(u, v)], width=width, alpha=alpha, edge_color='#CCCCCC')
        
        # Draw nodes
        node_colors = self.color_palettes['network'][:len(G.nodes())]
        node_sizes = [G.nodes[node]['influence'] * 50 for node in G.nodes()]
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                              alpha=0.9, edgecolors='white', linewidths=2)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', font_color='#333333')
        
        ax.set_title('D&D Class Spell Network\nNode size = Network Influence', 
                    fontsize=16, fontweight='bold', pad=20, color='#2C3E50')
        ax.set_facecolor('white')
        plt.axis('off')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def plot_8_multiclass_synergy_network(self):
        """8. Multiclass Synergy Network - solo PNG statico"""
        print("📊 8. Generating Multiclass Synergy Network...")
        
        if self.neo4j_analyzer is None:
            print("No Neo4j analyzer available")
            return
        
        with self.neo4j_analyzer.driver.session() as session:
            # Query dal neo4j_analyzer per synergy matrix
            synergy_query = """
            MATCH (c1:Class)-[:CAN_CAST]->(s:Spell)<-[:CAN_CAST]-(c2:Class)
            WHERE c1.name < c2.name
            WITH c1, c2, count(s) as shared_spells
            WHERE shared_spells > 15
            RETURN c1.name as class1, c2.name as class2, shared_spells,
                   round(shared_spells * 1.0 / 319 * 100, 2) as synergy_score
            ORDER BY shared_spells DESC
            """
            
            data = session.run(synergy_query).data()
        
        if not data:
            print("No synergy data available")
            return
        
        # Create static version
        self._create_static_synergy_plot(data, "8_multiclass_synergy_network.png")

    def _create_static_synergy_plot(self, data, filename):
        """Crea versione statica del synergy network"""
        G = nx.Graph()
        
        for item in data:
            G.add_edge(item['class1'], item['class2'], 
                      weight=item['synergy_score'],
                      shared_spells=item['shared_spells'])
        
        fig, ax = plt.subplots(figsize=(16, 12))
        fig.patch.set_facecolor('white')
        
        pos = nx.spring_layout(G, seed=42, k=2, iterations=50)
        
        # Draw edges with varying thickness
        edges = G.edges(data=True)
        for (u, v, d) in edges:
            weight = d['weight']
            width = (weight / 10) + 1
            alpha = min(0.9, 0.3 + (weight / 100) * 0.5)
            color = plt.cm.Pastel1(weight / 100)
            
            nx.draw_networkx_edges(G, pos, [(u, v)], width=width,
                                  edge_color=[color], alpha=alpha)
        
        # Draw nodes
        node_colors = self.color_palettes['network'][:len(G.nodes())]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=3000,
                              alpha=0.9, edgecolors='white', linewidths=3)
        
        # Draw labels
        for node, (x, y) in pos.items():
            ax.text(x, y, node, fontsize=11, fontweight='bold', color='#333333',
                   ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
        
        ax.set_title('Multiclass Synergy Network\nEdge thickness = Synergy strength', 
                    fontsize=18, fontweight='bold', pad=30, color='#2C3E50')
        ax.set_facecolor('white')
        plt.axis('off')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def plot_9_school_dominance_ecosystem(self):
        """9. School Dominance Ecosystem"""
        print("📊 9. Generating School Dominance Ecosystem...")
        
        if self.neo4j_analyzer is None:
            print("No Neo4j analyzer available")
            return
        
        with self.neo4j_analyzer.driver.session() as session:
            # Query dal neo4j_analyzer per school dominance
            dominance_query = """
            MATCH (s:Spell)-[:BELONGS_TO]->(school:School)
            MATCH (s)<-[:CAN_CAST]-(c:Class)
            WITH school, count(DISTINCT c) as class_reach, 
                 count(s) as spell_count
            ORDER BY class_reach DESC, spell_count DESC
            RETURN school.name as school_name, spell_count, class_reach,
                   round(class_reach * 1.0 / 12 * 100, 1) as market_penetration
            """
            
            data = session.run(dominance_query).data()
        
        if not data:
            print("No school dominance data available")
            return
        
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.patch.set_facecolor('white')
        
        schools = [item['school_name'] for item in data]
        penetration = [item['market_penetration'] for item in data]
        spell_counts = [item['spell_count'] for item in data]
        
        # Fix color array length to match data points
        colors = self.color_palettes['soft_greens'][:len(schools)]
        if len(colors) < len(schools):
            colors = (colors * ((len(schools) // len(colors)) + 1))[:len(schools)]
        
        scatter = ax.scatter(penetration, spell_counts, 
                           s=[s*3 for s in spell_counts],
                           c=colors, alpha=0.7, edgecolors='white', linewidth=2)
        
        for i, school in enumerate(schools):
            ax.annotate(school, (penetration[i], spell_counts[i]),
                       xytext=(8, 8), textcoords='offset points',
                       fontsize=10, fontweight='bold', color='#333333',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
        
        ax.set_xlabel('Market Penetration (%)', fontsize=12, fontweight='bold', color='#444444')
        ax.set_ylabel('Total Spells', fontsize=12, fontweight='bold', color='#444444')
        ax.set_title('School Dominance Ecosystem\nMarket Penetration vs Spell Count', 
                   fontsize=16, fontweight='bold', pad=20, color='#2C3E50')
        ax.grid(alpha=0.3, color='#DDDDDD')
        ax.set_facecolor('white')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "9_school_dominance_ecosystem.png"), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def plot_10_spell_bridge_analysis(self):
        """10. Spell Bridge Analysis"""
        print("📊 10. Generating Spell Bridge Analysis...")
        
        if self.neo4j_analyzer is None:
            print("No Neo4j analyzer available")
            return
        
        with self.neo4j_analyzer.driver.session() as session:
            # Query dal neo4j_analyzer per bridge spells
            bridge_query = """
            MATCH (c1:Class)-[:CAN_CAST]->(s:Spell)<-[:CAN_CAST]-(c2:Class)
            WHERE c1.name < c2.name
            WITH s, count(DISTINCT [c1.name, c2.name]) as bridge_count
            ORDER BY bridge_count DESC
            RETURN s.name as spell_name, s.level as level, bridge_count
            LIMIT 15
            """
            
            data = session.run(bridge_query).data()
        
        if not data:
            print("No bridge spell data available")
            return
        
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.patch.set_facecolor('white')
        
        spells = [item['spell_name'] for item in data[:10]]
        bridge_counts = [item['bridge_count'] for item in data[:10]]
        levels = [item['level'] for item in data[:10]]
        
        colors = [self.color_palettes['soft_greens'][min(level, 5)] for level in levels]
        
        bars = ax.bar(range(len(spells)), bridge_counts, color=colors, alpha=0.8,
                     edgecolor='white', linewidth=2)
        
        # Add level labels on bars
        for i, (bar, level) in enumerate(zip(bars, levels)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                   f'L{level}', ha='center', fontweight='bold', fontsize=9,
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        
        ax.set_xlabel('Spells', fontsize=12, fontweight='bold', color='#444444')
        ax.set_ylabel('Bridge Connections', fontsize=12, fontweight='bold', color='#444444')
        ax.set_title('Top Bridge Spells\nClass Connectors', 
                   fontsize=16, fontweight='bold', pad=20, color='#2C3E50')
        ax.set_xticks(range(len(spells)))
        ax.set_xticklabels(spells, rotation=45, ha='right', fontsize=9)
        ax.grid(axis='y', alpha=0.3, color='#DDDDDD')
        ax.set_facecolor('white')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "10_spell_bridge_analysis.png"), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def plot_11_school_competition_matrix(self):
        """11. School Competition Matrix"""
        print("📊 11. Generating School Competition Matrix...")
        
        if self.neo4j_analyzer is None:
            print("No Neo4j analyzer available")
            return
        
        with self.neo4j_analyzer.driver.session() as session:
            # Query dal neo4j_analyzer per school competition
            competition_query = """
            MATCH (s1:School)<-[:BELONGS_TO]-(spell1:Spell)<-[:CAN_CAST]-(c:Class)
            MATCH (c)-[:CAN_CAST]->(spell2:Spell)-[:BELONGS_TO]->(s2:School)
            WHERE s1.name < s2.name
            WITH s1, s2, count(DISTINCT c) as shared_classes
            WHERE shared_classes > 2
            RETURN s1.name as school1, s2.name as school2, shared_classes
            ORDER BY shared_classes DESC
            """
            
            data = session.run(competition_query).data()
        
        if not data:
            print("No school competition data available")
            return
        
        # Create competition matrix
        schools = list(set([item['school1'] for item in data] + [item['school2'] for item in data]))
        n = len(schools)
        matrix = np.zeros((n, n))
        
        school_to_idx = {school: i for i, school in enumerate(schools)}
        
        for item in data:
            i = school_to_idx[item['school1']]
            j = school_to_idx[item['school2']]
            shared = item['shared_classes']
            matrix[i, j] = shared
            matrix[j, i] = shared  # Make symmetric
        
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor('white')
        
        # Custom colormap for competition
        colors = ['#FFFFFF', '#FFE5E5', '#FFCCCC', '#FF9999', '#FF6666']
        from matplotlib.colors import LinearSegmentedColormap
        cmap = LinearSegmentedColormap.from_list('competition', colors, N=256)
        
        im = ax.imshow(matrix, cmap=cmap, aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(schools, rotation=45, ha='right', fontsize=10)
        ax.set_yticklabels(schools, fontsize=10)
        
        # Add text annotations
        for i in range(n):
            for j in range(n):
                if matrix[i, j] > 0:
                    text_color = '#333333' if matrix[i, j] < matrix.max() * 0.6 else '#FFFFFF'
                    ax.text(j, i, f'{int(matrix[i, j])}', ha='center', va='center',
                           color=text_color, fontweight='bold', fontsize=9)
        
        ax.set_title('School Competition Matrix\nShared Classes Analysis', 
                   fontsize=16, fontweight='bold', pad=20, color='#2C3E50')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "11_school_competition_matrix.png"), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def plot_12_component_dependency_analysis(self):
        """12. Component Dependency Analysis"""
        print("📊 12. Generating Component Dependency Analysis...")
        
        if self.neo4j_analyzer is None:
            print("No Neo4j analyzer available")
            return
        
        with self.neo4j_analyzer.driver.session() as session:
            # Query dal neo4j_analyzer per component analysis
            component_query = """
            MATCH (s:Spell)
            WITH s,
                 CASE WHEN 'V' IN s.components THEN 1 ELSE 0 END as needs_verbal,
                 CASE WHEN 'S' IN s.components THEN 1 ELSE 0 END as needs_somatic,
                 CASE WHEN 'M' IN s.components THEN 1 ELSE 0 END as needs_material,
                 s.level as spell_level
            WITH spell_level,
                 sum(needs_verbal) as verbal_count,
                 sum(needs_somatic) as somatic_count,
                 sum(needs_material) as material_count,
                 count(s) as total_spells
            WHERE spell_level <= 9
            ORDER BY spell_level
            RETURN spell_level,
                   round(verbal_count * 100.0 / total_spells, 1) as verbal_pct,
                   round(somatic_count * 100.0 / total_spells, 1) as somatic_pct,
                   round(material_count * 100.0 / total_spells, 1) as material_pct
            """
            
            data = session.run(component_query).data()
        
        if not data:
            print("No component dependency data available")
            return
        
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.patch.set_facecolor('white')
        
        levels = [item['spell_level'] for item in data]
        verbal_pcts = [item['verbal_pct'] for item in data]
        somatic_pcts = [item['somatic_pct'] for item in data]
        material_pcts = [item['material_pct'] for item in data]
        
        width = 0.25
        x = np.arange(len(levels))
        
        ax.bar(x - width, verbal_pcts, width, label='Verbal', color='#FF6B9D', alpha=0.8)
        ax.bar(x, somatic_pcts, width, label='Somatic', color='#87CEEB', alpha=0.8)
        ax.bar(x + width, material_pcts, width, label='Material', color='#98FB98', alpha=0.8)
        
        ax.set_xlabel('Spell Level', fontsize=12, fontweight='bold', color='#444444')
        ax.set_ylabel('Component Requirement (%)', fontsize=12, fontweight='bold', color='#444444')
        ax.set_title('Spell Component Dependencies\nBy Spell Level', 
                   fontsize=16, fontweight='bold', pad=20, color='#2C3E50')
        ax.set_xticks(x)
        ax.set_xticklabels([f'L{l}' if l > 0 else 'Cantrips' for l in levels])
        ax.legend()
        ax.grid(axis='y', alpha=0.3, color='#DDDDDD')
        ax.set_facecolor('white')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "12_component_dependency_analysis.png"), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def plot_13_power_progression_curves(self):
        """13. Power Progression Curves"""
        print("📊 13. Generating Power Progression Curves...")
        
        if self.neo4j_analyzer is None:
            print("No Neo4j analyzer available")
            return
        
        with self.neo4j_analyzer.driver.session() as session:
            # Query dal neo4j_analyzer per power curves
            progression_query = """
            MATCH (s:Spell)-[:BELONGS_TO]->(school:School)
            WITH school.name as school_name,
                 s.level as level,
                 count(s) as spell_count
            ORDER BY school_name, level
            WITH school_name,
                 collect({level: level, count: spell_count}) as distribution
            RETURN school_name, distribution
            """
            
            data = session.run(progression_query).data()
        
        if not data:
            print("No power progression data available")
            return
        
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.patch.set_facecolor('white')
        
        colors = self.color_palettes['gradient_pastels']
        
        for i, school_data in enumerate(data[:6]):  # Top 6 schools
            school = school_data['school_name']
            distribution = school_data['distribution']
            
            # Extract levels and counts, ensuring we have data for levels 0-9
            levels = list(range(10))
            counts = [0] * 10
            
            for level_data in distribution:
                level = level_data['level']
                if 0 <= level <= 9:
                    counts[level] = level_data['count']
            
            color = colors[i % len(colors)]
            ax.plot(levels, counts, 'o-', label=school, color=color, 
                   linewidth=2, markersize=6, alpha=0.8)
            ax.fill_between(levels, counts, alpha=0.2, color=color)
        
        ax.set_xlabel('Spell Level', fontsize=12, fontweight='bold', color='#444444')
        ax.set_ylabel('Number of Spells', fontsize=12, fontweight='bold', color='#444444')
        ax.set_title('Magic School Power Progression Curves\nSpell Distribution Across Levels', 
                   fontsize=16, fontweight='bold', pad=20, color='#2C3E50')
        
        # Customize x-axis labels
        ax.set_xticks(levels)
        ax.set_xticklabels([f'L{i}' if i > 0 else 'Cantrips' for i in levels])
        
        ax.grid(alpha=0.3, color='#DDDDDD')
        ax.set_facecolor('white')
        
        # Legend
        legend = ax.legend(frameon=True, fancybox=True, shadow=True, fontsize=10, 
                          loc='upper right')
        legend.get_frame().set_facecolor('white')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "13_power_progression_curves.png"), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    # ==========================================
    # MAIN EXECUTION
    # ==========================================

    def generate_all_visualizations(self):
        """Genera tutte le 13 visualizzazioni"""
        print("\n🌸 GENERATING ALL 13 D&D VISUALIZATIONS")
        print("="*70)
        
        # MongoDB visualizations (6)
        mongodb_visualizations = [
            ("Class Power Metrics", self.plot_1_class_power_metrics),
            ("Spell Rarity Distribution", self.plot_2_spell_rarity_distribution),
            ("School Market Dominance", self.plot_3_school_market_dominance),
            ("Equipment Market Tiers", self.plot_4_equipment_tiers),
            ("Racial Competitive Advantages", self.plot_5_racial_advantages),
            ("Spell Distribution Heatmap", self.plot_6_spell_distribution_heatmap)
        ]
        
        # Neo4j visualizations (7)
        neo4j_visualizations = [
            ("Spell-Class Network", self.plot_7_spell_class_network),
            ("Multiclass Synergy Network", self.plot_8_multiclass_synergy_network),
            ("School Dominance Ecosystem", self.plot_9_school_dominance_ecosystem),
            ("Spell Bridge Analysis", self.plot_10_spell_bridge_analysis),
            ("School Competition Matrix", self.plot_11_school_competition_matrix),
            ("Component Dependency Analysis", self.plot_12_component_dependency_analysis),
            ("Power Progression Curves", self.plot_13_power_progression_curves)
        ]
        
        print("\n📊 MONGODB ANALYZER VISUALIZATIONS:")
        print("-" * 50)
        for i, (name, func) in enumerate(mongodb_visualizations, 1):
            try:
                func()
                print(f"✅ {i:2d}. {name} completed")
            except Exception as e:
                print(f"❌ {i:2d}. Error in {name}: {e}")
        
        print("\n🔗 NEO4J ANALYZER VISUALIZATIONS:")
        print("-" * 50)
        for i, (name, func) in enumerate(neo4j_visualizations, 7):
            try:
                func()
                print(f"✅ {i:2d}. {name} completed")
            except Exception as e:
                print(f"❌ {i:2d}. Error in {name}: {e}")
        
        print(f"\n🎉 All visualizations completed!")
        print(f"📁 Images saved to: {self.output_dir}")

    def close_connections(self):
        """Chiude le connessioni ai database"""
        if self.mongo_client is not None:
            self.mongo_client.close()
            print("✅ MongoDB connection closed")
        
        if self.neo4j_analyzer is not None:
            self.neo4j_analyzer.close()
            print("✅ Neo4j connection closed")

# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    """Funzione principale per generare tutte le visualizzazioni"""
    print("🌸 D&D ENHANCED VISUALIZER - 13 CHARTS")
    print("=" * 60)
    
    # Initialize visualizer
    visualizer = DNDEnhancedVisualizer()
    
    try:
        # Generate all 13 visualizations
        visualizer.generate_all_visualizations()
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up connections
        visualizer.close_connections()
    
    print("\n🏁 Visualization generation complete!")

if __name__ == "__main__":
    main()