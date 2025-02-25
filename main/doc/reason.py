1. Competency Questions
1.1 What Are Competency Questions?

Competency questions capture the requirements that an ontology must fulfill. Think of them as the motivating queries an engineer, designer, or automated system wants to ask of the knowledge graph.

    Informal Competency Questions
        Definition: High-level, descriptive, human-readable queries.
        Purpose: Provide clarity on what the domain experts and stakeholders want from the ontology, before getting into the details of logic.
        Example (Aerospace manufacturing scenario):
            “Which activities must a particular technician perform to complete a scheduled maintenance event?”
            “Which components in the rocket engine assembly line are causing the most frequent delays?”
            “Which sub-system design changes require regulatory approval?”

    Formal Competency Questions

        Definition: The exact same questions rephrased in a logical language (e.g., first-order logic, OWL axioms, etc.).

        Purpose: Ensure questions can be tested automatically against the formal ontology. In other words, they become formal entailment or consistency queries that the ontology must satisfy.

        Example (Continuing the “technician” scenario above in a simplified first-order style):

        ∃activity, technician, time 
          [ AssignedTo(activity, technician) ∧ 
            ScheduledStart(activity, time) ∧ 
            HasTaskRequirement(activity, "MaintenanceCheck") ]

        Here, the query is: “Find any activity (event) assigned to some technician at a particular time, which includes the maintenance check task.”

How to Elicit Good Competency Questions

    Tie Them to Real-World Needs: Start with a scenario such as a machine breakdown or a design change request.
    Stratify: Have some questions that are straightforward lookups (“Which agent is assigned to X?”) and some that require reasoning over multiple facts or constraints (“If agent A has limited capacity, can agent B and A together finish the task on schedule?”).
    Test for Necessity: Each question should justify the inclusion of concepts and relationships in the ontology. If you can’t trace a piece of the ontology back to a competency question, reconsider whether it’s needed.

2. Specification in First-Order Logic

Once you know what questions you want to answer, the next step is specifying how you will represent the relevant entities, relationships, and constraints so that these questions can be formally addressed.
2.1 Terminology (Objects, Attributes, Relations)

    Objects / Classes: These can be physical artifacts (e.g., “EngineBlock”, “Nozzle”, “Technician”), more abstract entities (e.g., “Task”, “Requirement”), or situational placeholders (e.g., “Situation s”, “Action a”).
    Attributes (Unary Predicates): Properties that describe an object, e.g., isCritical(Task), hasClearance(Technician).
    Relations (N-ary Predicates): Relationships between two or more objects, e.g.,
        performs(Technician, Task)
        requires(Task, Resource)
        precedes(Task1, Task2)
        authorizedBy(Activity, Supervisor)

Example: Simplified Terminology

Suppose an aerospace maintenance scenario has these key terms:

    Classes:
        Technician, MaintenanceEvent, Resource, Component, TimeSlot
    Attributes:
        Critical(Component) indicates whether a component is safety-critical.
    Relations:
        assignedTo(MaintenanceEvent, Technician)
        requires(MaintenanceEvent, Resource)
        scheduledAt(MaintenanceEvent, TimeSlot)
        dependsOn(MaintenanceEvent1, MaintenanceEvent2)

In a first-order logic style, you might define domain sorts (e.g., Tech, Event, Res, ...) or simply rely on unary predicates: Technician(x), MaintenanceEvent(y).
2.2 Axioms (The Logical Theory)

    Purpose: Axioms specify the rules and constraints that give meaning to your terminology.
    Form: Each axiom is typically a first-order logic formula that says, “Under conditions X, Y must be true.”
    Types of Axioms:
        Definition Axioms: Precisely define a concept. For example, you could define that a MaintenanceEvent is something that requires at least one Resource.
        Constraint Axioms: Restrict the ways in which concepts can be combined. For instance:
            “If a maintenance event depends on another, they cannot be scheduled in the same time slot.”
            “No resource can be used by two maintenance events simultaneously if the resource’s capacity is 1.”
        Causal/Temporal Axioms (Situation Calculus Style): Describe how an action (e.g., performing a certain step) changes the state of the world.

Example: Axioms for Scheduling Constraints

    Resource Capacity

∀ev1, ev2, r 
  [requires(ev1, r) ∧ requires(ev2, r) ∧ ev1 ≠ ev2 ∧ SingleUseResource(r) 
    → scheduledAt(ev1, t1) ∧ scheduledAt(ev2, t2) ∧ t1 ≠ t2 ]

