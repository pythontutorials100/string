import csv

# Path to your extended CSV with defect+blend data
INPUT_CSV = "extended_defects.csv"
# Path to the final CSV with TBox + ABox lines
OUTPUT_CSV = "output_extended_csv.csv"

# 1) TBox lines: subClassOf statements
TBOX_LINES = [
    "Act of Inspection,Class,rdfs:subClassOf,Act of Measuring,Class",
    "Airfoil Defect,Class,rdfs:subClassOf,Defect,Class",
    "Tip,Class,rdfs:subClassOf,Fiat Object Part,Class",
    "Airfoil,Class,rdfs:subClassOf,Material Artifact,Class",
    "Edge,Class,rdfs:subClassOf,Fiat Object Part,Class",
    "Defect,Class,rdfs:subClassOf,Quality,Class",
    "Leading Edge,Class,rdfs:subClassOf,Edge,Class",
    "Trailing Edge,Class,rdfs:subClassOf,Edge,Class",
    "Surface,Class,rdfs:subClassOf,Fiat Object Part,Class",
    "Platform,Class,rdfs:subClassOf,Fiat Object Part,Class",
    "Defect Region,Class,rdfs:subClassOf,Fiat Object Part,Class",
    "Defect Depth,Class,rdfs:subClassOf,Distance Measurement Information Content Entity,Class",
    "Defect Length,Class,rdfs:subClassOf,Distance Measurement Information Content Entity,Class",
    "Defect Index2 Distance to Datum,Class,rdfs:subClassOf,Distance Measurement Information Content Entity,Class",
    "Defect Index1 Distance to Datum,Class,rdfs:subClassOf,Distance Measurement Information Content Entity,Class",
    "Blend On Edge Length Measurement,Class,rdfs:subClassOf,Distance Measurement Information Content Entity,Class",
    "Blend On Edge Flat Length Measurement,Class,rdfs:subClassOf,Distance Measurement Information Content Entity,Class",
    "Blend On Edge Depth Measurement,Class,rdfs:subClassOf,Distance Measurement Information Content Entity,Class",
    "Blend On Edge Fillet Radius Measurement,Class,rdfs:subClassOf,Distance Measurement Information Content Entity,Class",
    "Blend On Edge Proportional Factor Measurement,Class,rdfs:subClassOf,Ratio Measurement Information Content Entity,Class",
    "Blend On Edge Location Measurement,Class,rdfs:subClassOf,Distance Measurement Information Content Entity,Class",
    "Blend On Edge Node Component,Class,rdfs:subClassOf,Nominal Measurement Information Content Entity,Class"
]

def region_label(csv_region: str) -> str:
    """
    Convert short region codes from CSV (e.g., 'le', 'te', 'surface')
    into the label used in your individuals (e.g., 'leading edge', 'trailing edge').
    """
    csv_region = csv_region.strip().lower()
    if csv_region == "le":
        return "leading edge"
    elif csv_region == "te":
        return "trailing edge"
    elif csv_region == "surface":
        return "surface"
    return csv_region  # fallback

def datum_label(csv_datum: str) -> str:
    """
    Convert 'tip'/'platform' into a lowercased label, e.g. 'tip', 'platform'.
    """
    return csv_datum.strip().lower()

def generate_measurement_triples(
    base_label: str, 
    value_str: str, 
    measure_class: str,
    described_ind: str
) -> list:
    """
    Helper to create lines for numeric (or blank) measurement data.
    If value_str is empty, returns [] (skip).
    Otherwise returns lines like:
      Defect1 Depth IBE,Individual,has decimal value,0.092,Literal
      ...
      Defect1 Depth MICE,Individual,describes,airfoil defect1,Individual
      ...
    """
    if not value_str:
        return []  # no measurement
    lines = []
    ibe_name = f"{base_label} IBE"
    mice_name = f"{base_label} MICE"
    lines.append(f"{ibe_name},Individual,has decimal value,{value_str},Literal")
    # assume inches for demonstration
    lines.append(f"{ibe_name},Individual,uses measurement unit,inch measurement unit,Individual")
    lines.append(f"{ibe_name},Individual,rdf:type,Information Bearing Entity,Class")
    lines.append(f"{mice_name},Individual,generically depends on,{ibe_name},Individual")
    lines.append(f"{mice_name},Individual,describes,{described_ind},Individual")
    lines.append(f"{mice_name},Individual,rdf:type,{measure_class},Class")
    return lines

