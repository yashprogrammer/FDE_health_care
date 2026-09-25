# Same Feature, Two Engineers: FDE vs AI Engineer
### Webinar content, speaker script and visual ideas

**Total runtime:** about 75 min plus Q&A
**Running example:** *Discharge Copilot*, an AI feature added to a hospital's 14-year-old Hospital Management System (HMS)

| # | Section | Time |
|---|---------|------|
| 1 | Hook: same feature, two POVs | 7 min |
| 2 | What is an FDE | 6 min |
| 3 | Roles of an FDE (real JDs) | 8 min |
| 4 | FDE vs AI Engineer | 6 min |
| 5 | Analogy: renovating a house while the family lives in it | 7 min |
| 6 | Responsibilities across the lifecycle | 7 min |
| 7 | Clearing up role confusion | 6 min |
| 8 | The story: CityCare Hospitals | 18 min |
| 9 | The reveal: the AI engineer's slice | 4 min |
| 10 | Quiz | 6–8 min |

> The hospital, people and numbers in the story are **illustrative**. Say so on stage. It protects your credibility, and the numbers are realistic enough to teach with.

---

## 1. HOOK: Same feature, two POVs (7 min)

### What to show
Three screens, one after another:
1. **Legacy HMS** (old, grey, form-heavy). A resident doctor is copy-pasting from 5 screens into a Word template to write a discharge summary.
2. **POC**: a clean standalone app. Pick a patient, click "Generate", and an AI draft of the discharge summary appears with a "TPA-readiness" checklist.
3. **Integrated system**: the same legacy HMS, now with a "Discharge Copilot" link. The draft is waiting when the doctor opens it. The doctor edits and signs, and the PDF goes back into the HMS.

### What to say (script)
> "This is one feature: an AI that drafts hospital discharge summaries. Two engineers worked on it. Both wrote code, and both were essential. Now look at their calendars."

**Split-screen slide: two calendars**

| AI Engineer's calendar | FDE's calendar |
|---|---|
| **Day 1:** Gets a ticket: *"Build discharge-summary generator. Input: encounter JSON. Output: structured summary. Target: ≥90% clinician-rated accuracy."* | **Week 1:** Stands in a cardiology ward at 7 AM watching how discharges actually happen. Learns what TPA, cashless, ICD-10 and IPD mean. |
| **Days 2–6:** Prompt design, structured output, retrieval over templates, hallucination guardrails | **Week 1–2:** Reverse-engineers a 14-year-old Oracle-backed HMS with 400+ tables and one person (Suresh) who understands it |
| **Days 7–9:** Eval set, clinician rubric, error analysis, latency and cost tuning | **Week 2:** Pulls 3 months of timestamps and finds the *real* problem isn't the one the CEO asked about |
| **Day 10:** PR merged ✅ | **Week 3:** Brainstorms options, kills two of them (including "replace the HMS"), writes the HLD and LLD |
| | **Week 3:** Two meetings: one with IT (architecture, security), one with the CEO and CFO (money, beds, risk) |
| | **Week 4–5:** Builds the POC *with* the AI engineer, then validates it with engineers **and** with doctors and the insurance desk |
| | **Week 6–10:** Integrates with the legacy system without breaking it, runs shadow mode, pilots on one ward, trains doctors, measures impact, expands |

> "So who built the feature? Both of them. But only one of them decided **which** feature was worth building, **why**, **for whom**, and **how it would survive in the real hospital.**"

### The one line to leave on screen
> **The AI Engineer answers: "How do I build this well?"**
> **The FDE answers: "What should we build, why, and how does it survive in *their* world?"**
>
> *The difference isn't less work versus more work. It's different work.*

**Visual idea:** an iceberg. Above the water: "AI model + prompt + app" (what everyone sees in the demo). Below it: domain, legacy system, stakeholders, data access, compliance, business case, integration, rollout and adoption. Label the whole iceberg "FDE" and only the tip "AI Engineer".

---

## 2. What is an FDE? (6 min)

### Definition (put this on a slide)
> **A Forward Deployed Engineer is a software engineer who embeds with a customer, owns their problem end to end, and ships production software that works inside the customer's messy reality: their data, their legacy systems, their people and their constraints.**

