"""
MongoDB D&D 5e Data Analysis
"""

import pymongo
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
from collections import defaultdict, Counter
from pprint import pprint
import sys
import statistics

class DNDDataAnalyzer:
    
    def __init__(self, db):
        self.db = db
        self.verify_collections()
        
    def verify_collections(self):
        """Verifica le collezioni disponibili nel database"""
        collections = self.db.list_collection_names()
        print("Available collections:", collections)
        
        # Conta documenti per collezione
        self.collection_counts = {}
        for collection in collections:
            count = self.db[collection].count_documents({})
            self.collection_counts[collection] = count
            if count > 0:
                print(f"✓ {collection}: {count} documents")

    def print_section_header(self, title: str, char: str = "="):
        """Stampa un header decorativo per le sezioni"""
        print(f"\n{char * 70}")
        print(f" {title.upper()}")
        print(f"{char * 70}")

    def print_subsection(self, title: str):
        """Stampa un sub-header per le sottosezioni"""
        print(f"\n--- {title} ---")

    # ================
    # CLASS ANALYSIS - CORE METRICS
    # ================
    
    def analyze_class_power_metrics(self):
        """Analizza le metriche di potenza base delle classi"""
        self.print_section_header("CLASS POWER & SURVIVABILITY METRICS")
        
        pipeline = [
            # Stage 1: Ottieni spell data per ogni classe
            {"$lookup": {
                "from": "spells",
                "localField": "name",
                "foreignField": "classes.name",
                "as": "class_spells"
            }},
            
            # Stage 2: Calcola metriche base di potenza
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
            
            # Stage 3: Calcola scores compositi
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
            
            # Stage 4: Ranking composite
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
            results = list(self.db.classes.aggregate(pipeline))
            
            if results:
                self.print_subsection("Class Performance Metrics")
                
                print(f"{'Class':<15} {'Power':<8} {'Survival':<9} {'Versatile':<10} {'Special%':<8} {'Overall':<8}")
                print("-" * 70)
                
                for class_data in results:
                    name = class_data["name"]
                    power = class_data["power_score"]
                    survival = class_data["survivability_score"]
                    versatile = class_data["versatility_score"]
                    special = class_data["specialization_ratio"] * 100
                    overall = class_data["overall_performance"]
                    
                    print(f"{name:<15} {power:<8.1f} {survival:<9.1f} {versatile:<10.1f} {special:<8.1f}% {overall:<8.1f}")
                
                # Analisi dettagliata per le top 3 classi
                print("\n" + "="*50)
                print("TOP 3 CLASSES - DETAILED BREAKDOWN:")
                print("="*50)
                
                for i, class_data in enumerate(results[:3], 1):
                    name = class_data["name"]
                    print(f"\n#{i} - {name}:")
                    print(f"  Total Spells: {class_data['total_spells']}")
                    print(f"  Unique Spells: {class_data['unique_spells']} ({class_data['specialization_ratio']:.1%})")
                    print(f"  Damage Spells: {class_data['damage_spells']}")
                    print(f"  High Level Spells (6+): {class_data['high_level_spells']}")
                    print(f"  Hit Die: d{class_data['hit_die']}")
                    print(f"  Proficiencies: {class_data['proficiency_count']}")
                    print(f"  Saving Throws: {class_data['saving_throw_count']}")
                    
        except Exception as e:
            print(f"Error in class power analysis: {e}")

    def analyze_class_spell_distribution_patterns(self):
        """Analizza i pattern di distribuzione degli spell per livello per ogni classe"""
        self.print_section_header("CLASS SPELL LEVEL DISTRIBUTION ANALYSIS")
        
        pipeline = [
            # Stage 1: Unwind le classi dalle spell
            {"$unwind": "$classes"},
            
            # Stage 2: Raggruppa per classe e livello di spell
            {"$group": {
                "_id": {
                    "class": "$classes.name",
                    "level": "$level"
                },
                "spell_count": {"$sum": 1},
                "spell_names": {"$push": "$name"},
                "schools": {"$addToSet": "$school.name"},
                "concentration_spells": {
                    "$sum": {"$cond": [{"$eq": ["$concentration", True]}, 1, 0]}
                },
                "ritual_spells": {
                    "$sum": {"$cond": [{"$eq": ["$ritual", True]}, 1, 0]}
                }
            }},
            
            # Stage 3: Fa il reshape per classe con array di livelli
            {"$group": {
                "_id": "$_id.class",
                "level_distribution": {"$push": {
                    "level": "$_id.level",
                    "count": "$spell_count",
                    "schools": "$schools",
                    "concentration_count": "$concentration_spells",
                    "ritual_count": "$ritual_spells"
                }},
                "total_spells": {"$sum": "$spell_count"}
            }},
            
            # Stage 4: Calcola metriche di distribuzione
            {"$addFields": {
                "spell_levels_array": {
                    "$map": {
                        "input": "$level_distribution",
                        "as": "level_data",
                        "in": "$$level_data.level"
                    }
                },
                "spell_counts_array": {
                    "$map": {
                        "input": "$level_distribution",
                        "as": "level_data", 
                        "in": "$$level_data.count"
                    }
                }
            }},
            
            # Stage 5: Calcola weighted average e distribution metrics
            {"$addFields": {
                "avg_spell_level": {
                    "$divide": [
                        {
                            "$sum": {
                                "$map": {
                                    "input": "$level_distribution",
                                    "as": "level_data",
                                    "in": {"$multiply": ["$$level_data.level", "$$level_data.count"]}
                                }
                            }
                        },
                        "$total_spells"
                    ]
                },
                "cantrip_percentage": {
                    "$multiply": [
                        {
                            "$divide": [
                                {
                                    "$sum": {
                                        "$map": {
                                            "input": "$level_distribution",
                                            "as": "level_data",
                                            "in": {
                                                "$cond": [
                                                    {"$eq": ["$$level_data.level", 0]},
                                                    "$$level_data.count",
                                                    0
                                                ]
                                            }
                                        }
                                    }
                                },
                                "$total_spells"
                            ]
                        },
                        100
                    ]
                },
                "high_level_percentage": {
                    "$multiply": [
                        {
                            "$divide": [
                                {
                                    "$sum": {
                                        "$map": {
                                            "input": "$level_distribution",
                                            "as": "level_data",
                                            "in": {
                                                "$cond": [
                                                    {"$gte": ["$$level_data.level", 6]},
                                                    "$$level_data.count",
                                                    0
                                                ]
                                            }
                                        }
                                    }
                                },
                                "$total_spells"
                            ]
                        },
                        100
                    ]
                }
            }},
            
            {"$sort": {"avg_spell_level": -1}}
        ]
        
        try:
            results = list(self.db.spells.aggregate(pipeline))
            
            if results:
                self.print_subsection("Spell Distribution Analysis")
                
                print(f"{'Class':<15} {'Total':<6} {'Avg Lvl':<8} {'Cantrips':<9} {'High Lvl':<9} {'Pattern':<15}")
                print("-" * 75)
                
                for class_data in results:
                    name = class_data["_id"]
                    total = class_data["total_spells"]
                    avg_level = class_data["avg_spell_level"]
                    cantrip_pct = class_data["cantrip_percentage"]
                    high_pct = class_data["high_level_percentage"]
                    
                    # Determina il pattern della classe
                    if avg_level < 2.0:
                        pattern = "Low-Level Focus"
                    elif avg_level > 4.0:
                        pattern = "High-Level Focus"
                    elif cantrip_pct > 15:
                        pattern = "Cantrip Heavy"
                    elif high_pct > 20:
                        pattern = "End-Game Power"
                    else:
                        pattern = "Balanced"
                    
                    print(f"{name:<15} {total:<6} {avg_level:<8.2f} {cantrip_pct:<9.1f}% {high_pct:<9.1f}% {pattern:<15}")
                
                # Dettaglio distribuzione per le prime 5 classi
                print("\n" + "="*60)
                print("DETAILED LEVEL DISTRIBUTION (Top 5 Classes):")
                print("="*60)
                
                for class_data in results[:5]:
                    name = class_data["_id"]
                    print(f"\n{name}:")
                    
                    # Ordina per livello
                    level_dist = sorted(class_data["level_distribution"], key=lambda x: x["level"])
                    
                    for level_data in level_dist:
                        level = level_data["level"]
                        count = level_data["count"]
                        schools = len(level_data["schools"])
                        conc = level_data["concentration_count"]
                        ritual = level_data["ritual_count"]
                        
                        level_name = "Cantrips" if level == 0 else f"Level {level}"
                        print(f"  {level_name:<12}: {count:>3} spells ({schools} schools, {conc} conc, {ritual} ritual)")
                        
        except Exception as e:
            print(f"Error in spell distribution analysis: {e}")

    def analyze_class_resource_dependencies(self):
        """Analizza le dipendenze dalle risorse esterne per ogni classe"""
        self.print_section_header("CLASS RESOURCE DEPENDENCY ANALYSIS")
        
        pipeline = [
            # Stage 1: Lookup delle spell per classe
            {"$lookup": {
                "from": "spells",
                "localField": "name",
                "foreignField": "classes.name",
                "as": "class_spells"
            }},
            
            # Stage 2: Analizza dipendenze da materiali
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
                "verbal_spells": {
                    "$size": {
                        "$filter": {
                            "input": "$class_spells",
                            "cond": {"$in": ["V", {"$ifNull": ["$$this.components", []]}]}
                        }
                    }
                },
                "somatic_spells": {
                    "$size": {
                        "$filter": {
                            "input": "$class_spells",
                            "cond": {"$in": ["S", {"$ifNull": ["$$this.components", []]}]}
                        }
                    }
                },
                "total_spells": {"$size": "$class_spells"},
                "proficiency_count": {"$size": {"$ifNull": ["$proficiencies", []]}},
                "saving_throw_count": {"$size": {"$ifNull": ["$saving_throws", []]}},
                "hit_die_safe": {"$ifNull": ["$hit_die", 6]}
            }},
            
                # Stage 3: Calcola percentuali e dependency scores
                {"$addFields": {
                    "material_dependency_ratio": {
                        "$cond": [
                            {"$gt": ["$total_spells", 0]},
                            {"$divide": ["$material_dependent_spells", "$total_spells"]},
                            0
                        ]
                    },
                    "concentration_dependency_ratio": {
                        "$cond": [
                            {"$gt": ["$total_spells", 0]},
                            {"$divide": ["$concentration_spells", "$total_spells"]},
                            0
                        ]
                    },
                    "component_complexity_score": {
                        "$add": [
                            {"$multiply": [
                                {"$cond": [
                                    {"$gt": ["$total_spells", 0]},
                                    {"$divide": ["$material_dependent_spells", "$total_spells"]},
                                    0
                                ]}, 3]},
                            {"$multiply": [
                                {"$cond": [
                                    {"$gt": ["$total_spells", 0]},
                                    {"$divide": ["$concentration_spells", "$total_spells"]},
                                    0
                                ]}, 2]},
                            {
                                "$multiply": [
                                    {
                                        "$cond": [
                                            {"$gt": ["$total_spells", 0]},
                                            {"$divide": [
                                                {"$add": ["$verbal_spells", "$somatic_spells"]},
                                                {"$multiply": ["$total_spells", 2]}
                                            ]},
                                            0
                                        ]
                                    },
                                    1
                                ]
                            }
                        ]
                    },
                    "self_sufficiency_score": {
                        "$add": [
                            {"$multiply": ["$hit_die_safe", 0.5]},
                            {"$multiply": ["$saving_throw_count", 1.0]},
                            {"$multiply": ["$proficiency_count", 0.3]},
                            {"$multiply": [
                                {"$subtract": [1, 
                                    {"$cond": [
                                        {"$gt": ["$total_spells", 0]},
                                        {"$divide": ["$material_dependent_spells", "$total_spells"]},
                                        0
                                    ]}
                                ]}, 2]}
                        ]
                    }
                }},
                
                # Stage 4: Categorizza le classi
                {"$addFields": {
                    "dependency_category": {
                        "$switch": {
                            "branches": [
                                {"case": {"$gte": ["$component_complexity_score", 2.5]}, "then": "High Dependency"},
                                {"case": {"$gte": ["$component_complexity_score", 1.5]}, "then": "Medium Dependency"},
                                {"case": {"$gte": ["$component_complexity_score", 0.8]}, "then": "Low Dependency"}
                            ],
                            "default": "Self Sufficient"
                        }
                    },
                    "resilience_category": {
                        "$switch": {
                            "branches": [
                                {"case": {"$gte": ["$self_sufficiency_score", 6]}, "then": "Highly Resilient"},
                                {"case": {"$gte": ["$self_sufficiency_score", 4]}, "then": "Resilient"},
                                {"case": {"$gte": ["$self_sufficiency_score", 2]}, "then": "Moderate"}
                            ],
                            "default": "Fragile"
                        }
                    }
                }},
                
                {"$sort": {"self_sufficiency_score": -1}}
            ]
            
        try:
            results = list(self.db.classes.aggregate(pipeline))
            
            if results:
                self.print_subsection("Resource Dependency Rankings")
                
                print(f"{'Class':<15} {'Mat%':<6} {'Conc%':<7} {'Complex':<8} {'SelfSuff':<9} {'Category':<18}")
                print("-" * 75)
                
                for class_data in results:
                    name = class_data.get("name", "Unknown")
                    mat_ratio = class_data.get("material_dependency_ratio", 0)
                    conc_ratio = class_data.get("concentration_dependency_ratio", 0)
                    complex_score = class_data.get("component_complexity_score", 0)
                    self_suff = class_data.get("self_sufficiency_score", 0)
                    category = class_data.get("dependency_category", "Unknown")
                    
                    mat_pct = mat_ratio * 100 if mat_ratio is not None else 0
                    conc_pct = conc_ratio * 100 if conc_ratio is not None else 0
                    
                    print(f"{name:<15} {mat_pct:<6.1f}% {conc_pct:<7.1f}% {complex_score:<8.2f} {self_suff:<9.2f} {category:<18}")
                
                # Analisi per categoria
                print("\n" + "="*50)
                print("DEPENDENCY CATEGORIES BREAKDOWN:")
                print("="*50)
                
                categories = {}
                for class_data in results:
                    cat = class_data.get("dependency_category", "Unknown")
                    name = class_data.get("name", "Unknown")
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(name)
                
                for category, classes in categories.items():
                    print(f"\n{category}: {len(classes)} classes")
                    print(f"  Classes: {', '.join(classes)}")
                    
        except Exception as e:
                print(f"Error in dependency analysis: {e}")
                import traceback
                traceback.print_exc()

    # ================
    # SPELL MARKET VALUE ANALYSIS
    # ================
    
    def analyze_spell_rarity_and_access(self):
        """Analizza la rarità degli spell e la loro accessibilità"""
        self.print_section_header("SPELL RARITY & ACCESS ANALYSIS")
        
        pipeline = [
            # Stage 1: Calcola metriche di accesso per ogni spell
            {"$addFields": {
                "class_access_count": {"$size": {"$ifNull": ["$classes", []]}},
                "has_material_components": {"$in": ["M", {"$ifNull": ["$components", []]}]},
                "is_concentration": {"$eq": ["$concentration", True]},
                "is_ritual": {"$eq": ["$ritual", True]},
                "has_damage": {"$ne": ["$damage", None]},
                "spell_level": "$level"
            }},
            
            # Stage 2: Categorizza per rarità
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
                },
                "utility_score": {
                    "$add": [
                        {"$multiply": ["$spell_level", 1.0]},
                        {"$cond": [{"$eq": ["$has_damage", True]}, 2.0, 0]},
                        {"$cond": [{"$eq": ["$is_ritual", True]}, 3.0, 0]},
                        {"$cond": [{"$eq": ["$is_concentration", True]}, 1.0, 0]},
                        {"$cond": [{"$eq": ["$has_material_components", True]}, 0.5, 0]}
                    ]
                }
            }},
            
            # Stage 3: Raggruppa per rarità per l'analisi del livello
            {"$group": {
                "_id": {
                    "rarity": "$rarity_category",
                    "level": "$spell_level"
                },
                "spell_count": {"$sum": 1},
                "avg_utility": {"$avg": "$utility_score"},
                "damage_spells": {"$sum": {"$cond": [{"$eq": ["$has_damage", True]}, 1, 0]}},
                "ritual_spells": {"$sum": {"$cond": [{"$eq": ["$is_ritual", True]}, 1, 0]}},
                "concentration_spells": {"$sum": {"$cond": [{"$eq": ["$is_concentration", True]}, 1, 0]}},
                "material_spells": {"$sum": {"$cond": [{"$eq": ["$has_material_components", True]}, 1, 0]}},
                "example_spells": {"$push": {
                    "name": "$name",
                    "classes": "$classes",
                    "utility": "$utility_score"
                }}
            }},
            
            # Stage 4: Fa il reshape per rarità
            {"$group": {
                "_id": "$_id.rarity",
                "total_spells": {"$sum": "$spell_count"},
                "level_breakdown": {"$push": {
                    "level": "$_id.level",
                    "count": "$spell_count",
                    "avg_utility": "$avg_utility",
                    "examples": {"$slice": ["$example_spells", 3]}
                }},
                "overall_avg_utility": {"$avg": "$avg_utility"}
            }},
            
            # Stage 5: Ordina per rarità (Exclusive = più valutato)
            {"$addFields": {
                "rarity_value": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$_id", "Exclusive"]}, "then": 5},
                            {"case": {"$eq": ["$_id", "Rare"]}, "then": 4},
                            {"case": {"$eq": ["$_id", "Uncommon"]}, "then": 3},
                            {"case": {"$eq": ["$_id", "Common"]}, "then": 2}
                        ],
                        "default": 1
                    }
                }
            }},
            
            {"$sort": {"rarity_value": -1}}
        ]
        
        try:
            results = list(self.db.spells.aggregate(pipeline))
            
            if results:
                self.print_subsection("Spell Rarity Distribution")
                
                total_spells = sum(result["total_spells"] for result in results)
                
                print(f"{'Rarity':<12} {'Count':<6} {'%':<6} {'Avg Utility':<12} {'Value Score':<11}")
                print("-" * 55)
                
                for rarity_data in results:
                    rarity = rarity_data["_id"]
                    count = rarity_data["total_spells"]
                    percentage = (count / total_spells) * 100
                    avg_utility = rarity_data["overall_avg_utility"]
                    value_score = rarity_data["rarity_value"]
                    
                    print(f"{rarity:<12} {count:<6} {percentage:<6.1f}% {avg_utility:<12.2f} {value_score:<11}")
                
                # Dettaglio per categoria Exclusive (più preziosa)
                exclusive_data = next((r for r in results if r["_id"] == "Exclusive"), None)
                if exclusive_data:
                    print("\n" + "="*40)
                    print("EXCLUSIVE SPELLS BREAKDOWN:")
                    print("="*40)
                    
                    level_breakdown = sorted(exclusive_data["level_breakdown"], key=lambda x: x["level"])
                    
                    for level_data in level_breakdown:
                        level = level_data["level"]
                        count = level_data["count"]
                        utility = level_data["avg_utility"]
                        
                        level_name = "Cantrips" if level == 0 else f"Level {level}"
                        print(f"\n{level_name}: {count} spells (Avg Utility: {utility:.1f})")
                        
                        # Mostra esempi
                        examples = level_data["examples"]
                        for example in examples[:3]:
                            if example.get('name') and example.get('classes'):
                                classes = [c.get('name', 'Unknown') for c in example['classes'] if c.get('name')]
                                print(f"  • {example['name']} ({', '.join(classes)}) - Utility: {example['utility']:.1f}")
                        
        except Exception as e:
            print(f"Error in spell rarity analysis: {e}")

    def analyze_spell_school_market_presence(self):
        """Analizza la presenza delle scuole di magia nel 'mercato' degli spell"""
        self.print_section_header("MAGIC SCHOOL MARKET PRESENCE")
        
        pipeline = [
            # Stage 1: Match le spell con i dati delle scuole di magia
            {"$match": {"school.name": {"$exists": True, "$ne": None}}},
            
            # Stage 2: Aggiunge gli indicatori di valore di mercato
            {"$addFields": {
                "class_access_count": {"$size": {"$ifNull": ["$classes", []]}},
                "has_damage": {"$ne": ["$damage", None]},
                "is_high_level": {"$gte": ["$level", 5]},
                "is_concentration": {"$eq": ["$concentration", True]},
                "has_material": {"$in": ["M", {"$ifNull": ["$components", []]}]},
                "school_name": "$school.name"
            }},
            
            # Stage 3: Calcola le metriche di mercato per spell
            {"$addFields": {
                "exclusivity_value": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$class_access_count", 1]}, "then": 5},
                            {"case": {"$eq": ["$class_access_count", 2]}, "then": 4},
                            {"case": {"$lte": ["$class_access_count", 4]}, "then": 3},
                            {"case": {"$lte": ["$class_access_count", 7]}, "then": 2}
                        ],
                        "default": 1
                    }
                },
                "power_value": {
                    "$add": [
                        {"$multiply": ["$level", 1]},
                        {"$cond": [{"$eq": ["$has_damage", True]}, 3, 0]},
                        {"$cond": [{"$eq": ["$is_high_level", True]}, 2, 0]}
                    ]
                },
                "complexity_cost": {
                    "$add": [
                        {"$cond": [{"$eq": ["$is_concentration", True]}, 1, 0]},
                        {"$cond": [{"$eq": ["$has_material", True]}, 1, 0]}
                    ]
                }
            }},
            
            # Stage 4: Raggruppa per scuola
            {"$group": {
                "_id": "$school_name",
                "total_spells": {"$sum": 1},
                "avg_exclusivity": {"$avg": "$exclusivity_value"},
                "avg_power": {"$avg": "$power_value"},
                "avg_complexity": {"$avg": "$complexity_cost"},
                "total_market_value": {"$sum": {"$multiply": ["$exclusivity_value", "$power_value"]}},
                "exclusive_spells": {"$sum": {"$cond": [{"$eq": ["$exclusivity_value", 5]}, 1, 0]}},
                "high_power_spells": {"$sum": {"$cond": [{"$gte": ["$power_value", 7]}, 1, 0]}},
                "damage_spells": {"$sum": {"$cond": [{"$eq": ["$has_damage", True]}, 1, 0]}},
                "high_level_spells": {"$sum": {"$cond": [{"$eq": ["$is_high_level", True]}, 1, 0]}},
                "level_distribution": {"$push": "$level"},
                "class_reach": {"$addToSet": "$classes"}
            }},
            
            # Stage 5: Calcola le metriche di mercato
            {"$addFields": {
                "market_dominance": {"$divide": ["$total_market_value", "$total_spells"]},
                "exclusivity_ratio": {"$divide": ["$exclusive_spells", "$total_spells"]},
                "power_ratio": {"$divide": ["$high_power_spells", "$total_spells"]},
                "avg_spell_level": {"$avg": "$level_distribution"},
                "unique_class_access": {"$size": "$class_reach"}
            }},
            
            # Stage 6: Determina la posizione di mercato
            {"$addFields": {
                "market_position": {
                    "$switch": {
                        "branches": [
                            {"case": {"$and": [{"$gte": ["$market_dominance", 15]}, {"$gte": ["$exclusivity_ratio", 0.3]}]}, "then": "Premium Specialist"},
                            {"case": {"$and": [{"$gte": ["$market_dominance", 12]}, {"$gte": ["$power_ratio", 0.4]}]}, "then": "Power Player"},
                            {"case": {"$and": [{"$gte": ["$total_spells", 20]}, {"$gte": ["$unique_class_access", 8]}]}, "then": "Market Leader"},
                            {"case": {"$gte": ["$market_dominance", 8]}, "then": "Solid Performer"},
                            {"case": {"$gte": ["$total_spells", 15]}, "then": "Volume Player"}
                        ],
                        "default": "Niche Player"
                    }
                }
            }},
            
            {"$sort": {"market_dominance": -1}}
        ]
        
        try:
            results = list(self.db.spells.aggregate(pipeline))
            
            if results:
                self.print_subsection("Magic School Market Analysis")
                
                print(f"{'School':<15} {'Spells':<7} {'Dominance':<10} {'Excl%':<6} {'Power%':<7} {'Position':<17}")
                print("-" * 75)
                
                for school in results:
                    name = school["_id"]
                    spells = school["total_spells"]
                    dominance = school["market_dominance"]
                    excl_pct = school["exclusivity_ratio"] * 100
                    power_pct = school["power_ratio"] * 100
                    position = school["market_position"]
                    
                    print(f"{name:<15} {spells:<7} {dominance:<10.2f} {excl_pct:<6.1f}% {power_pct:<7.1f}% {position:<17}")
                
                # Top 3 school detailed analysis
                print("\n" + "="*60)
                print("TOP 3 SCHOOLS - MARKET BREAKDOWN:")
                print("="*60)
                
                for i, school in enumerate(results[:3], 1):
                    name = school["_id"]
                    print(f"\n#{i} - {name} ({school['market_position']}):")
                    print(f"  Total Market Value: {school['total_market_value']:.0f}")
                    print(f"  Average Spell Level: {school['avg_spell_level']:.1f}")
                    print(f"  Class Accessibility: {school['unique_class_access']} classes")
                    print(f"  Exclusive Spells: {school['exclusive_spells']} ({school['exclusivity_ratio']:.1%})")
                    print(f"  High Power Spells: {school['high_power_spells']} ({school['power_ratio']:.1%})")
                    print(f"  Damage Spells: {school['damage_spells']}")
                    
        except Exception as e:
            print(f"Error in school market analysis: {e}")

    # ================
    # EQUIPMENT VALUE ANALYSIS
    # ================
    
    def analyze_equipment_market_tiers(self):
        """Analizza i tier di mercato dell'equipaggiamento con utility scoring migliorato"""
        self.print_section_header("EQUIPMENT MARKET TIER ANALYSIS")
        
        pipeline = [
            # Stage 1: Filtra l'equipaggiamento con i dati dei costi
            {"$match": {
                "cost.quantity": {"$exists": True, "$ne": None},
                "cost.unit": {"$exists": True, "$ne": None}
            }},
            
            # Stage 2: Normalizza i costi e aggiunge gli indicatori di mercato
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
                },
                "weight_factor": {"$ifNull": ["$weight", 0]},
                "category": {"$ifNull": ["$equipment_category.name", "Unknown"]},
                "has_weapon_properties": {"$ne": ["$weapon_category", 'null']},
                "has_armor_class": {"$ne": ["$armor_class", 'null']}
            }},
            
            # Stage 3: Calcola le metriche
            {"$addFields": {
                "market_tier": {
                    "$switch": {
                        "branches": [
                            {"case": {"$lt": ["$cost_in_gp", 1]}, "then": "Budget"},
                            {"case": {"$lt": ["$cost_in_gp", 10]}, "then": "Economy"},
                            {"case": {"$lt": ["$cost_in_gp", 50]}, "then": "Standard"},
                            {"case": {"$lt": ["$cost_in_gp", 200]}, "then": "Premium"},
                            {"case": {"$lt": ["$cost_in_gp", 1000]}, "then": "Luxury"}
                        ],
                        "default": "Ultra-Luxury"
                    }
                },
                "utility_score": {
                    "$add": [
                        {"$cond": [{"$eq": ["$has_weapon_properties", True]}, 6, 0]},
                        {"$cond": [{"$eq": ["$has_armor_class", True]}, 5, 0]},
                        
                        # utility di base per tutti gli item
                        2,
                        
                        # Bonus specifici
                        {"$cond": [
                            {"$regexMatch": {"input": {"$ifNull": ["$category", ""]}, "regex": "Mounts|Vehicle", "options": "i"}}, 
                            4, 0
                        ]},
                        {"$cond": [
                            {"$regexMatch": {"input": {"$ifNull": ["$category", ""]}, "regex": "tool", "options": "i"}}, 
                            3, 0
                        ]},
                        {"$cond": [
                            {"$regexMatch": {"input": {"$ifNull": ["$category", ""]}, "regex": "Adventuring", "options": "i"}}, 
                            2, 0
                        ]},
                        
                        # Bonus per efficienza del peso (item più leggeri sono più utili nelle avventure)
                        {"$cond": [
                            {"$and": [
                                {"$gt": ["$weight_factor", 0]},
                                {"$lte": ["$weight_factor", 1]}
                            ]}, 
                            1, 0
                        ]},
                        
                        # Bonus per item di alto valore
                        {"$cond": [{"$gte": ["$cost_in_gp", 100]}, 1, 0]}
                    ]
                },
                "value_efficiency": {
                    "$cond": [
                        {"$gt": ["$cost_in_gp", 0]},
                        {"$divide": ["$utility_score", "$cost_in_gp"]},
                        0
                    ]
                }
            }},
            
            # Stage 4: Raggruppa per categoria e tier
            {"$group": {
                "_id": {
                    "category": "$category",
                    "tier": "$market_tier"
                },
                "item_count": {"$sum": 1},
                "avg_cost": {"$avg": "$cost_in_gp"},
                "min_cost": {"$min": "$cost_in_gp"},
                "max_cost": {"$max": "$cost_in_gp"},
                "avg_utility": {"$avg": "$utility_score"},
                "avg_efficiency": {"$avg": "$value_efficiency"},
                "sample_items": {"$push": {
                    "name": {"$ifNull": ["$name", "Unknown"]},
                    "cost": {"$ifNull": ["$cost_in_gp", 0]},
                    "utility": {"$ifNull": ["$utility_score", 0]},
                    "efficiency": {"$ifNull": ["$value_efficiency", 0]}
                }}
            }},
            
            # Stage 5: Fa il reshape per categoria
            {"$group": {
                "_id": "$_id.category",
                "total_items": {"$sum": "$item_count"},
                "tier_breakdown": {"$push": {
                    "tier": "$_id.tier",
                    "count": "$item_count",
                    "avg_cost": {"$ifNull": ["$avg_cost", 0]},
                    "cost_range": {
                        "min": {"$ifNull": ["$min_cost", 0]}, 
                        "max": {"$ifNull": ["$max_cost", 0]}
                    },
                    "avg_utility": {"$ifNull": ["$avg_utility", 0]},
                    "avg_efficiency": {"$ifNull": ["$avg_efficiency", 0]},
                    "top_items": {"$slice": [
                        {"$sortArray": {"input": "$sample_items", "sortBy": {"efficiency": -1}}}, 
                        3
                    ]}
                }},
                "category_avg_cost": {"$avg": "$avg_cost"},
                "category_avg_utility": {"$avg": "$avg_utility"}
            }},
            
            # Stage 6: Aggiunge categoria della posizione di mercato
            {"$addFields": {
                "market_position": {
                    "$switch": {
                        "branches": [
                            {"case": {"$gte": ["$category_avg_cost", 100]}, "then": "High-Value Segment"},
                            {"case": {"$gte": ["$category_avg_cost", 20]}, "then": "Mid-Market"},
                            {"case": {"$gte": ["$category_avg_cost", 5]}, "then": "Mass Market"}
                        ],
                        "default": "Budget Segment"
                    }
                }
            }},
            
            {"$sort": {"category_avg_cost": -1}}
        ]
        
        try:
            results = list(self.db.equipment.aggregate(pipeline))
            
            if results:
                self.print_subsection("Equipment Category Market Overview")
                
                print(f"\n{'Category':<22} {'Items':<8} {'Avg Cost':<12} {'Utility':<10} {'Market Position'}")
                print("─" * 85)
                
                for category in results:
                    name = category.get("_id", "Unknown") or "Unknown"
                    items = category.get("total_items", 0) or 0
                    avg_cost = category.get("category_avg_cost", 0) or 0
                    utility = category.get("category_avg_utility", 0) or 0
                    position = category.get("market_position", "Unknown") or "Unknown"
                    
                    print(f"{name:<22} {items:<8} {avg_cost:<9.1f}gp {utility:<10.1f} {position}")

                
                # Detailed tier analysis for top 3 categories
                print("\n" + "="*80)
                print("TOP 3 EQUIPMENT CATEGORIES - DETAILED MARKET ANALYSIS")
                print("="*80)
                
                for i, category in enumerate(results[:3], 1):
                    name = category.get("_id", "Unknown") or "Unknown"
                    position = category.get("market_position", "Unknown") or "Unknown"
                    total_items = category.get("total_items", 0)
                    avg_cost = category.get("category_avg_cost", 0) or 0
                    
                    print(f"\n┌─ #{i} - {name.upper()} ─────────────────────────────────")
                    print(f"│  Market Position: {position}")
                    print(f"│  Total Items: {total_items} | Average Cost: {avg_cost:.1f}gp")
                    print(f"└─────────────────────────────────────────────────────────")
                    
                    # Sort tiers by tier value
                    tier_order = {"Budget": 1, "Economy": 2, "Standard": 3, "Premium": 4, "Luxury": 5, "Ultra-Luxury": 6}
                    tier_breakdown = category.get("tier_breakdown", [])
                    tiers = sorted(tier_breakdown, key=lambda x: tier_order.get(x.get("tier", ""), 0))
                    
                    for tier_data in tiers:
                        tier = tier_data.get("tier", "Unknown") or "Unknown"
                        count = tier_data.get("count", 0) or 0
                        avg_cost = tier_data.get("avg_cost", 0)
                        cost_range = tier_data.get("cost_range", {})
                        efficiency = tier_data.get("avg_efficiency", 0)
                        utility = tier_data.get("avg_utility", 0) or 0
                        
                        # Safe null handling
                        if avg_cost is None:
                            avg_cost = 0
                        if efficiency is None:
                            efficiency = 0
                            
                        if cost_range and isinstance(cost_range, dict):
                            min_cost = cost_range.get("min", 0) or 0
                            max_cost = cost_range.get("max", 0) or 0
                        else:
                            min_cost = 0
                            max_cost = 0
                        
                        # Efficiency rating
                        if efficiency >= 1.0:
                            eff_rating = "EXCELLENT"
                        elif efficiency >= 0.5:
                            eff_rating = "GOOD"
                        elif efficiency >= 0.1:
                            eff_rating = "FAIR"
                        else:
                            eff_rating = "POOR"
                        
                        try:
                            print(f"\n{tier.upper():<12} │ {count:>2} items │ Avg: {avg_cost:>6.1f}gp │ Range: {min_cost:.0f}-{max_cost:.0f}gp")
                            print(f" └─ Utility: {utility:.1f} │ Efficiency: {efficiency:.3f} │ Rating: {eff_rating}")
                        except (TypeError, ValueError) as e:
                            print(f"   {tier.upper():<12} │ {count:>2} items │ Formatting error: {e}")
                            continue
                        
                        # Show top efficient item in this tier
                        top_items = tier_data.get("top_items", [])
                        if top_items and len(top_items) > 0:
                            best_item = top_items[0]
                            if best_item and isinstance(best_item, dict):
                                item_name = best_item.get('name', 'Unknown') or 'Unknown'
                                item_cost = best_item.get('cost', 0)
                                item_efficiency = best_item.get('efficiency', 0)
                                item_utility = best_item.get('utility', 0)
                                
                                if item_cost is None:
                                    item_cost = 0
                                if item_efficiency is None:
                                    item_efficiency = 0
                                if item_utility is None:
                                    item_utility = 0
                                    
                                # Truncate long names
                                display_name = item_name[:35] + "..." if len(item_name) > 35 else item_name
                                
                                try:
                                    print(f"      ★ Best Value: {display_name}")
                                    print(f"         Cost: {item_cost:.1f}gp │ Utility: {item_utility:.1f} │ Efficiency: {item_efficiency:.3f}")
                                except (TypeError, ValueError) as e:
                                    print(f"      ★ Best Value: {display_name} (formatting error: {e})")
                    
                    print()  # Extra spazio tra le categorie
                        
        except Exception as e:
            print(f"Error in equipment market analysis: {e}")
            import traceback
            traceback.print_exc()
    
    def analyze_equipment_cost_distribution(self):
        """Analizza la distribuzione dei costi dell'equipaggiamento """
        self.print_section_header("EQUIPMENT COST DISTRIBUTION ANALYSIS")
        
        pipeline = [
            # Stage 1: Match item con i dati dei costi
            {"$match": {
                "cost.quantity": {"$exists": True, "$ne": None},
                "cost.unit": {"$exists": True, "$ne": None}
            }},
            
            # Stage 2: Normalizza i costi per le monete di rame
            {"$addFields": {
                "cost_in_cp": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$cost.unit", "cp"]}, "then": "$cost.quantity"},
                            {"case": {"$eq": ["$cost.unit", "sp"]}, "then": {"$multiply": ["$cost.quantity", 10]}},
                            {"case": {"$eq": ["$cost.unit", "gp"]}, "then": {"$multiply": ["$cost.quantity", 100]}},
                            {"case": {"$eq": ["$cost.unit", "pp"]}, "then": {"$multiply": ["$cost.quantity", 1000]}}
                        ],
                        "default": 0
                    }
                },
                "weight": {"$ifNull": ["$weight", 0]},
                "category": "$equipment_category.name"
            }},
            
            # Stage 3: Aggiunge categorie dei costi
            {"$addFields": {
                "cost_tier": {
                    "$switch": {
                        "branches": [
                            {"case": {"$lt": ["$cost_in_cp", 100]}, "then": "Budget (< 1 gp)"},
                            {"case": {"$lt": ["$cost_in_cp", 1000]}, "then": "Affordable (1-9 gp)"},
                            {"case": {"$lt": ["$cost_in_cp", 5000]}, "then": "Moderate (10-49 gp)"},
                            {"case": {"$lt": ["$cost_in_cp", 10000]}, "then": "Expensive (50-99 gp)"},
                            {"case": {"$lt": ["$cost_in_cp", 50000]}, "then": "Luxury (100-499 gp)"}
                        ],
                        "default": "Premium (500+ gp)"
                    }
                },
                "cost_per_weight": {
                    "$cond": [
                        {"$gt": ["$weight", 0]},
                        {"$divide": ["$cost_in_cp", "$weight"]},
                        "null"
                    ]
                }
            }},
            
            # Stage 4: Raggruppa per categoria
            {"$group": {
                "_id": "$category",
                "total_items": {"$sum": 1},
                "avg_cost_cp": {"$avg": "$cost_in_cp"},
                "min_cost_cp": {"$min": "$cost_in_cp"},
                "max_cost_cp": {"$max": "$cost_in_cp"},
                "std_dev_cost": {"$stdDevPop": "$cost_in_cp"},
                "avg_weight": {"$avg": "$weight"},
                "cost_tiers": {"$push": "$cost_tier"},
                "items_with_weight": {"$sum": {"$cond": [{"$gt": ["$weight", 0]}, 1, 0]}},
                "avg_cost_per_weight": {"$avg": "$cost_per_weight"},
                "sample_items": {"$push": {
                    "name": "$name",
                    "cost_cp": "$cost_in_cp",
                    "weight": "$weight",
                    "cost_tier": "$cost_tier"
                }}
            }},
            
            # Stage 5: Aggiunge metriche di mercato
            {"$addFields": {
                "avg_cost_gp": {"$divide": ["$avg_cost_cp", 100]},
                "cost_variance_coefficient": {
                    "$cond": [
                        {"$gt": ["$avg_cost_cp", 0]},
                        {"$divide": ["$std_dev_cost", "$avg_cost_cp"]},
                        0
                    ]
                }
            }},
            
            {"$sort": {"avg_cost_cp": -1}}
        ]
        
        try:
            results = list(self.db.equipment.aggregate(pipeline))
            
            if results:
                self.print_subsection("Equipment Cost Analysis by Category")
                
                for category in results:
                    name = category["_id"] or "Unknown"
                    total = category["total_items"]
                    avg_cost = category["avg_cost_gp"]
                    variance_coeff = category["cost_variance_coefficient"]
                    
                    print(f"{name} ({total} items):")
                    print(f"  Average Cost: {avg_cost:.2f} gp")
                    print(f"  Price Range: {category['min_cost_cp']/100:.2f} - {category['max_cost_cp']/100:.2f} gp")
                    print(f"  Cost Variance: {variance_coeff:.2f}")
                    
                    if category["items_with_weight"] > 0:
                        avg_weight = category["avg_weight"]
                        cost_per_weight = category["avg_cost_per_weight"]
                        if cost_per_weight:
                            print(f"  Average Weight: {avg_weight:.1f} lbs")
                            print(f"  Cost/Weight Ratio: {cost_per_weight:.1f} cp/lb")
                    
                    # Analyze cost tier distribution
                    cost_tiers = Counter(category["cost_tiers"])
                    most_common_tier = cost_tiers.most_common(1)[0] if cost_tiers else ("Unknown", 0)
                    print(f"  Most Common Tier: {most_common_tier[0]} ({most_common_tier[1]}/{total})")
                    
                    # Show sample expensive and cheap items
                    sample_items = category["sample_items"]
                    if sample_items:
                        sorted_items = sorted(sample_items, key=lambda x: x["cost_cp"], reverse=True)
                        most_expensive = sorted_items[0]
                        cheapest = sorted_items[-1]
                        
                        print(f"  Most Expensive: {most_expensive['name']} ({most_expensive['cost_cp']/100:.0f} gp)")
                        print(f"  Cheapest: {cheapest['name']} ({cheapest['cost_cp']/100:.2f} gp)")
                    
                    print()
                    
        except Exception as e:
            print(f"Error in equipment cost analysis: {e}")

    # ================
    # RACE POTENTIAL ANALYSIS
    # ================
    
    def analyze_racial_competitive_advantage(self):
        """Analizza i vantaggi competitivi delle razze"""
        self.print_section_header("RACIAL COMPETITIVE ADVANTAGE ANALYSIS")
        
        pipeline = [
            # Stage 1: Estrae e normalizza le caratteristiche razziali
            {"$addFields": {
                "total_ability_bonuses": {
                    "$sum": {
                        "$map": {
                            "input": {"$ifNull": ["$ability_bonuses", []]},
                            "as": "bonus",
                            "in": "$bonus.bonus"
                        }
                    }
                },
                "unique_ability_bonuses": {"$size": {"$ifNull": ["$ability_bonuses", []]}},
                "base_speed": {"$ifNull": ["$speed", 30]},
                "size_category": "$size",
                "special_abilities_count": {"$size": {"$ifNull": ["$traits", []]}},
                "languages_count": {"$size": {"$ifNull": ["$languages", []]}},
                "proficiencies_count": {"$size": {"$ifNull": ["$proficiencies", []]}}
            }},
            
            # Stage 2: Calcola le metriche di competizione 
            {"$addFields": {
                "stat_optimization_score": {
                    "$add": [
                        {"$multiply": ["$total_ability_bonuses", 2]},
                        {"$multiply": ["$unique_ability_bonuses", 1.5]}
                    ]
                },
                "versatility_score": {
                    "$add": [
                        {"$multiply": ["$special_abilities_count", 1.5]},
                        {"$multiply": ["$languages_count", 0.5]},
                        {"$multiply": ["$proficiencies_count", 1.0]}
                    ]
                },
                "mobility_score": {
                    "$multiply": [
                        {"$divide": ["$base_speed", 30]},
                        3
                    ]
                },
                "size_advantage": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$size_category", "Small"]}, "then": 2},
                            {"case": {"$eq": ["$size_category", "Medium"]}, "then": 3},
                            {"case": {"$eq": ["$size_category", "Large"]}, "then": 1}
                        ],
                        "default": 1
                    }
                }
            }},
            
            # Stage 3: Calcola gli indici totali di competizione
            {"$addFields": {
                "competitive_index": {
                    "$add": [
                        {"$multiply": ["$stat_optimization_score", 0.4]},
                        {"$multiply": ["$versatility_score", 0.3]},
                        {"$multiply": ["$mobility_score", 0.2]},
                        {"$multiply": ["$size_advantage", 0.1]}
                    ]
                },
                "specialization_type": {
                    "$switch": {
                        "branches": [
                            {"case": {"$gte": ["$stat_optimization_score", 8]}, "then": "Stat Specialist"},
                            {"case": {"$gte": ["$versatility_score", 6]}, "then": "Utility Specialist"},
                            {"case": {"$gte": ["$mobility_score", 4]}, "then": "Mobility Specialist"},
                            {"case": {"$gte": ["$special_abilities_count", 4]}, "then": "Feature Rich"}
                        ],
                        "default": "Balanced"
                    }
                }
            }},
            
            # Stage 4: Determina il market tier
            {"$addFields": {
                "competitive_tier": {
                    "$switch": {
                        "branches": [
                            {"case": {"$gte": ["$competitive_index", 12]}, "then": "S-Tier"},
                            {"case": {"$gte": ["$competitive_index", 10]}, "then": "A-Tier"},
                            {"case": {"$gte": ["$competitive_index", 8]}, "then": "B-Tier"},
                            {"case": {"$gte": ["$competitive_index", 6]}, "then": "C-Tier"}
                        ],
                        "default": "D-Tier"
                    }
                }
            }},
            
            {"$sort": {"competitive_index": -1}}
        ]
        
        try:
            results = list(self.db.races.aggregate(pipeline))
            
            if results:
                self.print_subsection("Racial Competitive Rankings")
                
                print(f"{'Race':<20} {'Index':<6} {'Tier':<6} {'Stats':<6} {'Utility':<7} {'Speed':<6} {'Type':<17}")
                print("-" * 80)
                
                for race in results:
                    name = race["name"]
                    index = race["competitive_index"]
                    tier = race["competitive_tier"]
                    stats = race["stat_optimization_score"]
                    utility = race["versatility_score"]
                    speed = race["base_speed"]
                    spec_type = race["specialization_type"]
                    
                    print(f"{name:<20} {index:<6.1f} {tier:<6} {stats:<6.1f} {utility:<7.1f} {speed:<6} {spec_type:<17}")
                
                # Tier distribution
                print("\n" + "="*50)
                print("COMPETITIVE TIER DISTRIBUTION:")
                print("="*50)
                
                tier_counts = {}
                for race in results:
                    tier = race["competitive_tier"]
                    if tier not in tier_counts:
                        tier_counts[tier] = []
                    tier_counts[tier].append(race["name"])
                
                tier_order = ["S-Tier", "A-Tier", "B-Tier", "C-Tier", "D-Tier"]
                for tier in tier_order:
                    if tier in tier_counts:
                        races = tier_counts[tier]
                        print(f"\n{tier}: {len(races)} races")
                        print(f"  {', '.join(races)}")
                
                # Top performers analysis
                print("\n" + "="*50)
                print("TOP 5 COMPETITIVE ADVANTAGES:")
                print("="*50)
                
                for i, race in enumerate(results[:5], 1):
                    name = race["name"]
                    print(f"\n#{i} - {name} ({race['competitive_tier']}):")
                    print(f"  Competitive Index: {race['competitive_index']:.2f}")
                    print(f"  Specialization: {race['specialization_type']}")
                    print(f"  Total Ability Bonuses: +{race['total_ability_bonuses']}")
                    print(f"  Special Abilities: {race['special_abilities_count']}")
                    print(f"  Base Speed: {race['base_speed']} ft")
                    print(f"  Size: {race['size_category']}")
                    
        except Exception as e:
            print(f"Error in racial advantage analysis: {e}")

    # ==========================================
    # MAIN EXECUTION
    # ==========================================