def generate_triples_for_row(row: dict) -> list:
    """
    Given one row of extended CSV data, return a list of 
    "Subject,SubjectType,Predicate,Object,ObjectType" lines representing the instance data (ABox).
    """
    triples = []

    # Basic fields
    defect_id   = row["number"].strip()            # "1"
    airfoil_num = row["airfoil number"].strip()    # "1"
    region_val  = row["region"].strip().lower()    # "le"
    datum_val   = row["datum (1&2)"].strip()       # "tip"
    insp_method = row["inspect method"].strip()    # "scanbox"

    # Key individuals
    defect_ind        = f"airfoil defect{defect_id}"
    defect_region_ind = f"defect{defect_id} region"
    region_ind        = f"{region_label(region_val)}{defect_id}"
    datum_ind         = f"{datum_label(datum_val)}{airfoil_num}"
    airfoil_ind       = f"airfoil{airfoil_num}"
    inspection_ind    = f"inspection{defect_id}"

    # Defect numeric columns
    dmg_index1_str = row.get("Dmg. Edge Closest to Datum", "").strip()
    dmg_index2_str = row.get("Dmg. Edge Furthest to Datum", "").strip()
    dmg_depth_str  = row.get("Dmg. Depth", "").strip()
    dmg_length_str = row.get("Dmg. Length", "").strip()

    # 1) Index1 Distance
    triples += generate_measurement_triples(
        base_label=f"Defect{defect_id} Index1Dist",
        value_str=dmg_index1_str,
        measure_class="Defect Index1 Distance to Datum",
        described_ind=defect_ind
    )

    # 2) Index2 Distance
    triples += generate_measurement_triples(
        base_label=f"Defect{defect_id} Index2Dist",
        value_str=dmg_index2_str,
        measure_class="Defect Index2 Distance to Datum",
        described_ind=defect_ind
    )

    # 3) Depth
    triples += generate_measurement_triples(
        base_label=f"Defect{defect_id} Depth",
        value_str=dmg_depth_str,
        measure_class="Defect Depth",
        described_ind=defect_ind
    )

    # 4) Length
    triples += generate_measurement_triples(
        base_label=f"Defect{defect_id} Length",
        value_str=dmg_length_str,
        measure_class="Defect Length",
        described_ind=defect_ind
    )

    # A few designative ICEs:
    # Inspect method
    if insp_method:
        insp_ibe = f"insp{defect_id} IBE"
        insp_ice = f"insp{defect_id} ICE"
        triples.append(f"{insp_ibe},Individual,has text value,{insp_method},Literal")
        triples.append(f"{insp_ibe},Individual,rdf:type,Information Bearing Entity,Class")
        triples.append(f"{insp_ice},Individual,designates,{inspection_ind},Individual")
        triples.append(f"{insp_ice},Individual,generically depends on,{insp_ibe},Individual")
        triples.append(f"{insp_ice},Individual,rdf:type,Designative Information Content Entity,Class")
        # the inspection itself
        triples.append(f"{inspection_ind},Individual,rdf:type,Act of Inspection,Class")

    # Airfoil number
    if airfoil_num:
        airfoil_ibe = f"airfoil id{airfoil_num} IBE"
        airfoil_ice = f"airfoil ID{airfoil_num} ICE"
        triples.append(f"{airfoil_ibe},Individual,has text value,{airfoil_num},Literal")
        triples.append(f"{airfoil_ibe},Individual,rdf:type,Information Bearing Entity,Class")
        triples.append(f"{airfoil_ice},Individual,designates,{airfoil_ind},Individual")
        triples.append(f"{airfoil_ice},Individual,rdf:type,Part Number,Class")
        triples.append(f"{airfoil_ice},Individual,generically depends on,{airfoil_ibe},Individual")

    # Defect ID
    defect_ibe = f"airfoil defect id{defect_id} IBE"
    defect_ice = f"airfoil defect ID{defect_id} ICE"
    triples.append(f"{defect_ibe},Individual,has text value,{defect_id},Literal")
    triples.append(f"{defect_ibe},Individual,rdf:type,Information Bearing Entity,Class")
    triples.append(f"{defect_ice},Individual,designates,{defect_ind},Individual")
    triples.append(f"{defect_ice},Individual,rdf:type,Designative Information Content Entity,Class")
    triples.append(f"{defect_ice},Individual,generically depends on,{defect_ibe},Individual")

    # The airfoil
    triples.append(f"{airfoil_ind},Individual,rdf:type,Airfoil,Class")

    # The defect
    triples.append(f"{defect_ind},Individual,rdf:type,Airfoil Defect,Class")
    triples.append(f"{defect_ind},Individual,is object of,{inspection_ind},Individual")

    # The defect region
    triples.append(f"{defect_region_ind},Individual,rdf:type,Defect Region,Class")
    triples.append(f"{defect_ind},Individual,inheres in,{defect_region_ind},Individual")

    # region (leading edge/trailing edge/surface)
    if region_val == "le":
        triples.append(f"{region_ind},Individual,rdf:type,Leading Edge,Class")
    elif region_val == "te":
        triples.append(f"{region_ind},Individual,rdf:type,Trailing Edge,Class")
    elif region_val == "surface":
        triples.append(f"{region_ind},Individual,rdf:type,Surface,Class")
    else:
        # fallback
        triples.append(f"{region_ind},Individual,rdf:type,Edge,Class")

    # link region to that edge
    triples.append(f"{defect_region_ind},Individual,has continuant part,{region_ind},Individual")

    # The tip or platform
    if datum_val == "tip":
        triples.append(f"{datum_ind},Individual,rdf:type,Tip,Class")
    elif datum_val == "platform":
        triples.append(f"{datum_ind},Individual,rdf:type,Platform,Class")
    else:
        triples.append(f"{datum_ind},Individual,rdf:type,Fiat Object Part,Class")

    # link airfoil to (tip or platform) and region
    triples.append(f"{airfoil_ind},Individual,has continuant part,{datum_ind},Individual")
    triples.append(f"{airfoil_ind},Individual,has continuant part,{defect_region_ind},Individual")

    # measured from part => tip or platform
    if dmg_index1_str:
        triples.append(f"Defect{defect_id} Index1Dist MICE,Individual,measured from part,{datum_ind},Individual")
    if dmg_index2_str:
        triples.append(f"Defect{defect_id} Index2Dist MICE,Individual,measured from part,{datum_ind},Individual")

    # link airfoil to leading/trailing/surface
    triples.append(f"{airfoil_ind},Individual,has continuant part,{region_ind},Individual")

    # BLEND columns
    fillet_radius_str = row.get("fillet_radius", "").strip()
    blend_depth_str   = row.get("blend_depth", "").strip()
    blend_length_str  = row.get("blend_length", "").strip()
    flat_length_str   = row.get("flat_length", "").strip()
    prop_factor_str   = row.get("prop_factor", "").strip()
    blend_loc_str     = row.get("blend_loc", "").strip()
    edge_node_comp_str = row.get("edge_node_comp", "").strip()

    # If there's any blend info, create the process and associated measurements
    if (fillet_radius_str or blend_depth_str or blend_length_str or
        flat_length_str or prop_factor_str or blend_loc_str or edge_node_comp_str):

        blend_proc_ind = f"blend_on_edge_{defect_id}"
        # The process
        triples.append(f"{blend_proc_ind},Individual,is about,{defect_ind},Individual")
        triples.append(f"{blend_proc_ind},Individual,has participant,{region_ind},Individual")
        triples.append(f"{blend_proc_ind},Individual,rdf:type,Blend on Edge Process,Class")

        # Depth
        triples += generate_measurement_triples(
            base_label=f"{blend_proc_ind} depth",
            value_str=blend_depth_str,
            measure_class="Blend On Edge Depth Measurement",
            described_ind=blend_proc_ind
        )

        # Length
        triples += generate_measurement_triples(
            base_label=f"{blend_proc_ind} length",
            value_str=blend_length_str,
            measure_class="Blend On Edge Length Measurement",
            described_ind=blend_proc_ind
        )

        # Flat length
        triples += generate_measurement_triples(
            base_label=f"{blend_proc_ind} flatlength",
            value_str=flat_length_str,
            measure_class="Blend On Edge Flat Length Measurement",
            described_ind=blend_proc_ind
        )

        # Fillet radius
        if fillet_radius_str:
            triples += generate_measurement_triples(
                base_label=f"{blend_proc_ind} filletradius",
                value_str=fillet_radius_str,
                measure_class="Blend On Edge Fillet Radius Measurement",
                described_ind=blend_proc_ind
            )

        # Proportional factor (dimensionless ratio)
        if prop_factor_str:
            ibe_pf = f"{blend_proc_ind} propfactor_IBE"
            mice_pf = f"{blend_proc_ind} propfactor_MICE"
            triples.append(f"{ibe_pf},Individual,has decimal value,{prop_factor_str},Literal")
            triples.append(f"{ibe_pf},Individual,rdf:type,Information Bearing Entity,Class")
            triples.append(f"{mice_pf},Individual,generically depends on,{ibe_pf},Individual")
            triples.append(f"{mice_pf},Individual,describes,{blend_proc_ind},Individual")
            triples.append(f"{mice_pf},Individual,rdf:type,Blend On Edge Proportional Factor Measurement,Class")

        # Blend location
        if blend_loc_str:
            triples += generate_measurement_triples(
                base_label=f"{blend_proc_ind} loc",
                value_str=blend_loc_str,
                measure_class="Blend On Edge Location Measurement",
                described_ind=blend_proc_ind
            )

        # Edge node comp (a text field)
        if edge_node_comp_str:
            ibe_comp = f"{blend_proc_ind} node_comp_IBE"
            mice_comp = f"{blend_proc_ind} node_comp_MICE"
            triples.append(f"{ibe_comp},Individual,has text value,{edge_node_comp_str},Literal")
            triples.append(f"{ibe_comp},Individual,rdf:type,Information Bearing Entity,Class")
            triples.append(f"{mice_comp},Individual,generically depends on,{ibe_comp},Individual")
            triples.append(f"{mice_comp},Individual,describes,{blend_proc_ind},Individual")
            triples.append(f"{mice_comp},Individual,rdf:type,Blend On Edge Node Component,Class")

    # Return all triple lines
    return triples

def main():
    # We will write a CSV with a header: Subject,SubjectType,Predicate,Object,ObjectType
    fieldnames = ["Subject", "SubjectType", "Predicate", "Object", "ObjectType"]

    # We'll manually write the header line,
    # then TBOX lines, then for each row we generate ABox lines.
    with open(INPUT_CSV, "r", newline="", encoding="utf-8-sig") as f_in, \
         open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        
        # Write header
        writer.writerow(fieldnames)

        # 2) Write TBox lines
        for line in TBOX_LINES:
            parts = line.split(",")
            if len(parts) == 5:
                writer.writerow(parts)
            else:
                # If there's a minor mismatch, handle carefully; 
                # but here we assume we have 5 columns exactly.
                pass

        # 3) Read the CSV for ABox
        reader = csv.DictReader(f_in)
        for row in reader:
            # Build the triples for this row
            row_triples = generate_triples_for_row(row)
            for triple_str in row_triples:
                # Each triple_str also has 5 parts separated by commas
                parts = triple_str.split(",")
                writer.writerow(parts)

    print(f"Done! Wrote TBox + ABox lines to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()

