"""One-off export prepared with Suresh (hospital IT): past discharges that have a doctor-written
summary, read through IT's read-only MIS reporting login and de-identified before leaving the hospital network.

Usage: python -m poc.export_deidentified
"""
import json
from pathlib import Path

from copilot_core.encounter import connect_mis, deidentify, load_encounter

OUT = Path(__file__).resolve().parent / "data" / "deidentified_encounters.json"


def main() -> None:
    conn = connect_mis()   # read-only: SELECT on the mis views only
    ips = [r["IP_NO"] for r in conn.execute(
        "SELECT a.IP_NO FROM IP_ADM_DTL a JOIN IP_DSCH_SUMM s ON s.IP_NO = a.IP_NO "
        "WHERE a.STS = 'DSCH' ORDER BY a.DSCH_DT")]
    encounters = [deidentify(load_encounter(conn, ip), f"ENC-{i:02d}").model_dump() for i, ip in enumerate(ips, 1)]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(encounters, indent=1))
    print(f"Exported {len(encounters)} de-identified encounters -> {OUT}")


if __name__ == "__main__":
    main()
