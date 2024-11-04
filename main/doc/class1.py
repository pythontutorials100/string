from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SKOS, DC, DCTERMS
from rdflib.collection import Collection
import csv

# Load the TTL file
g = Graph()
g.parse("classcco.ttl", format="ttl", encoding='utf-8')

# Manually process imports to include BFO classes
for ontology in g.objects(None, OWL.imports):
    print(f"Importing ontology: {ontology}")
    try:
        g.parse(ontology, format='xml')
    except Exception as e:
        print(f"Failed to parse {ontology} as RDF/XML: {e}")
        # Optionally, try other formats like Turtle
        try:
            g.parse(ontology, format='turtle')
        except Exception as e2:
            print(f"Failed to parse {ontology} as Turtle: {e2}")
            print(f"Skipping ontology: {ontology}")

# Define namespaces
RDF_ns = RDF
RDFS_ns = RDFS
OWL_ns = OWL
XSD_ns = XSD
SKOS_ns = SKOS
DC_ns = DC
DCTERMS_ns = DCTERMS
CCO_ns = Namespace("http://www.ontologyrepository.com/CommonCoreOntologies/")
BFO_ns = Namespace("http://purl.obolibrary.org/obo/")
IAO_ns = Namespace("http://purl.obolibrary.org/obo/IAO_")
IOF_AV_ns = Namespace("https://spec.industrialontologies.org/ontology/core/meta/AnnotationVocabulary/")
IOF_CORE_ns = Namespace("https://spec.industrialontologies.org/ontology/core/Core/")

# Bind prefixes
g.bind('rdf', RDF_ns)
g.bind('rdfs', RDFS_ns)
g.bind('owl', OWL_ns)
g.bind('xsd', XSD_ns)
g.bind('skos', SKOS_ns)
g.bind('dc', DC_ns)
g.bind('dcterms', DCTERMS_ns)
g.bind('cco', CCO_ns)
g.bind('bfo', BFO_ns)
g.bind('IAO', IAO_ns)
g.bind('iof-av', IOF_AV_ns)
g.bind('iof-core', IOF_CORE_ns)

# Hardcoded mapping from BFO numbers to labels (Classes and Object Properties)
bfo_number_to_label = {
    # Include your existing mappings here
}

# Function to strip language tags and quotes from literals
def clean_literal(lit):
    if isinstance(lit, Literal):
        return str(lit)
    else:
        return lit

# List of properties to extract for classes
properties_to_extract = [
    (RDF.type, 'rdf_type'),
    (RDFS.subClassOf, 'rdfs_subClassOf'),
    (OWL.equivalentClass, 'owl_equivalentClass'),
    (OWL.disjointWith, 'owl_disjointWith'),
    (RDFS.label, 'class_label'),
    # CCO properties
    (CCO_ns.definition, 'cco_definition'),
    (CCO_ns.definition_source, 'cco_definition_source'),
    (CCO_ns.is_curated_in_ontology, 'cco_is_curated_in_ontology'),
    (CCO_ns.alternative_label, 'cco_alternative_label'),
    (CCO_ns.elucidation, 'cco_elucidation'),
    (CCO_ns.example_of_usage, 'cco_example_of_usage'),
    # Additional properties
    (RDFS.comment, 'rdfs_comment'),
    (SKOS_ns.definition, 'skos_definition'),
    (SKOS_ns.example, 'skos_example'),
    (SKOS_ns.scopeNote, 'skos_scopeNote'),
    (DC_ns.identifier, 'dc_identifier'),
    # IAO properties
    (IAO_ns['0000111'], 'editor_preferred_term'),      # IAO:0000111 is 'editor preferred term'
    (IAO_ns['0000112'], 'example_of_usage'),           # IAO:0000112 is 'example of usage'
    (IAO_ns['0000115'], 'definition'),                 # IAO:0000115 is 'definition'
    (IAO_ns['0000116'], 'editor_note'),                # IAO:0000116 is 'editor note'
    (IAO_ns['0000118'], 'alternative_term'),           # IAO:0000118 is 'alternative term'
    (IAO_ns['0000119'], 'definition_source'),          # IAO:0000119 is 'definition source'
    (IAO_ns['0000600'], 'elucidation'),                # IAO:0000600 is 'elucidation'
    (IAO_ns['0000601'], 'has_associated_axiom_nl'),    # IAO:0000601 is 'has associated axiom (nl)'
    (IAO_ns['0000602'], 'has_associated_axiom_fol'),   # IAO:0000602 is 'has associated axiom (fol)'
    (IAO_ns['0000231'], 'curation_status'),            # IAO:0000231 is 'curation status'
    # IOF-AV properties
    (IOF_AV_ns.abbreviation, 'iof-av_abbreviation'),
    (IOF_AV_ns.adaptedFrom, 'iof-av_adaptedFrom'),
    (IOF_AV_ns.explanatoryNote, 'iof-av_explanatoryNote'),
    (IOF_AV_ns.firstOrderLogicDefinition, 'iof-av_firstOrderLogicDefinition'),
    (IOF_AV_ns.naturalLanguageDefinition, 'iof-av_naturalLanguageDefinition'),
    (IOF_AV_ns.semiFormalNaturalLanguageDefinition, 'iof-av_semiFormalNaturalLanguageDefinition'),
    (IOF_AV_ns.counterExample, 'iof-av_counterExample'),
    (IOF_AV_ns.firstOrderLogicAxiom, 'iof-av_firstOrderLogicAxiom'),
    (IOF_AV_ns.isPrimitive, 'iof-av_isPrimitive'),
    (IOF_AV_ns.primitiveRationale, 'iof-av_primitiveRationale'),
    (IOF_AV_ns.semiFormalNaturalLanguageAxiom, 'iof-av_semiFormalNaturalLanguageAxiom'),
    (IOF_AV_ns.maturity, 'iof-av_maturity'),
]

