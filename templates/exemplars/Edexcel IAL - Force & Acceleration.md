<!-- PACK REFERENCE EXEMPLAR (F33) — Edexcel IAL Physics, "Force & Acceleration".
REGISTER AND DEPTH REFERENCE ONLY — never this course's content, never a research
source, never something to quote. Chosen by Katie (7 Aug 2026) as the A-level
register anchor for pilot writers on new courses. From a finished course on the
current template (frontmatter, spec quotes, flag blocks, per-SP exam sections),
so its STRUCTURE may be imitated as well as its register — with two caveats:
(1) it predates the F40 heading ruling, so it uses the retired
"### How <SP> Appears in Exams" form; new files use "### <SP name> — In the Exam";
(2) the course's own ratified exam skeleton and the project README's template
rules always take precedence over anything in this file;
(3) PROVENANCE (recorded 13 Aug 2026): this file is the hand-authored "enriched
v2 pilot" of 24 Jul 2026 — it predates the research pipeline, has no research
pack behind it, and never passed the adversarial checker gate. It is a REGISTER
AND DEPTH model only, never a content or claims model. Its unsupported marking
claims were re-scoped to the ruled hedged forms on 13 Aug 2026 (Katie's ruling,
IAL exposure assessment decision 5); do not imitate any residual sentence that
promises or denies marks — the current WRITER.md manufactured-certainty rules
outrank this file everywhere. -->

---
section: 1. Mechanics & Materials
topic: Forces & Momentum
subtopic: Force & Acceleration
tags: [physics, project-hero]
---

# Sub-topic: Force & Acceleration

## Spec Point: Newton's First Law of Motion

