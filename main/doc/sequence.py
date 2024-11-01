import pandas as pd
import re

def camel_case_to_lowercase_with_spaces(label):
    # Insert spaces before capital letters, except the first one
    s = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', label)
    s = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s)
    # Convert to lowercase
    s = s.lower()
    return s.strip()

def extract_class_labels_from_text_file(text_file_path):
    class_labels = []
    with open(text_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Remove leading/trailing whitespace
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            # Remove IDs in parentheses, e.g., 'material entity (BFO:0000040)' -> 'material entity'
            if '(' in line:
                label = line[:line.find('(')].strip()
            else:
                label = line
            # Normalize the label
            label = camel_case_to_lowercase_with_spaces(label)
            class_labels.append(label)
    return class_labels

def reorder_csv_by_class_labels(csv_file_path, text_file_path, output_csv_file_path):
    # Step 1: Extract class labels from text file and normalize them
    class_labels_in_order = extract_class_labels_from_text_file(text_file_path)
    
    # Step 2: Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file_path)
    
    # Ensure that 'class_label' in the DataFrame is of type string
    df['class_label'] = df['class_label'].astype(str)
    
    # Normalize 'class_label' in the DataFrame
    df['normalized_class_label'] = df['class_label'].apply(lambda x: x.strip().lower())
    
    # Step 3: Create a mapping from normalized class labels to DataFrame indices
    # Since class labels may not be unique, group by 'normalized_class_label'
    df_grouped = df.groupby('normalized_class_label', sort=False)
    
    # Step 4: Re-order the DataFrame according to class labels in the text file
    reordered_rows = []
    labels_found = set()
    for label in class_labels_in_order:
        if label in df_grouped.groups:
            # Get the rows corresponding to this label
            matching_rows = df_grouped.get_group(label)
            # Append these rows to reordered_rows
            reordered_rows.append(matching_rows)
            labels_found.add(label)
        else:
            print(f"Warning: Class label '{label}' not found in CSV file.")
    
    # Add rows for class labels that are in CSV but not in text file, at the end
    labels_in_csv = set(df['normalized_class_label'].unique())
    labels_not_in_text_file = labels_in_csv - labels_found
    if labels_not_in_text_file:
        print(f"Note: The following class labels are in CSV but not in text file: {labels_not_in_text_file}")
        for label in labels_not_in_text_file:
            matching_rows = df_grouped.get_group(label)
            reordered_rows.append(matching_rows)
    
    # Combine the reordered rows into a new DataFrame
    if reordered_rows:
        df_reordered = pd.concat(reordered_rows, ignore_index=True)
    else:
        df_reordered = pd.DataFrame(columns=df.columns)
    
    # Drop the 'normalized_class_label' column
    df_reordered = df_reordered.drop(columns=['normalized_class_label'])
    
    # Step 5: Write the reordered DataFrame to a new CSV file
    df_reordered.to_csv(output_csv_file_path, index=False, encoding='utf-8-sig')
    print(f"Reordered CSV file has been saved to {output_csv_file_path}")

# Example usage:
# Provide the paths to your CSV and text files, and the desired output CSV path
csv_file_path = 'output_core_classes6.csv'
text_file_path = 'coretree.txt'
output_csv_file_path = 'reordered_output_core_classes6.csv'

reorder_csv_by_class_labels(csv_file_path, text_file_path, output_csv_file_path)