def main():
    """Funzione principale per eseguire tutte le analisi"""
    print("=" * 70)
    print(" D&D 5E DATA ANALYZER - FINANCIAL SIMULATION BASE")
    print("=" * 70)
    
    # Connessione al database
    try:
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        client.admin.command('ping')
        db = client['HeroNomics']
        print(f"✓ Connected to MongoDB database: HeroNomics")
    except pymongo.errors.ConnectionFailure:
        print("✗ Error: Could not connect to MongoDB")
        sys.exit(1)
    
    # Inizializza analyzer
    analyzer = DNDDataAnalyzer(db)
    
    # Menu interattivo per scegliere le analisi
    analyses = {
        "1": ("Class Power & Survivability Metrics", analyzer.analyze_class_power_metrics),
        "2": ("Class Spell Distribution Patterns", analyzer.analyze_class_spell_distribution_patterns),
        "3": ("Class Resource Dependencies", analyzer.analyze_class_resource_dependencies),
        "4": ("Spell Rarity & Access Analysis", analyzer.analyze_spell_rarity_and_access),
        "5": ("Magic School Market Presence", analyzer.analyze_spell_school_market_presence),
        "6": ("Equipment Market Tiers", analyzer.analyze_equipment_market_tiers),
        "7": ("Racial Competitive Advantage", analyzer.analyze_racial_competitive_advantage),
        "8": ("Equipment Cost Distribution", analyzer.analyze_equipment_cost_distribution),
        "all": ("Run All Analyses", None)
    }
    
    print("\n" + "=" * 70)
    print("AVAILABLE ANALYSES:")
    print("=" * 70)
    
    for key, (description, _) in analyses.items():
        print(f"{key:>3}. {description}")
    
    print("\nEnter analysis number(s) separated by commas, or 'all' for everything:")
    choice = input("> ").strip().lower()
    
    if choice == 'all':
        selected_analyses = [key for key in analyses.keys() if key != 'all']
    else:
        selected_analyses = [c.strip() for c in choice.split(',')]
    
    # Esegui analisi selezionate
    for analysis_key in selected_analyses:
        if analysis_key in analyses and analysis_key != 'all':
            description, func = analyses[analysis_key]
            if func:
                try:
                    print(f"\n{'='*20} EXECUTING: {description.upper()} {'='*20}")
                    func()
                except Exception as e:
                    print(f"Error executing {description}: {e}")
    
    # Chiusura connessione
    client.close()
    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE - Database connection closed.")
    print("="*70)

if __name__ == "__main__":
    main()