> **Specification:** be able to understand situations involving objects at rest or travelling at constant velocity (Newton's first law of motion) where a = 0

**Key terminology:** resultant force · equilibrium · constant velocity · vector · resultant moment · rigid body · force balance

**Mathematical skills:** applying Σ*F* = 0 to find unknown forces · writing vector-sum equilibrium equations that equal zero · resolving forces into components with sin and cos · balancing forces on a slope with friction = *mg* sin *θ* · quoting show-that answers to more significant figures than the target

### The Law

Newton's first law states:

**A body will remain at rest or move with constant velocity unless acted on by a resultant force.**

The law covers two situations, and both require exactly the same condition — **zero resultant force**:

| Situation | Zero resultant force means |
|:---|:---|
| Object at rest | It stays at rest |
| Object moving | It continues at constant velocity (constant speed in a straight line) |

Velocity is a **vector** — it has both magnitude (speed) and direction. So the velocity of an object can only change if a resultant force acts on it. This includes changes of direction: an object turning a corner at constant speed is changing velocity, and that requires a resultant force.

- **Resultant force** — the single force that would have the same effect as all the forces acting together (defined fully under Newton's Second Law of Motion)
- **Equilibrium** — zero resultant force and zero **resultant moment** (the net turning effect of all the forces)
- **Constant/uniform velocity** — the standard signal in a question that ΣF = 0 applies

> [!tip] Why Does an Object Keep Moving Without a Force? (Teaching Point)
> Everyday experience suggests that things stop moving when nothing pushes them — but that is because friction and drag are themselves forces. A force is not needed to *keep* an object moving; a force is needed to *change* its motion. Zero resultant force means no change in motion.
>
> Students who carry the everyday intuition that "motion needs a force" into the exam tend to describe a drag-balanced object as if its driving force "ran out". Replace that intuition with the rule: no resultant force, no change in velocity.

### "Constant Velocity" Is an Instruction, Not Background Detail

The phrase *constant velocity*, *uniform velocity*, *constant speed in a straight line* or *at rest* in a question stem is the cue to write a **force balance** — an equation setting the sum of the forces to zero. It tells you, with certainty, that:

$$ΣF = 0$$

Use this to find unknown forces. For example, if a boat moves at constant velocity with a driving force of 2000 N, the total resistive force must be exactly 2000 N — no calculation beyond the balance itself is needed.

Where more than two forces act, balance each direction separately:

**Worked example:**
A cyclist travels at constant velocity. The forward driving force is 150 N and air resistance is 110 N. Calculate the friction force from the road.

- At constant velocity, the resultant force is zero: 150 N − 110 N − *F* = 0
- *F* = 40 N

Note that forces in opposite directions **subtract**. Adding all the magnitudes together is a common slip — keep track of directions from the start.

### Writing the Force Balance as a Vector Equation

For an object in equilibrium, the forces acting on it add to zero **as vectors**:

$$\overset{\rightarrow}{F_1} + \overset{\rightarrow}{F_2} + \overset{\rightarrow}{F_3} = 0$$

This is exactly what Section A tests. In October 2023 Q9, a box of weight *W* hangs in equilibrium from two ropes with tensions *T*₁ and *T*₂, and the correct vector expression is:

$$\overset{\rightarrow}{W} + \overset{\rightarrow}{T_1} + \overset{\rightarrow}{T_2} = 0$$

The three wrong options each set one force equal to the sum of the others. For a body in equilibrium that is never right: the forces must add to zero as vectors — which is exactly the reason the mark scheme gave for rejecting all three.

When forces act at angles, resolve into components first, then apply equilibrium in each direction separately.

**Worked example — June 2023 Q17:**
A buoy is held stationary by a chain. Water flowing past the buoy causes a horizontal force of 260 N. The chain exerts a force *F* on the buoy at an angle of 33° to the vertical. Show that *F* is about 500 N.

- The buoy is in equilibrium, so horizontal forces balance
- The horizontal component of the chain force is *F* sin 33° (the angle is measured from the **vertical**, so the horizontal component takes sin)
- *F* sin 33° = 260 N
- *F* = 260 ÷ sin 33° = 477 N ≈ 480 N, confirming the "about 500 N" in the question (a show-that answer keeps the extra significant figures)

The two marks here are for equating the correct component to the water force, then the evaluated answer. Choosing cos instead of sin — by not checking which side of the angle is which — is the standard way to lose both.

> [!tip] Resolving on Slopes (Teaching Point)
> An object on a slope at constant speed is in equilibrium **along the slope**: the component of weight down the slope, *mg* sin *θ*, is balanced by friction (or another resistive force) up the slope. Section A has asked exactly this — identify the relationship between friction and the weight component for a box sliding down a ramp at constant speed (June 2025 Q8, October 2024 Q5). The answer is always the balance: friction = *mg* sin *θ*.

### Equilibrium of a Rigid Body: Two Conditions

For a point object, equilibrium just means zero resultant force. For an **extended, rigid body** — an object with size and fixed shape, such as a door, a beam or a see-saw — there are **two** conditions, and exam answers must state both:

1. The resultant force is zero
2. The resultant moment (about any point) is zero

**Common exam question:** "State what is meant by equilibrium" (2 marks)
- Contexts: a stone held by a builder's foot (January 2023 Q13), a door on two hinges (January 2024 Q18)
- Mark schemes award exactly one mark per condition — stating only the force condition caps you at half marks

The same idea appears in Section A: a see-saw loaded symmetrically with equal weights at equal distances is in equilibrium, so **both** its resultant force and its resultant moment are zero (June 2025 Q2).

### Which Law Explains What

The first law explains *why velocity is constant* (zero resultant force). The second law explains *what happens when it is not* (acceleration). Extended answers are credited for invoking the right law for the right phase of motion.

> [!warning] Citing the Second Law for Constant Velocity
> **Constant velocity is explained by Newton's first law — never the second.** Before naming a law in an answer, ask one question: is the velocity constant or changing? Constant → first law (zero resultant force). Changing → second law (resultant force causes acceleration).
>
> Citing the second law for uniform motion is a recurring error in MCQs and extended responses alike. **June 2019 Unit 1:** "It is Newton's first law that explains why an object without a resultant force continues with a uniform velocity."

> [!warning] Answering the Wrong Question Entirely
> **Identify what the question is actually asking for before you start writing** — which quantity, which law, forces or energy. Underline the command word and the subject of the question, then choose the physics to match.
>
> Examiners regularly see whole cohorts answer a different question from the one set. **October 2021 Unit 1:** when a question asked for an account of the *forces* on a toy car, "the majority attempted an explanation in terms of energy"; in the same paper a Stokes' law part "was about Newton's first law" and many missed it.

### Reaching a New Constant Velocity

If something changes — an extra resistive force appears, a driving force increases — a body at constant velocity does not simply jump to a new constant velocity. There is a temporary **resultant force**, the body accelerates or decelerates, the speed-dependent forces adjust, and a **new balance** is reached at a different speed.

> [!warning] Explaining the Transition Needs the Resultant Force
> **When a body moves between two constant speeds, name the temporary resultant force that takes it there.** The mark-earning chain: a new or changed force creates a resultant → the body accelerates or decelerates → the speed-dependent forces adjust → the forces balance again → new constant speed. An answer that jumps from one equilibrium to the other, without the resultant force in between, misses the physics being tested.
>
> **January 2021 Unit 1:** a fireboat travelling at constant speed turned on its pump, projecting water forwards, and settled to a lower constant speed. "All three horizontal forces play a role… the process in between involves a resultant backward force, slowing the boat, and thus reducing the drag force. Many students did not mention any resultant force." This was the least well answered question on the whole paper.

This idea — a moving equilibrium that re-establishes itself — is developed fully under Terminal Velocity.

### How Newton's First Law Appears in Exams

This law is examined through Section B **state** and **explain** questions (1–6 marks, sometimes levelled), requiring you to reason that a body at rest or moving at constant velocity has zero resultant force (and, for a rigid body, zero resultant moment). It also appears in Section A multiple-choice questions testing the force balance directly.

#### Multiple Choice (Section A)

One mark each, within Q1–10.

**Typical questions:**
- Which statement about the frictional force on the tyres of a van moving at constant velocity is correct? (June 2021 Q3)
- Which vector expression relates the forces acting on a box suspended, in equilibrium, from two ropes? (October 2023 Q9)
- What are the resultant force and resultant moment on a balanced see-saw? (June 2025 Q2)
- Which relationship connects friction and the weight component for a box sliding down a ramp at constant speed? (October 2024 Q5, June 2025 Q8)

**Common question types:**
- **Force-balance statements** — pick the statement consistent with ΣF = 0 for an object at constant velocity. Decide what the balance must be *before* reading the options
- **Vector equations for equilibrium** — the correct option always makes all the forces sum to zero as vectors ($$\overset{\rightarrow}{W} + \overset{\rightarrow}{T_1} + \overset{\rightarrow}{T_2} = 0$$), never one force equal to a sum of the others with inconsistent signs
- **Rigid-body equilibrium** — both the resultant force and the resultant moment are zero; an option offering one without the other is wrong
- **Slope equilibrium** — constant speed on a slope means friction = *mg* sin *θ*

**Common distractors:**
- The driving force greater than resistance "to keep the object moving" — at constant velocity they are equal
- Magnitude-only equations where a vector sum is needed. All three wrong options in October 2023 Q9 failed for the same stated reason: the vector forces on a body in equilibrium must add to zero
- Options that omit one of the forces acting — count the forces on the diagram, then count the terms in the option

#### Structured Questions (Section B)

**Typical questions:**
- "State what is meant by equilibrium" — a stone held in place by a builder's foot (January 2023 Q13), a door on two hinges (January 2024 Q18)
- "Explain the motion of the unicycle. Your answer should make reference to all of the forces acting" (October 2020 Q12)
- "State the condition necessary for the droplet to move at constant speed" (October 2021 Q17)
- "Show that F is about 500 N" — a buoy held stationary by an anchored chain (June 2023 Q17)

**Question format — State (1–2 marks)**

**Example — January 2023 Q13:** a stone is held in place by a builder's foot. State what is meant by equilibrium. (2 marks)

**Marking points:**
- Zero resultant force (in any direction) (1)
- Zero moment (about any point) (1)

The marks are independent, one per condition. Write both every time the body is extended — a stone, a door, a beam — even if the question feels like it is only about forces.

**Question format — Explain constant-velocity motion (2–3 marks)**

**Example — October 2020 Q12:** a unicycle moves at constant speed on a horizontal surface. Explain the motion, referring to all of the forces acting. (2 marks)

**Marking points:**
- The resultant vertical force is zero, so there is no vertical acceleration — the unicycle stays at the same height (1)
- The speed is constant because the resultant horizontal force is zero — the forward frictional force balances the backward drag (1)

One mark per direction. An answer that balances only the vertical forces (or only the horizontal ones) stops at half marks — treat "all of the forces" as an instruction to work direction by direction, stating the balance *and* its consequence each time.

**Question format — Show that, via resolving (2 marks)**

**Example — June 2023 Q17:** a stationary buoy; horizontal water force 260 N; chain force *F* at 33° to the vertical. Show that *F* is about 500 N.

**Marking points:**
- Equate the horizontal component of *F* to the force from the current: *F* sin 33° = 260 N (1)
- *F* = 480 N — quoted beyond the "about 500 N" target (1)

The follow-up (3 marks) asked how *F* and *θ* change when the horizontal force increases. Its marking points build on each other: the horizontal component of *F* increases while the vertical component stays the same (1); so *F* increases (1); and tan *θ* = *F*ₕ/*F*ᵥ, so *θ* increases (1) — the second and third marks were dependent on the first, so establish what happens to the *components* before concluding anything about *F* or *θ*.

#### Levelled 6-Mark Questions (Section B)

Newton's first law rarely gets a levelled question to itself. Instead it supplies the constant-velocity phases inside multi-law explanations, such as:
- A lift moving at constant velocity before decelerating (January 2022 Q14)
- A balloon rocket reaching maximum speed (June 2023 Q18)
- A submarine raised at constant velocity while the upthrust on it falls (January 2025 Q18)

For each constant-velocity phase, the creditworthy statements are exactly this spec point's core moves. In the lift question, the credited points for the constant-speed phase were:
- The reading on the scales is the reaction (contact) force on the student
- At constant speed, the resultant force on the student is zero — weight = reaction
- So the reading equals his weight, 600 N

State the balance and its consequence for that phase explicitly, then hand over to the second law for the phases where the motion changes.

#### Command Words for Newton's First Law

| Command word | What to do | Common traps |
|:---|:---|:---|
| **State / State what is meant by** | Give the condition: zero resultant force — plus zero resultant moment for a rigid body | Giving only the force condition for a rigid body (caps a 2-mark definition at one) |
| **Explain** | Name the forces, state the balance (ΣF = 0), state the consequence for the motion, citing the first law | Citing the second law for constant velocity; giving the balance without its consequence; covering only one direction |
| **Show that** | Resolve the forces and apply the equilibrium condition in a chosen direction; quote the answer to more significant figures than the target | Using the wrong trig function for the stated angle |

#### Exam Strategy for Newton's First Law

> [!tip] The Golden Rule
> **"Constant velocity" or "at rest" anywhere in a question means ΣF = 0.** This single deduction is the way in to almost every question on this spec point:
> - **In calculations** — write the force balance (or the vector sum equal to zero) and solve for the unknown force
> - **In explanations** — it is the middle of your answer: the forces balance, so the resultant force is zero, so the motion does not change
> - **In multiple choice** — build the balance yourself first, then find the option that matches it

> [!tip] The Three-Step Constant-Velocity Explanation
> For any "explain why the object moves at constant velocity/speed" question, write three sentences:
> 1. Name the forces: "the driving force and the resistive force (drag/friction) act on the object"
> 2. State the balance: "these are equal in magnitude, so the resultant force is zero"
> 3. State the consequence: "so there is no acceleration and the velocity is constant" (Newton's first law)
>
> The balance and the consequence are separate marking points — an answer needs both. If the question says "referring to all the forces acting", run the three steps for each direction (vertical, then horizontal) in turn.

> [!warning] Errors That Cost Marks
> - Stating only the force condition when defining equilibrium for a rigid body
> - Explaining constant velocity with Newton's second law
> - Giving the force balance without its stated consequence for the motion
> - Addressing only one direction when the question says "referring to all forces acting"
> - Describing a transition between two constant speeds without mentioning the temporary resultant force

## Spec Point: Newton's Second Law of Motion

> **Specification:** be able to use the equation ΣF = ma, and understand how to use this equation in situations where m is constant (Newton's second law of motion)

**Key terminology:** resultant force · vector sum · acceleration · free-body force diagram · sign convention · weight · tension · component

**Mathematical skills:** building the resultant as a signed sum before applying Σ*F* = *ma* · converting mass to kg before substituting · vertical problems with *F*up − *mg* = *ma* · resolving weight on slopes to give *a* = *g* sin *θ* · using *W* = *mg* with *g* = 9.81 N kg⁻¹ · rounding answers to match the significant figures of the data

### The Law and the Equation

Newton's second law states:

**The acceleration of an object with constant mass is directly proportional to the resultant force acting on it.**

$$ΣF = ma$$

| Symbol | Quantity | Unit |
|:---|:---|:---|
| Σ*F* | Resultant force | N |
| *m* | Mass | kg |
| *a* | Acceleration — the rate of change of velocity | m s⁻² |

The Σ (sigma) matters: *F* here is the **sum of all the forces acting**, not any single force. Constructing that sum correctly is the assessed skill in almost every question on this spec point.

Acceleration is always in the **same direction** as the resultant force. If the resultant force is along the direction of motion, the body speeds up or slows down; if it acts at an angle, the body changes direction.

The IAL statement is restricted to **constant mass**. Situations where mass changes — a rocket burning fuel — are asked qualitatively: for a constant force, the acceleration increases as the mass falls (October 2023 Q11, 1 mark, asks exactly that).

**Worked example:**
An object with a mass of 750 g accelerates in a straight line at 11 m s⁻². Determine the resultant force acting on the object.

- Convert the mass to kilograms: *m* = 750 g = 0.750 kg
- Σ*F* = *ma* = 0.750 × 11 = 8.25 N
- Σ*F* = 8.3 N (2 significant figures, matching the data)

Mass must be in kg before substituting — forgetting the conversion gives an answer 1000 times too large.

### Defining Resultant Force

"State what is meant by a resultant force" is a real 1-mark question (October 2022 Q11), and it is not answerable by writing Σ*F* = *ma*. The mark scheme accepts:

- **The vector sum of all forces acting on an object** (the sum of the forces taking their directions into account), or
- **The single force that would have the same effect as all the other forces acting together**

The same scheme treats "net force" as a mere synonym for "resultant force" — writing "the net force" **scores no mark**, because it renames the quantity instead of defining it.

> [!warning] Learn the Definition Word for Word
> **Memorise one definition and write it exactly: "the vector sum of all the forces acting on an object."** One-mark definition questions reward precision — paraphrasing under pressure is where the mark goes missing.
>
> **October 2022 Unit 1:** "A simple statement defining a resultant force was all that was required. A surprising number of candidates were not able to provide a coherent definition… A focus on learning standard definitions would help many students."

### Build the Resultant First

The reliable method for every Σ*F* = *ma* calculation:

1. Draw or complete a **free-body force diagram** — a diagram of the object alone, showing every force acting on it
2. Choose a **positive direction** — by convention, the direction of motion
3. Write Σ*F* as an algebraic sum with consistent signs (opposing forces such as drag are negative)
4. Only then substitute into Σ*F* = *ma*

**Worked example — October 2022 Q11:**
The engine of a motor boat provides a constant horizontal force of 5.5 kN. At a certain time the drag force on the boat is 3.1 kN. Calculate the acceleration of the boat at this time. Mass of boat = 7.5 × 10³ kg.

- Build the resultant: Σ*F* = 5.5 kN − 3.1 kN = 2.4 × 10³ N
- Apply the law: 2.4 × 10³ N = 7.5 × 10³ kg × *a*
- *a* = 0.32 m s⁻²

The mark scheme awarded the "use of *F* = *ma*" method mark even to candidates who used a single force (3.1 or 5.5 kN) — but the answer mark only follows from the correct resultant. The resultant construction is where the credit sits, so write it explicitly.

> [!tip] Sign Convention Is Your Choice — Consistency Is Not (Teaching Point)
> The direction you take as positive is up to you, provided every term's sign is consistent with it. Taking the direction of motion as positive is the standard habit: driving forces positive, drag and friction negative. If your final acceleration comes out negative, you have discovered that the object is slowing down — the sign is information, not an error. (If a question asks for the *deceleration*, quote it as a positive magnitude.)

> [!warning] Using a Single Force Instead of the Resultant
> **Never substitute a single force into ΣF = ma — list every force acting and combine them into the resultant first.** Run one check before substituting: does your ΣF expression contain every force from your free-body diagram, each with the correct sign?
>
> This is the single most-penalised error on this spec point, across many sittings.
> 
> **January 2019 Unit 1:** "very few could correctly identify that there needed to be a component of the resistive force acting against the weight… only the best could construct a correct equation for the resultant force and equate this to ma" — and many who did build the three-term equation lost a mark on a missing negative sign. 
> 
> **October 2022 Unit 1:** "It was common for candidates to use an incorrect value for resultant force due to forgetting that two unequal horizontal forces were acting on the boat."

### Vertical Motion: Lifts, Cables, Rockets and Trampolines

Vertical problems combine **weight** (*W* = *mg*, the gravitational force on the object, always downwards) with one or more upward forces — **tension** (the pulling force exerted by a stretched cable or rope), thrust, a normal contact force. Taking up as positive:

$$F_{up} − mg = ma$$

**Worked example — June 2023 Q20:**
An actor of mass 77 kg is lifted vertically from the ground by a cable, with an acceleration of 2.1 m s⁻². Show that the tension in the cable is about 920 N.

- Weight: *W* = 77 × 9.81 = 755 N
- Newton's second law, upwards positive: *T* − 755 = 77 × 2.1
- *T* = 162 + 755 = 917 N — "about 920 N", quoted to 3 significant figures as a show-that answer requires

The 2-mark explain part just before this calculation (in the same June 2023 Q20) has the same logic in words: the tension is greater than the weight, so there is a resultant (upward) force — and a resultant force means acceleration.

**Worked example — January 2023 Q15:**
A trampoline gives a gymnast of mass 58 kg a maximum upward acceleration of 14.2 m s⁻². Calculate the maximum upward force of the trampoline on the gymnast. (4 marks)

- Two forces act on the gymnast: the trampoline's push *P* (up) and weight (down)
- Resultant: Σ*F* = *P* − *mg*, so *ma* = *P* − *mg*
- *P* = *m*(*a* + *g*) = 58 × (14.2 + 9.81) = 1.39 × 10³ N ≈ 1.4 kN

> [!warning] Adding vs Subtracting the Weight
> **Forces acting in opposite directions must be subtracted, not added — and the way to get every sign right is to fix a positive direction before writing anything.** Take the direction of the acceleration as positive, give each force its sign (here: trampoline push positive, weight negative), and only rearrange the algebra at the end: *ma* = *P* − *mg*, so *P* = *m*(*a* + *g*). If you find yourself deciding signs while substituting numbers, stop and go back to the diagram.
>
> **January 2023 Unit 1:** on this trampoline question, "many candidates subtracted the weight from the resultant force instead of adding it to find the upward force, scoring only two of the four available marks".

The same structure runs through rocket launches: thrust 7.3 × 10⁷ N and mass 5.0 × 10⁶ kg give Σ*F* = thrust − weight = 2.39 × 10⁷ N, so *a* = 4.8 m s⁻² (October 2023 Q11). It also appears in the classic Section A lift problem: a 70 kg student exerts 800 N on the floor of an upward-accelerating lift, so by Newton's third law the floor pushes up on the student with 800 N, and 800 − 70*g* = 70*a* (June 2019 Q10).

### Slopes and Components

When motion is along a slope at angle *θ*, resolve weight into **components** — the parts of the force acting along each of two perpendicular directions: *mg* sin *θ* along the slope, *mg* cos *θ* perpendicular to it. For a frictionless slope the along-slope resultant is just *mg* sin *θ*, and mass cancels:

$$ma = mg \sin θ \implies a = g \sin θ$$

**Worked example — October 2021 Q13:**
A sledge accelerates from rest down a frictionless slope at 6.9° to the horizontal. Show that the initial acceleration along the slope is about 1 m s⁻².

- *a* = *g* sin *θ* = 9.81 × sin 6.9° = 1.18 m s⁻² — "about 1 m s⁻²", with the extra significant figure a show-that answer needs

Harder variants add a second force to the component (a resistive force against the weight component — January 2019 Q16), or chain the acceleration into an equation of motion, such as finding the speed at the bottom of a frictionless incline with *v*² = *u*² + 2*as* (January 2026 Q17).

Two revision priorities follow directly from examiners' advice: practise Σ*F* = *ma* problems where more than one force acts and at least one needs resolving ("Practice using F=ma where there is more than 1 force acting on an object, particularly with one or more force that requires a component" — January 2019 Unit 1), and keep your trigonometry sharp ("Practice your trigonometry during revision time" — June 2023 Unit 1).

### When Mass Doesn't Matter

When the driving force is itself proportional to mass, the mass cancels in *a* = Σ*F*/*m* — so the acceleration is independent of mass. This is a recurring exam idea:

- A frictionless slope: *a* = *g* sin *θ* for any mass — which is why an athlete's mass has little effect on initial acceleration down a track (January 2019 Q18)
- A resistive force proportional to weight: deceleration = *F*/*m* is the same for a car and a truck on an escape lane (January 2025 Q13)
- Free fall itself: *mg* = *ma* gives *a* = *g* for every object — the same cancellation

### Changing Resultant Force, Changing Acceleration

Rearranged as *a* = Σ*F*/*m*, the second law is a qualitative reasoning tool: if the resultant force decreases (at constant mass), the acceleration decreases — even while the object is still speeding up. This one sentence answers a family of explain questions:

- A cyclist reaches level ground and the weight component vanishes from the resultant, so the acceleration changes (October 2022 Q19)
- A rocket's mass falls as fuel burns, so at constant thrust its acceleration rises (October 2023 Q11)
- A falling or driven object's drag grows with speed, so its acceleration shrinks towards zero — the terminal velocity story (see Terminal Velocity)

The key discipline is to reason through the **resultant**: "the force is big" is not an argument about acceleration until you have compared it with the opposing forces.

### The Second and Third Laws Together

Many 2–3 mark explain questions combine the third law (to identify a force) with the second law (to explain the motion). The high-jump version (October 2024 Q15, 3 marks) shows the full mark-earning chain:

1. **Third law:** the athlete pushes down on the ground with 890 N, so the ground pushes up on the athlete with 890 N (equal magnitude, opposite direction)
2. **Compare:** the upward force (890 N) is greater than the athlete's weight (680 N)
3. **Second law:** so there is a resultant upward force — and the athlete accelerates upwards

The same pattern explains why a bumper car or snooker ball decelerates in a collision: the other body exerts a force on it (third law), that force is opposite to its motion, so there is a resultant force and it decelerates (June 2022 Q17, June 2024 Q15, January 2026 (Alt) Q17).

### How Newton's Second Law Appears in Exams

This spec point appears on almost every paper, in both sections: Section A tests constructing Σ*F* = *ma* symbolically; Section B runs frequent calculate and show-that questions plus the signature levelled 6-markers.

#### Multiple Choice (Section A)

One mark each, within Q1–10.

**Typical questions:**
- Which expression could be used to determine the acceleration of a lift, given the force a student exerts on its floor? (June 2019 Q10)
- Which expression gives the drag on an accelerating rocket, given thrust, weight and acceleration? (October 2021 Q10)
- Which is the equation of motion for a ball moving upwards under its weight and air resistance? (January 2020 Q4)
- Which acceleration–time graph matches a rocket accelerating under constant force as its mass decreases? (June 2022 Q6)
- What is the drag force on a ship, given its mass, acceleration and engine force? (June 2024 Q10)

**Common question types:**
- **Construct the symbolic equation** — build Σ*F* = *ma* for the scenario yourself, then match it to an option. For the lift: the student pushes down on the floor with 800 N, so by Newton's third law the floor pushes up on the student with 800 N; weight acts down; hence 800 − 70*g* = 70*a*
- **Choose the law or the graph** — decide whether the resultant force is constant, increasing or decreasing, then translate that into acceleration and graph shape (mass falling at constant force → acceleration rising)
- **One-step numericals** — one subtraction to get the resultant, then Σ*F* = *ma*

**Common distractors:**
- A missing force — the weight, or the contact force, left out of the equation
- A sign in the wrong direction — opposing forces added instead of subtracted, or vice versa

The June 2019 mark scheme rejected every wrong lift option for exactly one of these two reasons, so run both checks — all forces present? all signs consistent? — on an option before selecting it.

#### Structured Questions (Section B)

**Typical questions:**
- "Calculate the acceleration of the boat at this time" — engine force, drag and mass given (October 2022 Q11)
- "Calculate the maximum upward force of the trampoline on the gymnast" (January 2023 Q15)
- "Show that the tension in the cable is about 920 N" (June 2023 Q20)
- "Show that the initial acceleration of the sledge along the slope is about 1 m s⁻²" (October 2021 Q13)
- "Explain why the athlete accelerates upwards. Your answer should refer to Newton's third law" (October 2024 Q15)
- "Give one reason why the acceleration will increase as the rocket rises" (October 2023 Q11)

**Question format — Calculate (2–4 marks)**

**Example — October 2022 Q11 (2 marks):** engine force 5.5 kN, drag force 3.1 kN, mass 7.5 × 10³ kg. Calculate the acceleration.

**Marking points:**
- Use of *F* = *ma* (1)
- *a* = 0.32 m s⁻², with unit (1)

The method mark was available even with a single force substituted — but the answer mark only follows from the resultant, (5.5 − 3.1) kN. At higher tariffs, each step of the routine earns its own "use of" mark:

**Example — January 2023 Q15 (4 marks):** a trampoline gives a 58 kg gymnast a maximum upward acceleration of 14.2 m s⁻². Calculate the maximum upward force on the gymnast.

**Marking points:**
- Use of *W* = *mg* (1)
- Use of: resultant force = push from trampoline − weight (1)
- Use of Σ*F* = *ma* (1)
- *P* = 1.4 × 10³ N (1)

The marking points, in order, are the calculation routine itself: forces → resultant → law → answer. Write each stage down and the marks track your working.

**Question format — Show that (2–3 marks)**

**Example — June 2023 Q20 (3 marks):** an actor of mass 77 kg is lifted vertically with acceleration 2.1 m s⁻². Show that the cable tension is about 920 N.

**Marking points:**
- Use of *W* = *mg* (1)
- Use of Σ*F* = *ma* (1)
- Tension = 917 N (1)

The final mark needs the unrounded value: quote 917 N, not "920 N" — a show-that answer must reach at least one more significant figure than the target, otherwise you have proved nothing.

**Example — October 2021 Q13 (2 marks):** a sledge on a frictionless slope at 6.9° to the horizontal. Show that the initial acceleration along the slope is about 1 m s⁻².

**Marking points:**
- Resolve the acceleration (the weight component) along the slope (1)
- *a* = 1.2 m s⁻² (1)

**Question format — Explain (1–3 marks)**

**Example — October 2024 Q15 (3 marks):** an athlete of weight 680 N exerts a force of 890 N on the ground. Explain why he accelerates upwards, referring to Newton's third law.

**Marking points:**
- By Newton's third law, the ground exerts an equal (890 N) and opposite (upward) force on the athlete (1)
- The upward force is greater than the weight: 890 N > 680 N (1)
- So there is a resultant (upward) force on the athlete (1)

The three marks are the three steps of the chain: identify the force with the third law, compare it with the opposing force, conclude with the resultant. Jumping from "the ground pushes up" straight to "he accelerates" skips the comparison and drops the middle mark.

**Example — October 2023 Q11 (1 mark):** give one reason why the rocket's acceleration increases as it rises.

**Marking points:**
- The mass (or weight) of the rocket decreases as fuel is used — or the thrust increases, or the resultant force increases (1)

For a 1-mark "give", one creditworthy line is enough — spend the saved time on the higher-tariff parts.

#### Levelled 6-Mark Questions (Section B)

The signature format for this spec point: an asterisked "explain, with reference to Newton's laws" question set in an unfamiliar context. Previous examples include:
- A spring-powered toy car (October 2021 Q15)
- Lift scale readings (January 2022 Q14)
- A rising balloon (October 2022 Q14)
- A gymnast on a trampoline (January 2023 Q15)
- A balloon rocket (June 2023 Q18)
- A weather balloon (October 2023 Q17)
- A ball striking a skittle (January 2024 Q16)
- A bungee jumper (October 2024 Q17)

**Example — January 2022 Q14:** a student of weight 600 N stands on scales in a lift that moves upwards at constant velocity, then decelerates. Explain the readings on the scales.

**Creditworthy statements (indicative content):**
- The reading on the scales is the reaction (contact) force on the student
- At constant speed, the resultant force on the student is zero — weight = reaction
- So at constant speed the reading is 600 N
- As the lift decelerates, the reaction force is less than the weight
- So there is a resultant downward force on the student
- So the reading falls below 600 N

Notice the shape: every credited statement identifies a force, states a resultant, or gives the consequence for the motion (or reading) — and each phase of the motion gets the same three moves. Build your answer phase by phase with those moves and the creditworthy content takes care of itself. None of the credit comes from quoting the laws by name alone.

#### Command Words for Newton's Second Law

| Command word               | What to do                                                                                             | Common traps                                                                                         |
| :------------------------- | :----------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------- |
| **Calculate**              | Build the resultant with a consistent sign convention, show Σ*F* = *ma*, give the answer with its unit | Using a single force as the resultant; sign errors; mass left in grams                               |
| **Show that**              | As calculate, but quote the result to at least one more significant figure than the target             | Rounding to the target's precision, which proves nothing                                             |
| **Explain**                | Invoke the named law explicitly for each phase of motion, linked with because/so reasoning             | Listing facts without linkage; citing the wrong law; arguing from one force instead of the resultant |
| **State what is meant by** | Define resultant force in words — the vector sum of all forces acting                                  | Writing Σ*F* = *ma*; writing "net force" (a synonym, not a definition — no mark)                     |
| **Determine**              | Extract the needed quantity first (a component, a gradient, a velocity change), then apply Σ*F* = *ma* | Skipping the resolving or conversion step                                                            |
| **Give a reason**          | One line, no development needed (e.g. mass decreases, so acceleration increases at constant force)     | Writing an essay for 1 mark                                                                          |

#### Exam Strategy for Newton's Second Law

> [!tip] The Calculation Routine
> Run the same five steps for every Σ*F* = *ma* calculation:
> 1. Draw or complete the free-body force diagram
> 2. Choose a positive direction — usually the direction of motion or of the acceleration
> 3. Write the resultant as an explicit signed sum, e.g. (5.5 − 3.1) × 10³ N
> 4. Substitute into Σ*F* = *ma* and solve
> 5. Check the finish: unit included, mass in kg, and *g* = 9.81 N kg⁻¹ (9.8 is accepted; **g = 10 loses a mark**)
>
> Writing step 3 on the page is what secures the method marks, even if the arithmetic slips afterwards.

> [!tip] Scoring the Levelled 6-Marker
> 1. Split the motion into phases — before/during/after, or accelerating/constant velocity
> 2. For each phase, make the same three moves: name the forces (for a third-law pair, name **both** bodies), state the resultant, state the acceleration consequence via Σ*F* = *ma*
> 3. Connect the phases with "because/so" reasoning rather than listing facts
>
> Use precise language — "exerts a force on", never "pushes" (flagged by examiners in June 2023) — and remember that quoting the laws without applying them to the situation scores nothing.

> [!tip] Mark-Scheme Conventions Worth Knowing
> - A bald correct answer (no working) scores full marks in a calculate question — but **zero** in a show-that question
> - A show-that worth 2 marks can be earned by reverse working; worth 3 marks, only 2 are available that way
> - There is no separate unit mark, but a missing or wrong unit forfeits the final answer mark (not in show-that questions)
> - Error carried forward: a wrong value from an earlier part, used correctly, still earns full marks in the later part

> [!warning] The Three Most-Penalised Errors
> - Substituting one force for the resultant
> - Inconsistent signs when combining forces (especially the weight term in vertical problems)
> - Having no worded definition of resultant force ready for a 1-mark state question

## Spec Point: Terminal Velocity

> **Specification:** use of the term terminal velocity is expected

**Key terminology:** terminal velocity · drag · upthrust · weight · free fall · resultant force · causal chain · free-body force diagram

**Mathematical skills:** writing the force balance for the direction of motion (e.g. *W* = *D* + *U*) · finding upthrust via *ρ* = *m*/*V* and *W* = *mg* · substituting drag laws *F* = 6*πηrv* or *D* = *kv*² and rearranging for *v* · extracting the radius from *V* = 4/3 *πr*³ · interpreting gradients of velocity–time and displacement–time graphs · determining terminal velocity from the gradient of a distance–time graph

### What Terminal Velocity Is

**Terminal velocity** is the constant, maximum velocity reached by an object moving through a fluid, attained when the **resultant force** on it — the vector sum of all the forces acting — is zero.

Mark schemes accept any of these equivalent statements (June 2019 and June 2021 schemes):
- the constant/maximum velocity the object reaches
- the velocity when acceleration = 0
- the velocity when the forces are in equilibrium — weight = drag (+ upthrust) for a falling object — or when the resultant force = 0

Here **weight** (*W* = *mg*) acts downwards, **drag** is the resistive force from the fluid — it opposes the motion and grows with speed — and **upthrust** is the upward force from the fluid, equal to the weight of fluid displaced.

"Terminal" means *final*: once it is reached, there is no further increase in velocity.

Terminal velocity is not only about falling. Any object driven through a fluid at constant force reaches a maximum speed by the same argument — a boat at full throttle, a car at top speed, a sphere pulled horizontally through oil. The role played by weight for a falling object is played by thrust or the applied force. As the October 2019 examiner report put it: "terminal velocity does not just apply to a falling sphere… the theory of terminal velocity will apply whenever an object is moving through a fluid."

> [!warning] Terminal Velocity Is Not Free Fall
> **Free fall and terminal velocity are opposites — check which one the question describes before writing.** Free fall: resistive forces are absent or ignored, the only force is weight, and *a* = *g*. Terminal velocity: resistive forces have grown to balance the weight, so *a* = 0. If the question mentions air resistance or drag acting, the object is not in free fall.
>
> **January 2019 Unit 1:** "many learners have a poor understanding of what free fall means" — candidates described free fall using terminal-velocity physics, with weight balanced by resistive forces.

### Why an Object Reaches Terminal Velocity: The Causal Chain

The explanation that earns marks is a **causal chain** — each statement causing the next — and the links must appear in causal order. For a sphere released from rest and falling through a fluid (this is the January 2025 Q20 mark scheme, 4 marks, almost word for word):

1. Initially, weight is greater than upthrust plus drag — there is a resultant force downwards
2. So the sphere accelerates, and its velocity increases
3. As velocity increases, drag increases (upthrust stays constant)
4. Until the resultant force becomes zero — so the acceleration is zero and the sphere moves at constant (terminal) velocity

> [!tip] Say Every Link Out Loud (Teaching Point)
> Students who jump from "drag increases" straight to "terminal velocity" leave out the marked middle links: resultant force decreases → acceleration decreases → resultant reaches zero → acceleration zero → velocity constant. Each arrow is potentially a separate marking point. The chain also transfers unchanged to driven motion — swap "weight" for "driving force".

> [!warning] Close the Loop
> **Always end the chain explicitly: the resultant force becomes zero, so the acceleration becomes zero, so the velocity is constant and maximum.** Write the final link even when it feels obvious — it is routinely a separate marking point. And answer the question actually set: some ask only about the situation *at* terminal velocity, not the build-up to it (June 2019 Unit 1).
>
> **January 2023 Unit 1:** "Many candidates failed to score the final mark by not explaining that a maximum velocity is reached because acceleration becomes zero" — and on the same question, many "concentrated on explaining why the lift bag accelerated in the first place and lost focus on the main points".

### The Force Balance at Terminal Velocity

At terminal velocity the resultant force is zero. Which forces balance depends on the situation — identifying the right balance **is** the physics being assessed:

| Situation | Balance at terminal velocity |
|:---|:---|
| Falling through air (upthrust negligible) | weight = drag |
| Falling through a liquid | weight = drag + upthrust |
| Driven horizontally through a fluid | applied/driving force = drag |
| Rising through a fluid (balloon, lift bag) | upthrust = weight + drag |

Note the rising case: drag opposes **motion**, so for a rising object it acts *downwards*, alongside weight. October 2025 Q5 asked exactly this — for a balloon rising at terminal velocity, *U* = *W* + *D*, so the correct statement is *U* > *W*.

> [!warning] Drag Is Not Upthrust
> **Drag depends on speed; upthrust does not.** Drag is zero when the object is stationary and grows as it speeds up. Upthrust is the weight of fluid displaced — constant for a fully submerged object, whatever its speed. So when you explain *changing* motion in a fluid, the force doing the changing is always drag.
>
> **October 2020 Unit 1:** on a skydiver acceleration–time graph question, "many students confused drag with upthrust".

### Terminal Velocity Calculations

Write the force balance first, then substitute whatever drag law the question supplies — Stokes' law *F* = 6*πηrv* (small spheres, see the Stokes' Law sub-topic), or a given formula such as *F* = 0.45*ρAv*² or *D* = *kv*². Marks are for the balance, the substitutions and the answer with unit.

**Worked example — January 2023 Q18:**
An object of mass 35 kg fell from a boat and reached terminal velocity as it sank. Volume of object = 1.60 × 10⁻² m³; density of seawater = 1.03 × 10³ kg m⁻³. (i) Show that the drag force at terminal velocity was about 200 N. (ii) The drag obeyed *D* = *kv*², with *k* = 2.2 N s² m⁻². Determine the terminal velocity.

Part (i) — balance: weight = drag + upthrust, so *D* = *W* − *U*:

- Upthrust = weight of seawater displaced: *m* = 1030 × 1.60 × 10⁻² = 16.5 kg, so *U* = 16.5 × 9.81 = 162 N
- Weight: *W* = 35 × 9.81 = 343 N
- *D* = 343 − 162 = 181 N ≈ 1.8 × 10² N — "about 200 N"

Part (ii) — substitute into the given drag law:

- 181 = 2.2 × *v*²
- *v* = √(181 ÷ 2.2) = 9.1 m s⁻¹

The five marks in part (i) were: use of *ρ* = *m*/*V*; identifying upthrust as the weight of fluid displaced; use of *W* = *mg*; use of *D* = *W* − *U*; the answer. Omitting upthrust — treating the balance as just weight = drag, as if in air — collapses the whole calculation.

The Stokes'-law version runs the same way: for a water droplet sinking through oil, *W* − *U* = 6*πηrv* gives *v* = 4.8 × 10⁻³ m s⁻¹ from the droplet's volume and the oil's viscosity (October 2021 Q17). Where the question gives a volume, expect to extract the radius from *V* = 4/3 *πr*³ first.

A follow-on favourite: the output power of an engine at terminal velocity is *P* = *Fv*, with *F* the driving force (October 2022 Q11). Resist any urge to bring kinetic energy into it — examiners called it "irrelevant" here, and candidates who calculated it earned nothing.

### Free-Body Force Diagrams at Terminal Velocity

Marks for the **free-body force diagram** — the diagram showing only the object and every force acting on it — follow strict, published criteria (June 2019 and October 2019 schemes):

- **Correct forces only** — for a sphere at terminal velocity in a liquid: upthrust (up), drag (up), weight (down). Every invented extra force costs a mark
- Arrows must **touch the dot** (or the object), be close to vertical, and carry **labels** (Weight/W/mg; Drag/D/friction; Upthrust/U)
- **Lengths:** where the question asks you to draw the balanced situation, the upward arrow lengths must together equal the weight arrow's length (for two forces, equal lengths; for three, upthrust + drag = weight). The length mark is dependent on the forces being correct

A "complete the diagram" variant supplies one arrow and asks for the rest (January 2024 Q15) — the same rules apply to what you add.

### Graphs of Motion Approaching Terminal Velocity

You are expected to translate between the motion and its graphs (a core mathematical skill on this paper):

| Graph | Shape for fall from rest to terminal velocity |
|:---|:---|
| Velocity–time | Starts at zero with maximum gradient (= *g* for free release); gradient decreases as drag grows; flattens to a horizontal line at terminal velocity |
| Displacement–time | Gradient starts at zero, steepens as velocity increases, then becomes a **constant slope** (straight line) at terminal velocity |

To score full marks on "explain the shape of the graph" (displacement–time, ball bearing falling through a liquid — October 2023 Q18), make each of these points in turn: initially the velocity is zero, so the gradient is zero; as the velocity increases, the gradient increases; the drag increases as the velocity increases; until terminal (constant) velocity, when the gradient becomes constant.

> [!warning] Refer to the Graph
> **In any "explain the shape of the graph" question, tie every stage of the physics to a named feature of the printed graph** — "the gradient is zero at first", "the gradient increases", "the line becomes straight". A forces-only explanation with no reference to the graph caps at 1 mark; a description of the graph with no mention of velocity scores zero.
>
> **October 2023 Unit 1:** "Most candidates scored no marks on this question. The most common reason… was that the answers did not often refer to the graph." Watch signs on a downward journey too: "a common misconception was that the increasingly negative gradient showed a decreasing speed, rather than showing an increasing downwards speed."

### Changing to a New Terminal Velocity

When conditions change, the object transitions — via a temporary resultant force — to a **new** terminal velocity. Two examined versions:

**The parachute (June 2025 Q20, 5 marks).** When the parachute opens, air resistance is suddenly greater than weight; the resultant force is upwards, so the skydiver decelerates; as speed decreases, air resistance decreases (so the deceleration shrinks); until air resistance again equals weight; then the resultant force is zero, the acceleration is zero — a new, lower terminal velocity. Keep the whole explanation in terms of forces and acceleration: the mark scheme explicitly ignored statements about speed alone.

**The fireboat** (January 2021 Q14, October 2025 (Alt) Q16): a new backward force appears, creating a backward resultant; the boat slows; drag falls; the forces rebalance at a lower constant speed. See Reaching a New Constant Velocity under Newton's First Law of Motion — it is the same physics.

**Comparing terminal velocities** is a related explain type: for a larger sphere of the same density, drag (Stokes) is proportional to *r*, but weight and upthrust are proportional to *r*³ — so the larger sphere reaches a greater terminal velocity and falls a set distance in less time (January 2025 Q20, 3 marks).

### Measuring Terminal Velocity: Core Practical 2

The falling-ball viscometry practical (see Core Practical 2: Investigating Viscosity of a Liquid) turns this spec point into method marks: October 2019 Q15 asked for a method "to determine an accurate value for the terminal velocity of the sphere" for 5 marks (the full marking points are in the exam section below).

An accurate method has five ingredients: two or more markers on the cylinder; the **top marker far enough below the surface for terminal velocity to have been reached** (or extra markers, to check the velocity between them is constant); a timed fall over a measured distance, using a stopwatch and metre rule; repeated measurements and an average; then terminal velocity = distance ÷ average time, or the **gradient of a distance–time graph**.

> [!tip] Why the Top Marker Sits Low (Teaching Point)
> Timing must not start until the sphere has stopped accelerating — otherwise the measured average speed is below the terminal value. Placing the first marker well below the surface (and checking constant velocity across multiple markers) is the accuracy step examiners look for, and it is exactly the causal-chain physics: the sphere needs time and distance for drag to grow until the forces balance.

### How Terminal Velocity Appears in Exams

Predominantly a Section B topic: explain, state, show-that, calculate and determine questions on why an object — sphere, droplet, skydiver, boat, balloon, athlete — reaches a constant maximum velocity, often with a free-body diagram or force-balance calculation attached. Occasional Section A questions test graph reading or the force relationship.

#### Multiple Choice (Section A)

One mark each, within Q1–10.

**Typical questions:**
- Which explanation accounts for the decreasing gradient of a velocity–time graph for an object falling through a liquid? (January 2020 Q10)
- Which displacement–time graph matches a ball falling through air from rest? (October 2023 Q4)
- Which statement about the magnitudes of upthrust *U*, viscous drag *D* and weight *W* is correct for a balloon rising at terminal velocity? (October 2025 Q5)
- How does the gradient of a terminal velocity–mass graph change for a more viscous liquid? (January 2022 Q6)
- How do viscous drag and viscosity change when the temperature of the liquid rises? (June 2023 Q9)

**Common question types:**
- **Graph interpretation** — translate graph features into physics: a decreasing gradient on a velocity–time graph means decreasing acceleration, which means drag is increasing; a displacement–time graph straightens to a constant slope at terminal velocity
- **Force relationships** — write the balance for the direction of motion before reading the options. For the rising balloon, drag acts downwards, so *U* = *W* + *D* — and the correct statement is *U* > *W*
- **Stokes'-law links** — chain the effects: temperature up → viscosity down → drag down → terminal velocity up

**Common distractors:**
- Balances with drag in the wrong direction — drag always opposes the motion, so it flips between rising and falling objects
- Graphs where the velocity keeps increasing after the terminal phase — once the curve flattens, it stays flat
- Two-force balances for motion through a liquid — the missing upthrust is exactly what the wrong options rely on you forgetting

#### Structured Questions (Section B)

**Typical questions:**
- "Explain what is meant by the terminal velocity of the raindrop. Your answer should include a free-body force diagram" (June 2019 Q18)
- "Explain why the lift bag and object reached a maximum velocity" (January 2023 Q18)
- "Show that the drag force acting on the object at terminal velocity was about 200 N" (January 2023 Q18)
- "Explain how the forces on the skydiver caused his acceleration to vary after his parachute opened" (June 2025 Q20)
- "Complete the free-body force diagram for the sphere when travelling at terminal velocity" (October 2019 Q15)
- "Describe a method that the student could use to determine an accurate value for the terminal velocity of the sphere" (October 2019 Q15)

**Question format — Explain what is meant by terminal velocity (2–4 marks)**

**Example — June 2021 Q18 (2 marks).**

**Marking points:**
- The constant, maximum velocity reached by an object falling (through a fluid) (1)
- Reached when the resultant force equals zero — or when drag plus upthrust equals weight (1)

Both halves are needed: the statement about the velocity *and* the force condition behind it.

**Example — June 2019 Q18 (4 marks):** the same question for a raindrop, with a free-body force diagram required (upthrust negligible).

**Marking points:**
- The two definition marks above (2)
- Weight and air resistance only, drawn with correct directions, arrows touching the dot, labelled (1)
- The two arrow lengths equal (1) — this mark depends on the forces mark being earned

**Question format — Explain why terminal velocity is reached (3–5 marks)**

**Example — January 2025 Q20 (4 marks):** a metal sphere is released from rest in a container of oil. Explain why it reaches terminal velocity.

**Marking points:**
- Initially, weight is greater than upthrust plus drag — there is a resultant force downwards (1)
- So the sphere accelerates and its velocity increases (1)
- Drag increases (while upthrust remains constant) (1)
- Until the resultant force becomes zero and the sphere moves at constant (terminal) velocity (1)

The marking points are the causal chain, one link per mark, in order.

**Example — January 2023 Q18 (3 marks):** a lift bag and object accelerate upwards through seawater and reach a maximum velocity. Explain why.

**Marking points:**
- The drag force increases as the velocity increases (1)
- Until the drag force plus the weight equals the upthrust (1)
- The resultant force is then zero, so the object stops accelerating (1)

Same chain, different balance — for a *rising* object, drag joins weight on the downward side. Choose the balance for the direction of motion before you start writing.

**Example — June 2025 Q20 (5 marks):** a skydiver's parachute opens; explain how the forces caused his acceleration to vary afterwards.

**Marking points:**
- When the parachute opens, air resistance is greater than weight (1)
- The resultant force is upwards, so the skydiver decelerates (1)
- As the speed decreases, the air resistance decreases (1)
- Until the air resistance (plus upthrust) equals the weight (1)
- So the resultant force is zero and the acceleration is zero (1)

Keep every statement in terms of forces and acceleration — the scheme explicitly ignored statements about speed alone.

**Question format — Show that / Calculate / Determine (2–5 marks)**

**Example — January 2023 Q18 (5 marks then 2 marks):** an object of mass 35 kg sank at terminal velocity; volume 1.60 × 10⁻² m³, seawater density 1.03 × 10³ kg m⁻³. (i) Show that the drag force was about 200 N. (ii) Given *D* = *kv*² with *k* = 2.2 N s² m⁻², determine the terminal velocity.

**Marking points (show that, 5):**
- Use of *ρ* = *m*/*V* (1)
- Identify upthrust as equal to the weight of fluid displaced (1)
- Use of *W* = *mg* (1)
- Use of *D* = *W* − *U* (1)
- *D* = 1.8 × 10² N (1)

**Marking points (determine, 2):**
- Use of *D* = *kv*² (1)
- *v* = 9.1 m s⁻¹ (1)

**Example — October 2021 Q17 (4 marks):** a spherical water droplet (volume 3.35 × 10⁻⁸ m³) sinks slowly through oil (viscosity 0.11 Pa s). Calculate its terminal velocity.

**Marking points:**
- Use upthrust and weight to determine the viscous force: *F* = *W* − *U* (1)
- Use of *V* = 4/3 *πr*³ to find the radius (1)
- Use of *F* = 6*πηrv* (1)
- *v* = 4.8 × 10⁻³ m s⁻¹ (1)

Both examples carry the same lesson: the first marks are for the force balance, before any drag law appears. A deduce variant reverses the comparison — calculate the Stokes drag from 6*πηrv* and compare it with the measured weight−upthrust difference to decide whether Stokes' law applies (October 2024 Q19, 5 marks): the conclusion mark needs the numerical comparison, not just a claim.

**Question format — Complete the free-body force diagram (2–3 marks)**

**Example — October 2019 Q15 (3 marks):** a sphere falling at terminal velocity through washing-up liquid.

**Marking points:**
- Upthrust, upwards (1)
- Drag, upwards (1)
- Weight, downwards (1)

Penalties applied on top: one mark lost for each extra force, for any arrow not touching the dot, and for any arrow not close to vertical. Draw only what the force balance requires — nothing else.

**Question format — Describe the method (5 marks)**

**Example — October 2019 Q15:** describe a method to determine an accurate value for the terminal velocity of the sphere.

**Marking points:**
- Place two or more rubber bands/markers on the cylinder (1)
- The top marker far enough below the surface for terminal velocity to have been reached — or more than two markers, checking the velocity between them is constant (1)
- Measure the time for the sphere to fall a measured distance, using the stopwatch and metre rule (1)
- Repeat the measurements and average (1)
- Terminal velocity = distance between markers ÷ average time — or time the fall over several different distances and take the gradient of a distance–time graph (1)

#### Levelled 6-Mark Questions (Section B)

When terminal velocity appears in a levelled question, it is usually the end point of a full motion story. Previous examples include:
- A rising balloon (October 2022 Q14)
- A balloon rocket reaching maximum speed (June 2023 Q18)

The creditworthy content is this spec point's causal chain, delivered in order for the context given. For the rising balloon, the credited statements were:
- Drag increases as the velocity increases (upthrust and weight are constant)
- The resultant (upward) force decreases, so the acceleration decreases
- Eventually upthrust = weight + drag — the forces are balanced, the resultant force is zero
- The balloon continues to move upwards at constant (terminal) velocity

Deliver the chain link by link for the object in the question, closing the loop at constant velocity — the standard skydiver paragraph, recited unadapted, will not fit a rising object because the balance is different.

#### Command Words for Terminal Velocity

| Command word | What to do | Common traps |
|:---|:---|:---|
| **Explain (what is meant by)** | Definition statement plus the force condition | Giving only one of the two halves |
| **Explain (why reached)** | The full causal chain in order, ending at acceleration = 0; anchor to the graph if one is printed | Skipping the middle links; never mentioning the graph; not closing the loop |
| **State** | The force-balance condition (resultant force = 0) in one line | Naming the wrong balance for rising objects |
| **Show that / Calculate** | Write the balance, substitute the drag law, answer with unit to sufficient significant figures | Omitting upthrust in liquids; using weight where the balance needs weight − upthrust |
| **Determine / Deduce** | Rearrange the given drag relationship, or compute both sides of a comparison and state the conclusion | Deducing without a numerical comparison |
| **Complete** | Add only the missing forces: correct directions, labels, arrows from the dot | Extra invented forces (each one costs a mark) |
| **Describe** | The CP2 sequence: markers below the surface, timed fall over a known distance, repeat and average | Starting the timing at the surface, before terminal velocity is reached |
| **Suggest** | Apply the force-balance reasoning to an unfamiliar context | Answering from memory of the standard case instead of the context given |

#### Exam Strategy for Terminal Velocity

> [!tip] Your First Decision: Which Force Balance?
> The force balance is the foundation of terminal-velocity questions, explain and calculate alike, so make it your first written line. Ask two questions: **which way is the object moving**, and **is it in air or in a liquid**? Then match the situation:
> - Falling through air (raindrop, skydiver): weight = drag
> - Falling through a liquid (sphere in oil, sinking object): weight = drag + upthrust
> - Driven through a fluid (boat, car, towed sphere): driving force = drag
> - Rising through a fluid (balloon, lift bag): upthrust = weight + drag
>
> Drag always opposes the motion — that is what moves it from one side of the balance to the other. Get this line right and everything downstream, qualitative or numerical, follows from it.

> [!tip] For Explain Questions: the Chain, the Graph, the Loop
> **The chain** — give the causal links in order, one per sentence: resultant force acts → the object accelerates → drag increases with velocity → the resultant force decreases → the acceleration decreases → the forces balance → the acceleration is zero → the velocity is constant.
>
> **The graph** — if the question prints a graph, tie each link to a named feature of it ("the gradient decreases", "the line becomes straight"). An answer that never mentions the graph is not answering the question that was asked.
>
> **The loop** — always finish with the closing sentence: "the resultant force is zero, so the acceleration is zero, so the velocity is constant and maximum — the terminal velocity". This closing link is the easiest one to leave out, so write it deliberately.
>
> If the context is unfamiliar — a rising lift bag, a fireboat, a sphere pulled sideways through oil — keep the chain but swap in the forces from your balance. The reasoning transfers; a memorised skydiver paragraph does not.

> [!tip] For Calculations: Balance → Forces → Drag Law → Answer
> 1. Write the force balance for the situation (first section above)
> 2. Work out any forces you do not have directly: *W* = *mg*; upthrust = weight of fluid displaced, via *ρ* = *m*/*V*
> 3. Substitute the drag law the question supplies — Stokes' law *F* = 6*πηrv*, or a given formula such as *D* = *kv*²
> 4. Rearrange for the unknown and give the answer with its unit
>
> If the question gives a volume but the drag law needs a radius, extract it from *V* = 4/3 *πr*³ first. And for a body falling or rising through a liquid, the balance is incomplete without upthrust — leaving it out invalidates every line that follows.

> [!warning] Errors That Cost Marks
> - Stopping the chain at "forces balance" without stating zero acceleration and constant velocity
> - Answering a graph question without referring to the graph
> - Dropping upthrust from the balance for a body falling or rising through a liquid
> - Confusing drag (speed-dependent) with upthrust (constant)
> - Reciting the falling-skydiver explanation for an object that is rising or driven — the balance is different
> - In the practical, starting the timing at the surface, before terminal velocity has been reached