### Where the name comes from
- **"Forward deployed"** is a military term: units stationed *at the front*, close to the action, rather than at headquarters.
- In tech, **Palantir** made the role famous. They embedded "Forward Deployed Software Engineers" directly with customers (governments, hospitals, manufacturers) to solve their hardest problems with data. Internally the roles were nicknamed *"Deltas"* (the engineers) and *"Echos"* (deployment strategists on the business side).
- Palantir describes the FDSE role as close to being a **startup CTO**: small teams, end-to-end ownership, and days that mix architecture, data wrangling, coding an app, talking to customer executives and setting strategy.

### Why everyone is hiring FDEs now
- **The models already work. Deployments stall.** A widely cited 2025 MIT NANDA report found that about **95% of enterprise GenAI pilots showed no measurable business impact**. The gap is deployment, not model quality.
- **Demand exploded.** Indeed data reported by the FT and Fast Company showed FDE job postings rose about **800% between January and September 2025**.
- **Who's hiring:** OpenAI, Anthropic, Google Cloud, AWS, Microsoft AI, Salesforce, Databricks, Scale AI, and many AI startups.

### The mental model
> General-purpose AI + a specific customer's messy world = **a gap**.
> The FDE is the person who closes that gap.

---

## 3. Roles of an FDE: what the real JDs say (8 min)

> Tip: open 2–3 of these job postings live in the browser during the webinar. Seeing the real postings convinces people faster than any slide.

### Snapshot of real postings

| Company | Role | What the JD emphasises (paraphrased) |
|---|---|---|
| **Google** | Forward Deployed Engineer, GenAI / Applied AI, Google Cloud | Embedded "innovator-builders" who code, debug and ship agentic solutions **inside the customer's environment**. They clear production blockers (integration complexity, data readiness, state management) and feed field insights back into the Google Cloud roadmap. Preferred: RAG and vector DBs, multi-agent frameworks (LangGraph, CrewAI, ADK). |
| **Amazon (AWS)** | Sr Forward Deployed Engineer, AWS FDE | Embeds inside strategic enterprise customers to **design, build, deploy and run** AI production systems. Leads technical delivery across workstreams, owns production readiness (evals, observability, incident playbooks), mentors junior FDEs, spots expansion opportunities. Requires explaining tech to technical and non-technical stakeholders. |
| **Microsoft** | Forward Deployed AI Engineer, **Health** (Microsoft AI) | Technical lead embedded between Microsoft AI and **Mayo Clinic**. Must understand complex clinical data platforms and **legacy systems** and find "the shortest path from ambiguity to working AI." *(This is almost exactly our story. Show it.)* |
| **OpenAI** | Forward Deployed Engineer | Leads end-to-end deployments with strategic customers and **owns discovery, scoping, system design, build and production rollout**. Success = production adoption, measurable workflow impact, and eval-driven feedback into product and model roadmaps. |
| **Anthropic** | Forward Deployed Engineer, Applied AI | Embeds with strategic customers to ship AI applications for real business problems. Codifies repeatable deployment patterns, feeds insights back to Product and Engineering, and finds new AI opportunities. 25–50% travel to customer sites. |
| **Palantir** | Forward Deployed Software Engineer | Gathers requirements, analyses data and workflows, defines a **roadmap from prototype to scaled deployment**, and ships pipelines and apps that turn data into operational decisions. |

### The 8 core responsibilities, distilled from these JDs
1. **Discovery and domain immersion**: learn the customer's business, workflows and vocabulary.
2. **Problem framing**: turn a vague ask into a sharp, measurable problem statement.
3. **Solution design**: architecture (HLD and LLD), trade-offs, and what *not* to build.
4. **Build**: prototype first, then production. FDEs write real code.
5. **Integration**: make it work with the customer's legacy systems, data, auth and security rules.
6. **Production excellence**: evals, observability, reliability, incident handling.
7. **Stakeholder communication**: talk tech with engineers and ROI with executives, often on the same day.
8. **Feedback loop and expansion**: bring field learnings back to the product team, codify reusable patterns, and find the next use case.

### Skills pattern across all JDs
- **Hard skills:** Python/TypeScript, cloud, APIs, data pipelines, RAG, agents, evals
- **Soft skills that are actually hard:** ambiguity tolerance, customer empathy, executive communication, ownership
- **Common signals:** "founder or startup experience", "customer-facing", "travel"

