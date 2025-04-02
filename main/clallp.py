PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX voc: <http://example.org/voc/>

SELECT ?student_uri ?firstName ?lastName
WHERE {
  ?student_uri a voc:Student ;
         foaf:firstName ?firstName ;
         foaf:lastName ?lastName .
}
