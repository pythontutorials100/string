#this code inputs csv and json and gives extended csv. working final 

import csv
import json
from collections import defaultdict

# Adjust input/output file names as needed
CSV_INPUT_FILE = "inputcsv.csv"
JSON_INPUT_FILE = "blen.json"
CSV_OUTPUT_FILE = "extended_defects.csv"

def region_to_edge_node_comp(region_value: str) -> str:
    """
    Map CSV 'region' values (e.g., 'le', 'te', etc.)
    to the 'edge_node_comp' values in the JSON (e.g., 'LENODES', 'TENODES').
    Adjust this function’s logic to suit your data.
    """
    if region_value.lower() == "le":
        return "LENODES"
    elif region_value.lower() == "te":
        return "TENODES"
    # You can handle more cases here if needed
    return "LENODES"  # default fallback, or raise an error

def main():
    # 1. Read the CSV file into a list of dicts
    with open(CSV_INPUT_FILE, mode="r", newline="", encoding="utf-8") as f:
        csv_reader = csv.DictReader(f)
        csv_data = list(csv_reader)

    # 2. Read the JSON file
    with open(JSON_INPUT_FILE, mode="r", encoding="utf-8") as f:
        blends_data = json.load(f)

    # The JSON structure is something like:
    # {
    #   "blends": {
    #       "airfoils": {
    #           "1": [
    #               { "blend_on_edge": {...} },
    #               { "blend_on_edge": {...} }
    #           ],
    #           "3": [
    #               { "blend_on_edge": {...} }
    #           ]
    #       }
    #   }
    # }
    airfoils_dict = blends_data["blends"]["airfoils"]

    # 3. Build a lookup that groups blend data by (airfoil_number, edge_node_comp),
    #    so we can pop them in sequence to match each CSV defect row.
    json_map = defaultdict(list)

    # Loop over each airfoil number in the JSON
    for airfoil_str, blend_list in airfoils_dict.items():
        # blend_list is a list of objects like { "blend_on_edge": {...} }
        for blend_item in blend_list:
            blend_data = blend_item["blend_on_edge"]
            edge_node_comp = blend_data["edge_node_comp"]
            # Store in our dictionary under a tuple key (airfoil_str, edge_node_comp)
            json_map[(airfoil_str, edge_node_comp)].append(blend_data)

    # 4. Merge CSV row by row
    output_rows = []
    for row in csv_data:
        # e.g. row["airfoil number"] might be '1'
        airfoil_id = row["airfoil number"].strip()
        region_value = row["region"].strip().lower()
        
        # Convert CSV 'region' to the JSON's edge_node_comp
        edge_node_comp = region_to_edge_node_comp(region_value)
        
        # Try to pop the matching blend data entry
        # If none is found (or the list is empty), we can either skip or fill with blanks.
        blend_info = {}
        blend_list_key = (airfoil_id, edge_node_comp)
        if blend_list_key in json_map and len(json_map[blend_list_key]) > 0:
            blend_info = json_map[blend_list_key].pop(0)  # get first unused blend
        else:
            # Provide blank or default values if no matching JSON entry
            blend_info = {
                "fillet_radius": "",
                "blend_depth": "",
                "blend_length": "",
                "flat_length": "",
                "prop_factor": "",
                "blend_loc": "",
                "edge_node_comp": ""
            }
        
        # 5. Build the extended row
        extended_row = dict(row)  # start with all original CSV columns
        # Add the JSON-based keys
        # (You can add or remove fields as needed; these are from your JSON example)
        extended_row["fillet_radius"] = blend_info.get("fillet_radius", "")
        extended_row["blend_depth"]   = blend_info.get("blend_depth", "")
        extended_row["blend_length"]  = blend_info.get("blend_length", "")
        extended_row["flat_length"]   = blend_info.get("flat_length", "")
        extended_row["prop_factor"]   = blend_info.get("prop_factor", "")
        extended_row["blend_loc"]     = blend_info.get("blend_loc", "")
        extended_row["edge_node_comp"] = blend_info.get("edge_node_comp", "")
        
        output_rows.append(extended_row)

    # 6. Determine column order for writing. We'll collect all keys
    #    from the first extended row for convenience.
    if not output_rows:
        print("No rows found in CSV input. Exiting.")
        return
    
    fieldnames = list(output_rows[0].keys())

    # 7. Write the extended CSV
    with open(CSV_OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Extended CSV written to {CSV_OUTPUT_FILE}")

if __name__ == "__main__":
    main()

