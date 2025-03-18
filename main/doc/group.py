Create an object property :measuredFromPart as a subproperty of :is_about (or :describes), domain = your measurement class, range = FiatObjectPart (or MaterialEntity, depending on how you structure Tip, LeadingEdge, etc.).

For structural constraints (like “Index1 must only reference tip or platform”), add subclass axioms to the measurement classes in Protégé:

:Index1Measurement
   SubClassOf ( 
      :MeasurementInformationContentEntity
      and ( :measuredFromPart only ( :Tip or :Platform ) ) 
   ).

For numeric threshold‐based constraints (like “If chordwise < 0.080” from the leading edge, then the reference must be :leadingEdge”), you generally need SWRL:

Index3Measurement(?m)
^ hasDecimalValue(?m, ?val)
^ swrlb:lessThan(?val, 0.08)
-> measuredFromPart(?m, :leadingEdge1).

To enforce that any contradictory statement is inconsistent, add a subclass axiom that says an Index3Measurement must only be measured from whichever parts are valid. Then if your data says “less than 0.08 but measuredFromPart = tip,” the reasoner should reveal an inconsistency or classification conflict.






=====================


Index3Measurement 
  SubClassOf 
    (measuredFromPart exactly 1 LeadingEdge) 
    or (measuredFromPart exactly 1 TrailingEdge).

Then the SWRL rule ensures that if the distance < 0.08, we also infer measuredFromPart LeadingEdge. If the data explicitly states a contradictory measuredFromPart, the reasoner sees a conflict.
