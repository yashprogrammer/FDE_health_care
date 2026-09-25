"""Synthetic, fictional clinical data for CityCare Hospitals, Pune.

Every person, policy number and TPA below is invented for teaching purposes.
"""

DOCTORS = [
    ("D01", "Dr. Anjali Mehta", "Cardiology", "MMC-2009-04512"),
    ("D02", "Dr. Rajesh Gokhale", "Internal Medicine", "MMC-2005-11873"),
    ("D03", "Dr. Sameer Bhide", "Orthopaedics", "MMC-2011-07734"),
    ("D04", "Dr. Neha Rao", "General Surgery", "MMC-2013-02291"),
]

RMO = "Dr. Karan Shah (RMO)"

GOLDEN_IP = "IP2609-0142"

# ---------------------------------------------------------------------------
# Current in-patients (census)
# ---------------------------------------------------------------------------
CURRENT = [
    dict(
        ip=GOLDEN_IP, uhid="CC-2026-018734", name="Ramesh Kulkarni", age=62, sex="M",
        mob="98220 41873", addr="Kothrud, Pune",
        adm="2026-09-21 06:40", ward="4B-CARD", bed="12", dr="D01",
        pay="CASHLESS", tpa="SecureHealth TPA", pol="SHI/2026/0048812",
        rsn="Retrosternal chest pain radiating to left arm x 2 hrs with sweating",
        sts="ADM",
        diags=[
            ("I21.0", "Acute transmural MI of anterior wall", "PROV"),
            ("I21.0", "Acute ST-elevation myocardial infarction, anterior wall", "FINAL"),
            ("I10", "Essential (primary) hypertension", "FINAL"),
            ("E78.5", "Hyperlipidaemia, unspecified", "FINAL"),
        ],
        procs=[
            ("93458", "Coronary angiography", "2026-09-21 07:55", "D01"),
            ("92928", "Primary PTCA with drug-eluting stent to proximal LAD", "2026-09-21 08:15", "D01"),
        ],
        labs=[
            ("Troponin I", "12.4", "ng/mL", "<0.04", "H", "2026-09-21 07:00", "FINAL"),
            ("CK-MB", "86", "U/L", "<25", "H", "2026-09-21 07:00", "FINAL"),
            ("Haemoglobin", "13.2", "g/dL", "13-17", "", "2026-09-21 07:00", "FINAL"),
            ("Serum Creatinine", "1.1", "mg/dL", "0.7-1.3", "", "2026-09-21 07:00", "FINAL"),
            ("Serum Potassium", "4.2", "mmol/L", "3.5-5.1", "", "2026-09-21 07:00", "FINAL"),
            ("LDL Cholesterol", "162", "mg/dL", "<100", "H", "2026-09-22 06:30", "FINAL"),
            ("HbA1c", "6.1", "%", "<5.7", "H", "2026-09-22 06:30", "FINAL"),
            ("2D Echo LVEF", "40", "%", "55-70", "L", "2026-09-22 11:00", "FINAL"),
            ("Troponin I (repeat)", "3.1", "ng/mL", "<0.04", "H", "2026-09-23 06:30", "FINAL"),
            ("Lipoprotein(a)", "", "mg/dL", "<30", "", "2026-09-23 06:30", "PENDING"),
        ],
        meds=[
            ("Aspirin", "325 mg stat, then 75 mg", "OD", "Oral", "", "INPATIENT"),
            ("Ticagrelor", "180 mg stat, then 90 mg", "BD", "Oral", "", "INPATIENT"),
            ("Atorvastatin", "80 mg", "HS", "Oral", "", "INPATIENT"),
            ("Metoprolol succinate", "25 mg", "OD", "Oral", "", "INPATIENT"),
            ("Enoxaparin", "60 mg", "BD", "SC", "2 days", "INPATIENT"),
            ("Pantoprazole", "40 mg", "OD", "IV", "", "INPATIENT"),
            ("Ramipril", "2.5 mg", "OD", "Oral", "", "INPATIENT"),
            ("Aspirin", "75 mg", "OD", "Oral", "Lifelong", "DISCHARGE"),
            ("Ticagrelor", "90 mg", "BD", "Oral", "12 months", "DISCHARGE"),
            ("Atorvastatin", "80 mg", "HS", "Oral", "Continue", "DISCHARGE"),
            ("Metoprolol succinate", "25 mg", "OD", "Oral", "Continue", "DISCHARGE"),
            ("Ramipril", "2.5 mg", "OD", "Oral", "Continue", "DISCHARGE"),
            ("Pantoprazole", "40 mg", "OD before breakfast", "Oral", "1 month", "DISCHARGE"),
            ("Isosorbide dinitrate", "5 mg", "SOS chest pain", "Sublingual", "As needed", "DISCHARGE"),
        ],
        notes=[
            ("2026-09-21 07:10", "DR", "Dr. Anjali Mehta",
             "62M, k/c/o HTN on amlodipine (irregular), smoker 20 pack-yrs. C/o retrosternal chest pain since 04:30 "
             "radiating to L arm with diaphoresis. ECG: ST elevation V1-V5. Trop I 12.4. Dx: acute anterior wall STEMI. "
             "Plan: primary PCI. High-risk consent taken from patient and wife."),
            ("2026-09-21 09:30", "DR", "Dr. Anjali Mehta",
             "CAG: proximal LAD 99% thrombotic occlusion, LCx 40% non-critical, RCA normal. Primary PTCA + DES "
             "(Xience 3.0 x 28 mm) to proximal LAD via right radial. TIMI III flow achieved. Uneventful. Shift to CCU."),
            ("2026-09-22 10:00", "DR", "Dr. Anjali Mehta",
             "Pain free. Haemodynamically stable. BP 128/80, HR 72/min. No arrhythmia on monitor. Echo: LVEF 40%, "
             "anterior wall hypokinesia, no MR, no clot. Amlodipine stopped, ramipril 2.5 mg started. "
             "Counselled on smoking cessation."),
            ("2026-09-23 10:15", "DR", RMO,
             "Shifted from CCU to ward 4B. Ambulating with support. Repeat Trop I 3.1 (downtrending). "
             "Lp(a) sent to outside lab - report awaited."),
            ("2026-09-24 10:30", "DR", "Dr. Anjali Mehta",
             "Stable, pain free, ambulating independently. Radial site healthy. Plan discharge tomorrow if stable. "
             "Cardiac rehab referral. Review in OPD after 1 week with reports."),
            ("2026-09-21 14:10", "NRS", "Sr. Meena Jadhav",
             "Post-PCI right radial site: no haematoma, distal pulses good. TR band removed at 14:00."),
            ("2026-09-22 20:00", "NRS", "Sr. Meena Jadhav",
             "Vitals stable. Tolerating soft diet. Patient anxious about returning to work (bank cashier) - reassured."),
            ("2026-09-24 16:00", "NRS", "Sr. Pooja More",
             "Ambulating in corridor, no complaints. Dietitian counselling done: low salt, low fat, no smoking."),
        ],
        docs=["ID_PROOF", "CONSENT", "CATH_RPT"],   # IMPLANT_STKR deliberately missing (TPA will query)
    ),
    dict(
        ip="IP2609-0151", uhid="CC-2026-019022", name="Mohammed Shaikh", age=45, sex="M",
        mob="97660 22318", addr="Kondhwa, Pune",
        adm="2026-09-22 21:15", ward="4B-CARD", bed="07", dr="D01",
        pay="CASHLESS", tpa="CarePlus TPA Services", pol="CPT/HL/2025/771203",
        rsn="Chest tightness on exertion, worsening over 3 days, one episode at rest",
        sts="DA", adv="2026-09-25 10:05",
        diags=[
            ("I20.0", "Unstable angina", "FINAL"),
            ("E11.9", "Type 2 diabetes mellitus without complications", "FINAL"),
        ],
        procs=[("93458", "Coronary angiography", "2026-09-23 11:00", "D01")],
        labs=[
            ("Troponin I", "0.02", "ng/mL", "<0.04", "", "2026-09-22 21:40", "FINAL"),
            ("Troponin I (repeat)", "0.03", "ng/mL", "<0.04", "", "2026-09-23 03:40", "FINAL"),
            ("HbA1c", "8.2", "%", "<5.7", "H", "2026-09-23 06:30", "FINAL"),
            ("LDL Cholesterol", "138", "mg/dL", "<100", "H", "2026-09-23 06:30", "FINAL"),
            ("Serum Creatinine", "0.9", "mg/dL", "0.7-1.3", "", "2026-09-22 21:40", "FINAL"),
        ],
        meds=[
            ("Aspirin", "75 mg", "OD", "Oral", "", "INPATIENT"),
            ("Atorvastatin", "40 mg", "HS", "Oral", "", "INPATIENT"),
            ("Metformin", "500 mg", "BD", "Oral", "", "INPATIENT"),
            ("Nitroglycerin", "5 mcg/min infusion", "Continuous", "IV", "24 hrs", "INPATIENT"),
            ("Aspirin", "75 mg", "OD", "Oral", "Lifelong", "DISCHARGE"),
            ("Atorvastatin", "40 mg", "HS", "Oral", "Continue", "DISCHARGE"),
            ("Metformin", "1000 mg", "BD", "Oral", "Continue", "DISCHARGE"),
            ("Metoprolol succinate", "25 mg", "OD", "Oral", "Continue", "DISCHARGE"),
        ],
        notes=[
            ("2026-09-22 21:30", "DR", RMO,
             "45M, T2DM on metformin. Exertional chest tightness x 3 days, 1 episode at rest today lasting 10 min. "
             "ECG: T inversion V4-V6. Trop I negative. Admit for unstable angina, NTG infusion."),
            ("2026-09-23 13:00", "DR", "Dr. Anjali Mehta",
             "CAG: LAD mid 60% non-critical lesion, LCx and RCA normal. Plan medical management, optimise risk factors."),
            ("2026-09-25 09:50", "DR", "Dr. Anjali Mehta",
             "Symptom free for 48 hrs on oral meds. Discharge today. Metformin up-titrated. Stress test after 4 weeks."),
            ("2026-09-24 08:00", "NRS", "Sr. Pooja More", "No chest pain overnight. Blood sugars 140-190 mg/dL."),
        ],
        docs=["ID_PROOF", "CONSENT", "CATH_RPT"],
    ),
    dict(
        ip="IP2609-0138", uhid="CC-2026-018611", name="Sunita Deshpande", age=58, sex="F",
        mob="99700 13478", addr="Aundh, Pune",
        adm="2026-09-20 11:20", ward="3C-MED", bed="04", dr="D02",
        pay="CASH", tpa=None, pol=None,
        rsn="Fever with cough and breathlessness x 5 days",
        sts="ADM",
        diags=[("J18.9", "Community-acquired pneumonia, unspecified organism", "FINAL")],
        procs=[],
        labs=[
            ("Total Leucocyte Count", "16400", "/cumm", "4000-11000", "H", "2026-09-20 12:00", "FINAL"),
            ("CRP", "84", "mg/L", "<6", "H", "2026-09-20 12:00", "FINAL"),
            ("Chest X-ray", "Right lower zone consolidation", "", "", "", "2026-09-20 12:30", "FINAL"),
            ("Blood culture", "", "", "", "", "2026-09-20 12:00", "PENDING"),
        ],
        meds=[
            ("Ceftriaxone", "1 g", "BD", "IV", "", "INPATIENT"),
            ("Azithromycin", "500 mg", "OD", "Oral", "5 days", "INPATIENT"),
            ("Paracetamol", "650 mg", "SOS fever", "Oral", "", "INPATIENT"),
        ],
        notes=[
            ("2026-09-20 11:45", "DR", "Dr. Rajesh Gokhale",
             "58F, fever 5 days, productive cough, SpO2 91% RA. Crepts R base. CXR RLZ consolidation. "
             "Dx CAP. Start ceftriaxone + azithromycin, O2 support."),
            ("2026-09-23 10:00", "DR", "Dr. Rajesh Gokhale", "Afebrile 24 hrs. SpO2 96% on RA. Continue IV antibiotics."),
        ],
        docs=["ID_PROOF"],
    ),
    dict(
        ip="IP2609-0144", uhid="CC-2026-018790", name="Lata Joshi", age=67, sex="F",
        mob="94230 55109", addr="Karve Nagar, Pune",
        adm="2026-09-21 08:00", ward="3A-ORTH", bed="02", dr="D03",
        pay="CASHLESS", tpa="Medinsure TPA", pol="MIT/SR/2024/339120",
        rsn="Planned right total knee replacement for osteoarthritis",
        sts="ADM",
        diags=[("M17.1", "Primary osteoarthritis, right knee", "FINAL")],
        procs=[("27447", "Right total knee arthroplasty", "2026-09-21 10:30", "D03")],
        labs=[
            ("Haemoglobin", "11.2", "g/dL", "12-15", "L", "2026-09-22 06:30", "FINAL"),
            ("Serum Creatinine", "0.8", "mg/dL", "0.6-1.1", "", "2026-09-22 06:30", "FINAL"),
        ],
        meds=[
            ("Cefuroxime", "1.5 g", "BD", "IV", "3 days", "INPATIENT"),
            ("Enoxaparin", "40 mg", "OD", "SC", "", "INPATIENT"),
            ("Tramadol", "50 mg", "TDS", "Oral", "", "INPATIENT"),
        ],
        notes=[
            ("2026-09-21 13:00", "DR", "Dr. Sameer Bhide", "Right TKR done under spinal anaesthesia. Uneventful."),
            ("2026-09-23 10:00", "DR", "Dr. Sameer Bhide", "Mobilising with walker. Wound dry. Physio ongoing."),
        ],
        docs=["ID_PROOF", "CONSENT", "OT_NOTE", "IMPLANT_STKR"],
    ),
    dict(
        ip="IP2609-0147", uhid="CC-2026-018855", name="Arjun Nair", age=34, sex="M",
        mob="98905 77620", addr="Baner, Pune",
        adm="2026-09-22 14:30", ward="3C-MED", bed="09", dr="D02",
        pay="CASH", tpa=None, pol=None,
        rsn="High grade fever with body ache x 4 days",
        sts="ADM",
        diags=[("A97.1", "Dengue with warning signs", "FINAL")],
        procs=[],
        labs=[
            ("NS1 Antigen", "Positive", "", "Negative", "H", "2026-09-22 15:00", "FINAL"),
            ("Platelet Count", "48000", "/cumm", "150000-450000", "L", "2026-09-22 15:00", "FINAL"),
            ("Platelet Count (repeat)", "72000", "/cumm", "150000-450000", "L", "2026-09-24 06:30", "FINAL"),
        ],
        meds=[
            ("Paracetamol", "650 mg", "TDS", "Oral", "", "INPATIENT"),
            ("Normal saline", "100 ml/hr", "Continuous", "IV", "", "INPATIENT"),
        ],
        notes=[
            ("2026-09-22 15:10", "DR", "Dr. Rajesh Gokhale", "Dengue NS1+, platelets 48k, abdominal pain. Admit, IV fluids, monitor."),
            ("2026-09-24 10:00", "DR", "Dr. Rajesh Gokhale", "Platelets rising 72k. Afebrile. Oral intake good."),
        ],
        docs=["ID_PROOF"],
    ),
    dict(
        ip="IP2609-0149", uhid="CC-2026-018902", name="Priya Iyer", age=29, sex="F",
        mob="90110 34522", addr="Viman Nagar, Pune",
        adm="2026-09-23 07:30", ward="2B-SURG", bed="05", dr="D04",
        pay="CASHLESS", tpa="SecureHealth TPA", pol="SHI/2025/0391177",
        rsn="Recurrent right upper abdominal pain, USG gallstones",
        sts="ADM",
        diags=[("K80.2", "Calculus of gallbladder without cholecystitis", "FINAL")],
        procs=[("47562", "Laparoscopic cholecystectomy", "2026-09-23 10:00", "D04")],
        labs=[
            ("USG Abdomen", "Multiple gallbladder calculi, CBD normal", "", "", "", "2026-09-19 10:00", "FINAL"),
            ("Liver Function Test", "Within normal limits", "", "", "", "2026-09-23 06:30", "FINAL"),
            ("Histopathology - gallbladder", "", "", "", "", "2026-09-23 12:00", "PENDING"),
        ],
        meds=[
            ("Ceftriaxone", "1 g", "OD", "IV", "1 day", "INPATIENT"),
            ("Paracetamol", "1 g", "TDS", "IV", "", "INPATIENT"),
            ("Ondansetron", "4 mg", "SOS", "IV", "", "INPATIENT"),
        ],
        notes=[
            ("2026-09-23 11:30", "DR", "Dr. Neha Rao", "Lap chole done, 4 ports, GB sent for HPE. Uneventful."),
            ("2026-09-24 10:00", "DR", "Dr. Neha Rao", "Tolerating liquids. Port sites healthy."),
        ],
        docs=["ID_PROOF", "CONSENT"],   # OT_NOTE missing
    ),
    dict(
        ip="IP2609-0133", uhid="CC-2026-018402", name="Vikram Patil", age=71, sex="M",
        mob="98500 60213", addr="Hadapsar, Pune",
        adm="2026-09-20 02:10", ward="4B-CARD", bed="03", dr="D01",
        pay="CASHLESS", tpa="CarePlus TPA Services", pol="CPT/SR/2023/118340",
        rsn="Breathlessness on lying down and bilateral leg swelling x 1 week",
        sts="ADM",
        diags=[("I50.9", "Heart failure, unspecified", "PROV")],   # no FINAL diagnosis entered yet
        procs=[],
        labs=[
            ("NT-proBNP", "6800", "pg/mL", "<450", "H", "2026-09-20 03:00", "FINAL"),
            ("2D Echo LVEF", "30", "%", "55-70", "L", "2026-09-20 11:00", "FINAL"),
            ("Serum Sodium", "131", "mmol/L", "135-145", "L", "2026-09-21 06:30", "FINAL"),
        ],
        meds=[
            ("Furosemide", "40 mg", "BD", "IV", "", "INPATIENT"),
            ("Spironolactone", "25 mg", "OD", "Oral", "", "INPATIENT"),
            ("Bisoprolol", "2.5 mg", "OD", "Oral", "", "INPATIENT"),
        ],
        notes=[
            ("2026-09-20 02:30", "DR", RMO, "71M, orthopnoea, PND, pedal oedema. Bibasal crepts. Admit ADHF, IV diuretics."),
            ("2026-09-23 10:00", "DR", "Dr. Anjali Mehta", "Net negative 3.2 L. Breathing better. Continue diuresis."),
        ],
        docs=["ID_PROOF"],
    ),
    dict(
        ip="IP2609-0150", uhid="CC-2026-018968", name="Fatima Sayyed", age=52, sex="F",
        mob="95525 80147", addr="Camp, Pune",
        adm="2026-09-23 19:40", ward="3C-MED", bed="11", dr="D02",
        pay="CASH", tpa=None, pol=None,
        rsn="Vomiting, abdominal pain and drowsiness, sugar 'HI' on glucometer",
        sts="ADM",
        diags=[("E11.1", "Type 2 diabetes mellitus with ketoacidosis", "FINAL")],
        procs=[],
        labs=[
            ("Random Blood Sugar", "486", "mg/dL", "70-140", "H", "2026-09-23 19:50", "FINAL"),
            ("Arterial pH", "7.18", "", "7.35-7.45", "L", "2026-09-23 20:00", "FINAL"),
            ("Serum Ketones", "Positive (3+)", "", "Negative", "H", "2026-09-23 20:00", "FINAL"),
        ],
        meds=[
            ("Insulin regular", "0.1 U/kg/hr infusion", "Continuous", "IV", "", "INPATIENT"),
            ("Normal saline", "1 L/hr then titrate", "Continuous", "IV", "", "INPATIENT"),
            ("Potassium chloride", "20 mEq in each litre", "With fluids", "IV", "", "INPATIENT"),
        ],
        notes=[
            ("2026-09-23 20:10", "DR", RMO, "52F, known T2DM, stopped meds 2 weeks. DKA. Start DKA protocol, ICU."),
            ("2026-09-24 12:00", "DR", "Dr. Rajesh Gokhale", "Anion gap closed. Shifted to SC basal-bolus insulin."),
        ],
        docs=["ID_PROOF"],
    ),
]

