PREFIX :    <http://api.stardog.com/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT 
  ?defect ?defectID
  ?index1Val ?index1Unit
  ?index2Val ?index2Unit
  ?depthVal  ?depthUnit
  ?lengthVal ?lengthUnit
WHERE {
  #############################################################################
  # 1) Defect instance & optional Defect ID
  #############################################################################
  ?defect rdf:type :Airfoil_Defect .
  
  OPTIONAL {
    ?defectICE rdf:type :Designative_Information_Content_Entity ;
               :designates ?defect ;
               :generically_depends_on ?defectIBE .
    ?defectIBE :has_text_value ?defectID .
  }

  #############################################################################
  # 2) Index1
  #############################################################################
  OPTIONAL {
    ?index1MICE rdf:type :Defect_Index1_Distance_to_Datum ;
                :describes ?defect ;
                :generically_depends_on ?index1IBE .
    ?index1IBE :has_decimal_value ?index1Val .
    OPTIONAL {
      ?index1IBE :uses_measurement_unit ?index1Unit .
    }
  }

  #############################################################################
  # 3) Index2
  #############################################################################
  OPTIONAL {
    ?index2MICE rdf:type :Defect_Index2_Distance_to_Datum ;
                :describes ?defect ;
                :generically_depends_on ?index2IBE .
    ?index2IBE :has_decimal_value ?index2Val .
    OPTIONAL {
      ?index2IBE :uses_measurement_unit ?index2Unit .
    }
  }

  #############################################################################
  # 4) Depth
  #############################################################################
  OPTIONAL {
    ?depthMICE rdf:type :Defect_Depth ;
               :describes ?defect ;
               :generically_depends_on ?depthIBE .
    ?depthIBE :has_decimal_value ?depthVal .
    OPTIONAL {
      ?depthIBE :uses_measurement_unit ?depthUnit .
    }
  }

  #############################################################################
  # 5) Length
  #############################################################################
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
