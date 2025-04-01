import requests
import os
import pandas as pd
from pandasgui import show
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
username = os.getenv('username')
password = os.getenv('password')

# GraphDB setup
graphdb_url = "http://localhost:7200"  # Adjust if remote
repo_name = "defect"
endpoint = f"{graphdb_url}/repositories/{repo_name}"

# SPARQL Query
query = """
PREFIX :    <http://api.stardog.com/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT 
  ?defect ?defectID
  ?index1Val ?index1Unit
  ?index2Val ?index2Unit
  ?depthVal  ?depthUnit
  ?lengthVal ?lengthUnit
WHERE {
  ?defect rdf:type :Airfoil_Defect .
  
  OPTIONAL {
    ?defectICE rdf:type :Designative_Information_Content_Entity ;
               :designates ?defect ;
               :generically_depends_on ?defectIBE .
    ?defectIBE :has_text_value ?defectID .
  }

  OPTIONAL {
    ?index1MICE rdf:type :Defect_Index1_Distance_to_Datum ;
                :describes ?defect ;
                :generically_depends_on ?index1IBE .
    ?index1IBE :has_decimal_value ?index1Val .
    OPTIONAL {
      ?index1IBE :uses_measurement_unit ?index1Unit .
    }
  }

  OPTIONAL {
    ?index2MICE rdf:type :Defect_Index2_Distance_to_Datum ;
                :describes ?defect ;
                :generically_depends_on ?index2IBE .
    ?index2IBE :has_decimal_value ?index2Val .
    OPTIONAL {
      ?index2IBE :uses_measurement_unit ?index2Unit .
    }
  }

  OPTIONAL {
    ?depthMICE rdf:type :Defect_Depth ;
               :describes ?defect ;
               :generically_depends_on ?depthIBE .
    ?depthIBE :has_decimal_value ?depthVal .
    OPTIONAL {
      ?depthIBE :uses_measurement_unit ?depthUnit .
    }
  }

  OPTIONAL {
    ?lengthMICE rdf:type :Defect_Length ;
                :describes ?defect ;
                :generically_depends_on ?lengthIBE .
    ?lengthIBE :has_decimal_value ?lengthVal .
    OPTIONAL {
      ?lengthIBE :uses_measurement_unit ?lengthUnit .
    }
  }
}
ORDER BY ?defect
"""

# Helper to clean URIs
def clean_uri(uri):
    return uri.split("/")[-1] if uri else None

# Authentication setup
if username and password:
    auth = (username, password)
else:
    auth = None
    print("No username or password provided.  Attempting query without authentication.")


# Run the query
try:
    if auth:
        response = requests.post(
            endpoint,
            data={"query": query},
            headers={"Accept": "application/sparql-results+json"},
            auth=auth
        )
    else:
        response = requests.post(
            endpoint,
            data={"query": query},
            headers={"Accept": "application/sparql-results+json"},
        )
except requests.exceptions.RequestException as e:
    print(f"Error connecting to GraphDB: {e}")
    exit()



# Parse and display
if response.status_code == 200:
    results = response.json()
    data = []

    for result in results["results"]["bindings"]:
        row = {
            "Defect": clean_uri(result.get("defect", {}).get("value")),
            "Defect ID": result.get("defectID", {}).get("value", ""),
            "Index1 Value": result.get("index1Val", {}).get("value", ""),
            "Index1 Unit": clean_uri(result.get("index1Unit", {}).get("value", "")),
            "Index2 Value": result.get("index2Val", {}).get("value", ""),
            "Index2 Unit": clean_uri(result.get("index2Unit", {}).get("value", "")),
            "Depth Value": result.get("depthVal", {}).get("value", ""),
            "Depth Unit": clean_uri(result.get("depthUnit", {}).get("value", "")),
            "Length Value": result.get("lengthVal", {}).get("value", ""),
            "Length Unit": clean_uri(result.get("lengthUnit", {}).get("value", "")),
        }
        data.append(row)

    df = pd.DataFrame(data)
    show(df)
else:
    print("Query failed:", response.status_code, response.text)
