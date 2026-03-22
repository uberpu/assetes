import sys
import os
import json
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from projects.shared.db import get_connection, load_q_values

def export_model_to_json():
    print("Exporting AI Brain (Q-Table) to JSON...")

    q_table = {}
    try:
        q_table = load_q_values()
    except Exception as e:
        print(f"[!] Could not connect to the database. ({e})")
        return

    # Structure for JSON: { "state": { "action": q_value } }
    model_data = {}
    for (state, action), q_value in q_table.items():
        if state not in model_data:
            model_data[state] = {}
        model_data[state][str(action)] = q_value

    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs')
    models_dir = os.path.join(docs_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    num_states = len(model_data)

    # Save the specific model version
    model_filename = f"model_v{timestamp}.json"
    model_filepath = os.path.join(models_dir, model_filename)

    with open(model_filepath, 'w', encoding='utf-8') as f:
        json.dump(model_data, f, indent=2)

    print(f"[+] Saved model with {num_states} known states to {model_filepath}")

    # Update manifest
    manifest_filepath = os.path.join(models_dir, 'manifest.json')
    manifest = []

    if os.path.exists(manifest_filepath):
        try:
            with open(manifest_filepath, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except json.JSONDecodeError:
            pass

    # Add new entry to the top of the manifest
    new_entry = {
        "id": f"v{timestamp}",
        "filename": model_filename,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "states": num_states,
        "description": f"AI Brain with {num_states} learned board states."
    }
    manifest.insert(0, new_entry)

    with open(manifest_filepath, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"[+] Updated manifest.json with entry {new_entry['id']}")

if __name__ == '__main__':
    export_model_to_json()
