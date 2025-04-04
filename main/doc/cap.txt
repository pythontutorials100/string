<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive KG - Controlled Individual Placement</title>
    <!-- 1. Include vis.js library -->
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        body { font-family: sans-serif; } /* Added for consistency */
        #mynetwork {
            width: 95%;
            height: 700px;
            border: 1px solid lightgray;
            margin: 10px;
        }
        button {
            margin: 5px;
            padding: 0;
            width: 30px;
            height: 30px;
            vertical-align: middle;
            border: 1px solid #ccc;
            background-color: #f0f0f0;
            cursor: pointer;
        }
        button:disabled { cursor: not-allowed; opacity: 0.5; }
        button:hover:not(:disabled) { background-color: #e0e0e0; }
        #controls {
             padding: 5px;
             border-bottom: 1px solid #ccc;
             margin-bottom: 10px;
             display: flex;
             align-items: center;
        }
        /* Style for SPARQL query display (added for completeness if you add it later) */
        #sparqlQueryDisplay {
            margin: 15px 10px;
            padding: 10px;
            border: 1px dashed #aaa;
            background-color: #f9f9f9;
            font-family: monospace;
            white-space: pre;
            overflow-x: auto;
        }
        #sparqlQueryDisplay h3 {
            margin-top: 0; font-family: sans-serif; font-size: 1em;
            font-weight: bold; color: #333;
        }
    </style>
</head>
<body>

<!-- Title Removed -->

<div id="controls">
    <button id="showDefect1Btn" title="Show Defect 1" disabled></button>
    <button id="showDefect2Btn" title="Show Defect 2" disabled></button>
    <button id="highlightQueryBtn" title="Highlight Defect 2 Length" disabled></button>
</div>

<div id="mynetwork"></div>

<!-- Optional: Placeholder for SPARQL query -->
<!-- <div id="sparqlQueryDisplay" style="display: none;"> -->
<!--     <h3>SPARQL Query for Highlighted Path:</h3> -->
<!--     <code id="sparqlCode"></code> -->
<!-- </div> -->


