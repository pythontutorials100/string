from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SKOS, DC, DCTERMS
from rdflib.collection import Collection
import csv

# Load the TTL file
g = Graph()
g.parse("classcco.ttl", format="ttl", encoding='utf-8')

# Manually process imports to include BFO properties
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

# Mapping from identifiers to labels (Classes and Object Properties)
bfo_id_to_label = {
    # Classes
    'BFO_0000001': "entity",
    'BFO_0000002': "continuant",
    'BFO_0000003': "occurrent",
    'BFO_0000004': "independent continuant",
    'BFO_0000006': "spatial region",
    'BFO_0000008': "temporal region",
    'BFO_0000009': "two-dimensional spatial region",
    'BFO_0000011': "spatiotemporal region",
    'BFO_0000015': "process",
    'BFO_0000016': "disposition",
    'BFO_0000017': "realizable entity",
    'BFO_0000018': "zero-dimensional spatial region",
    'BFO_0000019': "quality",
    'BFO_0000020': "specifically dependent continuant",
    'BFO_0000023': "role",
    'BFO_0000024': "fiat object part",
    'BFO_0000026': "one-dimensional spatial region",
    'BFO_0000027': "object aggregate",
    'BFO_0000028': "three-dimensional spatial region",
    'BFO_0000029': "site",
    'BFO_0000030': "object",
    'BFO_0000031': "generically dependent continuant",
    'BFO_0000034': "function",
    'BFO_0000035': "process boundary",
    'BFO_0000038': "one-dimensional temporal region",
    'BFO_0000040': "material entity",
    'BFO_0000140': "continuant fiat boundary",
    'BFO_0000141': "immaterial entity",
    'BFO_0000142': "fiat line",
    'BFO_0000145': "relational quality",
    'BFO_0000146': "fiat surface",
    'BFO_0000147': "fiat point",
    'BFO_0000148': "zero-dimensional temporal region",
    'BFO_0000182': "history",
    'BFO_0000202': "temporal interval",
    'BFO_0000203': "temporal instant",
    # Object Properties
    'BFO_0000054': "has realization",
    'BFO_0000055': "realizes",
    'BFO_0000056': "participates in",
    'BFO_0000057': "has participant",
    'BFO_0000058': "is concretized by",
    'BFO_0000059': "concretizes",
    'BFO_0000062': "preceded by",
    'BFO_0000063': "precedes",
    'BFO_0000066': "occurs in",
    'BFO_0000084': "generically depends on",
    'BFO_0000101': "is carrier of",
    'BFO_0000108': "exists at",
    'BFO_0000115': "has member part",
    'BFO_0000117': "has occurrent part",
    'BFO_0000121': "has temporal part",
    'BFO_0000124': "location of",
    'BFO_0000127': "material basis of",
    'BFO_0000129': "member part of",
    'BFO_0000132': "occurrent part of",
    'BFO_0000139': "temporal part of",
    'BFO_0000153': "temporally projects onto",
    'BFO_0000171': "located in",
    'BFO_0000176': "continuant part of",
    'BFO_0000178': "has continuant part",
    'BFO_0000183': "environs",
    'BFO_0000184': "history of",
    'BFO_0000185': "has history",
    'BFO_0000194': "specifically depended on by",
    'BFO_0000195': "specifically depends on",
    'BFO_0000196': "bearer of",
    'BFO_0000197': "inheres in",
    'BFO_0000199': "occupies temporal region",
    'BFO_0000200': "occupies spatiotemporal region",
    'BFO_0000210': "occupies spatial region",
    'BFO_0000216': "spatially projects onto",
    'BFO_0000218': "has material basis",
    'BFO_0000221': "first instant of",
    'BFO_0000222': "has first instant",
    'BFO_0000223': "last instant of",
    'BFO_0000224': "has last instant",
}

# Function to strip language tags and quotes from literals
def clean_literal(lit):
    if isinstance(lit, Literal):
        return str(lit)
    else:
        return lit

# List of properties to extract for object properties
properties_to_extract = [
    (RDF.type, 'rdf_type'),
    (RDFS.subPropertyOf, 'rdfs_subPropertyOf'),
    (OWL.equivalentProperty, 'owl_equivalentProperty'),
    (OWL.inverseOf, 'owl_inverseOf'),
    (RDFS.domain, 'rdfs_domain'),
    (RDFS.range, 'rdfs_range'),
    (OWL.propertyDisjointWith, 'owl_propertyDisjointWith'),
    (RDFS.label, 'property_label'),
    # CCO properties
    (CCO_ns.definition, 'cco_definition'),
    (CCO_ns.definition_source, 'cco_definition_source'),
    (CCO_ns.is_curated_in_ontology, 'cco_is_curated_in_ontology'),
    (CCO_ns.alternative_label, 'cco_alternative_label'),
    (CCO_ns.elucidation, 'cco_elucidation'),
    (CCO_ns.example_of_usage, 'cco_example_of_usage'),
    # Annotations
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
    # Add any other properties you need
]

# Get all object properties with URIs (exclude blank nodes)
object_properties = set(prop for prop in g.subjects(RDF.type, OWL.ObjectProperty) if isinstance(prop, URIRef))

# Function to serialize nodes (URIs or literals)
def serialize_node(node, graph, namespace_manager, visited=None):
    if isinstance(node, URIRef):
        # Try to get the label from the graph
        labels = set()
        for label in graph.objects(node, RDFS.label):
            labels.add(clean_literal(label))
        if labels:
            return '; '.join(labels)  # Use all labels
        else:
            # Extract identifier and check in bfo_id_to_label
            uri_str = str(node)
            identifier = uri_str.split('/')[-1]
            if '#' in identifier:
                identifier = identifier.split('#')[-1]
            if identifier in bfo_id_to_label:
                return bfo_id_to_label[identifier]
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
                obj_str = serialize_node(obj, graph, namespace_manager, visited)
            components.append(f"{pred_str} {obj_str}")
        return '[ ' + ' ; '.join(components) + ' ]'

# Prepare CSV file
with open('output_object_properties.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['property_uri'] + [name for uri, name in properties_to_extract]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for prop in object_properties:
        row = {}
        # property_uri: keep as is
        row['property_uri'] = prop.n3(g.namespace_manager)
        for prop_uri, prop_name in properties_to_extract:
            values = set()
            for obj in g.objects(prop, prop_uri):
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