**Pay (US, reported):** Palantir's listed base for FDSE is about $135K–$200K. Industry reports put mid-to-senior FDE total comp at frontier AI labs at roughly $300K–$550K+. *(Quote these as reported ranges, not promises.)*

---

## 4. FDE vs AI Engineer (6 min)

| Dimension | AI Engineer | FDE |
|---|---|---|
| **Core question** | "How do I build this AI component well?" | "What should we build, and how does it succeed *here*?" |
| **Starting input** | A well-defined spec or ticket | A vague business pain ("we want AI") |
| **Primary output** | A working, evaluated AI component (pipeline, agent, RAG, model service) | A business outcome: a deployed, adopted, integrated solution |
| **Who they talk to** | Engineers, PMs, sometimes data teams | Doctors, CFOs, IT heads, compliance, end users, *and* engineers |
| **Where they sit** | Inside their own company's product or platform team | Inside (or right next to) the **customer's** world |
| **Ambiguity level** | Low to medium: the problem is already framed | Very high: the problem has to be *discovered* |
| **Success metric** | Accuracy, latency, cost, eval scores | Adoption, business KPI moved, customer renews or expands |
| **Artifacts** | Code, prompts, eval sets, model configs | Problem statement, stakeholder map, HLD, LLD, business case, POC, integration plan, rollout plan, *and* code |
| **Depth vs breadth** | Deep in AI/ML | T-shaped: broad across business, systems and people, deep enough in AI to build |
| **Typical failure mode** | Model is great but solves the wrong problem | Solves the right problem but the solution has weak AI internals |

### Two myths to kill
- ❌ *"FDE = AI engineer + soft skills."* An FDE also owns **problem discovery, business case, integration and adoption**. Those are separate skills that can be learned.
- ❌ *"AI engineer is a junior FDE."* No. It's a different axis. The best AI engineers go **deeper** (evals, fine-tuning, agent architectures, inference optimization). The best FDEs go **wider**. A great team needs both.

> **Line to say:** "The AI engineer makes sure the engine is world-class. The FDE makes sure the car is going where the customer actually needs to go, on *their* roads."

---

## 5. Analogy: renovating a house while the family still lives in it (7 min)

### Set the scene
> "The Sharma family lives in a 30-year-old house in Pune. Three generations under one roof. Dad calls a builder and says: *'We want a modern smart home.'*"

The important part is that **this is a renovation, not a new build**. The family keeps living there during the work. You can't switch off the water, you can't knock down load-bearing walls, and the original blueprints are lost. Only old Ramesh Kaka, who helped build the house in 1995, knows where the pipes run.

**That is exactly an enterprise with a legacy system.**

### The cast

| House | Software world |
|---|---|
| The Sharma family (Dad, Mom, Grandma, kids) | Customer stakeholders, each with different needs |
| The old house, still lived in | The legacy system, still running in production |
| Load-bearing walls | Core legacy DB and system you must not break |
| Lost blueprints | No documentation |
| Ramesh Kaka, who knows the pipes | The one veteran IT person who knows the legacy code |
| Municipal rules and building codes | Compliance (patient-data law, security policies) |
| **Architect-cum-site-lead** who lives near the site and runs the whole project | **FDE** |
| **Smart-home and electrical specialist engineer** | **AI Engineer** |

### What the architect (FDE) does, step by step
1. **Site visit and soil test**: walks the house, taps walls, checks the wiring and plumbing. *Understand the legacy system.*
2. **Listens to the family in *their* language**: Dad says "smart home", Mom says "more light in the kitchen", the kids want fast Wi-Fi. The architect never says "cantilever" at the dinner table. *Non-technical stakeholder conversations.*
3. **Discovers the real need**: while chatting, the architect notices Grandma holding the railing on every step. Her knees are bad. The *real* priority is a **ground-floor bedroom with an accessible bathroom**, not smart bulbs. *The stated problem is not the real problem.*
4. **Brainstorms options**: demolish and rebuild (too costly, family has nowhere to go), extend the ground floor, or convert the study. *Solution options and trade-offs.*
5. **Blueprint**: the overall layout and how the new rooms connect to the old house. *HLD.*
6. **Structural, electrical and plumbing drawings**: exact beam sizes, wire gauges, pipe routes. *LLD.*
7. **Cost estimate and value pitch to Dad**: "₹12 lakh. Grandma stops climbing stairs, the house resale value goes up, and the electricity bill drops 30% with solar." *Business pitch and value proposition.*
8. **Builds one room first**: converts the study into Grandma's room, and the family tries it for two weeks. *POC.*
9. **Connects new to old without breaking anything**: taps into the existing plumbing and wiring while the family keeps living there, with no day without water. *Integration with legacy, zero downtime.*
10. **Handover and snag list**: fixes issues, shows the family how to use things, checks back in a month. *Rollout, training, monitoring.*

