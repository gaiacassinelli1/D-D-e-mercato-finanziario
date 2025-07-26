import requests
import json
import os
import time
from typing import Dict, List, Any, Set
from urllib.parse import urlparse, urljoin

class DNDDataCollector:
    def __init__(self, base_url: str = "https://www.dnd5eapi.co"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DND-Data-Collector/1.0'
        })
        
        # Definizione delle tabelle principali
        self.main_tables = {
            "ability-scores": "/api/2014/ability-scores",
            "alignments": "/api/2014/alignments",
            "backgrounds": "/api/2014/backgrounds",
            "classes": "/api/2014/classes",
            "conditions": "/api/2014/conditions",
            "damage-types": "/api/2014/damage-types",
            "equipment": "/api/2014/equipment",
            "equipment-categories": "/api/2014/equipment-categories",
            "feats": "/api/2014/feats",
            "features": "/api/2014/features",
            "languages": "/api/2014/languages",
            "magic-items": "/api/2014/magic-items",
            "magic-schools": "/api/2014/magic-schools",
            "monsters": "/api/2014/monsters",
            "proficiencies": "/api/2014/proficiencies",
            "races": "/api/2014/races",
            "rule-sections": "/api/2014/rule-sections",
            "rules": "/api/2014/rules",
            "skills": "/api/2014/skills",
            "spells": "/api/2014/spells",
            "subclasses": "/api/2014/subclasses",
            "subraces": "/api/2014/subraces",
            "traits": "/api/2014/traits",
            "weapon-properties": "/api/2014/weapon-properties"
        }
        
        # Dizionario per mappare URL alle tabelle principali
        self.url_to_table = {}
        for table_name, url_path in self.main_tables.items():
            full_url = urljoin(self.base_url, url_path)
            self.url_to_table[full_url] = table_name
            self.url_to_table[url_path] = table_name
        
        # Set per tenere traccia degli URL già processati
        self.processed_urls: Set[str] = set()
        
        # Dizionario per mappare URL agli indici univoci
        self.url_to_index: Dict[str, str] = {}
        
    def make_request(self, url: str) -> Dict[str, Any]:
        """Fa una richiesta HTTP con gestione degli errori e rate limiting"""
        try:
            # Normalizza l'URL
            if not url.startswith('http'):
                url = urljoin(self.base_url, url)
                
            if url in self.processed_urls:
                print(f"URL già processato: {url}")
                return {}
                
            print(f"Richiesta a: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Rate limiting gentile
            time.sleep(0.1)
            
            self.processed_urls.add(url)
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Errore nella richiesta a {url}: {e}")
            return {}
    
    def is_main_table_url(self, url: str) -> tuple[bool, str]:
        """Verifica se un URL appartiene a una tabella principale"""
        # Normalizza l'URL
        if not url.startswith('http'):
            url = urljoin(self.base_url, url)
            
        # Controlla se l'URL base corrisponde a una tabella principale
        for table_name, table_path in self.main_tables.items():
            table_full_url = urljoin(self.base_url, table_path)
            if url.startswith(table_full_url):
                return True, table_name
                
        return False, ""
    
    def create_reference_index(self, url: str, table_name: str) -> str:
        """Crea un indice univoco per un URL che fa riferimento a una tabella principale"""
        # Estrae l'identificatore dall'URL (ultima parte del path)
        path_parts = urlparse(url).path.strip('/').split('/')
        if path_parts:
            identifier = path_parts[-1]
            reference_index = f"{table_name}:{identifier}"
            self.url_to_index[url] = reference_index
            return reference_index
        return url
    
    def process_nested_data(self, data: Any, parent_context: str = "") -> Any:
        """Processa ricorsivamente i dati per espandere URL annidati o creare riferimenti"""
        if isinstance(data, dict):
            processed_dict = {}
            
            for key, value in data.items():
                if key == "url" and isinstance(value, str):
                    # Verifica se è un URL di tabella principale
                    is_main, table_name = self.is_main_table_url(value)
                    
                    if is_main:
                        # Crea un riferimento invece di espandere
                        reference_index = self.create_reference_index(value, table_name)
                        processed_dict[f"{key}_ref"] = reference_index
                        processed_dict[key] = value  # Mantieni anche l'URL originale
                    else:
                        # URL non di tabella principale - espandi se necessario
                        processed_dict[key] = value
                        
                        # Se il contesto suggerisce che dovremmo espandere questo URL
                        if parent_context in ["results", "spells", "equipment"] and value not in self.processed_urls:
                            expanded_data = self.make_request(value)
                            if expanded_data:
                                processed_dict[f"{key}_expanded"] = self.process_nested_data(
                                    expanded_data, 
                                    f"{parent_context}_expanded"
                                )
                else:
                    # Processa ricorsivamente altri tipi di dati
                    processed_dict[key] = self.process_nested_data(value, key)
                    
            return processed_dict
            
        elif isinstance(data, list):
            return [self.process_nested_data(item, parent_context) for item in data]
        else:
            return data
    
    def collect_table_data(self, table_name: str, url_path: str) -> Dict[str, Any]:
        """Raccoglie tutti i dati per una specifica tabella"""
        print(f"\n=== Raccogliendo dati per: {table_name} ===")
        
        # Prima richiesta per ottenere la lista
        list_data = self.make_request(url_path)
        if not list_data:
            return {}
            
        processed_data = {
            "table_info": {
                "name": table_name,
                "base_url": url_path,
                "total_count": list_data.get("count", 0)
            },
            "items": []
        }
        
        # Se abbiamo una lista di risultati, espandiamo ogni elemento
        if "results" in list_data:
            for i, item in enumerate(list_data["results"]):
                print(f"  Processando item {i+1}/{len(list_data['results'])}: {item.get('name', 'Unknown')}")
                
                if "url" in item:
                    # Ottieni i dettagli completi dell'item
                    item_details = self.make_request(item["url"])
                    if item_details:
                        # Processa i dati annidati
                        processed_item = self.process_nested_data(item_details, "item_details")
                        processed_data["items"].append(processed_item)
                    else:
                        # Se non riesci a ottenere i dettagli, salva almeno i dati base
                        processed_data["items"].append(self.process_nested_data(item, "basic_item"))
                else:
                    processed_data["items"].append(self.process_nested_data(item, "basic_item"))
        else:
            # Se non c'è una lista results, processa direttamente i dati
            processed_data = self.process_nested_data(list_data, table_name)
            
        return processed_data
    
    def save_data(self, data: Dict[str, Any], filename: str, output_dir: str = "dnd_data"):
        """Salva i dati in un file JSON"""
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{filename}.json")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Dati salvati in: {filepath}")
        except Exception as e:
            print(f"Errore nel salvataggio di {filepath}: {e}")
    
    def collect_all_data(self, output_dir: str = "dnd_data"):
        """Raccoglie tutti i dati dalle API di D&D"""
        print("Iniziando la raccolta dati D&D 5e API...")
        print(f"Numero di tabelle da processare: {len(self.main_tables)}")
        
        # Crea directory di output
        os.makedirs(output_dir, exist_ok=True)
        
        all_collected_data = {}
        reference_mapping = {}
        
        for table_name, url_path in self.main_tables.items():
            try:
                table_data = self.collect_table_data(table_name, url_path)
                if table_data:
                    all_collected_data[table_name] = table_data
                    self.save_data(table_data, table_name, output_dir)
                    
            except Exception as e:
                print(f"Errore nel processare la tabella {table_name}: {e}")
                continue
        
        # Salva il mapping dei riferimenti
        if self.url_to_index:
            reference_mapping = {
                "description": "Mapping degli URL ai riferimenti univoci delle tabelle principali",
                "mappings": self.url_to_index
            }
            self.save_data(reference_mapping, "_reference_mapping", output_dir)
        
        # Salva un file di riepilogo
        summary = {
            "collection_info": {
                "total_tables": len(self.main_tables),
                "successfully_collected": len(all_collected_data),
                "total_processed_urls": len(self.processed_urls),
                "total_references_created": len(self.url_to_index)
            },
            "table_summary": {
                table_name: {
                    "item_count": len(data.get("items", [])) if isinstance(data.get("items"), list) else 0,
                    "has_data": bool(data)
                }
                for table_name, data in all_collected_data.items()
            }
        }
        
        self.save_data(summary, "_collection_summary", output_dir)
        
        print(f"\n=== Raccolta completata! ===")
        print(f"Tabelle raccolte: {len(all_collected_data)}/{len(self.main_tables)}")
        print(f"URL processati: {len(self.processed_urls)}")
        print(f"Riferimenti creati: {len(self.url_to_index)}")
        print(f"File salvati in: {output_dir}/")
        
        return all_collected_data

def main():
    """Funzione principale per eseguire la raccolta dati"""
    collector = DNDDataCollector()
    
    # Raccogli tutti i dati
    collected_data = collector.collect_all_data("dnd_data")
    
    print("\nRaccolta dati completata!")
    return collected_data

if __name__ == "__main__":
    main()
