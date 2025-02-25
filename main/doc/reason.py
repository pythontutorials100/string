Slide: Object Properties (CCO-Compliant)

Description

    Object properties define how classes (entities) relate to each other, crucial for answering DSQs.
    In CCO, properties typically derive from upper-level relations such as part-of, occurs-in, or has-agent.

Examples

    JetEngine cco:partOf Aircraft
        Indicates an engine is part of (or integrated into) an aircraft.
    MaintenanceCrew cco:agentOf MaintenanceEvent
        Specifies that a maintenance crew is the agent (actor) of a maintenance event.
    PerformanceEvent cco:occursDuring TimeInterval
        Captures that the performance event takes place over a specific time interval.