<script type="text/javascript">
    // --- User Defined Colors ---
    const CLASS_COLOR_FILL = '#F0A30A'; // Orange-Yellow
    const CLASS_COLOR_BORDER = '#B8860B';
    const INDIVIDUAL_COLOR_FILL = '#76608A'; // Purple
    const INDIVIDUAL_COLOR_BORDER = '#4A3C5A';
    const LITERAL_COLOR_FILL = '#D5E8D4'; // Light Green
    const LITERAL_COLOR_BORDER = '#82B366';

    // --- Prefixes and Shorten Function (Unchanged) ---
    const prefixes = {
        "pw": "http://prattwhitney.com/ontology#", // Added pw prefix mapping
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "xsd": "http://www.w3.org/2001/XMLSchema#"
    };
    function shorten(uriOrLiteral) {
        if (typeof uriOrLiteral !== 'string') return String(uriOrLiteral);
        const literalMatch = uriOrLiteral.match(/^(.*)\^\^(.*)$/);
        if (literalMatch) {
            const value = JSON.stringify(literalMatch[1]);
            let datatype = literalMatch[2];
             // Attempt to shorten datatype as well
            for (const prefix in prefixes) {
                const uri = prefixes[prefix];
                 if (datatype.startsWith(uri)) {
                    datatype = prefix + ":" + datatype.substring(uri.length);
                    break; // Stop after first match
                 }
             }
             if (datatype === literalMatch[2]) { // If not shortened by prefix, get last part
                const parts = datatype.split(/[#/]/);
                datatype = parts[parts.length - 1] || datatype;
             }
            return `${value}^^${datatype}`;
        }
         // Shorten URI
        for (const prefix in prefixes) {
            const uri = prefixes[prefix];
            if (uriOrLiteral.startsWith(uri)) {
                return prefix + ":" + uriOrLiteral.substring(uri.length);
            }
        }
        const parts = uriOrLiteral.split(/[#/]/);
        return parts[parts.length - 1] || uriOrLiteral;
     }


    // --- Data Preparation (Unchanged from your provided code) ---
    const initialClassNodes = [ /* ... */
        { id: "pw:MaterialArtifact", label: shorten("http://prattwhitney.com/ontology#MaterialArtifact"), group: "class" },
        { id: "pw:FiatObjectPart", label: shorten("http://prattwhitney.com/ontology#FiatObjectPart"), group: "class" },
        { id: "pw:Quality", label: shorten("http://prattwhitney.com/ontology#Quality"), group: "class" },
        { id: "pw:InformationContentEntity", label: shorten("http://prattwhitney.com/ontology#InformationContentEntity"), group: "class" },
        { id: "pw:InformationBearingEntity", label: shorten("http://prattwhitney.com/ontology#InformationBearingEntity"), group: "class" },
        { id: "pw:MeasurementUnit", label: shorten("http://prattwhitney.com/ontology#MeasurementUnit"), group: "class" },
        { id: "pw:Airfoil", label: shorten("http://prattwhitney.com/ontology#Airfoil"), group: "class" },
        { id: "pw:Defect", label: shorten("http://prattwhitney.com/ontology#Defect"), group: "class" },
        { id: "pw:AirfoilDefect", label: shorten("http://prattwhitney.com/ontology#AirfoilDefect"), group: "class" },
        { id: "pw:DefectRegion", label: shorten("http://prattwhitney.com/ontology#DefectRegion"), group: "class" },
        { id: "pw:LeadingEdge", label: shorten("http://prattwhitney.com/ontology#LeadingEdge"), group: "class" },
        { id: "pw:DistanceMeasurementInformationContentEntity", label: shorten("http://prattwhitney.com/ontology#DistanceMeasurementInformationContentEntity"), group: "class" },
        { id: "pw:DefectDepth", label: shorten("http://prattwhitney.com/ontology#DefectDepth"), group: "class" },
        { id: "pw:DefectLength", label: shorten("http://prattwhitney.com/ontology#DefectLength"), group: "class" },
        { id: "pw:MeasurementUnitOfLength", label: shorten("http://prattwhitney.com/ontology#MeasurementUnitOfLength"), group: "class" },
    ];
    const subClassEdges_Initial = [ /* ... */
        { from: "pw:Airfoil", to: "pw:MaterialArtifact"}, { from: "pw:DefectRegion", to: "pw:FiatObjectPart"},
        { from: "pw:LeadingEdge", to: "pw:FiatObjectPart"}, { from: "pw:Defect", to: "pw:Quality"},
        { from: "pw:AirfoilDefect", to: "pw:Defect"}, { from: "pw:DistanceMeasurementInformationContentEntity", to: "pw:InformationContentEntity"},
        { from: "pw:MeasurementUnitOfLength", to: "pw:MeasurementUnit"}, { from: "pw:DefectDepth", to: "pw:DistanceMeasurementInformationContentEntity" },
        { from: "pw:DefectLength", to: "pw:DistanceMeasurementInformationContentEntity" },
    ].map(e => ({ ...e, label: shorten("rdfs:subClassOf"), arrows: "to", color: { color: 'darkgrey', inherit: false }, dashes: [5, 5] }));

    const nodes_D1 = [ /* ... */
        { id: "pw:airfoil1", label: shorten("pw:airfoil1"), group: "individual" }, { id: "pw:leading_edge1", label: shorten("pw:leading_edge1"), group: "individual" },
        { id: "pw:defect1_region", label: shorten("pw:defect1_region"), group: "individual" }, { id: "pw:airfoil_defect1", label: shorten("pw:airfoil_defect1"), group: "individual" },
        { id: "pw:Defect1_Depth_MICE", label: shorten("pw:D1_Depth_MICE"), group: "individual" }, { id: "pw:Defect1_Length_MICE", label: shorten("pw:D1_Length_MICE"), group: "individual" },
        { id: "pw:Defect1_Depth_IBE", label: shorten("pw:D1_Depth_IBE"), group: "individual" }, { id: "pw:Defect1_Length_IBE", label: shorten("pw:D1_Length_IBE"), group: "individual" },
        { id: "pw:inch_unit", label: shorten("pw:inch_unit"), group: "individual" },
        { id: "lit:D1_0.092", label: shorten('"0.092"^^http://www.w3.org/2001/XMLSchema#decimal'), group: "literal" },
        { id: "lit:D1_0.249", label: shorten('"0.249"^^http://www.w3.org/2001/XMLSchema#decimal'), group: "literal" },
    ];
    const typeEdges_D1 = [ /* ... */
        { from: "pw:airfoil1", to: "pw:Airfoil" }, { from: "pw:leading_edge1", to: "pw:LeadingEdge" }, { from: "pw:defect1_region", to: "pw:DefectRegion" },
        { from: "pw:airfoil_defect1", to: "pw:AirfoilDefect" }, { from: "pw:Defect1_Depth_MICE", to: "pw:DefectDepth" }, { from: "pw:Defect1_Length_MICE", to: "pw:DefectLength" },
        { from: "pw:Defect1_Depth_IBE", to: "pw:InformationBearingEntity" }, { from: "pw:Defect1_Length_IBE", to: "pw:InformationBearingEntity" }, { from: "pw:inch_unit", to: "pw:MeasurementUnitOfLength" },
    ].map(e => ({ ...e, label: shorten("rdf:type"), arrows: "to", color: { color: '#FF8C00', inherit: false } }));
    const relationEdges_D1 = [ /* ... */
        { from: "pw:airfoil1", to: "pw:leading_edge1", label: shorten("pw:hasContinuantPart") }, { from: "pw:airfoil1", to: "pw:defect1_region", label: shorten("pw:hasContinuantPart") },
        { from: "pw:airfoil_defect1", to: "pw:defect1_region", label: shorten("pw:inheresIn") }, { from: "pw:Defect1_Depth_MICE", to: "pw:airfoil_defect1", label: shorten("pw:describes") },
        { from: "pw:Defect1_Depth_MICE", to: "pw:Defect1_Depth_IBE", label: shorten("pw:genericallyDependsOn") }, { from: "pw:Defect1_Length_MICE", to: "pw:airfoil_defect1", label: shorten("pw:describes") },
        { from: "pw:Defect1_Length_MICE", to: "pw:Defect1_Length_IBE", label: shorten("pw:genericallyDependsOn") }, { from: "pw:Defect1_Depth_IBE", to: "lit:D1_0.092", label: shorten("pw:hasDecimalValue") },
        { from: "pw:Defect1_Depth_IBE", to: "pw:inch_unit", label: shorten("pw:usesMeasurementUnit") }, { from: "pw:Defect1_Length_IBE", to: "lit:D1_0.249", label: shorten("pw:hasDecimalValue") },
        { from: "pw:Defect1_Length_IBE", to: "pw:inch_unit", label: shorten("pw:usesMeasurementUnit") },
    ].map(e => ({ ...e, arrows: "to", color: { color: '#663399', inherit: false } }));

    const nodes_D2 = [ /* ... */
        { id: "pw:defect2_region", label: shorten("pw:defect2_region"), group: "individual" }, { id: "pw:airfoil_defect2", label: shorten("pw:airfoil_defect2"), group: "individual" },
        { id: "pw:Defect2_Depth_MICE", label: shorten("pw:D2_Depth_MICE"), group: "individual" }, { id: "pw:Defect2_Length_MICE", label: shorten("pw:D2_Length_MICE"), group: "individual" },
        { id: "pw:Defect2_Depth_IBE", label: shorten("pw:D2_Depth_IBE"), group: "individual" }, { id: "pw:Defect2_Length_IBE", label: shorten("pw:D2_Length_IBE"), group: "individual" },
        { id: "lit:D2_0.110", label: shorten('"0.110"^^http://www.w3.org/2001/XMLSchema#decimal'), group: "literal" },
        { id: "lit:D2_0.199", label: shorten('"0.199"^^http://www.w3.org/2001/XMLSchema#decimal'), group: "literal" },
    ];
    const typeEdges_D2 = [ /* ... */
        { from: "pw:defect2_region", to: "pw:DefectRegion" }, { from: "pw:airfoil_defect2", to: "pw:AirfoilDefect" }, { from: "pw:Defect2_Depth_MICE", to: "pw:DefectDepth" },
        { from: "pw:Defect2_Length_MICE", to: "pw:DefectLength" }, { from: "pw:Defect2_Depth_IBE", to: "pw:InformationBearingEntity" }, { from: "pw:Defect2_Length_IBE", to: "pw:InformationBearingEntity" },
    ].map(e => ({ ...e, label: shorten("rdf:type"), arrows: "to", color: { color: '#FF8C00', inherit: false } }));
    const relationEdges_D2 = [ /* ... */
        { from: "pw:airfoil1", to: "pw:defect2_region", label: shorten("pw:hasContinuantPart") }, { from: "pw:airfoil_defect2", to: "pw:defect2_region", label: shorten("pw:inheresIn") },
        { from: "pw:Defect2_Depth_MICE", to: "pw:airfoil_defect2", label: shorten("pw:describes") }, { from: "pw:Defect2_Depth_MICE", to: "pw:Defect2_Depth_IBE", label: shorten("pw:genericallyDependsOn") },
        { from: "pw:Defect2_Length_MICE", to: "pw:airfoil_defect2", label: shorten("pw:describes") }, { from: "pw:Defect2_Length_MICE", to: "pw:Defect2_Length_IBE", label: shorten("pw:genericallyDependsOn") },
        { from: "pw:Defect2_Depth_IBE", to: "lit:D2_0.110", label: shorten("pw:hasDecimalValue") }, { from: "pw:Defect2_Depth_IBE", to: "pw:inch_unit", label: shorten("pw:usesMeasurementUnit") },
        { from: "pw:Defect2_Length_IBE", to: "lit:D2_0.199", label: shorten("pw:hasDecimalValue") }, { from: "pw:Defect2_Length_IBE", to: "pw:inch_unit", label: shorten("pw:usesMeasurementUnit") },
    ].map(e => ({ ...e, arrows: "to", color: { color: '#663399', inherit: false } }));

    const highlightNodeIds = [ /* ... */
        "pw:airfoil_defect2", "pw:Defect2_Length_MICE", "pw:Defect2_Length_IBE", "lit:D2_0.199"
    ];
     const highlightEdgeConnections = [ /* ... */
         { from: "pw:Defect2_Length_MICE", to: "pw:airfoil_defect2", label: "describes" }, { from: "pw:Defect2_Length_MICE", to: "pw:Defect2_Length_IBE", label: "genericallyDependsOn" },
         { from: "pw:Defect2_Length_IBE", to: "lit:D2_0.199", label: "hasDecimalValue" }, { from: "pw:airfoil_defect2", to: "pw:AirfoilDefect", label: "type" },
         { from: "pw:Defect2_Length_MICE", to: "pw:DefectLength", label: "type" }, { from: "pw:Defect2_Length_IBE", to: "pw:InformationBearingEntity", label: "type" }
     ];
    // --- SPARQL Query String (Optional - Add if needed) ---
    // const sparqlQueryDefect2Length = `...`;


    // --- 3. Setup vis.js Network ---
    const container = document.getElementById('mynetwork');
    const showDefect1Btn = document.getElementById('showDefect1Btn');
    const showDefect2Btn = document.getElementById('showDefect2Btn');
    const highlightQueryBtn = document.getElementById('highlightQueryBtn');
    // const sparqlQueryDisplayDiv = document.getElementById('sparqlQueryDisplay'); // Uncomment if using
    // const sparqlCodeElement = document.getElementById('sparqlCode'); // Uncomment if using

    const nodes = new vis.DataSet();
    const edges = new vis.DataSet();

    nodes.add(initialClassNodes);
    edges.add(subClassEdges_Initial);

    const data = { nodes: nodes, edges: edges };
    const initialClassNodeIds = initialClassNodes.map(n => n.id);

    const initialOptions = { // Options for the initial hierarchical layout
        layout: {
            hierarchical: {
                enabled: true, direction: "UD", sortMethod: "directed",
                levelSeparation: 150, nodeSpacing: 130, treeSpacing: 200
            }
        },
        physics: {
            enabled: true, // Physics needed for hierarchical layout to run
            hierarchicalRepulsion: {
                 centralGravity: 0.1, springLength: 120, springConstant: 0.01,
                 nodeDistance: 150, damping: 0.09
            },
            minVelocity: 0.75,
            solver: 'hierarchicalRepulsion', // Use solver compatible with hierarchical
            stabilization: { // Stabilization options for initial layout
                 enabled: true, iterations: 1000, updateInterval: 50,
                 onlyDynamicEdges: false, fit: true
            }
        },
        interaction: { hover: true, tooltipDelay: 200, navigationButtons: true },
        nodes: { font: { size: 12, face: 'tahoma' }, borderWidth: 2 },
        edges: { width: 1.5, font: { size: 9, align: 'middle' }, smooth: { enabled: false } }, // Straight edges often better for hierarchical
        groups: {
             class: { color: { background: CLASS_COLOR_FILL, border: CLASS_COLOR_BORDER }, shape: 'box' },
             individual: { color: { background: INDIVIDUAL_COLOR_FILL, border: INDIVIDUAL_COLOR_BORDER }, shape: 'ellipse' },
             literal: { color: { background: LITERAL_COLOR_FILL, border: LITERAL_COLOR_BORDER }, shape: 'circle', font: { size: 10 } }
         }
    };

    // Store calculated start position globally or pass it appropriately
    let calculatedStartX = 0;
    let calculatedStartY = 0;

    const network = new vis.Network(container, data, initialOptions); // Use initial options

    // --- 4. Logic to Fix Class Positions & Enable Buttons ---
    network.once("stabilizationIterationsDone", function () {
        console.log("Initial Class layout stabilization complete.");
        const classPositions = network.getPositions(initialClassNodeIds);
        const classUpdates = [];
        let minY = Infinity, maxY = -Infinity, minX = Infinity, maxX = -Infinity;

        for (const nodeId in classPositions) {
            if (initialClassNodeIds.includes(nodeId)) {
                const pos = classPositions[nodeId];
                classUpdates.push({ id: nodeId, fixed: { x: true, y: true }, physics: false });
                // Find bounds of fixed nodes
                if (pos.y < minY) minY = pos.y;
                if (pos.y > maxY) maxY = pos.y;
                if (pos.x < minX) minX = pos.x;
                if (pos.x > maxX) maxX = pos.x;
            }
        }

        if (classUpdates.length > 0) {
             nodes.update(classUpdates);
             console.log(`Fixed positions for ${classUpdates.length} initial class nodes.`);
             // Calculate starting position for the *first* set of individuals
             calculatedStartX = (minX + maxX) / 2; // Center X below classes
             calculatedStartY = maxY + 180; // Position below the lowest class node + buffer
             console.log(`Calculated initial position for D1 individuals: X=${calculatedStartX.toFixed(2)}, Y=${calculatedStartY.toFixed(2)}`);
        } else {
            console.warn("No class nodes found to fix or calculate position from.");
            // Fallback position if needed
            calculatedStartX = container.offsetWidth / 2;
            calculatedStartY = 200;
        }

        showDefect1Btn.disabled = false; // Enable first button

        // NOW switch layout options AFTER fixing classes and calculating start positions
        network.setOptions({
            layout: { hierarchical: false }, // Turn off hierarchical
            physics: {
                enabled: true, // Keep physics enabled
                solver: 'barnesHut', // Switch to BarnesHut
                barnesHut: { // Configure BarnesHut
                    gravitationalConstant: -15000, // Standard repulsion
                    centralGravity: 0.1,        // Slight pull to center
                    springLength: 130,          // Resting edge length
                    springConstant: 0.04,       // Edge stiffness
                    damping: 0.1,               // Slow down movement
                    avoidOverlap: 0.2           // Prevent nodes overlapping (adjust 0 to 1)
                },
                stabilization: { // Stabilization for BarnesHut (can be shorter)
                    enabled: true,
                    iterations: 300
                }
            }
        });
        console.log("Switched to physics (BarnesHut) layout for individuals.");
    });

    // Helper to add nodes only if they don't exist
    function addUniqueNodes(nodeArray) {
        const nodesToAdd = nodeArray.filter(n => !nodes.get(n.id));
        if (nodesToAdd.length > 0) {
            nodes.add(nodesToAdd);
        }
        return nodesToAdd.length;
    }

    // --- 5. Button Event Handlers ---
    showDefect1Btn.onclick = function() {
        console.log("Showing Defect 1 Data with initial positions...");
        try {
            // Prepare D1 nodes with calculated initial positions
            const nodesWithPositions_D1 = nodes_D1.map((node, index) => {
                const spacing = 100; // Horizontal spacing between initial nodes
                const numNodes = nodes_D1.length;
                // Calculate x position centered around calculatedStartX
                const xPos = calculatedStartX + (index - (numNodes - 1) / 2) * spacing;
                return {
                    ...node, // Copy existing node properties
                    x: xPos,
                    y: calculatedStartY + (Math.random() * 40 - 20) // Add slight random y variation around the target Y
                };
            });

            // Add the prepared nodes (use the helper, it filters correctly)
            const addedNodesCount = addUniqueNodes(nodesWithPositions_D1);
            console.log(`Added ${addedNodesCount} new nodes for Defect 1 with initial positions.`);

            // Add edges for D1
            edges.add(typeEdges_D1);
            edges.add(relationEdges_D1);

            showDefect1Btn.disabled = true;
            showDefect2Btn.disabled = false; // Enable next stage

            // No need for extra stabilize here, BarnesHut is running. Fit the view.
            network.fit();

        } catch (error) {
             console.error("Error adding Defect 1 data:", error);
         }
    };

    showDefect2Btn.onclick = function() {
        console.log("Showing Defect 2 Data...");
        try {
            // Add D2 nodes WITHOUT predefined positions.
            // The physics engine will place them relative to existing nodes.
            const addedNodesCount = addUniqueNodes(nodes_D2);
            edges.add(typeEdges_D2);
            edges.add(relationEdges_D2);
            console.log(`Added ${addedNodesCount} new nodes for Defect 2.`);

            showDefect2Btn.disabled = true;
            highlightQueryBtn.disabled = false; // Enable highlighting

            // Maybe a brief stabilization helps settle the new nodes smoothly
            network.stabilize(200);
            network.fit(); // Fit view after adding D2

        } catch (error) {
             console.error("Error adding Defect 2 data:", error);
         }
    };

    highlightQueryBtn.onclick = function() {
        console.log("Highlighting Defect 2 Length Path...");
        try {
            // --- Reset Highlights (robust version) ---
             const allNodeIds = nodes.getIds();
             const nodeResets = allNodeIds.map(id => {
                 const node = nodes.get(id);
                 if (!node) return null;
                 const groupColors = initialOptions.groups[node.group]?.color || {}; // Use initial options groups
                 const defaultFill = groupColors.background || '#97C2FC';
                 const defaultBorder = groupColors.border || '#2B7CE9';
                 return {
                     id: id, color: { background: defaultFill, border: defaultBorder },
                     borderWidth: 2, font: { size: node.group === 'literal' ? 10 : 12, bold: false, color: 'black' }
                 };
             }).filter(u => u !== null);
             if (nodeResets.length > 0) nodes.update(nodeResets);

             const allEdgeIds = edges.getIds();
             const edgeResets = allEdgeIds.map(id => {
                 const edge = edges.get(id);
                 if (!edge) return null;
                 let originalColor = '#663399'; // Default relation
                 if (edge.label === shorten('rdf:type')) originalColor = '#FF8C00'; // Type
                 else if (edge.dashes) originalColor = 'darkgrey'; // Subclass
                 return {
                     id: id, color: { color: originalColor, highlight: originalColor, hover: originalColor },
                     width: 1.5, arrows: { to: { enabled: true, scaleFactor: 1.0 } }
                 };
             }).filter(u => u !== null);
             if (edgeResets.length > 0) edges.update(edgeResets);
             console.log("Reset previous highlights.");

             // --- Apply new highlights ---
            const nodeUpdates = highlightNodeIds
                .filter(id => nodes.get(id)) // Ensure node exists
                .map(id => ({
                    id: id, color: { background: 'salmon', border: 'red' }, borderWidth: 3,
                    font: { size: 14, color: 'black', bold: true }
                }));
             if (nodeUpdates.length > 0) nodes.update(nodeUpdates);

             const edgeUpdates = [];
             const currentEdges = edges.get({ fields: ['id', 'from', 'to', 'label'] });
             currentEdges.forEach(edge => {
                 // Use shorten on the label definition for comparison consistency
                 const isHighlight = highlightEdgeConnections.some(hc =>
                     hc.from === edge.from && hc.to === edge.to && edge.label?.includes(shorten("pw:"+hc.label)) // Add pw: prefix for lookup
                 );
                  const isHighlightType = highlightEdgeConnections.some(hc =>
                     hc.from === edge.from && hc.to === edge.to && edge.label?.includes(shorten("rdf:"+hc.label)) // Check rdf:type
                 );

                 if (isHighlight || isHighlightType) {
                     edgeUpdates.push({
                         id: edge.id, color: { color: 'red', highlight: 'darkred', hover: 'darkred' },
                         width: 3, arrows: { to: { enabled: true, scaleFactor: 1.5 } }
                     });
                 }
             });
             if(edgeUpdates.length > 0) {
                 edges.update(edgeUpdates);
                 console.log(`Highlighted ${nodeUpdates.length} nodes and ${edgeUpdates.length} edges for Defect 2 Length.`);
             } else {
                 console.warn("No D2 Length edges found matching highlight criteria.");
             }

            highlightQueryBtn.disabled = true; // Disable after one click

            // --- Optional: Show SPARQL Query ---
            // if (sparqlCodeElement && sparqlQueryDisplayDiv) {
            //      sparqlCodeElement.textContent = sparqlQueryDefect2Length.trim();
            //      sparqlQueryDisplayDiv.style.display = 'block';
            // }

        } catch (error) {
             console.error("Error highlighting query path:", error);
         }
    };

</script>

</body>
</html>
