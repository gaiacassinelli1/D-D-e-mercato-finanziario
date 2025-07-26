import os
import json
from pymongo import MongoClient

# Connessione a MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['HeroNomics']

# Cartella principale
base_folder = 'dnd_data'

# File di riferimento speciale
reference_file = '_reference_mapping'
reference_path = os.path.join(base_folder, reference_file)
reference_json = reference_path + '.json'

def import_json_files(folder_path, collection_name):
    """Importa tutti i file JSON da una cartella in una collezione MongoDB"""
    collection = db[collection_name]
    file_count = 0
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Inserisci in base al tipo (array o oggetto singolo)
                    if isinstance(data, list):
                        if data:  # Verifica che la lista non sia vuota
                            collection.insert_many(data)
                            file_count += len(data)
                    else:
                        collection.insert_one(data)
                        file_count += 1
                        
            except json.JSONDecodeError as e:
                print(f"Errore JSON in {file_path}: {e}")
            except Exception as e:
                print(f"Errore durante l'importazione di {file_path}: {e}")
    
    return file_count

# Gestione del file reference_mapping (se esiste)
if os.path.exists(reference_json) and os.path.isfile(reference_json):
    # Se è un singolo file JSON
    print(f"Importazione file {reference_file}.json...")
    count = import_json_files(base_folder, reference_file)  # passa solo il nome base
    print(f"Importati {count} documenti in reference_mapping")

elif os.path.isdir(reference_path):
    # Se è una cartella
    print(f"Importazione cartella {reference_file}...")
    count = import_json_files(reference_path, '_reference_mapping')
    print(f"Importati {count} documenti in reference_mapping")

else:
    print(f"❌ File o cartella non trovati: {reference_json} o {reference_path}")

# Loop sulle sottocartelle
print("\nImportazione sottocartelle...")
for subfolder in os.listdir(base_folder):
    subfolder_path = os.path.join(base_folder, subfolder)
    
    # Salta il file/cartella reference_mapping già gestito
    if subfolder == reference_file:
        continue
    
    # Processa solo le cartelle
    if os.path.isdir(subfolder_path):
        print(f"Elaborazione cartella: {subfolder}")
        
        # Usa il nome della cartella come nome della collezione
        collection_name = subfolder.lower().replace(' ', '_').replace('-', '_')
        
        # Importa tutti i JSON della sottocartella
        count = import_json_files(subfolder_path, collection_name)
        
        if count > 0:
            print(f"  -> Importati {count} documenti nella collezione '{collection_name}'")
        else:
            print(f"  -> Nessun file JSON trovato in {subfolder}")

print("\nImportazione completata!")

# Mostra un riepilogo delle collezioni create
print("\nCollezioni create:")
collection_names = db.list_collection_names()
for name in sorted(collection_names):
    count = db[name].count_documents({})
    print(f"  - {name}: {count} documenti")
