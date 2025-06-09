import sqlite3
import json
from fetch_api import fetch_neighbors_securely
from db_handler import write_to_neighbors, write_to_neighbors_checked_time_update, DB_PATH


def get_existing_neighbors():
    """Lädt bestehende Nachbarn aus der Datenbank"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM neighbors")
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        # Konvertiert zu Dictionary-Liste für einfacheren Vergleich
        neighbors_dict = {}
        for row in rows:
            neighbor = dict(zip(columns, row))
            neighbors_dict[neighbor['id']] = neighbor
        
        return neighbors_dict

def clear_neighbors_table():
    """Löscht alle Daten aus der neighbors Tabelle"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM neighbors")
        conn.commit()

def compare_and_update_checked_time(existing_neighbors, new_neighbors):
    """Vergleicht checked time und schreibt Unterschiede in update Tabelle"""
    for neighbor in new_neighbors:
        neighbor_id = neighbor['id']
        new_checked_time = neighbor.get('totalCheckedTime', 0)
        
        if neighbor_id in existing_neighbors:
            old_checked_time = existing_neighbors[neighbor_id].get('totalCheckedTime', 0)
            
            # Prüft ob sich die checked time geändert hat
            if new_checked_time != old_checked_time:
                # Berechnet die Differenz
                time_difference = new_checked_time - old_checked_time
                
                # Erstellt Update-Record
                update_data = neighbor.copy()
                update_data['totalCheckedTimeUpdate'] = time_difference
                
                # Schreibt in update Tabelle
                write_to_neighbors_checked_time_update(update_data)
                print(f"Checked time update für {neighbor.get('fullName', neighbor_id)}: {time_difference} Stunden")

def main():
    """Hauptfunktion der Anwendung"""
    print("Starte Neighborhood Check...")
    
    # Setup Datenbank
    
    # Lade bestehende Nachbarn
    existing_neighbors = get_existing_neighbors()
    print(f"Gefunden: {len(existing_neighbors)} bestehende Nachbarn")
    
    # API-Aufruf
    print("Rufe API auf...")
    new_data = fetch_neighbors_securely()
    
    if new_data is None:
        print("Fehler beim Abrufen der API-Daten. Programm wird beendet.")
        return
    
    # Prüft ob die Daten als String zurückgegeben wurden und konvertiert zu JSON
    if isinstance(new_data, str):
        try:
            new_data = json.loads(new_data)
        except json.JSONDecodeError:
            print("Fehler beim Parsen der API-Daten. Ungültiges JSON-Format.")
            return
    
    # Stellt sicher, dass new_data eine Liste ist
    if not isinstance(new_data, list):
        # Prüft ob die Daten ein Objekt mit neighbors Array sind
        if isinstance(new_data, dict) and 'neighbors' in new_data:
            new_data = new_data['neighbors']
            print(f"Neighbors Array aus API-Response extrahiert")
        else:
            print("Unerwartetes Datenformat von der API. Erwartet wird eine Liste oder ein Objekt mit 'neighbors' Array.")
            return
    
    print(f"API lieferte {len(new_data)} Nachbarn")
    
    # Vergleiche checked time und update wenn nötig
    compare_and_update_checked_time(existing_neighbors, new_data)
    
    # Lösche alte neighbors Tabelle
    print("Lösche alte Nachbarn-Daten...")
    clear_neighbors_table()
    
    # Schreibe neue Daten
    print("Schreibe neue Nachbarn-Daten...")
    for neighbor in new_data:
        # Konvertiere Listen zu JSON-Strings für SQLite-Kompatibilität
        processed_neighbor = neighbor.copy()
        for key, value in processed_neighbor.items():
            if isinstance(value, list):
                processed_neighbor[key] = json.dumps(value)
        
        # Ergänze fehlende Felder mit Standardwerten
        required_fields = {
            'airport': None,
            'totalCheckedTime': 0,
            'fullName': processed_neighbor.get('id', 'Unknown')
        }
        
        for field, default_value in required_fields.items():
            if field not in processed_neighbor:
                processed_neighbor[field] = default_value
        
        write_to_neighbors(processed_neighbor)
    
    print(f"Erfolgreich {len(new_data)} Nachbarn aktualisiert!")

if __name__ == "__main__":
    main()