[PrefixDeclaration]
:		http://example.org/voc/  # Base prefix (optional but convenient)
foaf:	http://xmlns.com/foaf/0.1/
voc:	http://example.org/voc/
rdf:	http://www.w3.org/1999/02/22-rdf-syntax-ns#
rdfs:	http://www.w3.org/2000/01/rdf-schema#
owl:	http://www.w3.org/2002/07/owl#
xsd:	http://www.w3.org/2001/XMLSchema#

[MappingDeclaration] @collection [[
mappingId	StudentMapping
target		voc:student/{s_id} a voc:Student ; 
            foaf:firstName {first_name} ; 
            foaf:lastName {last_name} .
source		SELECT s_id, first_name, last_name FROM student
]]


PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX voc: <http://example.org/voc/>

SELECT ?student_uri ?firstName ?lastName
WHERE {
  ?student_uri a voc:Student ;
         foaf:firstName ?firstName ;
         foaf:lastName ?lastName .
}



PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX voc: <http://example.org/voc/>

SELECT ?student_uri ?firstName ?lastName
WHERE {
  ?student_uri a voc:Student ;
         foaf:firstName ?firstName ;
         foaf:lastName ?lastName .
}
