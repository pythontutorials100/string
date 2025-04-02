[MappingDeclaration] @collection [[
mappingId     StudentMapping
target        <http://example.org/student/{s_id}> a <http://example.org/voc/Student> ; <http://xmlns.com/foaf/0.1/firstName> "{first_name}"^^xsd:string ; <http://xmlns.com/foaf/0.1/lastName> "{last_name}"^^xsd:string .
source        SELECT s_id, first_name, last_name FROM student
]]

[PrefixDeclaration]
xsd:    <http://www.w3.org/2001/XMLSchema#>
foaf:   <http://xmlns.com/foaf/0.1/>
:       <http://example.org/voc/>