### What the specialist engineer (AI engineer) does
Gets a precise drawing: *"Install 5 kW solar, 12 smart switches in these rooms, automation panel here, load calculations attached."* Then executes it **superbly**.

- If the specialist is bad, the house **catches fire**. The expertise is non-negotiable.
- But the specialist **doesn't decide** whether the house needs solar at all, and doesn't know Grandma can't climb stairs.

### The punchline
> "Imagine the smart-home engineer installs brilliant automation... in the upstairs room Grandma can no longer reach. Technically perfect, and useless. **That is the 95% of AI pilots that show no business impact.**"

> "And a good architect understands electrical engineering well enough to design around it. In a small team, the FDE may even do the wiring themselves. The roles overlap, but the **ownership** is different."

---

## 6. Responsibilities across the lifecycle: problem → idea → software (7 min)

### Visual idea
A horizontal **swimlane** from left to right: *Human problem → Understanding → Design → Alignment → Build → Validate → Integrate → Adopt → Improve*. Two lanes, **FDE** and **AI Engineer**. The FDE lane is filled almost end to end. The AI Engineer lane lights up mainly in the middle (Build and Validate) and again in Improve.

### Responsibility matrix
● = Owns ◐ = Contributes ○ = Usually not involved

| # | Phase and activity | FDE | AI Eng |
|---|---|:-:|:-:|
| 1 | Customer discovery and domain immersion | ● | ○ |
| 2 | Legacy system archaeology (data, APIs, hidden constraints) | ● | ○ |
| 3 | Problem framing and success metrics | ● | ○ |
| 4 | Stakeholder mapping and alignment | ● | ○ |
| 5 | Brainstorming options and what *not* to use AI for | ● | ◐ |
| 6 | High-Level Design (HLD) | ● | ◐ |
| 7 | Low-Level Design: whole system | ● | ◐ |
| 8 | Low-Level Design: AI component (prompts, RAG, agents, eval design) | ◐ | ● |
| 9 | Security, compliance and data-governance sign-off | ● | ◐ |
| 10 | Business case, value proposition, exec pitch | ● | ○ |
| 11 | POC: AI pipeline build | ◐ | ● |
| 12 | Evals, guardrails, hallucination control | ◐ | ● |
| 13 | POC verification: technical | ● | ● |
| 14 | POC verification: business and end users | ● | ○ |
| 15 | Integration with legacy (adapters, data contracts, auth) | ● | ◐ |
| 16 | Rollout: shadow mode, pilot, training, change management | ● | ○ |
| 17 | Model quality monitoring and iteration | ◐ | ● |
| 18 | Business impact measurement and expansion | ● | ○ |
| 19 | Feedback to product and HQ, reusable patterns | ● | ◐ |

> **Line to say:** "Count the black dots. The AI engineer *owns* about 4 of 19 activities. Those 4 are deep, hard and critical. The FDE owns or co-owns almost everything else. That's the whole difference in one slide."

---

## 7. Clearing up role confusion (6 min)

When people first hear "FDE", they map it to a role they already know. Here's how to separate them.

