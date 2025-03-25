PREFIX :    <http://api.stardog.com/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?defect ?defectID
WHERE {
  # 1) Find every individual typed as an Airfoil_Defect
  ?defect rdf:type :Airfoil_Defect .
  
  # 2) Optionally match its “designative info” that carries a text ID
  OPTIONAL {
    ?defectICE rdf:type :Designative_Information_Content_Entity ;
               :designates ?defect ;
               :generically_depends_on ?defectIBE .
    ?defectIBE :has_text_value ?defectID .
  }
}
ORDER BY ?defect
