Hello everyone. 
I'm Shatad Purohit. 
Today, I'll be discussing data integration for connected products, specifically through the lens of our recent PW-USAF Pilot. 
This effort focused on creating an Inspection Digital thread with the goal of significantly Improving Repair Process Efficiency. 
I will share the challenges and the knowledge-based solution we've developed.
-----
Slide 1---
Ensuring the safety and readiness of our advanced engines depends critically on how efficiently and accurately we inspect parts like airfoils and determine the right repairs. Pratt & Whitney has invested in excellent tools that generate incredibly valuable data for this...
But here's the core challenge in simple terms: We possess all the critical information needed – from detailed scans to precise repair calculations. However, this data lives in separate 'digital boxes' and speaks different 'languages'. There's no easy way for these boxes to talk to each other automatically. This forces engineers to manually connect the dots, which takes time and introduces risk. Now let's look at the specific pieces...

..First, we have sophisticated inspection systems doing detailed 3D scans, like a high-res medical scan for the part. These capture precise defect details – size, depth, location coordinates – giving us numerical data and updated 3D models.

Then, we often have localization rules, frequently as plain text documents. These are essential instructions telling an engineer how to use the scan's numbers to find the exact physical spot on the airfoil. This requires manual reading and interpretation.

Furthermore, Pratt & Whitney developed cutting-edge FEA simulations. 
that run complex calculations to determine the optimal repair procedure – like precise blend shapes or fillet radii. This vital repair specification often comes out as semi-structured data in JSON format.
So, we have these incredibly valuable pieces: the detailed scan data, the human-readable rules, the 3D models, and the specific FEA-generated repair specifications. As the slide highlights, they exist separately. The data is heterogeneous – different types and formats – and siloed – locked in different places

Crucially, there's no established, automated way to connect these dots. This lack of integration forces engineers into time-consuming manual efforts – finding the right scan file, matching it with the correct rule, locating the specific FEA JSON output, and interpreting how they all relate, whether working internally or preparing data to share between PW and the Air Force.

•	First, it inevitably slows down analysis and repair decisions. Time is spent manually assembling data instead of acting on it.
•	Second, it blocks standardized data sharing. We can't easily automate data exchange or build a robust digital thread if the foundational data isn't structured and linked in a machine-readable way.
•	And third, it prevents a holistic view and hinders advanced analysis. You can't easily see the defect and its calculated repair plan together, making it difficult to optimize processes or identify trends across many parts.

In short, we have rich, valuable islands of data, but no automated bridges connecting them. This creates inefficiency today and limits our ability to build a truly connected and intelligent future for engine maintenance. Our Knowledge Graph pilot was designed specifically to build those essential bridges.