| Role | Primary job | Writes production code? | Owns the outcome after launch? | Key difference from FDE |
|---|---|:-:|:-:|---|
| **Consultant** (IT/management) | Diagnose and recommend | Rarely | No, hands off a deck and roadmap | Consultant *advises*. FDE *builds and ships*. |
| **Project / Program Manager** | Plan, track, remove blockers, manage timelines | No | Owns *delivery schedule* | PM manages *when*. FDE decides *what* and builds *how*. |
| **Solutions Architect** | Design reference architectures, often pre-sales | Sometimes (demos) | Usually no | SA draws the blueprint. FDE draws it **and** builds it in the customer's environment. |
| **Sales / Solutions Engineer (pre-sales)** | Prove the product can work to win the deal | Demo code | No, leaves after the deal | SE shows it *can* work. FDE makes it *actually* work after the deal. |
| **Product Manager** | Decide what the *product* should be for *many* customers | No | Owns the product roadmap | PM optimizes for the market. FDE optimizes for *this* customer and feeds learnings back to PM. |
| **Business Analyst** | Gather and document requirements | No | No | BA writes requirements. FDE writes requirements **and** the code **and** the pitch. |
| **Customer Success / TAM** | Adoption, renewals, relationship health | No | Owns account health | CSM keeps the customer happy. FDE builds the thing that makes them happy. |
| **Implementation / Professional Services Engineer** | Configure and install the *existing* product | Config and scripts | Partially | Implements *known* features. FDE builds *new* solutions for unsolved problems. |
| **AI / ML Engineer** | Build AI components deeply | Yes | Owns component quality | Deep on the model side. FDE is broad across business, systems and people. |

### Memory hook (put this on its own slide)
> **Consultant** tells you what to build.
> **Project Manager** tracks when it gets built.
> **Solutions Architect** draws how it *could* be built.
> **Sales Engineer** proves it *can* be built.
> **AI Engineer** builds the smartest part of it.
> **FDE** figures out what's worth building, builds it *inside your world*, and stays until it works.

---

## 8. The story: CityCare Hospitals and the Discharge Copilot (18 min)

> Tell it as a story with a protagonist. Call the FDE **Ananya**. At every chapter, show the **artifact** she produces. Those artifacts are the proof of the FDE's work.

### Chapter 0: The ask
CityCare is a 300-bed private hospital in Pune. The CEO tells Ananya's company:

> *"Our doctors are drowning in paperwork. Build us a ChatGPT for discharge summaries."*

A pure build mindset opens a code editor right here. Ananya books a train to Pune.

---

### Chapter 1: Understanding the domain and the legacy system (Weeks 1–2)

**Domain immersion.** Ananya shadows Ward 4B (Cardiology) from 7 AM. She learns the vocabulary:
- **IPD**: in-patient department (admitted patients)
- **ADT**: Admit, Discharge, Transfer events
- **Discharge summary**: the legal and clinical document a patient leaves with (diagnosis, procedures, hospital course, medications, follow-up)
- **ICD-10**: diagnosis codes
- **TPA / cashless**: third-party administrators who approve insurance claims. For cashless patients, the hospital sends the **final bill + discharge summary** to the TPA and waits for approval before the patient can leave.
- **NABH**: Indian hospital accreditation, with rules about documentation quality

She maps the real discharge flow:
`Doctor advises discharge (rounds, ~10 AM) → resident writes summary → pharmacy returns → final bill → (insured) TPA approval → patient leaves`

