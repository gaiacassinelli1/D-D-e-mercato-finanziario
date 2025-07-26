import json
import os
from pathlib import Path

def process_json_files(source_folder="dnd_data"):
    """
    Processa tutti i file JSON nella cartella specificata.
    Per ogni file crea una sottocartella col nome dell'oggetto principale
    e divide gli items in file JSON separati.
    """
    
    # Verifica che la cartella esista
    source_path = Path(source_folder)
    if not source_path.exists():
        print(f"Errore: La cartella '{source_folder}' non esiste!")
        return
    
    # Trova tutti i file JSON nella cartella
    json_files = list(source_path.glob("*.json"))
    
    if not json_files:
        print(f"Nessun file JSON trovato nella cartella '{source_folder}'")
        return
    
    print(f"Trovati {len(json_files)} file JSON da processare...")
    
    for json_file in json_files:
        print(f"\nProcessando: {json_file.name}")
        
        try:
            # Legge il file JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Estrae il nome dalla table_info
            if 'table_info' not in data or 'name' not in data['table_info']:
                print(f"  ⚠️  Saltato: manca 'table_info.name' in {json_file.name}")
                continue
                
            folder_name = data['table_info']['name']
            
            # Crea la sottocartella
            output_folder = source_path / folder_name
            output_folder.mkdir(exist_ok=True)
            print(f"  📁 Creata cartella: {folder_name}")
            
            # Processa gli items
            if 'items' not in data:
                print(f"  ⚠️  Nessun array 'items' trovato in {json_file.name}")
                continue
                
            items = data['items']
            if not items:
                print(f"  ⚠️  Array 'items' vuoto in {json_file.name}")
                continue
            
            # Crea un file JSON per ogni item
            for item in items:
                if 'name' not in item:
                    print(f"  ⚠️  Item senza 'name' saltato")
                    continue
                    
                item_name = item['name']
                # Pulisce il nome per usarlo come nome file
                safe_name = "".join(c for c in item_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')
                
                item_file = output_folder / f"{safe_name}.json"
                
                # Scrive il file JSON per questo item
                with open(item_file, 'w', encoding='utf-8') as f:
                    json.dump(item, f, indent=2, ensure_ascii=False)
                
                print(f"  ✅ Creato: {folder_name}/{safe_name}.json")
            
            print(f"  🎉 Completato {json_file.name}: {len(items)} file creati")
            
        except json.JSONDecodeError as e:
            print(f"  ❌ Errore parsing JSON in {json_file.name}: {e}")
        except Exception as e:
            print(f"  ❌ Errore generico con {json_file.name}: {e}")
    
    print(f"\n🏁 Processamento completato!")

def main():
    """
    Funzione principale
    """
    # Nome della cartella
    source_folder = "dnd_data"
    
    print("🚀 Avvio processamento file JSON D&D...")
    print(f"📂 Cartella sorgente: {source_folder}")
    
    process_json_files(source_folder)

if __name__ == "__main__":
    main()
