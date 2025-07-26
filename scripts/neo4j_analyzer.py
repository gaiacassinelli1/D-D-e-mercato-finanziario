"""
D&D 5e Neo4j Graph Analytics Engine
===================================

Analisi avanzate dei dati D&D 5e usando Neo4j per scoprire pattern nascosti,
relazioni complesse e insights attraverso algoritmi di graph analytics.
"""

from neo4j import GraphDatabase
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import json
from dataclasses import dataclass
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
import sys

@dataclass
class GraphMetrics:
    """Metriche di rete"""
    centrality_scores: Dict[str, float]
    clustering_coefficient: float
    avg_path_length: float
    density: float
    modularity: float

class DNDGraphAnalyzer:
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "admin123", database: str = "heronomics"):
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password), database=database)
            self.verify_connection()
            print(f"✓ Connected to Neo4j at {uri}")
        except Exception as e:
            print(f"✗ Failed to connect to Neo4j: {e}")
            sys.exit(1)
    
    def verify_connection(self):
        """Verifica connessione e mostra statistiche database"""
        with self.driver.session() as session:
            # Conta nodi e relazioni
            node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
            rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
            
            print(f"Database stats: {node_count} nodes, {rel_count} relationships")
            
            # Mostra tipi di nodi
            node_types = session.run("""
                MATCH (n) 
                RETURN labels(n)[0] as type, count(*) as count 
                ORDER BY count DESC
            """).data()
            
            print("Node types:", {item['type']: item['count'] for item in node_types})

    def print_section_header(self, title: str, char: str = "="):
        """Stampa header decorativo"""
        print(f"\n{char * 70}")
        print(f" {title.upper()}")
        print(f"{char * 70}")

    def print_subsection(self, title: str):
        """Stampa sub-header"""
        print(f"\n--- {title} ---")

    # ==========================================
    # NETWORK TOPOLOGY ANALYSIS
    # ==========================================
    
    def analyze_spell_class_network(self):
        """Analizza la rete di connessioni tra spell e classi"""
        self.print_section_header("SPELL-CLASS NETWORK TOPOLOGY ANALYSIS")
        
        with self.driver.session() as session:
            # 1. ANALISI CENTRALITÀ - Chi sono i "nodi hub"?
            self.print_subsection("Centrality Analysis")
            
            # Degree Centrality - classi con più spell
            class_centrality = session.run("""
                MATCH (c:Class)-[:CAN_CAST]->(s:Spell)
                WITH c, count(s) as spell_count
                ORDER BY spell_count DESC
                RETURN c.name as class_name, spell_count,
                       round(spell_count * 1.0 / 319 * 100, 2) as network_influence
                LIMIT 10
            """).data()
            
            print("🎯 Most Central Classes (Spell Hub Analysis):")
            for item in class_centrality:
                print(f"  {item['class_name']}: {item['spell_count']} spells ({item['network_influence']}% network influence)")
            
            # Betweenness Centrality - spell che "collegano" classi diverse
            spell_bridges = session.run("""
                MATCH (c1:Class)-[:CAN_CAST]->(s:Spell)<-[:CAN_CAST]-(c2:Class)
                WHERE c1.name < c2.name
                WITH s, count(DISTINCT [c1.name, c2.name]) as bridge_count
                ORDER BY bridge_count DESC
                RETURN s.name as spell_name, s.level as level, bridge_count,
                       round(bridge_count * 1.0 / 12 * 100, 2) as bridge_percentage
                LIMIT 10
            """).data()
            
            print(f"\n🌉 Bridge Spells (Connect Most Class Pairs):")
            for item in spell_bridges:
                print(f"  {item['spell_name']} (L{item['level']}): bridges {item['bridge_count']} class pairs ({item['bridge_percentage']}%)")

    def analyze_multiclass_synergy_patterns(self):
        """Analizza le sinergie tra multiclassi attraverso spell condivisi"""
        self.print_section_header("MULTICLASS SYNERGY NETWORK ANALYSIS")
        
        with self.driver.session() as session:
            # 1. MATRICE DI COMPATIBILITÀ MULTICLASSE
            self.print_subsection("Multiclass Compatibility Matrix")
            
            synergy_matrix = session.run("""
                MATCH (c1:Class)-[:CAN_CAST]->(s:Spell)<-[:CAN_CAST]-(c2:Class)
                WHERE c1.name < c2.name
                WITH c1, c2, count(s) as shared_spells,
                     collect(DISTINCT s.name) as spell_list
                ORDER BY shared_spells DESC
                RETURN c1.name as class1, c2.name as class2, shared_spells,
                       round(shared_spells * 1.0 / 319 * 100, 2) as synergy_score
                LIMIT 15
            """).data()
            
            print("🤝 Best Multiclass Combinations (by Shared Spells):")
            for item in synergy_matrix:
                print(f"  {item['class1']} + {item['class2']}: {item['shared_spells']} shared spells (synergy: {item['synergy_score']}%)")
            
            # 2. ANALISI CLUSTER DI CLASSI SIMILI
            self.print_subsection("Class Clustering by Spell Similarity")
            
            # Usa Jaccard similarity per trovare cluster
            class_clusters = session.run("""
                MATCH (c1:Class)-[:CAN_CAST]->(s:Spell)<-[:CAN_CAST]-(c2:Class)
                WHERE c1.name <> c2.name
                WITH c1, c2, 
                     count(s) as intersection,
                     [(c1)-[:CAN_CAST]->(spell) | spell.name] as c1_spells,
                     [(c2)-[:CAN_CAST]->(spell) | spell.name] as c2_spells
                WITH c1, c2, intersection,
                     size(c1_spells) + size(c2_spells) - intersection as union_size
                WHERE union_size > 0
                WITH c1.name as class1, c2.name as class2,
                     round(intersection * 1.0 / union_size, 3) as jaccard_similarity
                WHERE jaccard_similarity > 0.1
                ORDER BY jaccard_similarity DESC
                RETURN class1, class2, jaccard_similarity
                LIMIT 10
            """).data()
            
            print("📊 Most Similar Class Pairs (Jaccard Similarity):")
            for item in class_clusters:
                similarity_pct = item['jaccard_similarity'] * 100
                print(f"  {item['class1']} ↔ {item['class2']}: {similarity_pct:.1f}% spell overlap")

    def analyze_spell_school_ecosystems(self):
        """Analizza gli ecosistemi delle scuole di magia come network"""
        self.print_section_header("MAGIC SCHOOL ECOSYSTEM ANALYSIS")
        
        with self.driver.session() as session:
            # 1. ANALISI DOMINANZA TERRITORIALE
            self.print_subsection("School Territorial Dominance")
            
            school_dominance = session.run("""
                MATCH (s:Spell)-[:BELONGS_TO]->(school:School)
                MATCH (s)<-[:CAN_CAST]-(c:Class)
                WITH school, count(DISTINCT c) as class_reach, 
                     count(s) as spell_count,
                     collect(DISTINCT c.name) as classes
                ORDER BY class_reach DESC, spell_count DESC
                RETURN school.name as school_name, spell_count, class_reach,
                       classes,
                       round(class_reach * 1.0 / 12 * 100, 1) as market_penetration,
                       round(spell_count * 1.0 / class_reach, 1) as spells_per_class
            """).data()
            
            print("🏰 School Market Dominance:")
            for item in school_dominance:
                print(f"  {item['school_name']}:")
                print(f"    Spells: {item['spell_count']}")
                print(f"    Class Reach: {item['class_reach']}/12 ({item['market_penetration']}%)")
                print(f"    Efficiency: {item['spells_per_class']} spells/class")
                print(f"    Classes: {', '.join(item['classes'][:4])}...")
                print()
            
            # 2. ANALISI COMPETIZIONE TRA SCUOLE
            self.print_subsection("Inter-School Competition Analysis")
            
            school_competition = session.run("""
                MATCH (s1:School)<-[:BELONGS_TO]-(spell1:Spell)<-[:CAN_CAST]-(c:Class)
                MATCH (c)-[:CAN_CAST]->(spell2:Spell)-[:BELONGS_TO]->(s2:School)
                WHERE s1.name < s2.name
                WITH s1, s2, count(DISTINCT c) as shared_classes,
                     collect(DISTINCT c.name) as competing_classes
                ORDER BY shared_classes DESC
                RETURN s1.name as school1, s2.name as school2, shared_classes,
                       competing_classes,
                       round(shared_classes * 1.0 / 12 * 100, 1) as competition_intensity
                LIMIT 10
            """).data()
            
            print("⚔️ Highest School Competition (Shared Classes):")
            for item in school_competition:
                print(f"  {item['school1']} vs {item['school2']}: {item['shared_classes']} shared classes ({item['competition_intensity']}%)")

    def analyze_spell_power_hierarchies(self):
        """Analizza le gerarchie di potere degli spell attraverso upgrade paths"""
        self.print_section_header("SPELL POWER HIERARCHY & UPGRADE PATH ANALYSIS")
        
        with self.driver.session() as session:
            # 1. ANALISI CATENE DI POTENZIAMENTO
            self.print_subsection("Spell Upgrade Chain Analysis")
            
            # Trova spell dello stesso nome ma livelli diversi (upgrade chains)
            upgrade_chains = session.run("""
                MATCH (low:Spell), (high:Spell)
                WHERE low.level < high.level 
                  AND (
                    low.name CONTAINS split(high.name, ' ')[0] OR
                    high.name CONTAINS split(low.name, ' ')[0] OR
                    low.name = high.name
                  )
                WITH low, high, abs(high.level - low.level) as level_gap
                WHERE level_gap <= 3
                ORDER BY low.name, low.level
                RETURN low.name as base_spell, low.level as base_level,
                       high.name as upgraded_spell, high.level as high_level,
                       level_gap
                LIMIT 15
            """).data()
            
            print("🔼 Spell Upgrade Chains Detected:")
            for item in upgrade_chains:
                print(f"  {item['base_spell']} (L{item['base_level']}) → {item['upgraded_spell']} (L{item['high_level']}) [gap: {item['level_gap']}]")
            
            # 2. ANALISI SPELL "APEX" - spell senza upgrade
            self.print_subsection("Apex Spells Analysis")
            
            apex_spells = session.run("""
                MATCH (s:Spell)
                WHERE s.level >= 7
                WITH s.school.name as school, s.level as level, 
                     count(*) as apex_count,
                     collect(s.name) as apex_spells
                ORDER BY level DESC, apex_count DESC
                RETURN school, level, apex_count, apex_spells
            """).data()
            
            print("👑 Apex Spells by School (Level 7-9):")
            for item in apex_spells:
                if item['apex_count'] > 0:
                    print(f"  {item['school']} Level {item['level']}: {item['apex_count']} spells")
                    for spell in item['apex_spells'][:3]:
                        print(f"    - {spell}")

    def analyze_equipment_dependency_networks(self):
        """Analizza le reti di dipendenze dell'equipaggiamento"""
        self.print_section_header("EQUIPMENT DEPENDENCY NETWORK ANALYSIS")
        
        with self.driver.session() as session:
            # 1. ANALISI PREREQUISITI E DIPENDENZE
            self.print_subsection("Equipment Prerequisite Chain Analysis")
            
            # Analizza le catene di prerequisiti basate su proficiency
            prereq_chains = session.run("""
                MATCH (c:Class)-[:HAS_PROFICIENCY]->(p:Proficiency)
                MATCH (e:Equipment)-[:REQUIRES]->(p)
                WITH c, count(e) as accessible_equipment,
                     collect(DISTINCT e.equipment_category.name) as categories,
                     collect(e.name) as equipment_list
                ORDER BY accessible_equipment DESC
                RETURN c.name as class_name, accessible_equipment, categories,
                       size(categories) as category_diversity,
                       equipment_list[0..3] as sample_equipment
                LIMIT 10
            """).data()
            
            if prereq_chains:
                print("🔗 Class Equipment Access Chains:")
                for item in prereq_chains:
                    print(f"  {item['class_name']}: {item['accessible_equipment']} items, {item['category_diversity']} categories")
                    print(f"    Sample: {', '.join(item['sample_equipment'])}")
            else:
                print("No equipment prerequisite relationships found.")
            
            # 2. ANALISI COSTO-UTILITÀ NETWORK
            self.print_subsection("Cost-Utility Network Analysis")
            
            cost_utility = session.run("""
                MATCH (e:Equipment)
                WHERE e.cost.quantity IS NOT NULL AND e.weight IS NOT NULL
                WITH e.equipment_category.name as category,
                     avg(e.cost.quantity) as avg_cost,
                     avg(e.weight) as avg_weight,
                     count(*) as item_count,
                     collect(e.name)[0..2] as sample_items
                WHERE item_count >= 3
                ORDER BY avg_cost DESC
                RETURN category, avg_cost, avg_weight, item_count,
                       round(avg_cost / avg_weight, 2) as cost_per_pound,
                       sample_items
                LIMIT 10
            """).data()
            
            print("💰 Equipment Category Economics:")
            for item in cost_utility:
                print(f"  {item['category']}:")
                print(f"    Avg Cost: {item['avg_cost']:.1f} gp")
                print(f"    Avg Weight: {item['avg_weight']:.1f} lbs")
                print(f"    Cost/Weight: {item['cost_per_pound']} gp/lb")
                print(f"    Sample: {', '.join(item['sample_items'])}")
                print()

    def analyze_racial_trait_clustering(self):
        """Analizza i cluster di tratti razziali per scoprire archetipi"""
        self.print_section_header("RACIAL TRAIT CLUSTERING & ARCHETYPE ANALYSIS")
        
        with self.driver.session() as session:
            # 1. ANALISI CLUSTER DI TRATTI
            self.print_subsection("Racial Archetype Discovery")
            
            trait_clusters = session.run("""
                MATCH (r:Race)-[:HAS_TRAIT]->(t:Trait)
                WITH r, collect(t.name) as traits, count(t) as trait_count
                UNWIND traits as trait
                MATCH (other_race:Race)-[:HAS_TRAIT]->(other_trait:Trait {name: trait})
                WHERE other_race <> r
                WITH r, trait, count(other_race) as trait_commonality,
                     collect(other_race.name) as races_with_trait
                WITH r, 
                     sum(trait_commonality) as total_commonality,
                     collect({trait: trait, commonality: trait_commonality}) as trait_analysis
                ORDER BY total_commonality ASC
                RETURN r.name as race_name, total_commonality,
                       [x IN trait_analysis WHERE x.commonality <= 2 | x.trait] as unique_traits,
                       [x IN trait_analysis WHERE x.commonality > 2 | x.trait] as common_traits
                LIMIT 10
            """).data()
            
            print("🧬 Racial Uniqueness Analysis:")
            for item in trait_clusters:
                print(f"  {item['race_name']} (uniqueness score: {item['total_commonality']}):")
                if item['unique_traits']:
                    print(f"    Unique traits: {', '.join(item['unique_traits'][:3])}")
                if item['common_traits']:
                    print(f"    Common traits: {', '.join(item['common_traits'][:3])}")
                print()
            
            # 2. ANALISI SINERGIE RAZZIALI CON CLASSI
            self.print_subsection("Race-Class Synergy Matrix")
            
            race_class_synergy = session.run("""
                MATCH (r:Race)-[:GRANTS_BONUS]->(ab:AbilityScore)
                MATCH (c:Class)-[:SAVES_WITH]->(ab)
                WITH r, c, count(ab) as synergy_score
                WHERE synergy_score > 0
                ORDER BY synergy_score DESC, r.name, c.name
                RETURN r.name as race_name, c.name as class_name, synergy_score,
                       'High' as synergy_level
                LIMIT 15
            """).data()
            
            if race_class_synergy:
                print("🎯 Optimal Race-Class Combinations (Ability Synergy):")
                current_race = None
                for item in race_class_synergy:
                    if item['race_name'] != current_race:
                        current_race = item['race_name']
                        print(f"  {current_race}:")
                    print(f"    → {item['class_name']} (synergy: {item['synergy_score']})")
            else:
                print("No direct ability score synergies found in current data model.")

    def analyze_spell_component_economy(self):
        """Analizza l'economia dei componenti degli spell"""
        self.print_section_header("SPELL COMPONENT ECONOMY & RESOURCE ANALYSIS")
        
        with self.driver.session() as session:
            # 1. ANALISI DIPENDENZE DA COMPONENTI
            self.print_subsection("Component Dependency Analysis")
            
            component_analysis = session.run("""
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
                ORDER BY spell_level
                RETURN spell_level,
                       round(verbal_count * 100.0 / total_spells, 1) as verbal_pct,
                       round(somatic_count * 100.0 / total_spells, 1) as somatic_pct,
                       round(material_count * 100.0 / total_spells, 1) as material_pct,
                       total_spells
            """).data()
            
            print("📊 Component Requirements by Spell Level:")
            print("Level | Verbal% | Somatic% | Material% | Total Spells")
            print("------|---------|----------|-----------|-------------")
            for item in component_analysis:
                level = item['spell_level']
                v_pct = item['verbal_pct']
                s_pct = item['somatic_pct']
                m_pct = item['material_pct']
                total = item['total_spells']
                print(f"  {level:2d}  |  {v_pct:5.1f}%  |  {s_pct:5.1f}%   |  {m_pct:5.1f}%    |     {total:2d}")
            
            # 2. ANALISI SPELL "RESOURCE INTENSIVE"
            self.print_subsection("Resource-Intensive Spell Analysis")
            
            resource_intensive = session.run("""
                MATCH (s:Spell)
                WHERE s.concentration = true AND size(s.components) = 3
                WITH s.school.name as school, count(s) as intensive_count,
                     collect(s.name) as intensive_spells,
                     avg(s.level) as avg_level
                WHERE intensive_count > 0
                ORDER BY intensive_count DESC
                RETURN school, intensive_count, avg_level, intensive_spells[0..3] as samples
            """).data()
            
            print("⚡ Most Resource-Intensive Schools (Concentration + All Components):")
            for item in resource_intensive:
                print(f"  {item['school']}: {item['intensive_count']} spells (avg L{item['avg_level']:.1f})")
                print(f"    Examples: {', '.join(item['samples'])}")

    def analyze_power_level_progression_curves(self):
        """Analizza le curve di progressione del potere attraverso i livelli"""
        self.print_section_header("POWER PROGRESSION CURVE ANALYSIS")
        
        with self.driver.session() as session:
            # 1. ANALISI CURVE DI POTENZA PER SCUOLA
            self.print_subsection("School Power Curve Analysis")
            
            power_curves = session.run("""
                MATCH (s:Spell)-[:BELONGS_TO]->(school:School)
                WITH school.name as school_name,
                     s.level as level,
                     count(s) as spell_count,
                     avg(s.level) as avg_complexity
                ORDER BY school_name, level
                WITH school_name,
                     collect({level: level, count: spell_count}) as distribution
                RETURN school_name, distribution,
                       [x IN distribution | x.count] as spell_counts,
                       size([x IN distribution WHERE x.count > 0]) as level_coverage
            """).data()
            
            print("📈 Spell Distribution Curves by School:")
            for item in power_curves:
                school = item['school_name']
                counts = item['spell_counts']
                coverage = item['level_coverage']
                total_spells = sum(counts)
                
                print(f"  {school} ({total_spells} spells, {coverage} level coverage):")
                
                # Simple ASCII bar chart
                max_count = max(counts) if counts else 1
                for i, (level_data, count) in enumerate(zip(item['distribution'], counts)):
                    level = level_data['level']
                    if count > 0:
                        bar = "█" * int(count * 20 / max_count)
                        print(f"    L{level}: {bar} ({count})")
                print()

    def analyze_network_resilience(self):
        """Analizza la resilienza della rete D&D alle interruzioni"""
        self.print_section_header("NETWORK RESILIENCE & ROBUSTNESS ANALYSIS")
        
        with self.driver.session() as session:
            # 1. ANALISI NODI CRITICI
            self.print_subsection("Critical Node Analysis")
            
            # Identifica spell che, se rimossi, disconnetterebbero classi
            critical_spells = session.run("""
                MATCH (c1:Class)-[:CAN_CAST]->(s:Spell)<-[:CAN_CAST]-(c2:Class)
                WHERE c1.name <> c2.name
                WITH s, count(DISTINCT [c1.name, c2.name]) as connection_count
                ORDER BY connection_count DESC
                RETURN s.name as spell_name, s.level as level, connection_count,
                       round(connection_count * 100.0 / 66, 1) as network_criticality
                LIMIT 10
            """).data()
            
            print("🔧 Network Critical Points (Spell Removal Impact):")
            for item in critical_spells:
                print(f"  {item['spell_name']} (L{item['level']}): connects {item['connection_count']} class pairs ({item['network_criticality']}% criticality)")
            
            # 2. ANALISI RIDONDANZA
            self.print_subsection("Network Redundancy Analysis")
            
            redundancy = session.run("""
                MATCH (s:Spell)
                WHERE s.level <= 3
                WITH s.school.name as school, s.level as level, count(s) as low_level_count
                ORDER BY low_level_count DESC
                RETURN school, level, low_level_count,
                       CASE WHEN low_level_count >= 10 THEN 'High'
                            WHEN low_level_count >= 5 THEN 'Medium'
                            ELSE 'Low' END as redundancy_level
            """).data()
            
            print("🛡️ School Redundancy (Low-Level Spell Availability):")
            for item in redundancy:
                if item['low_level_count'] > 0:
                    print(f"  {item['school']} L{item['level']}: {item['low_level_count']} spells ({item['redundancy_level']} redundancy)")

    # ==========================================
    # DATA SETUP & GRAPH CREATION
    # ==========================================

    def setup_graph_schema(self):
        """Crea lo schema del grafo e gli indici"""
        self.print_section_header("SETTING UP NEO4J GRAPH SCHEMA")
        
        with self.driver.session() as session:
            # Crea constraints e indici
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Spell) REQUIRE s.name IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Class) REQUIRE c.name IS UNIQUE", 
                "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Race) REQUIRE r.name IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Equipment) REQUIRE e.name IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (sch:School) REQUIRE sch.name IS UNIQUE"
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"✓ Created: {constraint}")
                except Exception as e:
                    print(f"⚠ Constraint exists: {constraint}")

    def import_data_from_mongodb(self, mongo_uri: str = "mongodb://localhost:27017/", db_name: str = "HeroNomics"):
        """Importa dati da MongoDB e crea il grafo Neo4j"""
        self.print_section_header("IMPORTING DATA FROM MONGODB TO NEO4J")
        
        try:
            import pymongo
            mongo_client = pymongo.MongoClient(mongo_uri)
            mongo_db = mongo_client[db_name]
            
            with self.driver.session() as session:
                # Pulisce dai dati esistenti
                session.run("MATCH (n) DETACH DELETE n")
                print("✓ Cleared existing Neo4j data")
                
                # Crea constraints
                constraints = [
                    "CREATE CONSTRAINT spell_name IF NOT EXISTS FOR (s:Spell) REQUIRE s.name IS UNIQUE",
                    "CREATE CONSTRAINT class_name IF NOT EXISTS FOR (c:Class) REQUIRE c.name IS UNIQUE", 
                    "CREATE CONSTRAINT race_name IF NOT EXISTS FOR (r:Race) REQUIRE r.name IS UNIQUE",
                    "CREATE CONSTRAINT school_name IF NOT EXISTS FOR (sch:School) REQUIRE sch.name IS UNIQUE",
                    "CREATE CONSTRAINT equipment_name IF NOT EXISTS FOR (e:Equipment) REQUIRE e.name IS UNIQUE"
                ]
                
                for constraint in constraints:
                    try:
                        session.run(constraint)
                        print(f"✓ Created constraint: {constraint.split()[2]}")
                    except Exception as e:
                        print(f"⚠️  Constraint exists: {constraint.split()[2]}")
                
                # 1. Importa le Spell
                print("\n📚 Importing Spells and Schools...")
                spells = list(mongo_db.spells.find())
                spell_count = 0
                
                for spell in spells:
                    try:
                        # Estrae le spell
                        name = spell.get('name', 'Unknown')
                        level = spell.get('level', 0)
                        concentration = spell.get('concentration', False)
                        ritual = spell.get('ritual', False)
                        components = spell.get('components', [])
                        duration = spell.get('duration', '')
                        casting_time = spell.get('casting_time', '')
                        range_val = spell.get('range', '')
                        
                        # Extract school from dict structure
                        school_data = spell.get('school', {})
                        if isinstance(school_data, dict):
                            school_name = school_data.get('name', 'Unknown')
                        else:
                            school_name = str(school_data) if school_data else 'Unknown'
                        
                        # crea spell e scuola
                        session.run("""
                            MERGE (s:Spell {name: $name})
                            SET s.level = $level,
                                s.concentration = $concentration,
                                s.ritual = $ritual,
                                s.components = $components,
                                s.duration = $duration,
                                s.casting_time = $casting_time,
                                s.range = $range
                            MERGE (sch:School {name: $school_name})
                            MERGE (s)-[:BELONGS_TO]->(sch)
                        """, name=name, level=level, concentration=concentration,
                             ritual=ritual, components=components, duration=duration,
                             casting_time=casting_time, range=range_val, school_name=school_name)
                        
                        spell_count += 1
                        
                        if spell_count % 50 == 0:
                            print(f"   Imported {spell_count} spells...")
                            
                    except Exception as e:
                        print(f"❌ Error importing spell {spell.get('name', 'Unknown')}: {e}")
                
                print(f"✅ Imported {spell_count} spells")
                
                # 2. Importa Classi
                print("\n⚔️ Importing Classes...")
                classes = list(mongo_db.classes.find())
                class_count = 0
                
                for cls in classes:
                    try:
                        name = cls.get('name', 'Unknown')
                        hit_die = cls.get('hit_die', 0)
                        
                        session.run("""
                            MERGE (c:Class {name: $name})
                            SET c.hit_die = $hit_die
                        """, name=name, hit_die=hit_die)
                        
                        class_count += 1
                        
                    except Exception as e:
                        print(f"❌ Error importing class {cls.get('name', 'Unknown')}: {e}")
                
                print(f"✅ Imported {class_count} classes")
                
                # 3. Crea le relazioni classe-spell
                print("\n🔗 Creating Class-Spell Relationships...")
                relationship_count = 0
                
                for spell in spells:
                    spell_name = spell.get('name', '')
                    classes_data = spell.get('classes', [])
                    
                    if not spell_name or not classes_data:
                        continue
                    
                    for cls_data in classes_data:
                        try:
                            # Estrae il nome della classe dalla struttura del dict
                            if isinstance(cls_data, dict):
                                class_name = cls_data.get('name', '')
                            else:
                                class_name = str(cls_data)
                            
                            if class_name:
                                session.run("""
                                    MATCH (c:Class {name: $class_name})
                                    MATCH (s:Spell {name: $spell_name})
                                    MERGE (c)-[:CAN_CAST]->(s)
                                """, class_name=class_name, spell_name=spell_name)
                                
                                relationship_count += 1
                                
                        except Exception as e:
                            print(f"⚠️ Error creating relationship for {spell_name}: {e}")
                
                print(f"✅ Created {relationship_count} Class-Spell relationships")
                
                # 4. Importa le razze con abilità bonus
                print("\n🏃 Importing Races...")
                races = list(mongo_db.races.find())
                race_count = 0
                
                for race in races:
                    try:
                        name = race.get('name', 'Unknown')
                        size = race.get('size', 'Unknown')
                        speed = race.get('speed', 0)
                        
                        session.run("""
                            MERGE (r:Race {name: $name})
                            SET r.size = $size, r.speed = $speed
                        """, name=name, size=size, speed=speed)
                        
                        # Aggiunge abilità bonus
                        ability_bonuses = race.get('ability_bonuses', [])
                        for bonus in ability_bonuses:
                            if isinstance(bonus, dict):
                                ability_data = bonus.get('ability_score', {})
                                if isinstance(ability_data, dict):
                                    ability_name = ability_data.get('name', '')
                                    bonus_value = bonus.get('bonus', 0)
                                    
                                    if ability_name:
                                        session.run("""
                                            MATCH (r:Race {name: $race_name})
                                            MERGE (a:AbilityScore {name: $ability_name})
                                            MERGE (r)-[:GRANTS_BONUS {value: $bonus_value}]->(a)
                                        """, race_name=name, ability_name=ability_name, bonus_value=bonus_value)
                        
                        race_count += 1
                        
                    except Exception as e:
                        print(f"❌ Error importing race {race.get('name', 'Unknown')}: {e}")
                
                print(f"✅ Imported {race_count} races")
                
                # 5. Importa l'equipaggiamento
                print("\n⚡ Importing Equipment...")
                equipment = list(mongo_db.equipment.find())
                equipment_count = 0
                
                for item in equipment:
                    try:
                        name = item.get('name', 'Unknown')
                        weight = item.get('weight', 0)
                        
                        # Estrae la categoria dal dict
                        category_data = item.get('equipment_category', {})
                        if isinstance(category_data, dict):
                            category = category_data.get('name', 'Unknown')
                        else:
                            category = str(category_data) if category_data else 'Unknown'
                        
                        # Extract cost from dict structure
                        cost_data = item.get('cost', {})
                        cost_quantity = cost_data.get('quantity', 0) if isinstance(cost_data, dict) else 0
                        cost_unit = cost_data.get('unit', 'gp') if isinstance(cost_data, dict) else 'gp'
                        
                        session.run("""
                            MERGE (e:Equipment {name: $name})
                            SET e.weight = $weight,
                                e.cost_quantity = $cost_quantity,
                                e.cost_unit = $cost_unit,
                                e.category = $category
                            MERGE (cat:EquipmentCategory {name: $category})
                            MERGE (e)-[:BELONGS_TO_CATEGORY]->(cat)
                        """, name=name, weight=weight, cost_quantity=cost_quantity,
                             cost_unit=cost_unit, category=category)
                        
                        equipment_count += 1
                        
                        if equipment_count % 50 == 0:
                            print(f"   Imported {equipment_count} equipment items...")
                            
                    except Exception as e:
                        print(f"❌ Error importing equipment {item.get('name', 'Unknown')}: {e}")
                
                print(f"✅ Imported {equipment_count} equipment items")
                
                # 6. Crea le relazioni classe-punteggioAbilità per i saving throws
                print("\n🎯 Creating Class-Ability Relationships...")
                ability_relationship_count = 0
                
                for cls in classes:
                    class_name = cls.get('name', '')
                    saving_throws = cls.get('saving_throws', [])
                    
                    for save in saving_throws:
                        try:
                            if isinstance(save, dict):
                                ability_name = save.get('name', '')
                            else:
                                ability_name = str(save)
                            
                            if ability_name and class_name:
                                session.run("""
                                    MATCH (c:Class {name: $class_name})
                                    MERGE (a:AbilityScore {name: $ability_name})
                                    MERGE (c)-[:SAVES_WITH]->(a)
                                """, class_name=class_name, ability_name=ability_name)
                                
                                ability_relationship_count += 1
                                
                        except Exception as e:
                            print(f"⚠️ Error creating saving throw relationship: {e}")
                
                print(f"✅ Created {ability_relationship_count} Class-AbilityScore relationships")
                
                # 7. Verifica i risultati dell'import
                print("\n📊 Verifying Import Results...")
                
                result = session.run("MATCH (n) RETURN labels(n)[0] as type, count(*) as count ORDER BY count DESC")
                
                print("Node counts:")
                total_nodes = 0
                for record in result:
                    node_type = record['type']
                    count = record['count']
                    total_nodes += count
                    print(f"   {node_type}: {count}")
                
                rel_result = session.run("MATCH ()-[r]->() RETURN type(r) as rel_type, count(*) as count ORDER BY count DESC")
                
                print("Relationship counts:")
                total_rels = 0
                for record in rel_result:
                    rel_type = record['rel_type']
                    count = record['count']
                    total_rels += count
                    print(f"   {rel_type}: {count}")
                
                print(f"\n✅ Total: {total_nodes} nodes, {total_rels} relationships")
                
            mongo_client.close()
            print("\n🎉 Data import completed successfully!")
            
        except ImportError:
            print("❌ pymongo not installed. Install with: pip install pymongo")
        except Exception as e:
            print(f"❌ Error importing data: {e}")

    # ==========================================
    # ADVANCED GRAPH ALGORITHMS
    # ==========================================

    def run_community_detection(self):
        """Esegue algoritmi di community detection per trovare cluster nascosti"""
        self.print_section_header("COMMUNITY DETECTION & CLUSTERING ANALYSIS")
        
        with self.driver.session() as session:
            # 1. LOUVAIN COMMUNITY DETECTION per classi
            self.print_subsection("Class Communities (Louvain Algorithm)")
            
            try:
                # Prima installa il graph catalog se necessario
                session.run("""
                    CALL gds.graph.exists('dnd-class-network') YIELD exists
                    CALL CASE WHEN exists THEN gds.graph.drop('dnd-class-network') ELSE gds.util.NaN() END
                    YIELD graphName
                    RETURN graphName
                """)
                
                # Crea proiezione del grafo per algoritmi GDS
                session.run("""
                    CALL gds.graph.project(
                        'dnd-class-network',
                        'Class',
                        {
                            SHARES_SPELL: {
                                type: 'CAN_CAST',
                                aggregation: 'COUNT'
                            }
                        },
                        {
                            relationshipProperties: 'weight'
                        }
                    )
                """)
                
                # Esegui Louvain community detection
                communities = session.run("""
                    CALL gds.louvain.stream('dnd-class-network')
                    YIELD nodeId, communityId
                    WITH gds.util.asNode(nodeId) AS class, communityId
                    RETURN communityId, collect(class.name) as classes, count(*) as size
                    ORDER BY size DESC
                """).data()
                
                print("🏘️ Detected Class Communities:")
                for i, community in enumerate(communities):
                    print(f"  Community {community['communityId']}: {', '.join(community['classes'])}")
                
                # Cleanup
                session.run("CALL gds.graph.drop('dnd-class-network')")
                
            except Exception as e:
                print(f"⚠ GDS not available, using alternative clustering: {e}")
                
                # Alternativa: analisi semplice delle spell condivise
                alt_communities = session.run("""
                    MATCH (c1:Class)-[:CAN_CAST]->(s:Spell)<-[:CAN_CAST]-(c2:Class)
                    WHERE c1.name < c2.name
                    WITH c1, c2, count(s) as shared_spells
                    WHERE shared_spells > 20
                    RETURN c1.name as class1, c2.name as class2, shared_spells
                    ORDER BY shared_spells DESC
                    LIMIT 10
                """).data()
                
                print("🔗 Strong Class Pairs (>20 shared spells):")
                for pair in alt_communities:
                    print(f"  {pair['class1']} ↔ {pair['class2']}: {pair['shared_spells']} shared spells")

    def analyze_information_flow(self):
        """Analizza il flusso di informazioni attraverso la rete"""
        self.print_section_header("INFORMATION FLOW & KNOWLEDGE NETWORKS")
        
        with self.driver.session() as session:
            # 1. ANALISI "KNOWLEDGE BROKERS" - classi che collegano scuole diverse
            self.print_subsection("Knowledge Brokers Analysis")
            
            knowledge_brokers = session.run("""
                MATCH (c:Class)-[:CAN_CAST]->(s:Spell)-[:BELONGS_TO]->(sch:School)
                WITH c, count(DISTINCT sch) as school_diversity, 
                     collect(DISTINCT sch.name) as schools,
                     count(s) as total_spells
                WHERE school_diversity > 5
                ORDER BY school_diversity DESC, total_spells DESC
                RETURN c.name as class_name, school_diversity, schools, total_spells,
                       round(school_diversity * 1.0 / total_spells * 100, 2) as diversity_ratio
                LIMIT 8
            """).data()
            
            print("🧠 Top Knowledge Brokers (Multi-School Access):")
            for broker in knowledge_brokers:
                print(f"  {broker['class_name']}:")
                print(f"    Schools: {broker['school_diversity']}/8 ({', '.join(broker['schools'][:4])}...)")
                print(f"    Spells: {broker['total_spells']}")
                print(f"    Diversity Ratio: {broker['diversity_ratio']}%")
                print()
            
            # 2. ANALISI "INFORMATION BOTTLENECKS"
            self.print_subsection("Information Bottleneck Analysis")
            
            bottlenecks = session.run("""
                MATCH (sch1:School)<-[:BELONGS_TO]-(s:Spell)<-[:CAN_CAST]-(c:Class)
                MATCH (c)-[:CAN_CAST]->(s2:Spell)-[:BELONGS_TO]->(sch2:School)
                WHERE sch1.name <> sch2.name
                WITH c, count(DISTINCT [sch1.name, sch2.name]) as bridge_connections,
                     collect(DISTINCT sch1.name) + collect(DISTINCT sch2.name) as connected_schools
                ORDER BY bridge_connections DESC
                RETURN c.name as bridge_class, bridge_connections,
                       size(apoc.coll.toSet(connected_schools)) as unique_schools_connected
                LIMIT 5
            """).data()
            
            if bottlenecks:
                print("🌉 Information Bridge Classes:")
                for bridge in bottlenecks:
                    print(f"  {bridge['bridge_class']}: bridges {bridge['bridge_connections']} school pairs")
            else:
                # Fallback senza APOC
                simple_bridges = session.run("""
                    MATCH (c:Class)-[:CAN_CAST]->(s:Spell)-[:BELONGS_TO]->(sch:School)
                    WITH c, collect(DISTINCT sch.name) as schools
                    WHERE size(schools) > 4
                    RETURN c.name as class_name, schools, size(schools) as school_count
                    ORDER BY school_count DESC
                    LIMIT 5
                """).data()
                
                print("🌉 Multi-School Bridge Classes:")
                for bridge in simple_bridges:
                    print(f"  {bridge['class_name']}: connects {bridge['school_count']} schools")

    def analyze_evolutionary_pressures(self):
        """Analizza le 'pressioni evolutive' nel sistema D&D"""
        self.print_section_header("EVOLUTIONARY PRESSURE & META ANALYSIS")
        
        with self.driver.session() as session:
            # 1. ANALISI "SURVIVAL FITNESS" delle scuole di magia
            self.print_subsection("School Survival Fitness Analysis")
            
            school_fitness = session.run("""
                MATCH (sch:School)<-[:BELONGS_TO]-(s:Spell)
                MATCH (s)<-[:CAN_CAST]-(c:Class)
                WITH sch, 
                     count(DISTINCT s) as spell_diversity,
                     count(DISTINCT c) as class_adoption,
                     avg(s.level) as avg_complexity,
                     sum(CASE WHEN s.level <= 3 THEN 1 ELSE 0 END) as accessible_spells
                WITH sch, spell_diversity, class_adoption, avg_complexity, accessible_spells,
                     (spell_diversity * class_adoption + accessible_spells * 2 - avg_complexity * 3) as fitness_score
                ORDER BY fitness_score DESC
                RETURN sch.name as school, fitness_score, spell_diversity, class_adoption, 
                       round(avg_complexity, 1) as avg_complexity, accessible_spells
            """).data()
            
            print("🧬 School Evolutionary Fitness Rankings:")
            print("School           | Fitness | Diversity | Adoption | Complexity | Accessible")
            print("-----------------|---------|-----------|----------|------------|------------")
            for school in school_fitness:
                name = school['school'][:15].ljust(15)
                fitness = f"{school['fitness_score']:.1f}".rjust(7)
                diversity = f"{school['spell_diversity']}".rjust(8)
                adoption = f"{school['class_adoption']}".rjust(8)
                complexity = f"{school['avg_complexity']}".rjust(10)
                accessible = f"{school['accessible_spells']}".rjust(10)
                print(f" {name} | {fitness} | {diversity} | {adoption} | {complexity} | {accessible}")
            
            # 2. ANALISI "COMPETITIVE ADVANTAGES"
            self.print_subsection("Competitive Advantage Analysis")
            
            advantages = session.run("""
                MATCH (s:Spell)-[:BELONGS_TO]->(sch:School)
                WHERE s.concentration = false AND size(s.components) < 3
                WITH sch, count(s) as low_cost_spells,
                     collect(s.name)[0..3] as sample_spells
                ORDER BY low_cost_spells DESC
                RETURN sch.name as school, low_cost_spells, sample_spells,
                       CASE WHEN low_cost_spells > 15 THEN 'High Efficiency'
                            WHEN low_cost_spells > 8 THEN 'Medium Efficiency'
                            ELSE 'Low Efficiency' END as efficiency_class
                LIMIT 8
            """).data()
            
            print("⚡ School Efficiency Advantages (Low-Cost Spells):")
            for adv in advantages:
                print(f"  {adv['school']}: {adv['low_cost_spells']} efficient spells ({adv['efficiency_class']})")
                print(f"    Examples: {', '.join(adv['sample_spells'])}")

    def generate_strategic_recommendations(self):
        """Genera raccomandazioni strategiche basate sull'analisi del grafo"""
        self.print_section_header("STRATEGIC RECOMMENDATIONS & INSIGHTS")
        
        with self.driver.session() as session:
            # 1. RACCOMANDAZIONI MULTICLASSE
            self.print_subsection("Optimal Multiclass Recommendations")
            
            multiclass_recs = session.run("""
                MATCH (c1:Class)-[:CAN_CAST]->(s:Spell)<-[:CAN_CAST]-(c2:Class)
                WHERE c1.name < c2.name AND s.level <= 2
                WITH c1, c2, count(s) as low_level_synergy,
                     collect(s.name)[0..3] as shared_low_spells
                WHERE low_level_synergy > 5
                MATCH (c1)-[:SAVES_WITH]->(a:AbilityScore)<-[:SAVES_WITH]-(c2)
                WITH c1, c2, low_level_synergy, shared_low_spells, count(a) as stat_synergy
                ORDER BY (low_level_synergy * 2 + stat_synergy * 5) DESC
                RETURN c1.name as primary_class, c2.name as secondary_class, 
                       low_level_synergy, stat_synergy, shared_low_spells,
                       (low_level_synergy * 2 + stat_synergy * 5) as synergy_score
                LIMIT 8
            """).data()
            
            print("🎯 Top Multiclass Synergy Combinations:")
            for rec in multiclass_recs:
                print(f"  {rec['primary_class']} / {rec['secondary_class']}:")
                print(f"    Synergy Score: {rec['synergy_score']}")
                print(f"    Shared Low-Level Spells: {rec['low_level_synergy']}")
                print(f"    Stat Synergy: {rec['stat_synergy']} abilities")
                print(f"    Key Spells: {', '.join(rec['shared_low_spells'])}")
                print()
            
            # 2. RACCOMANDAZIONI TACTICAL
            self.print_subsection("Tactical Play Recommendations")
            
            tactical_insights = session.run("""
                MATCH (s:Spell)-[:BELONGS_TO]->(sch:School)
                WHERE s.level >= 3 AND s.concentration = false
                WITH sch, count(s) as high_impact_spells, avg(s.level) as avg_level
                ORDER BY high_impact_spells DESC
                RETURN sch.name as school, high_impact_spells, round(avg_level, 1) as avg_level,
                       CASE WHEN high_impact_spells > 8 THEN 'Offensive Powerhouse'
                            WHEN high_impact_spells > 5 THEN 'Versatile Arsenal' 
                            ELSE 'Specialized Tools' END as tactical_role
                LIMIT 6
            """).data()
            
            print("⚔️ Tactical School Roles:")
            for insight in tactical_insights:
                print(f"  {insight['school']}: {insight['tactical_role']}")
                print(f"    High-Impact Spells: {insight['high_impact_spells']} (avg L{insight['avg_level']})")
            
            # 3. RESOURCE OPTIMIZATION
            self.print_subsection("Resource Optimization Insights") 
            
            resource_opts = session.run("""
                MATCH (s:Spell)
                WHERE s.ritual = true OR (s.concentration = false AND s.level <= 1)
                WITH s.school.name as school, 
                     sum(CASE WHEN s.ritual = true THEN 1 ELSE 0 END) as ritual_count,
                     sum(CASE WHEN s.concentration = false AND s.level <= 1 THEN 1 ELSE 0 END) as efficient_cantrips,
                     count(s) as resource_efficient_total
                WHERE resource_efficient_total > 3
                ORDER BY resource_efficient_total DESC
                RETURN school, ritual_count, efficient_cantrips, resource_efficient_total,
                       round(resource_efficient_total * 100.0 / 40, 1) as efficiency_percentage
                LIMIT 5
            """).data()
            
            print("💎 Resource Efficiency Leaders:")
            for opt in resource_opts:
                print(f"  {opt['school']}: {opt['resource_efficient_total']} resource-efficient options")
                print(f"    Rituals: {opt['ritual_count']}, Low-cost options: {opt['efficient_cantrips']}")
                print(f"    Efficiency Rating: {opt['efficiency_percentage']}%")

    # ==========================================
    # MAIN EXECUTION & UTILITIES
    # ==========================================

    def run_all_analyses(self):
        """Esegue tutte le analisi in sequenza"""
        analyses = [
            ("Network Topology", self.analyze_spell_class_network),
            ("Multiclass Synergies", self.analyze_multiclass_synergy_patterns),
            ("School Ecosystems", self.analyze_spell_school_ecosystems),
            ("Power Hierarchies", self.analyze_spell_power_hierarchies),
            ("Equipment Networks", self.analyze_equipment_dependency_networks),
            ("Racial Clustering", self.analyze_racial_trait_clustering),
            ("Component Economy", self.analyze_spell_component_economy),
            ("Power Progression", self.analyze_power_level_progression_curves),
            ("Network Resilience", self.analyze_network_resilience),
            ("Community Detection", self.run_community_detection),
            ("Information Flow", self.analyze_information_flow),
            ("Evolutionary Pressure", self.analyze_evolutionary_pressures),
            ("Strategic Recommendations", self.generate_strategic_recommendations)
        ]
        
        for name, func in analyses:
            try:
                print(f"\n🔄 Running {name} Analysis...")
                func()
            except Exception as e:
                print(f"❌ Error in {name}: {e}")
                continue

    def close(self):
        """Chiude la connessione"""
        if self.driver:
            self.driver.close()
            print("✓ Neo4j connection closed")

# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    """Funzione principale"""
    print("="*80)
    print("  D&D 5E NEO4J GRAPH ANALYTICS - ADVANCED NETWORK ANALYSIS")  
    print("="*80)
    
    # Setup analyzer
    try:
        analyzer = DNDGraphAnalyzer()
    except Exception as e:
        print(f"Failed to initialize analyzer: {e}")
        return
    
    # Menu interattivo
    while True:
        print("\n" + "="*50)
        print("AVAILABLE ANALYSES:")
        print("="*50)
        
        options = {
            "1": ("Setup Graph Schema", analyzer.setup_graph_schema),
            "2": ("Import Data from MongoDB", lambda: analyzer.import_data_from_mongodb()),
            "3": ("Network Topology Analysis", analyzer.analyze_spell_class_network),
            "4": ("Multiclass Synergy Analysis", analyzer.analyze_multiclass_synergy_patterns),
            "5": ("School Ecosystem Analysis", analyzer.analyze_spell_school_ecosystems),
            "6": ("Power Hierarchy Analysis", analyzer.analyze_spell_power_hierarchies),
            "7": ("Equipment Network Analysis", analyzer.analyze_equipment_dependency_networks),
            "8": ("Racial Trait Clustering", analyzer.analyze_racial_trait_clustering),
            "9": ("Component Economy Analysis", analyzer.analyze_spell_component_economy),
            "10": ("Power Progression Curves", analyzer.analyze_power_level_progression_curves),
            "11": ("Network Resilience Analysis", analyzer.analyze_network_resilience),
            "12": ("Community Detection", analyzer.run_community_detection),
            "13": ("Information Flow Analysis", analyzer.analyze_information_flow),
            "14": ("Evolutionary Pressure Analysis", analyzer.analyze_evolutionary_pressures),
            "15": ("Strategic Recommendations", analyzer.generate_strategic_recommendations),
            "all": ("Run All Analyses", analyzer.run_all_analyses),
            "q": ("Quit", None)
        }
        
        for key, (description, _) in options.items():
            print(f"{key:>3}. {description}")
        
        choice = input("\nSelect analysis (or 'q' to quit): ").strip().lower()
        
        if choice == 'q':
            break
        elif choice in options:
            description, func = options[choice]
            if func:
                try:
                    print(f"\n{'='*20} EXECUTING: {description.upper()} {'='*20}")
                    func()
                except Exception as e:
                    print(f"❌ Error executing {description}: {e}")
        else:
            print("Invalid choice. Please try again.")
    
    # Cleanup
    analyzer.close()
    print("\n" + "="*80)
    print("GRAPH ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()