**Legacy archaeology.** The HMS, "MediTrack", was built in 2011:
- A Java monolith on Oracle with 400+ tables and names like `PT_ADM_DTL` and `IP_DSCH_HDR`
- The vendor no longer supports it. **Suresh** from hospital IT is the only person who understands it (he's the "Ramesh Kaka" of this house).
- **No APIs.** A **read-only reporting replica** exists for monthly MIS reports.
- Lab results arrive from the lab system over **HL7 v2** messages. Nursing notes are free text.
- The discharge summary is a **Word template**. Residents copy-paste from 5 different screens.

📄 **Artifacts:** Domain glossary, current-state process map, legacy system map (modules, tables, data flows, access points), a "don't touch" list

---

### Chapter 2: Finding the real problem (Week 2)
Ananya asks Suresh for 3 months of timestamps from the replica and analyses them:

| Metric | Found |
|---|---|
| Time spent writing a summary | 35–45 min per patient |
| Discharge advised → patient leaves (**cash** patients) | ~2.5 hours |
| Discharge advised → patient leaves (**insured** patients) | **~6.2 hours** |
| TPA submissions that bounce back with a **query** | **38%** (each adds about 2 hours) |
| Top query reasons | Missing investigation reports, diagnosis/procedure mismatch, missing doctor details |

**The reframe:**
- ❌ Stated problem: *"Doctors need AI to write summaries."*
- ✅ Real problem: ***"Insured patients wait over 6 hours to go home because discharge summaries are slow to write AND often incomplete for insurers. That blocks beds and frustrates patients."***

**Stakeholder map:**

| Stakeholder | What they care about |
|---|---|
| CEO / CFO | Bed turnover, revenue, patient complaints |
| Medical Superintendent | Clinical safety, NABH compliance |
| Resident doctors | Time, less clerical work |
| TPA desk | Fewer insurer queries |
| IT Head + Suresh | "Don't break MediTrack", security |
| Compliance | Patient-data privacy (India's DPDP Act), audit trails |
| Patients | Go home sooner |

📄 **Artifacts:** Data analysis, problem statement, success metrics (discharge time, TPA query rate, doctor minutes per summary), stakeholder map

---

### Chapter 3: Brainstorming (Week 3)

| Option | Verdict | Why |
|---|---|---|
| A. Fully automatic AI summary, auto-sent to TPA | ❌ Rejected | Clinical and legal liability. A doctor **must** review and sign. |
| B. Replace MediTrack with a modern HMS | ❌ Rejected | Costs crores, takes 18+ months, high risk, and doesn't fix the problem |
| C. Voice dictation for doctors | ⚠️ Partial | Faster typing, but doesn't fix incompleteness for TPA |
| **D. Discharge Copilot**: AI drafts the summary from HMS data, a **rule-based TPA-readiness checker** flags gaps, and the doctor reviews, edits and signs | ✅ **Chosen** | Solves both causes, keeps a human in the loop, doesn't modify the legacy core |

**Key FDE insights (say these slowly):**
- **Discharge medications are *not* generated by the LLM.** They're pulled **deterministically** from pharmacy records. The source of truth already exists, so don't let a model paraphrase a drug dose.
- **The TPA checklist is a rules engine, not AI.** The rules are known, so use code.
- The LLM does what it's best at: turning messy notes and lab data into a coherent **hospital course** narrative.
- > *"The best AI solution was about 30% AI and 70% good engineering and good judgment."*

📄 **Artifacts:** Options analysis with trade-offs, decision log

---

### Chapter 4: Proposing the solution (Week 3–4)

#### Meeting 1, technical: IT Head, Suresh, security

**HLD (high level):**
```
MediTrack (Oracle, untouched)
        │  read-only
        ▼
Reporting Replica ──► Adapter Service ──► Encounter JSON
                                             │
                                             ▼
                               Discharge Copilot Service
                        ┌──────────────┬──────────────┬─────────────┐
                        │ LLM Gateway  │ TPA Rules    │ Meds Puller │
                        │ (PII redact, │ Engine       │ (determin-  │
                        │  audit log)  │              │  istic)     │
                        └──────────────┴──────────────┴─────────────┘
                                             │
                                             ▼
                          Copilot UI (doctor reviews, edits, signs)
                                             │
                                             ▼
                     Signed PDF ──► MediTrack document module (existing)
```

**LLD (low level):**
- **Data contract**: an `Encounter` JSON schema (patient, admission, diagnoses, procedures, labs, meds, notes)
- **Adapter**: SQL queries against replica tables, HL7 lab parsing, polling for "discharge advised" status changes
- **Copilot API**: `POST /drafts/{encounterId}`, `GET /drafts/{id}`, `POST /drafts/{id}/sign`
- **Prompt templates** per specialty, with structured output (sections as JSON)
- **Guardrails**: every medication, lab value and diagnosis in the draft must trace back to source data. Anything else gets flagged.
- **Audit tables**: who generated, who edited, what changed, who signed
- **Failure mode**: if the LLM is down, fall back to the old Word template. The hospital never stops.
- **Security**: patient data stays within approved infrastructure, identifiers are masked before any model call, and every access is logged

#### Meeting 2, business: CEO, CFO, Medical Superintendent
Ananya does **not** show the architecture diagram here. She shows this:

> **Value proposition:** *"Insured patients go home about 3 hours sooner, insurer queries drop by more than half, and residents get 30 minutes back per discharge. We don't touch MediTrack, and a doctor signs every summary."*

**Business case (illustrative numbers):**
- 60 discharges/day × 60% insured = **36 insured discharges/day**
- ~3 hours saved each ≈ **108 bed-hours/day ≈ 4.5 beds freed every day**
- ≈ 1,640 extra bed-days/year × illustrative ₹35,000 average revenue per occupied bed per day ≈ **₹5.7 crore/year potential**. *(Ananya's honest caveat: "This only counts if there is waiting demand, such as ER boarding or an elective backlog. You have both.")*
- **~28 resident-hours/day** returned to patient care
- Top patient complaint (discharge delays) addressed

**Risks and mitigations:** hallucination (source tracing plus doctor sign-off), doctor adoption (pilot with their own feedback), data privacy (masking, audit, on-approved-infra), legacy risk (read-only, zero writes to the core DB)

**The ask:** a 4-week pilot on Cardiology, with success criteria agreed upfront.

📄 **Artifacts:** HLD, LLD, security note, business case, value proposition, pitch deck, pilot plan with success criteria

---

### Chapter 5: POC and verification (Weeks 4–5)
- 50 past discharges, **de-identified**, exported from the replica
- The AI pipeline, eval set and guardrails get built. **(This is where the AI engineer shines.)**
- **Technical verification:**
  - Factual accuracy per section, checked against the source data
  - **Zero** invented medications (guaranteed by design, since meds are pulled deterministically)
  - Draft ready in under 60 seconds, at a cost of a few rupees per summary
- **Business verification:**
  - Blind review: 5 cardiologists compare AI drafts against real summaries
  - The TPA desk lead checks the readiness checklist against last month's actual insurer queries and says: *"That's exactly what they keep sending back."*
- **Surprise learning:** doctors wanted the hospital course as **bullets, not paragraphs**, and wanted "pending reports" highlighted in red. Neither was in any spec. Both came from watching doctors use the POC.

📄 **Artifacts:** Eval report, clinician feedback, updated LLD, go/no-go memo

---

### Chapter 6: Integration with the legacy system (Weeks 6–10)
- **Adapter goes live**: it watches the replica for "discharge advised" events and generates drafts automatically
- **Entry point without changing MediTrack's code**: Suresh reveals MediTrack supports **custom menu links**, so a "Discharge Copilot" link opens the draft for that patient. *(Only someone who sat with Suresh finds this.)*
- **Write-back**: the signed summary goes back as a PDF through MediTrack's **existing** document upload module
- **Shadow mode (1 week)**: drafts are generated but not shown, then compared silently against what doctors wrote
- **Pilot (Cardiology, 4 weeks)**: a 20-minute training for residents, a feedback button, a daily check-in
- **Monitoring dashboard**: discharge time, TPA query rate, doctor edit distance, flagged hallucinations, usage
- **Results after the pilot (illustrative):**

| Metric | Before | After |
|---|---|---|
| Insured discharge time | 6.2 h | 3.4 h |
| TPA query rate | 38% | 14% |
| Doctor time per summary | ~40 min | ~12 min |

- **Expansion**: hospital-wide rollout, then the same pattern for **pre-authorization at admission** (the next use case Ananya spotted)

📄 **Artifacts:** Integration runbook, rollout plan, training material, monitoring dashboard, impact report, expansion proposal

---

## 9. The reveal: this was the AI engineer's part (4 min)

### How to do it on stage
Show the full story as a timeline of 6 chapters. Then **grey out everything** except the AI engineer's slice:

| Chapter | AI Engineer's slice |
|---|---|
| 0–4 | *(Optionally reviews the LLD of the AI component)* |
| **5: POC** | ✅ Prompt design, structured output, hallucination guardrails, source tracing, eval set and clinician rubric, error analysis, latency and cost tuning |
| **6: Integration** | ✅ LLM gateway hardening, model monitoring (quality drift, flagged outputs), prompt iteration from doctor feedback |

### What to say
> "Out of 10 weeks, the AI engineer was core for about 3. Those 3 weeks are **hard**: if the model hallucinates a diagnosis, nothing else matters. But notice everything the AI engineer *never had to deal with*: the 7 AM ward rounds, Suresh and his Oracle tables, the TPA desk, the CFO's spreadsheet, the menu-link hack, the shadow mode, the training."
>
> "**That** is the FDE. Not a better AI engineer. A different engineer, one who owns the whole iceberg."

### Closing thought for students
> "If you love going deep on models, evals and agents, be an AI engineer, and be world-class at it. If you love ambiguity, people, business and building, all in the same week, the FDE path is wide open. Either way, **learn to see the whole iceberg**."

---

## 10. Quiz: 4 questions (medium)

> Run it as a live poll. Reveal the answer and take 30 seconds on the explanation.

**Q1. CityCare's CEO says, "Build us a ChatGPT for discharge summaries." As the FDE, what's your best first move?**
- A) Benchmark 3 LLMs to choose the most accurate one
- B) Quickly build a demo to impress the CEO
- C) Shadow the discharge workflow and pull real timing data to see where time actually goes ✅
- D) Write the HLD so engineering can start immediately

