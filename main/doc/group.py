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


1. First-Order Logic Statement

Statement:
∀x(RocketEngine(x)→[∀y(uses(x,y)→RocketPropellant(y))  ∧  ∃z(uses(x,z)∧CryogenicPropellant(z))])
∀x(RocketEngine(x)→[∀y(uses(x,y)→RocketPropellant(y))∧∃z(uses(x,z)∧CryogenicPropellant(z))])

How to Read It Aloud (Script):

        “For every object x—
            if x is a RocketEngine, then two things must be true:
                For every object y, if x uses y, then y must be a RocketPropellant.
                There exists at least one object z such that x uses z, and that z is a CryogenicPropellant.”

Then you might add an interpretation:

        “In simpler terms, every rocket engine uses only rocket propellants, and must use at least one cryogenic propellant.”

2. Description Logic Statement

Statement:
RocketEngine  ⊑  ∀uses.RocketPropellant  ⊓  ∃uses.CryogenicPropellant
RocketEngine⊑∀uses.RocketPropellant⊓∃uses.CryogenicPropellant

How to Read It Aloud (Script):

        “RocketEngine is a subclass of ‘for all uses RocketPropellant’ and ‘there exists uses CryogenicPropellant.’”

To clarify further:

        “Any entity classified as a RocketEngine has the property that everything it ‘uses’ is a RocketPropellant, and there is at least one thing it ‘uses’ that is a CryogenicPropellant.”

Simplified Interpretation:

        “So, if something is a RocketEngine, it can’t use anything that isn’t a RocketPropellant, and it must use at least one cryogenic propellant.”

Additional Notes to Emphasize

    ∀ (For all): Imposes a universal condition (e.g., “all items used are rocket propellants”).
    ∃ (There exists): Imposes an existential condition (“at least one such item is cryogenic”).
    ⊑ (Subclass or ‘is a subset of’): Means every instance of the left class meets the conditions on the right.

By reading them in plain English, you can convey the logic without overwhelming the audience with symbols.