# ---------------------------------------------------------------------------
# Past discharges with doctor-written summaries (used for POC evals)
# ---------------------------------------------------------------------------
PAST = [
    dict(
        ip="IP2607-0412", uhid="CC-2026-011204", name="Suresh Bhosale", age=58, sex="M",
        mob="98221 55410", addr="Sinhagad Road, Pune",
        adm="2026-07-08 23:10", ward="4B-CARD", bed="05", dr="D01",
        pay="CASHLESS", tpa="SecureHealth TPA", pol="SHI/2025/0211045",
        rsn="Chest heaviness for 6 hours", sts="DSCH",
        adv="2026-07-12 10:30", dsch="2026-07-12 17:05",
        diags=[("I21.4", "Non-ST elevation myocardial infarction", "FINAL"),
               ("E11.9", "Type 2 diabetes mellitus without complications", "FINAL")],
        procs=[("93458", "Coronary angiography", "2026-07-09 12:00", "D01"),
               ("92928", "PTCA with drug-eluting stent to RCA", "2026-07-09 12:40", "D01")],
        labs=[("Troponin I", "2.8", "ng/mL", "<0.04", "H", "2026-07-08 23:40", "FINAL"),
              ("HbA1c", "7.9", "%", "<5.7", "H", "2026-07-09 06:30", "FINAL"),
              ("LDL Cholesterol", "128", "mg/dL", "<100", "H", "2026-07-09 06:30", "FINAL"),
              ("2D Echo LVEF", "50", "%", "55-70", "L", "2026-07-09 10:00", "FINAL")],
        meds=[("Aspirin", "75 mg", "OD", "Oral", "", "INPATIENT"),
              ("Clopidogrel", "75 mg", "OD", "Oral", "", "INPATIENT"),
              ("Heparin", "5000 IU", "QID", "SC", "2 days", "INPATIENT"),
              ("Aspirin", "75 mg", "OD", "Oral", "Lifelong", "DISCHARGE"),
              ("Clopidogrel", "75 mg", "OD", "Oral", "12 months", "DISCHARGE"),
              ("Rosuvastatin", "20 mg", "HS", "Oral", "Continue", "DISCHARGE"),
              ("Metformin", "500 mg", "BD", "Oral", "Continue", "DISCHARGE")],
        notes=[("2026-07-08 23:30", "DR", RMO, "58M, DM. Chest heaviness 6 hrs. ECG ST depression II, III, aVF. Trop I 2.8. NSTEMI."),
               ("2026-07-09 13:30", "DR", "Dr. Anjali Mehta", "CAG: RCA 90% mid lesion. PTCA + DES to RCA. LAD, LCx minor plaques."),
               ("2026-07-11 10:00", "DR", "Dr. Anjali Mehta", "Stable, ambulant. Echo LVEF 50%. Plan discharge tomorrow."),
               ("2026-07-10 20:00", "NRS", "Sr. Meena Jadhav", "Femoral site clean, no bleed. Vitals stable.")],
        docs=["ID_PROOF", "CONSENT", "CATH_RPT"],
        tpa_claim=("2026-07-12 12:40", "QUERY", "Stent implant sticker / invoice not attached", "2026-07-12 16:10"),
        summary="""Diagnosis: NSTEMI (inferior). Type 2 diabetes mellitus.
Presenting complaints: Chest heaviness for 6 hours.
Hospital course: 58 year old diabetic male admitted with chest heaviness. ECG showed ST depression in inferior leads, Troponin I 2.8. Diagnosed NSTEMI. CAG showed 90% mid RCA lesion, treated with PTCA and drug eluting stent to RCA. Post procedure uneventful. Echo LVEF 50%. Ambulant and stable at discharge.
Procedures: CAG, PTCA + DES to RCA (09/07/2026).
Investigations: Trop I 2.8 ng/mL, HbA1c 7.9%, LDL 128 mg/dL, LVEF 50%.
Condition at discharge: Stable, pain free.
Discharge medications: Tab Aspirin 75 mg OD, Tab Clopidogrel 75 mg OD x 12 months, Tab Rosuvastatin 20 mg HS, Tab Metformin 500 mg BD.
Follow-up: Cardiology OPD after 1 week. Diabetic diet. Avoid heavy exertion for 4 weeks.""",
    ),
    dict(
        ip="IP2607-0455", uhid="CC-2026-011530", name="Kavita More", age=41, sex="F",
        mob="97300 11827", addr="Pimpri, Pune",
        adm="2026-07-15 09:20", ward="3C-MED", bed="02", dr="D02",
        pay="CASH", tpa=None, pol=None,
        rsn="Loose motions and vomiting x 2 days", sts="DSCH",
        adv="2026-07-17 10:00", dsch="2026-07-17 12:20",
        diags=[("A09", "Infectious gastroenteritis and colitis", "FINAL"),
               ("E86.0", "Dehydration", "FINAL")],
        procs=[],
        labs=[("Serum Sodium", "131", "mmol/L", "135-145", "L", "2026-07-15 10:00", "FINAL"),
              ("Serum Potassium", "3.1", "mmol/L", "3.5-5.1", "L", "2026-07-15 10:00", "FINAL"),
              ("Serum Creatinine", "1.4", "mg/dL", "0.6-1.1", "H", "2026-07-15 10:00", "FINAL"),
              ("Serum Creatinine (repeat)", "0.9", "mg/dL", "0.6-1.1", "", "2026-07-16 06:30", "FINAL")],
        meds=[("Ringer lactate", "100 ml/hr", "Continuous", "IV", "", "INPATIENT"),
              ("Ondansetron", "4 mg", "TDS", "IV", "", "INPATIENT"),
              ("Oral rehydration salts", "1 sachet in 1 L water", "Sip frequently", "Oral", "3 days", "DISCHARGE"),
              ("Racecadotril", "100 mg", "TDS", "Oral", "3 days", "DISCHARGE"),
              ("Probiotic", "1 capsule", "BD", "Oral", "5 days", "DISCHARGE")],
        notes=[("2026-07-15 09:40", "DR", "Dr. Rajesh Gokhale", "41F, 12-14 loose stools/day, vomiting. Dry tongue, tachycardia. AKI prerenal. IV fluids."),
               ("2026-07-16 10:00", "DR", "Dr. Rajesh Gokhale", "Stools reduced to 3. Tolerating orally. Creat 0.9."),
               ("2026-07-16 21:00", "NRS", "Sr. Pooja More", "No vomiting since morning. Accepting soft diet.")],
        docs=["ID_PROOF"],
        summary="""Diagnosis: Acute gastroenteritis with dehydration and pre-renal AKI.
Presenting complaints: Loose motions and vomiting for 2 days.
Hospital course: 41 year old female admitted with frequent loose stools and vomiting with signs of dehydration. Sodium 131, potassium 3.1, creatinine 1.4. Treated with IV fluids, antiemetics and electrolyte correction. Creatinine normalised to 0.9. Tolerating oral diet at discharge.
Investigations: Na 131, K 3.1, Creat 1.4 -> 0.9 mg/dL.
Condition at discharge: Stable, hydrated.
Discharge medications: ORS 1 sachet in 1 L water sip frequently x 3 days, Tab Racecadotril 100 mg TDS x 3 days, Cap Probiotic BD x 5 days.
Follow-up: Medicine OPD after 5 days or earlier if symptoms recur. Boiled water, light diet.""",
    ),
    dict(
        ip="IP2607-0480", uhid="CC-2026-011802", name="Shobha Kale", age=69, sex="F",
        mob="94220 67311", addr="Warje, Pune",
        adm="2026-07-20 08:00", ward="3A-ORTH", bed="06", dr="D03",
        pay="CASHLESS", tpa="Medinsure TPA", pol="MIT/SR/2023/210556",
        rsn="Planned left total knee replacement", sts="DSCH",
        adv="2026-07-25 10:15", dsch="2026-07-25 16:50",
        diags=[("M17.1", "Primary osteoarthritis, left knee", "FINAL"),
               ("I10", "Essential (primary) hypertension", "FINAL")],
        procs=[("27447", "Left total knee arthroplasty", "2026-07-20 10:00", "D03")],
        labs=[("Haemoglobin", "10.8", "g/dL", "12-15", "L", "2026-07-21 06:30", "FINAL"),
              ("Serum Creatinine", "0.9", "mg/dL", "0.6-1.1", "", "2026-07-21 06:30", "FINAL"),
              ("X-ray left knee (post-op)", "Implant in situ, good alignment", "", "", "", "2026-07-21 10:00", "FINAL")],
        meds=[("Cefuroxime", "1.5 g", "BD", "IV", "3 days", "INPATIENT"),
              ("Enoxaparin", "40 mg", "OD", "SC", "", "INPATIENT"),
              ("Apixaban", "2.5 mg", "BD", "Oral", "14 days", "DISCHARGE"),
              ("Paracetamol", "650 mg", "TDS", "Oral", "7 days", "DISCHARGE"),
              ("Telmisartan", "40 mg", "OD", "Oral", "Continue", "DISCHARGE"),
              ("Calcium + Vitamin D3", "1 tablet", "OD", "Oral", "3 months", "DISCHARGE")],
        notes=[("2026-07-20 12:30", "DR", "Dr. Sameer Bhide", "Left TKR under spinal. Tourniquet 70 min. Uneventful."),
               ("2026-07-22 10:00", "DR", "Dr. Sameer Bhide", "Walking with walker. Knee flexion 80 degrees. Wound healthy."),
               ("2026-07-24 10:00", "DR", "Dr. Sameer Bhide", "Flexion 95 degrees. Climbing 2 steps. Fit for discharge tomorrow."),
               ("2026-07-21 18:00", "NRS", "Sr. Anita Gaikwad", "Drain removed. Physio session done twice.")],
        docs=["ID_PROOF", "CONSENT", "OT_NOTE", "IMPLANT_STKR"],
        tpa_claim=("2026-07-25 12:00", "APPROVED", None, "2026-07-25 15:45"),
        summary="""Diagnosis: Primary osteoarthritis left knee. Hypertension.
Presenting complaints: Planned admission for left TKR.
Hospital course: 69 year old female with advanced OA left knee underwent left total knee arthroplasty under spinal anaesthesia on 20/07/2026. Post-op uneventful. DVT prophylaxis given. Mobilised with walker from day 1. At discharge knee flexion 95 degrees, wound healthy. Post op Hb 10.8.
Procedures: Left total knee arthroplasty (20/07/2026).
Investigations: Hb 10.8 g/dL, creatinine 0.9, post-op X-ray satisfactory.
Condition at discharge: Stable, walking with walker.
Discharge medications: Tab Apixaban 2.5 mg BD x 14 days, Tab Paracetamol 650 mg TDS x 7 days, Tab Telmisartan 40 mg OD, Tab Calcium + D3 OD x 3 months.
Follow-up: Ortho OPD on day 14 for suture removal. Continue physiotherapy.""",
    ),
    dict(
        ip="IP2608-0105", uhid="CC-2026-012590", name="Rohan Deshmukh", age=24, sex="M",
        mob="99230 40018", addr="Wakad, Pune",
        adm="2026-08-02 22:00", ward="2B-SURG", bed="03", dr="D04",
        pay="CASHLESS", tpa="CarePlus TPA Services", pol="CPT/HL/2026/092211",
        rsn="Pain right lower abdomen x 1 day with vomiting", sts="DSCH",
        adv="2026-08-04 10:00", dsch="2026-08-04 15:30",
        diags=[("K35.8", "Acute appendicitis, other and unspecified", "FINAL")],
        procs=[("44970", "Laparoscopic appendectomy", "2026-08-03 01:30", "D04")],
        labs=[("Total Leucocyte Count", "14800", "/cumm", "4000-11000", "H", "2026-08-02 22:30", "FINAL"),
              ("USG Abdomen", "Inflamed appendix 9 mm, no collection", "", "", "", "2026-08-02 23:00", "FINAL"),
              ("Histopathology - appendix", "Acute suppurative appendicitis", "", "", "", "2026-08-04 09:00", "FINAL")],
        meds=[("Ceftriaxone", "1 g", "BD", "IV", "", "INPATIENT"),
              ("Metronidazole", "500 mg", "TDS", "IV", "", "INPATIENT"),
              ("Cefuroxime axetil", "500 mg", "BD", "Oral", "5 days", "DISCHARGE"),
              ("Paracetamol", "650 mg", "SOS pain", "Oral", "5 days", "DISCHARGE"),
              ("Pantoprazole", "40 mg", "OD", "Oral", "5 days", "DISCHARGE")],
        notes=[("2026-08-02 22:20", "DR", RMO, "24M, RIF pain, McBurney tenderness, TLC 14.8k. USG appendicitis. Surgery planned."),
               ("2026-08-03 02:30", "DR", "Dr. Neha Rao", "Lap appendectomy done. Inflamed appendix, no perforation."),
               ("2026-08-03 18:00", "NRS", "Sr. Rekha Pawar", "Passed flatus. Started liquids.")],
        docs=["ID_PROOF", "CONSENT", "OT_NOTE"],
        tpa_claim=("2026-08-04 11:30", "APPROVED", None, "2026-08-04 15:00"),
        summary="""Diagnosis: Acute appendicitis.
Presenting complaints: Right lower abdominal pain for 1 day with vomiting.
Hospital course: 24 year old male with RIF pain and tenderness, TLC 14800, USG suggestive of acute appendicitis. Underwent emergency laparoscopic appendectomy on 03/08/2026. Intra-op inflamed appendix without perforation. Post-op recovery uneventful, tolerating diet. HPE: acute suppurative appendicitis.
Procedures: Laparoscopic appendectomy (03/08/2026).
Investigations: TLC 14800, USG inflamed appendix 9 mm, HPE acute suppurative appendicitis.
Condition at discharge: Stable, port sites healthy.
Discharge medications: Tab Cefuroxime axetil 500 mg BD x 5 days, Tab Paracetamol 650 mg SOS, Tab Pantoprazole 40 mg OD x 5 days.
Follow-up: Surgery OPD after 7 days for dressing. Avoid lifting weights for 2 weeks.""",
    ),
    dict(
        ip="IP2608-0188", uhid="CC-2026-013144", name="Dattatray Jagtap", age=66, sex="M",
        mob="98814 20956", addr="Yerawada, Pune",
        adm="2026-08-11 05:30", ward="3C-MED", bed="08", dr="D02",
        pay="CASH", tpa=None, pol=None,
        rsn="Increased breathlessness and wheeze x 3 days", sts="DSCH",
        adv="2026-08-15 10:30", dsch="2026-08-15 13:10",
        diags=[("J44.1", "COPD with acute exacerbation", "FINAL")],
        procs=[],
        labs=[("Arterial pCO2", "52", "mmHg", "35-45", "H", "2026-08-11 06:00", "FINAL"),
              ("Chest X-ray", "Hyperinflated lungs, no consolidation", "", "", "", "2026-08-11 07:00", "FINAL"),
              ("Total Leucocyte Count", "11800", "/cumm", "4000-11000", "H", "2026-08-11 06:00", "FINAL")],
        meds=[("Salbutamol + Ipratropium nebulisation", "2.5 mg + 500 mcg", "QID", "Nebulised", "", "INPATIENT"),
              ("Methylprednisolone", "40 mg", "OD", "IV", "3 days", "INPATIENT"),
              ("Doxycycline", "100 mg", "BD", "Oral", "", "INPATIENT"),
              ("Tiotropium", "18 mcg", "OD", "Inhaled", "Continue", "DISCHARGE"),
              ("Budesonide + Formoterol", "200/6 mcg", "BD", "Inhaled", "Continue", "DISCHARGE"),
              ("Prednisolone", "30 mg", "OD", "Oral", "5 days", "DISCHARGE"),
              ("Doxycycline", "100 mg", "BD", "Oral", "3 days", "DISCHARGE")],
        notes=[("2026-08-11 05:50", "DR", RMO, "66M, ex-smoker, COPD. Breathless, wheeze, SpO2 86% RA, pCO2 52. Nebs, steroids, BiPAP night."),
               ("2026-08-13 10:00", "DR", "Dr. Rajesh Gokhale", "Off BiPAP. SpO2 93% RA. Wheeze reduced."),
               ("2026-08-14 20:00", "NRS", "Sr. Pooja More", "Inhaler technique taught to patient and son.")],
        docs=["ID_PROOF"],
        summary="""Diagnosis: Acute exacerbation of COPD.
Presenting complaints: Increased breathlessness and wheeze for 3 days.
Hospital course: 66 year old ex-smoker, known COPD, admitted with acute exacerbation, SpO2 86% on room air, pCO2 52. Managed with nebulised bronchodilators, IV steroids, antibiotics and night-time BiPAP. Weaned off BiPAP on day 3, SpO2 93% on room air at discharge. Inhaler technique taught.
Investigations: pCO2 52 mmHg, TLC 11800, CXR hyperinflation, no consolidation.
Condition at discharge: Stable, SpO2 93% RA.
Discharge medications: Tiotropium 18 mcg inhaler OD, Budesonide + Formoterol 200/6 inhaler BD, Tab Prednisolone 30 mg OD x 5 days, Cap Doxycycline 100 mg BD x 3 days.
Follow-up: Chest/Medicine OPD after 1 week with PFT. Pneumococcal and influenza vaccination advised.""",
    ),
    dict(
        ip="IP2608-0231", uhid="CC-2026-013610", name="Usha Pingle", age=74, sex="F",
        mob="94033 18820", addr="Bibwewadi, Pune",
        adm="2026-08-18 13:00", ward="4B-CARD", bed="09", dr="D01",
        pay="CASHLESS", tpa="SecureHealth TPA", pol="SHI/2024/0170432",
        rsn="Breathlessness and swelling of feet x 5 days", sts="DSCH",
        adv="2026-08-23 10:20", dsch="2026-08-23 18:40",
        diags=[("I50.9", "Heart failure with reduced ejection fraction", "FINAL"),
               ("N18.3", "Chronic kidney disease, stage 3", "FINAL")],
        procs=[],
        labs=[("NT-proBNP", "9200", "pg/mL", "<450", "H", "2026-08-18 14:00", "FINAL"),
              ("2D Echo LVEF", "32", "%", "55-70", "L", "2026-08-19 10:00", "FINAL"),
              ("Serum Creatinine", "1.8", "mg/dL", "0.6-1.1", "H", "2026-08-18 14:00", "FINAL"),
              ("Serum Potassium", "4.9", "mmol/L", "3.5-5.1", "", "2026-08-21 06:30", "FINAL")],
        meds=[("Furosemide", "40 mg", "BD", "IV", "", "INPATIENT"),
              ("Metoprolol succinate", "12.5 mg", "OD", "Oral", "", "INPATIENT"),
              ("Furosemide", "40 mg", "OD", "Oral", "Continue", "DISCHARGE"),
              ("Metoprolol succinate", "25 mg", "OD", "Oral", "Continue", "DISCHARGE"),
              ("Dapagliflozin", "10 mg", "OD", "Oral", "Continue", "DISCHARGE"),
              ("Spironolactone", "12.5 mg", "OD", "Oral", "Continue", "DISCHARGE")],
        notes=[("2026-08-18 13:30", "DR", "Dr. Anjali Mehta", "74F, HFrEF, CKD3. Orthopnoea, pedal oedema, basal crepts. IV diuretics. Fluid restriction 1.5 L."),
               ("2026-08-21 10:00", "DR", "Dr. Anjali Mehta", "Weight down 3.8 kg. Creat stable 1.7. Start dapagliflozin, low dose spironolactone."),
               ("2026-08-22 20:00", "NRS", "Sr. Meena Jadhav", "Daily weight chart explained to daughter.")],
        docs=["ID_PROOF", "CONSENT"],
        tpa_claim=("2026-08-23 13:30", "QUERY", "Final diagnosis does not match provisional diagnosis at pre-auth; clarify CKD", "2026-08-23 18:00"),
        summary="""Diagnosis: Acute decompensated heart failure (HFrEF, LVEF 32%). CKD stage 3.
Presenting complaints: Breathlessness and pedal oedema for 5 days.
Hospital course: 74 year old female with HFrEF and CKD admitted with decompensated heart failure. NT-proBNP 9200. Treated with IV furosemide and fluid restriction, 3.8 kg weight loss. Creatinine stable around 1.7-1.8. Guideline directed therapy optimised with dapagliflozin and spironolactone. Potassium 4.9 prior to discharge.
Investigations: NT-proBNP 9200 pg/mL, LVEF 32%, creatinine 1.8 mg/dL, K 4.9.
Condition at discharge: Stable, no orthopnoea.
Discharge medications: Tab Furosemide 40 mg OD, Tab Metoprolol succinate 25 mg OD, Tab Dapagliflozin 10 mg OD, Tab Spironolactone 12.5 mg OD.
Follow-up: Cardiology OPD after 1 week with serum creatinine and potassium. Daily weight, fluid restriction 1.5 L/day, low salt diet.""",
    ),
    dict(
        ip="IP2608-0276", uhid="CC-2026-014022", name="Pooja Salunkhe", age=33, sex="F",
        mob="98600 33491", addr="Dhanori, Pune",
        adm="2026-08-24 16:40", ward="3C-MED", bed="05", dr="D02",
        pay="CASH", tpa=None, pol=None,
        rsn="Fever with chills and burning micturition x 3 days, right flank pain", sts="DSCH",
        adv="2026-08-27 10:00", dsch="2026-08-27 12:45",
        diags=[("N10", "Acute pyelonephritis", "FINAL")],
        procs=[],
        labs=[("Urine routine", "Pus cells 40-50/hpf", "", "0-5/hpf", "H", "2026-08-24 17:00", "FINAL"),
              ("Urine culture", "E. coli, sensitive to ceftriaxone, nitrofurantoin", "", "", "", "2026-08-26 10:00", "FINAL"),
              ("Total Leucocyte Count", "15200", "/cumm", "4000-11000", "H", "2026-08-24 17:00", "FINAL")],
        meds=[("Ceftriaxone", "1 g", "BD", "IV", "", "INPATIENT"),
              ("Paracetamol", "650 mg", "SOS fever", "Oral", "", "INPATIENT"),
              ("Cefixime", "200 mg", "BD", "Oral", "7 days", "DISCHARGE"),
              ("Paracetamol", "650 mg", "SOS fever", "Oral", "3 days", "DISCHARGE")],
        notes=[("2026-08-24 17:10", "DR", "Dr. Rajesh Gokhale", "33F, fever with chills, R renal angle tenderness. Urine pus cells++. Pyelonephritis. IV ceftriaxone."),
               ("2026-08-26 10:00", "DR", "Dr. Rajesh Gokhale", "Afebrile 36 hrs. Culture E. coli sensitive. Plan oral step-down."),
               ("2026-08-25 21:00", "NRS", "Sr. Rekha Pawar", "Encouraged oral fluids > 3 L/day.")],
        docs=["ID_PROOF"],
        summary="""Diagnosis: Acute pyelonephritis (E. coli).
Presenting complaints: Fever with chills, burning micturition and right flank pain for 3 days.
Hospital course: 33 year old female admitted with features of right sided pyelonephritis. TLC 15200, urine pus cells 40-50/hpf. Treated with IV ceftriaxone. Urine culture grew E. coli sensitive to ceftriaxone. Afebrile for 36 hours, switched to oral antibiotics.
Investigations: TLC 15200, urine pus cells 40-50/hpf, urine culture E. coli.
Condition at discharge: Afebrile, stable.
Discharge medications: Tab Cefixime 200 mg BD x 7 days, Tab Paracetamol 650 mg SOS.
Follow-up: Medicine OPD after 1 week with repeat urine routine. Oral fluids 3 L/day.""",
    ),
    dict(
        ip="IP2609-0021", uhid="CC-2026-014817", name="Meera Thakur", age=44, sex="F",
        mob="97667 02145", addr="Kharadi, Pune",
        adm="2026-09-03 07:00", ward="2B-SURG", bed="02", dr="D04",
        pay="CASHLESS", tpa="Medinsure TPA", pol="MIT/HL/2025/403318",
        rsn="Recurrent epigastric and right upper abdominal pain after fatty meals", sts="DSCH",
        adv="2026-09-05 10:00", dsch="2026-09-05 17:20",
        diags=[("K80.2", "Calculus of gallbladder without cholecystitis", "FINAL")],
        procs=[("47562", "Laparoscopic cholecystectomy", "2026-09-03 11:00", "D04")],
        labs=[("USG Abdomen", "Cholelithiasis, largest calculus 14 mm, CBD 5 mm", "", "", "", "2026-08-28 10:00", "FINAL"),
              ("Liver Function Test", "Within normal limits", "", "", "", "2026-09-03 06:30", "FINAL"),
              ("Histopathology - gallbladder", "", "", "", "", "2026-09-03 13:00", "PENDING")],
        meds=[("Ceftriaxone", "1 g", "OD", "IV", "1 day", "INPATIENT"),
              ("Paracetamol", "1 g", "TDS", "IV", "", "INPATIENT"),
              ("Paracetamol", "650 mg", "TDS", "Oral", "5 days", "DISCHARGE"),
              ("Pantoprazole", "40 mg", "OD", "Oral", "7 days", "DISCHARGE")],
        notes=[("2026-09-03 12:30", "DR", "Dr. Neha Rao", "Lap chole done. GB with multiple calculi. Sent for HPE."),
               ("2026-09-04 10:00", "DR", "Dr. Neha Rao", "Tolerating soft diet. Mild port site pain."),
               ("2026-09-04 19:00", "NRS", "Sr. Rekha Pawar", "Ambulating. Port site dressing dry.")],
        docs=["ID_PROOF", "CONSENT"],
        tpa_claim=("2026-09-05 12:10", "QUERY", "Operation notes not attached; HPE report status to be mentioned", "2026-09-05 16:55"),
        summary="""Diagnosis: Symptomatic cholelithiasis.
Presenting complaints: Recurrent right upper abdominal pain after fatty meals.
Hospital course: 44 year old female with USG proven cholelithiasis underwent elective laparoscopic cholecystectomy on 03/09/2026. Intra-op gallbladder with multiple calculi. Post-op uneventful, tolerating diet.
Procedures: Laparoscopic cholecystectomy (03/09/2026).
Investigations: USG cholelithiasis (14 mm), LFT normal. Histopathology report awaited.
Condition at discharge: Stable, port sites healthy.
Discharge medications: Tab Paracetamol 650 mg TDS x 5 days, Tab Pantoprazole 40 mg OD x 7 days.
Follow-up: Surgery OPD after 7 days with HPE report. Low fat diet for 4 weeks.""",
    ),
    dict(
        ip="IP2609-0064", uhid="CC-2026-015302", name="Gangubai Shinde", age=79, sex="F",
        mob="98509 44127", addr="Kasba Peth, Pune",
        adm="2026-09-08 18:30", ward="3A-ORTH", bed="04", dr="D03",
        pay="CASHLESS", tpa="CarePlus TPA Services", pol="CPT/SR/2022/067701",
        rsn="Fall at home, unable to bear weight on right leg", sts="DSCH",
        adv="2026-09-14 10:10", dsch="2026-09-14 16:30",
        diags=[("S72.0", "Fracture of neck of femur, right", "FINAL"),
               ("M81.0", "Postmenopausal osteoporosis", "FINAL")],
        procs=[("27125", "Right hip hemiarthroplasty", "2026-09-09 11:00", "D03")],
        labs=[("X-ray right hip", "Displaced subcapital fracture neck of femur", "", "", "", "2026-09-08 19:00", "FINAL"),
              ("Haemoglobin", "9.6", "g/dL", "12-15", "L", "2026-09-10 06:30", "FINAL"),
              ("Vitamin D (25-OH)", "11", "ng/mL", "30-100", "L", "2026-09-10 06:30", "FINAL")],
        meds=[("Cefuroxime", "1.5 g", "BD", "IV", "3 days", "INPATIENT"),
              ("Enoxaparin", "40 mg", "OD", "SC", "", "INPATIENT"),
              ("Packed red cells", "1 unit", "Once", "IV", "", "INPATIENT"),
              ("Apixaban", "2.5 mg", "BD", "Oral", "28 days", "DISCHARGE"),
              ("Paracetamol", "500 mg", "TDS", "Oral", "7 days", "DISCHARGE"),
              ("Cholecalciferol", "60000 IU", "Once weekly", "Oral", "8 weeks", "DISCHARGE"),
              ("Calcium carbonate", "500 mg", "BD", "Oral", "3 months", "DISCHARGE")],
        notes=[("2026-09-08 19:10", "DR", RMO, "79F, fall at home, R leg shortened and externally rotated. X-ray: displaced # NOF."),
               ("2026-09-09 13:30", "DR", "Dr. Sameer Bhide", "R hip bipolar hemiarthroplasty. EBL 400 ml. Stable."),
               ("2026-09-10 11:00", "DR", "Dr. Sameer Bhide", "Hb 9.6, transfused 1 unit PRBC. Vit D 11, start supplementation."),
               ("2026-09-13 10:00", "DR", "Dr. Sameer Bhide", "Walking with walker and assistance. Fit for discharge tomorrow."),
               ("2026-09-12 18:00", "NRS", "Sr. Anita Gaikwad", "Pressure areas checked, no sores. Family trained on transfers.")],
        docs=["ID_PROOF", "CONSENT", "OT_NOTE", "IMPLANT_STKR"],
        tpa_claim=("2026-09-14 12:00", "APPROVED", None, "2026-09-14 16:00"),
        summary="""Diagnosis: Fracture neck of right femur (displaced subcapital). Osteoporosis. Vitamin D deficiency.
Presenting complaints: Fall at home, unable to bear weight on right leg.
Hospital course: 79 year old female sustained a fall at home. X-ray showed displaced subcapital fracture neck of right femur. Underwent right hip bipolar hemiarthroplasty on 09/09/2026. Post-op Hb 9.6, transfused 1 unit PRBC. Vitamin D 11, supplementation started. Mobilised with walker and assistance.
Procedures: Right hip hemiarthroplasty (09/09/2026).
Investigations: Hb 9.6 g/dL, Vitamin D 11 ng/mL.
Condition at discharge: Stable, walking with walker and support.
Discharge medications: Tab Apixaban 2.5 mg BD x 28 days, Tab Paracetamol 500 mg TDS x 7 days, Cholecalciferol 60000 IU once weekly x 8 weeks, Tab Calcium carbonate 500 mg BD x 3 months.
Follow-up: Ortho OPD on day 14 for suture removal. Fall prevention at home. Continue physiotherapy.""",
    ),
    dict(
        ip="IP2609-0092", uhid="CC-2026-015760", name="Nikhil Wagh", age=27, sex="M",
        mob="90280 61174", addr="Hinjewadi, Pune",
        adm="2026-09-12 12:00", ward="3C-MED", bed="10", dr="D02",
        pay="CASH", tpa=None, pol=None,
        rsn="Fever, headache and body ache x 3 days", sts="DSCH",
        adv="2026-09-16 10:00", dsch="2026-09-16 12:15",
        diags=[("A97.0", "Dengue without warning signs", "FINAL")],
        procs=[],
        labs=[("NS1 Antigen", "Positive", "", "Negative", "H", "2026-09-12 12:30", "FINAL"),
              ("Platelet Count", "62000", "/cumm", "150000-450000", "L", "2026-09-13 06:30", "FINAL"),
              ("Platelet Count (repeat)", "118000", "/cumm", "150000-450000", "L", "2026-09-16 06:30", "FINAL"),
              ("SGPT", "96", "U/L", "<40", "H", "2026-09-13 06:30", "FINAL")],
        meds=[("Paracetamol", "650 mg", "TDS", "Oral", "", "INPATIENT"),
              ("Normal saline", "75 ml/hr", "Continuous", "IV", "", "INPATIENT"),
              ("Paracetamol", "650 mg", "SOS fever", "Oral", "3 days", "DISCHARGE"),
              ("Oral rehydration salts", "1 sachet in 1 L water", "Sip frequently", "Oral", "3 days", "DISCHARGE")],
        notes=[("2026-09-12 12:20", "DR", "Dr. Rajesh Gokhale", "27M, fever 3 days, NS1+, no warning signs, poor oral intake. Admit for IV fluids."),
               ("2026-09-15 10:00", "DR", "Dr. Rajesh Gokhale", "Afebrile 48 hrs. Platelets rising. Discharge tomorrow."),
               ("2026-09-14 20:00", "NRS", "Sr. Pooja More", "No bleeding manifestations. Oral intake improved.")],
        docs=["ID_PROOF"],
        summary="""Diagnosis: Dengue fever without warning signs.
Presenting complaints: Fever, headache and body ache for 3 days.
Hospital course: 27 year old male with NS1 positive dengue admitted for poor oral intake. Platelet nadir 62000, SGPT 96. Managed with IV fluids and paracetamol. No bleeding. Afebrile for 48 hours with platelets rising to 118000 at discharge.
Investigations: NS1 positive, platelets 62000 -> 118000, SGPT 96 U/L.
Condition at discharge: Afebrile, stable.
Discharge medications: Tab Paracetamol 650 mg SOS, ORS 1 sachet in 1 L water x 3 days.
Follow-up: Medicine OPD after 3 days with CBC. Avoid NSAIDs. Plenty of oral fluids.""",
    ),
    dict(
        ip="IP2609-0118", uhid="CC-2026-016233", name="Harish Gaikwad", age=63, sex="M",
        mob="97640 58831", addr="Pashan, Pune",
        adm="2026-09-15 04:20", ward="4B-CARD", bed="10", dr="D01",
        pay="CASHLESS", tpa="Medinsure TPA", pol="MIT/SR/2025/288170",
        rsn="Severe chest pain with sweating x 1 hour", sts="DSCH",
        adv="2026-09-19 10:40", dsch="2026-09-19 17:55",
        diags=[("I21.1", "Acute ST-elevation myocardial infarction, inferior wall", "FINAL"),
               ("I10", "Essential (primary) hypertension", "FINAL")],
        procs=[("93458", "Coronary angiography", "2026-09-15 05:10", "D01"),
               ("92928", "Primary PTCA with drug-eluting stent to RCA", "2026-09-15 05:30", "D01")],
        labs=[("Troponin I", "8.6", "ng/mL", "<0.04", "H", "2026-09-15 04:40", "FINAL"),
              ("2D Echo LVEF", "48", "%", "55-70", "L", "2026-09-16 10:00", "FINAL"),
              ("LDL Cholesterol", "144", "mg/dL", "<100", "H", "2026-09-16 06:30", "FINAL"),
              ("Serum Creatinine", "1.0", "mg/dL", "0.7-1.3", "", "2026-09-15 04:40", "FINAL")],
        meds=[("Aspirin", "325 mg stat, then 75 mg", "OD", "Oral", "", "INPATIENT"),
              ("Prasugrel", "60 mg stat, then 10 mg", "OD", "Oral", "", "INPATIENT"),
              ("Heparin", "5000 IU", "QID", "SC", "2 days", "INPATIENT"),
              ("Aspirin", "75 mg", "OD", "Oral", "Lifelong", "DISCHARGE"),
              ("Prasugrel", "10 mg", "OD", "Oral", "12 months", "DISCHARGE"),
              ("Atorvastatin", "80 mg", "HS", "Oral", "Continue", "DISCHARGE"),
              ("Metoprolol succinate", "25 mg", "OD", "Oral", "Continue", "DISCHARGE"),
              ("Telmisartan", "40 mg", "OD", "Oral", "Continue", "DISCHARGE")],
        notes=[("2026-09-15 04:35", "DR", RMO, "63M, HTN. Severe chest pain 1 hr. ECG ST elevation II, III, aVF. Inferior STEMI. Cath lab activated."),
               ("2026-09-15 06:30", "DR", "Dr. Anjali Mehta", "Primary PCI: RCA proximal total occlusion, DES deployed, TIMI III. Temp pacing not needed."),
               ("2026-09-17 10:00", "DR", "Dr. Anjali Mehta", "Stable, pain free. LVEF 48%. Shift to ward."),
               ("2026-09-18 18:00", "NRS", "Sr. Meena Jadhav", "Ambulating. Cardiac diet education done.")],
        docs=["ID_PROOF", "CONSENT", "CATH_RPT"],
        tpa_claim=("2026-09-19 13:20", "QUERY", "Stent implant sticker / invoice not attached", "2026-09-19 17:30"),
        summary="""Diagnosis: Acute inferior wall STEMI. Hypertension.
Presenting complaints: Severe chest pain with sweating for 1 hour.
Hospital course: 63 year old hypertensive male presented with inferior STEMI, Trop I 8.6. Primary PCI done: proximal RCA total occlusion treated with DES, TIMI III flow. Post PCI stable, no arrhythmias. Echo LVEF 48%. Ambulant at discharge.
Procedures: CAG, primary PTCA + DES to RCA (15/09/2026).
Investigations: Trop I 8.6 ng/mL, LVEF 48%, LDL 144 mg/dL, creatinine 1.0.
Condition at discharge: Stable, pain free.
Discharge medications: Tab Aspirin 75 mg OD, Tab Prasugrel 10 mg OD x 12 months, Tab Atorvastatin 80 mg HS, Tab Metoprolol succinate 25 mg OD, Tab Telmisartan 40 mg OD.
Follow-up: Cardiology OPD after 1 week. Cardiac rehab. Stop smoking. Low fat low salt diet.""",
    ),
]