*Why:* The stated problem is rarely the real problem. The data showed the bottleneck was insured discharges and TPA queries, not just writing time. A, B and D all assume the problem is already understood.

---

**Q2. In the Discharge Copilot, why were discharge medications pulled deterministically from pharmacy records instead of generated by the LLM?**
- A) LLMs can't read medication names
- B) It was cheaper in tokens
- C) A reliable source of truth already existed, and a hallucinated drug or dose is a patient-safety risk ✅
- D) The TPA requires medications in a different language

*Why:* A core FDE judgment call is knowing **what not to use AI for**. When a source of truth exists and errors are dangerous, use deterministic code.

---

**Q3. Which statement best separates an FDE from a Consultant and a Solutions Architect?**
- A) The FDE only works after the sale and never talks to executives
- B) The FDE owns the outcome: they design **and** ship production code inside the customer's environment and stay until it works ✅
- C) The FDE writes the requirements document and hands it to the customer's IT team
- D) The FDE is a sales role focused on winning deals

*Why:* The consultant advises, the SA designs (often pre-sale), and the FDE designs, builds, integrates and owns adoption. C describes a BA or consultant. D describes a sales engineer.

---

**Q4. In the house-renovation analogy, what do the "load-bearing walls you can't touch while the family lives there" correspond to, and how did Ananya respect them?**
- A) The LLM's context window, so she used a bigger model
- B) The legacy HMS core in production, so she read only from the reporting replica, used existing menu links and document upload, and never modified MediTrack's core ✅
- C) The hospital budget, so she chose the cheapest cloud provider
- D) Doctor resistance, so she made the AI fully automatic

