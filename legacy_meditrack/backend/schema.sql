-- MediTrack HMS v3.2 schema (Medisoft Solutions Pvt. Ltd., 2011)
-- NOTE: original vendor documentation lost. Column meanings reverse-engineered by S. Pawar (IT), 2019.

CREATE TABLE DR_MST (          -- doctor master
    DR_ID      TEXT PRIMARY KEY,
    DR_NM      TEXT,
    DR_SPCL    TEXT,           -- speciality
    DR_REG_NO  TEXT            -- medical council registration no.
);

CREATE TABLE PT_MST (          -- patient master
    PT_ID    INTEGER PRIMARY KEY,
    UHID     TEXT UNIQUE,      -- unique hospital id
    PT_NM    TEXT,
    PT_AGE   INTEGER,
    PT_SEX   TEXT,
    PT_MOB   TEXT,
    PT_ADDR  TEXT
);

CREATE TABLE IP_ADM_DTL (      -- in-patient admission
    IP_NO        TEXT PRIMARY KEY,
    PT_ID        INTEGER,
    ADM_DT       TEXT,
    WRD_CD       TEXT,
    BED_NO       TEXT,
    DR_ID        TEXT,         -- treating consultant
    PAY_MODE     TEXT,         -- CASH | CASHLESS
    TPA_NM       TEXT,
    POL_NO       TEXT,
    ADM_RSN      TEXT,
    STS          TEXT,         -- ADM = admitted, DA = discharge advised, DSCH = discharged
    DSCH_ADV_DT  TEXT,
    DSCH_DT      TEXT
);

CREATE TABLE IP_DIAG_DTL (
    ID         INTEGER PRIMARY KEY,
    IP_NO      TEXT,
    ICD_CD     TEXT,
    DIAG_DESC  TEXT,
    DIAG_TYP   TEXT            -- PROV | FINAL
);

CREATE TABLE IP_PROC_DTL (
    ID         INTEGER PRIMARY KEY,
    IP_NO      TEXT,
    PROC_CD    TEXT,           -- CPT code
    PROC_DESC  TEXT,
    PROC_DT    TEXT,
    SURGEON    TEXT
);

CREATE TABLE LAB_RSLT (        -- fed by LIS over HL7 v2 (ORU^R01)
    ID        INTEGER PRIMARY KEY,
    IP_NO     TEXT,
    TST_NM    TEXT,
    RSLT_VAL  TEXT,
    UOM       TEXT,
    REF_RNG   TEXT,
    FLG       TEXT,            -- H | L | blank
    RSLT_DT   TEXT,
    STS       TEXT             -- FINAL | PENDING
);

CREATE TABLE PHR_ISS_DTL (     -- pharmacy issue
    ID       INTEGER PRIMARY KEY,
    IP_NO    TEXT,
    DRUG_NM  TEXT,
    DOSE     TEXT,
    FREQ     TEXT,
    ROUTE    TEXT,
    DUR      TEXT,
    ISS_TYP  TEXT              -- INPATIENT | DISCHARGE
);

CREATE TABLE CLN_NOTE (        -- clinical notes, free text
    ID        INTEGER PRIMARY KEY,
    IP_NO     TEXT,
    NOTE_DT   TEXT,
    NOTE_TYP  TEXT,            -- DR | NRS
    AUTH      TEXT,
    NOTE_TXT  TEXT
);

CREATE TABLE PT_DOC (          -- scanned / uploaded documents
    DOC_ID   INTEGER PRIMARY KEY,
    IP_NO    TEXT,
    DOC_TYP  TEXT,             -- CATH_RPT | IMPLANT_STKR | OT_NOTE | CONSENT | ID_PROOF | DSCH_SUMM | ...
    FILE_NM  TEXT,
    UPL_DT   TEXT,
    UPL_BY   TEXT
);

CREATE TABLE IP_DSCH_SUMM (    -- manually typed discharge summary
    IP_NO    TEXT PRIMARY KEY,
    SUMM_TXT TEXT,
    CRT_BY   TEXT,
    CRT_DT   TEXT
);

CREATE TABLE TPA_CLM_DTL (     -- insurer final-approval submissions
    ID       INTEGER PRIMARY KEY,
    IP_NO    TEXT,
    SUBM_DT  TEXT,
    CLM_STS  TEXT,             -- APPROVED | QUERY
    QRY_RSN  TEXT,
    APPR_DT  TEXT
);

CREATE TABLE SYS_EXT_LNK (     -- admin-configurable external links (added v3.1, 2016)
    LNK_ID   INTEGER PRIMARY KEY,
    LNK_LBL  TEXT,
    LNK_URL  TEXT,             -- {IP_NO} and {UHID} placeholders supported
    IS_ACTV  INTEGER,
    CRT_BY   TEXT,
    CRT_DT   TEXT
);

CREATE TABLE SYS_AUDIT (
    ID    INTEGER PRIMARY KEY,
    TS    TEXT,
    USR   TEXT,
    ACTN  TEXT,
    REF   TEXT
);