Meaning: If ev1 and ev2 both require the same single-use resource, they cannot occupy the same time slot.

Dependency Ordering

    ∀ev1, ev2 
      [dependsOn(ev1, ev2) → 
          ∀t1, t2 (scheduledAt(ev1, t1) ∧ scheduledAt(ev2, t2) → t2 < t1)]

    Meaning: If an event ev1 depends on ev2, then the time for ev2 must be strictly earlier than the time for ev1.

3. Completeness Theorems / Ontology Evaluation
3.1 Why Evaluate Ontologies?

After defining the objects, relationships, and axioms, you must check that your ontology is actually capable of answering the competency questions you started with.

    Completeness: Is the ontology sufficient to yield answers to each competency question? Or is there some question Q that remains unanswerable (no axiom or chain of axioms that can confirm or deny Q)?
    Necessity: Are all the axioms genuinely needed for those answers, or is there redundant modeling?

3.2 Proving or Demonstrating Completeness

    Proving Completeness typically involves showing, for each competency question, that it is entailed by (or consistent with) the axioms in exactly the ways you intend.
    Methods can range from fully formal mathematical proofs (like situation calculus completeness theorems) to smaller-scale test queries in a reasoner (e.g., using SPARQL or SWRL rules in an OWL context).

Example: Checking a Competency Question

    Informal Question: “Does the scheduling ontology allow us to determine whether two maintenance events can be performed in parallel?”
    Formal Version: ∃ev1, ev2 [scheduledAt(ev1, t1) ∧ scheduledAt(ev2, t2) ∧ t1 = t2 ∧ ev1 ≠ ev2 ∧ canCoexist(ev1, ev2)]
    Check:
        Is there an axiom that states under what conditions canCoexist(ev1, ev2) is true or false?
        If an event requires a single-use resource, does that forbid parallel scheduling?
        When you load these axioms into a reasoner (or do the relevant proofs), can you see the engine concluding that certain events indeed can or cannot be parallelized?

If the ontology and its axioms do not enable the system to determine parallel feasibility, that reveals an incompleteness. Perhaps you need a new predicate or axiom to specify concurrency constraints more precisely.
3.3 Iterating Until All Questions Are Answerable

    In practice, you almost always discover you need more detail in your domain definitions or constraints to capture real-world scenarios.
    This is iterative: define a piece, test it on the competency questions, refine, and repeat until the ontology is robust enough.

Putting It All Together: A Mini Example

Imagine a small ontology for “Maintenance Events” in a hypothetical aerospace facility:

    Motivating Scenario:
        Frequent scheduling conflicts over shared calibration equipment are delaying engine production. Managers want to automate scheduling in a way that respects resource constraints and technician qualifications.

    Some Sample Competency Questions:
        Informal:
            “Which technicians are qualified to perform an event’s calibration tasks?”
            “Can two different maintenance events occur at the same time if they share resources?”
        Formal:
            ∃tech, event [ Technician(tech) ∧ MaintenanceEvent(event) ∧ qualifiedFor(tech, event) ]
            ∀ev1, ev2 [ scheduledAt(ev1, t) ∧ scheduledAt(ev2, t) → (∀r [requires(ev1, r) → ¬requires(ev2, r)]) ]

    Terminology:
        Technician(x), MaintenanceEvent(y), Resource(r), etc.
        qualifiedFor(tech, event), requires(ev, res), scheduledAt(ev, timeslot), etc.

    Axioms:
        Qualification Axiom: A technician is qualified for an event if the event’s required skill is in the technician’s skill set.
        Resource Constraint Axiom: A single-use resource cannot be used by two events at the same overlapping time slot.
        And so on.

    Evaluation:
        Load or encode these axioms in a logical reasoner.
        Ask: “Which technicians are suggested for the next calibration event?” “Are two events sharing the same single-use resource scheduled at the same time?”
        Confirm the model’s inferences match your domain expectations.

If it doesn’t answer them correctly or fully, refine your definitions, relations, or axioms until it does.
Key Takeaways

    Competency Questions are your guiding star—tie every piece of the ontology to at least one of them.
    Specification in First-Order Logic (or another formalism) ensures your ontology is precise and machine-processable.
    Completeness Theorems / Evaluation close the loop by verifying that your ontology can truly handle the initial requirements.
    Iterate: This is rarely a linear, one-pass process. Each new insight from testing or domain feedback can lead you back to refine your questions, terminology, or axioms.

For engineers, this approach yields a practically useful knowledge graph or ontology—one that not only defines domain concepts but can genuinely reason about them in a way that aligns with your real-world applications.
