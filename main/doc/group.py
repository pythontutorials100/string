import requests
import os
import pandas as pd
from pandasgui import show
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
username = os.getenv('username')
password = os.getenv('password')

# GraphDB endpoint config
graphdb_url = "http://localhost:7200"
repo_name = "defect"
endpoint = f"{graphdb_url}/repositories/{repo_name}"

# Helper to get the local name from a URI
def clean_uri(uri):
    return uri.split('/')[-1] if uri else None

# SPARQL Query
query = """
PREFIX :    <http://api.stardog.com/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT
  ?defect
  ?defectID
  ?airfoil
  ?airfoilPartNum
  ?defectRegion
  ?regionPart
  ?index1Val
  ?index1DatumPart
  ?index2Val
  ?index2DatumPart
  ?depthVal
  ?lengthVal
  ?blendProc
  ?blendParticipant
  ?blendDepth
  ?blendLength
  ?blendFlatLen
  ?blendFillet
  ?blendPropFactor
  ?blendLoc
  ?blendNodeComp
WHERE {
  ?defect rdf:type :Airfoil_Defect .

  OPTIONAL {
    ?defectICE rdf:type :Designative_Information_Content_Entity ;
               :designates ?defect ;
               :generically_depends_on ?defectIBE .
    ?defectIBE :has_text_value ?defectID .
  }

  ?defect :inheres_in ?defectRegion .
  ?airfoil :has_continuant_part ?defectRegion .

  OPTIONAL {
    ?defectRegion :has_continuant_part ?regionPart .
  }

  OPTIONAL {
    ?partNumICE rdf:type :Part_Number ;
                :designates ?airfoil ;
                :generically_depends_on ?partNumIBE .
    ?partNumIBE :has_text_value ?airfoilPartNum .
  }

  OPTIONAL {
    ?index1MICE rdf:type :Defect_Index1_Distance_to_Datum ;
                :describes ?defect ;
                :generically_depends_on ?index1IBE .
    ?index1IBE :has_decimal_value ?index1Val .
    OPTIONAL { ?index1MICE :measured_from_part ?index1DatumPart . }
  }

  OPTIONAL {
    ?index2MICE rdf:type :Defect_Index2_Distance_to_Datum ;
                :describes ?defect ;
                :generically_depends_on ?index2IBE .
    ?index2IBE :has_decimal_value ?index2Val .
    OPTIONAL { ?index2MICE :measured_from_part ?index2DatumPart . }
  }

  OPTIONAL {
    ?depthMICE rdf:type :Defect_Depth ;
               :describes ?defect ;
               :generically_depends_on ?depthIBE .
    ?depthIBE :has_decimal_value ?depthVal .
  }

  OPTIONAL {
    ?lengthMICE rdf:type :Defect_Length ;
                :describes ?defect ;
                :generically_depends_on ?lengthIBE .
    ?lengthIBE :has_decimal_value ?lengthVal .
  }

  OPTIONAL {
    ?blendProc rdf:type :Blend_on_Edge_Process ;
               :is_about ?defect .
    OPTIONAL { ?blendProc :has_participant ?blendParticipant . }

    OPTIONAL {
      ?blendDepthMICE rdf:type :Blend_On_Edge_Depth_Measurement ;
                       :describes ?blendProc ;
                       :generically_depends_on ?blendDepthIBE .
      ?blendDepthIBE :has_decimal_value ?blendDepth .
    }

    OPTIONAL {
      ?blendLengthMICE rdf:type :Blend_On_Edge_Length_Measurement ;
                        :describes ?blendProc ;
                        :generically_depends_on ?blendLengthIBE .
      ?blendLengthIBE :has_decimal_value ?blendLength .
    }

    OPTIONAL {
      ?blendFlatLenMICE rdf:type :Blend_On_Edge_Flat_Length_Measurement ;
                         :describes ?blendProc ;
                         :generically_depends_on ?blendFlatLenIBE .
      ?blendFlatLenIBE :has_decimal_value ?blendFlatLen .
    }

    OPTIONAL {
      ?blendFilletMICE rdf:type :Blend_On_Edge_Fillet_Radius_Measurement ;
                        :describes ?blendProc ;
                        :generically_depends_on ?blendFilletIBE .
      ?blendFilletIBE :has_decimal_value ?blendFillet .
    }

    OPTIONAL {
      ?blendPropMICE rdf:type :Blend_On_Edge_Proportional_Factor_Measurement ;
                     :describes ?blendProc ;
                     :generically_depends_on ?blendPropIBE .
      ?blendPropIBE :has_decimal_value ?blendPropFactor .
    }

    OPTIONAL {
      ?blendLocMICE rdf:type :Blend_On_Edge_Location_Measurement ;
                    :describes ?blendProc ;
                    :generically_depends_on ?blendLocIBE .
      ?blendLocIBE :has_decimal_value ?blendLoc .
    }

    OPTIONAL {
      ?blendNodeCompMICE rdf:type :Blend_On_Edge_Node_Component ;
                         :describes ?blendProc ;
                         :generically_depends_on ?blendNodeCompIBE .
      ?blendNodeCompIBE :has_text_value ?blendNodeComp .
    }
  }
}
ORDER BY ?defect ?blendProc
"""

# Authentication setup
if username and password:
    auth = (username, password)
else:
    auth = None
    print("No username or password provided.  Attempting query without authentication.")

# Send the request
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


# Process the result
if response.status_code == 200:
    results = response.json()
    data = []

    for result in results["results"]["bindings"]:
        row = {
            "Defect": clean_uri(result.get("defect", {}).get("value")),
            "Defect ID": result.get("defectID", {}).get("value", ""),
            "Airfoil": clean_uri(result.get("airfoil", {}).get("value")),
            "Airfoil Part Num": result.get("airfoilPartNum", {}).get("value", ""),
            "Defect Region": clean_uri(result.get("defectRegion", {}).get("value")),
            "Region Part": clean_uri(result.get("regionPart", {}).get("value", "")),
            "Index1 Val": result.get("index1Val", {}).get("value", ""),
            "Index1 Datum Part": clean_uri(result.get("index1DatumPart", {}).get("value", "")),
            "Index2 Val": result.get("index2Val", {}).get("value", ""),
            "Index2 Datum Part": clean_uri(result.get("index2DatumPart", {}).get("value", "")),
            "Depth Val": result.get("depthVal", {}).get("value", ""),
            "Length Val": result.get("lengthVal", {}).get("value", ""),
            "Blend Process": clean_uri(result.get("blendProc", {}).get("value", "")),
            "Blend Participant": clean_uri(result.get("blendParticipant", {}).get("value", "")),
            "Blend Depth": result.get("blendDepth", {}).get("value", ""),
            "Blend Length": result.get("blendLength", {}).get("value", ""),
            "Blend Flat Len": result.get("blendFlatLen", {}).get("value", ""),
            "Blend Fillet": result.get("blendFillet", {}).get("value", ""),
            "Blend Prop Factor": result.get("blendPropFactor", {}).get("value", ""),
            "Blend Loc": result.get("blendLoc", {}).get("value", ""),
            "Blend Node Comp": result.get("blendNodeComp", {}).get("value", "")
        }
        data.append(row)

    df = pd.DataFrame(data)
    show(df)
else:
    print("Query failed:", response.status_code)
    print(response.text)