*Why:* You don't knock down load-bearing walls in an occupied house. Likewise, you integrate *around* a live legacy system with read replicas, adapters and existing extension points, with zero downtime.

---

## Sources (for your own reference and to show live)
- [Palantir: Forward Deployed Software Engineer posting (Lever)](https://jobs.lever.co/palantir/dab396d4-2f14-4796-aac0-0d82883dccf0)
- [Palantir blog: A Day in the Life of a Palantir FDSE](https://blog.palantir.com/a-day-in-the-life-of-a-palantir-forward-deployed-software-engineer-45ef2de257b1)
- [OpenAI: Forward Deployed Engineer (FDE), SF](https://openai.com/careers/forward-deployed-engineer-(fde)-sf-san-francisco/)
- [Anthropic: Forward Deployed Engineer (Greenhouse)](https://job-boards.greenhouse.io/anthropic/jobs/5302966008)
- [Google Careers: Forward Deployed Engineer, Google Cloud Consulting](https://careers.google.com/jobs/results/106365505090003654-forward-deployed-engineer/)
- [Google Careers: Forward Deployed Engineer III, GenAI, Google Cloud](https://careers.google.com/jobs/results/87580366008656582-forward-deployed-engineer-iii/)
- [Amazon: Sr Forward Deployed Engineer, AWS FDE](https://www.amazon.jobs/en/jobs/10517491/sr-forward-deployed-engineer-aws-forward-deployed-engineering)
- [Microsoft AI: Forward Deployed AI Engineer, Health (Mayo Clinic)](https://microsoft.ai/careers/job/4407776009/forward-deployed-ai-engineer-health/)
- [Fast Company: Postings for this AI job are up 800%](https://www.fastcompany.com/91435680/postings-for-this-ai-job-are-up-800)
- [The Pragmatic Engineer: What are Forward Deployed Engineers?](https://newsletter.pragmaticengineer.com/p/forward-deployed-engineers)
- [The New Stack: FDE is AI's hottest job](https://thenewstack.io/forward-deployed-engineer-fde-openai-google/)
