Slide Title: What Does an Ontology Look Like? (Aerospace Example)
Script / Speaker Notes

Intro:

    “On this slide, I’ll show you how the same piece of knowledge—about a rocket engine and the propellants it uses—can be represented in different forms: from formal logic to a graphical diagram, and finally in a machine-processable OWL file.”

1. Multiple Ways to Represent the Same Knowledge

    Formal Logic (FOL)
        Speaker Note: “Here’s the rigorous mathematical statement of our domain fact: every rocket engine uses only rocket propellant, plus at least one of them is cryogenic. This is how a logician might express it.”

    Description Logic
        Speaker Note: “In Description Logics, we capture essentially the same constraints. This language is often used by ontologists and knowledge engineers to drive automated reasoning about class hierarchies and relationships.”

    User-Friendly/Natural Language
        Speaker Note: “Of course, domain experts prefer something easier to read. We can automatically generate a plain-English sentence: ‘Every rocket engine uses only rocket propellants and uses at least one cryogenic propellant.’”

    Graphical Diagram (Protégé/UML)
        Speaker Note: “Using a visual editor like Protégé or a UML-style diagram, we draw a ‘RocketEngine’ class connected to ‘RocketPropellant’ by the property ‘uses,’ with annotations or constraints showing ‘only rocket propellant’ and ‘at least one cryogenic propellant.’”

2. Machine-Processable (OWL/RDF) Example

    Speaker Note:
    “Finally, here’s the OWL/RDF code. A computer can read this directly. Notice how we have <owl:Restriction> blocks defining ‘allValuesFrom’ (only RocketPropellant) and ‘someValuesFrom’ (at least one CryogenicPropellant). This is the backbone of semantic web technologies—allowing reasoners and applications to interpret these axioms unambiguously.

    We see classes like RocketEngine, Engine, and RocketPropellant, as well as the object property uses. The comment is optional metadata for human readers.”

Closing:

    “All these representations describe the same fact: a rocket engine relies exclusively on rocket propellants, and at least one of those propellants is cryogenic. Each format has a specific purpose—from helping domain experts grasp constraints in plain language to enabling software agents to perform automated reasoning and consistency checks.”0