# Get all classes with URIs (exclude blank nodes)
classes = set(cls for cls in g.subjects(RDF.type, OWL.Class) if isinstance(cls, URIRef))

# Function to serialize nodes (URIs or literals)
def serialize_node(node, graph, namespace_manager, visited=None):
    if isinstance(node, URIRef):
        # Check if node is in the hardcoded mapping
        if node in bfo_number_to_label:
            return bfo_number_to_label[node]
        else:
            # Try to get the label from the graph
            labels = set()
            for label in graph.objects(node, RDFS.label):
                labels.add(clean_literal(label))
            if labels:
                return '; '.join(labels)  # Use all labels
            else:
                return node.n3(namespace_manager)
    elif isinstance(node, Literal):
        return clean_literal(node)
    else:
        return serialize_blank_node(node, graph, namespace_manager, visited)

# Function to serialize blank nodes
def serialize_blank_node(node, graph, namespace_manager, visited=None):
    if visited is None:
        visited = set()
    if node in visited:
        return ''  # Avoid infinite loops
    visited.add(node)

    # Check if node is a list (rdf:List)
    if (node, RDF_ns.first, None) in graph:
        # It's a list
        collection = Collection(graph, node)
        items = []
        for item in collection:
            if isinstance(item, BNode):
                item_str = serialize_blank_node(item, graph, namespace_manager, visited)
            else:
                item_str = serialize_node(item, graph, namespace_manager, visited)
            items.append(item_str)
        return '( ' + ' '.join(items) + ' )'
    else:
        # It's a regular blank node
        components = []
        for predicate, obj in graph.predicate_objects(node):
            pred_str = serialize_node(predicate, graph, namespace_manager, visited)
            if isinstance(obj, BNode):
                obj_str = serialize_blank_node(obj, graph, namespace_manager, visited)
            else:
                obj_str = serialize_node(obj, graph, namespace_manager)
            components.append(f"{pred_str} {obj_str}")
        return '[ ' + ' ; '.join(components) + ' ]'

# Prepare CSV file
with open('output_cco_classes7.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['class_uri'] + [name for uri, name in properties_to_extract]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for cls in classes:
        row = {}
        # class_uri: keep as is
        row['class_uri'] = cls.n3(g.namespace_manager)
        for prop_uri, prop_name in properties_to_extract:
            values = set()
            for obj in g.objects(cls, prop_uri):
                if isinstance(obj, BNode):
                    serialized_obj = serialize_blank_node(obj, g, g.namespace_manager)
                    values.add(serialized_obj)
                else:
                    obj_str = serialize_node(obj, g, g.namespace_manager)
                    values.add(obj_str)
            # Clean literals in values
            cleaned_values = [clean_literal(value) for value in values if value]
            row[prop_name] = '; '.join(cleaned_values)
        writer.writerow(row)