# ---------------------------------------------------------------------------
# Generator settings for ~3 months of MIS-level historic admissions
# (timestamps only - used for discharge TAT / TPA query-rate baseline)
# ---------------------------------------------------------------------------
HISTORIC_COUNT = 140
HISTORIC_FIRST_NAMES = ["Anil", "Sunil", "Rekha", "Manisha", "Prakash", "Vaishali", "Ganesh", "Swati", "Mahesh",
                        "Sneha", "Ajay", "Deepa", "Santosh", "Asha", "Nitin", "Jyoti", "Rahul", "Smita", "Vijay", "Rupali"]
HISTORIC_LAST_NAMES = ["Pawar", "Jadhav", "Shinde", "Chavan", "Kadam", "Mane", "Gaikwad", "Deshpande", "Joshi",
                       "Kulkarni", "Patil", "More", "Sawant", "Bhosale", "Naik", "Salve"]
TPA_NAMES = ["SecureHealth TPA", "CarePlus TPA Services", "Medinsure TPA"]
TPA_QUERY_REASONS = [
    "Stent implant sticker / invoice not attached",
    "Investigation reports not attached",
    "Final diagnosis does not match provisional diagnosis at pre-auth",
    "Operation notes not attached",
    "Treating doctor registration number missing",
    "Pending report status not mentioned in discharge summary",
]
