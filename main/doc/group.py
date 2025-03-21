PREFIX :    <http://api.stardog.com/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT
  ?defect
  (SAMPLE(?defectID)       AS ?defectIDVal)
  (SAMPLE(?airfoil)        AS ?airfoilIRI)
  (SAMPLE(?airfoilID)      AS ?airfoilIDVal)
  (SAMPLE(?index1Val)      AS ?index1ValSample)
  (SAMPLE(?index1Datum)    AS ?index1DatumSample)
  (SAMPLE(?index2Val)      AS ?index2ValSample)
  (SAMPLE(?index2Datum)    AS ?index2DatumSample)
  (SAMPLE(?defectDepth)    AS ?defectDepthSample)
  (SAMPLE(?defectLength)   AS ?defectLengthSample)
  (SAMPLE(?inspection)     AS ?inspectionIRI)
  (SAMPLE(?blendProc)      AS ?blendProcIRI)
  (SAMPLE(?blendDepth)     AS ?blendDepthSample)
  (SAMPLE(?blendLength)    AS ?blendLengthSample)
  (SAMPLE(?blendFlatLen)   AS ?blendFlatLenSample)
  (SAMPLE(?blendFillet)    AS ?blendFilletSample)
  (SAMPLE(?blendProp)      AS ?blendPropSample)
  (SAMPLE(?blendLoc)       AS ?blendLocSample)

WHERE {
  #############################################################################
  # 1) Find all Defects
  #############################################################################
  ?defect rdf:type :Airfoil_Defect .

  #############################################################################
  # 2) Defect ID (Designative ICE -> IBE -> text value)
  #    Make sure :airfoil_defect_ID1_ICE has rdf:type :Designative_Information_Content_Entity
  #############################################################################
  OPTIONAL {
    ?defectICE rdf:type :Designative_Information_Content_Entity ;
               :designates ?defect ;
               :generically_depends_on ?defectIBE .
    ?defectIBE :has_text_value ?defectID .
  }

  #############################################################################
  # 3) Link Defect to Airfoil
  #############################################################################
  ?defect :inheres_in ?defectRegion .
  ?airfoil :has_continuant_part ?defectRegion .
  
  # Airfoil ID
  OPTIONAL {
    ?airfoilICE rdf:type :Designative_Information_Content_Entity ;
                :designates ?airfoil ;
                :generically_depends_on ?airfoilIBE .
    ?airfoilIBE :has_text_value ?airfoilID .
  }

  #############################################################################
  # 4) Defect Measurements (Index1, Index2, Depth, Length)
  #############################################################################
  OPTIONAL {
    ?index1MICE rdf:type :Defect_Index1_Distance_to_Datum ;
                :describes ?defect ;
                :generically_depends_on ?index1IBE .
    ?index1IBE :has_decimal_value ?index1Val .
    OPTIONAL { ?index1MICE :measured_from_part ?index1Datum . }
  }
  
  OPTIONAL {
    ?index2MICE rdf:type :Defect_Index2_Distance_to_Datum ;
                :describes ?defect ;
                :generically_depends_on ?index2IBE .
    ?index2IBE :has_decimal_value ?index2Val .
    OPTIONAL { ?index2MICE :measured_from_part ?index2Datum . }
  }

  OPTIONAL {
    ?depthMICE rdf:type :Defect_Depth ;
               :describes ?defect ;
               :generically_depends_on ?depthIBE .
    ?depthIBE :has_decimal_value ?defectDepth .
  }

  OPTIONAL {
    ?lengthMICE rdf:type :Defect_Length ;
                :describes ?defect ;
                :generically_depends_on ?lengthIBE .
    ?lengthIBE :has_decimal_value ?defectLength .
  }

  #############################################################################
  # 5) Inspection referencing this defect
  #############################################################################
  OPTIONAL {
    ?defect :is_object_of ?inspection .
    ?inspection rdf:type :Act_of_Inspection .
  }

  #############################################################################
  # 6) Blend_on_Edge_Process referencing this defect, plus each blend param
  #############################################################################
  OPTIONAL {
    ?blendProc rdf:type :Blend_on_Edge_Process ;
               :is_about ?defect .
    
    # Blend Depth
    OPTIONAL {
      ?blendDepthMICE :describes ?blendProc ;
                       :generically_depends_on ?blendDepthIBE .
      ?blendDepthIBE :has_decimal_value ?blendDepth .
    }
    # Blend Length
    OPTIONAL {
      ?blendLengthMICE :describes ?blendProc ;
                        :generically_depends_on ?blendLengthIBE .
      ?blendLengthIBE :has_decimal_value ?blendLength .
    }
    # Blend Flat Length
    OPTIONAL {
      ?blendFlatLenMICE :describes ?blendProc ;
                         :generically_depends_on ?blendFlatLenIBE .
      ?blendFlatLenIBE :has_decimal_value ?blendFlatLen .
    }
    # Blend Fillet Radius
    OPTIONAL {
      ?blendFilletMICE :describes ?blendProc ;
                         :generically_depends_on ?blendFilletIBE .
      ?blendFilletIBE :has_decimal_value ?blendFillet .
    }
    # Blend Prop Factor
    OPTIONAL {
      ?blendPropMICE :describes ?blendProc ;
                      :generically_depends_on ?blendPropIBE .
      ?blendPropIBE :has_decimal_value ?blendProp .
    }
    # Blend Loc
    OPTIONAL {
      ?blendLocMICE :describes ?blendProc ;
                     :generically_depends_on ?blendLocIBE .
      ?blendLocIBE :has_decimal_value ?blendLoc .
    }
  }

}
#############################################################################
# 7) Group by ?defect to get one row per defect
#############################################################################
GROUP BY ?defect
ORDER BY ?defect
