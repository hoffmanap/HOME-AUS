"""
Austin permits + MLS pipeline -- FINAL INTEGRATED VERSION
=============================================================
Install: pip install pandas requests rapidfuzz openpyxl --break-system-packages

Changes in this version vs. earlier ones:
1. HOME flag now PRIMARILY sourced from validated Plan Review Cases (n8ck-xkda),
   matched against real DSD/KXAN ground truth at 78% (206/264). The old
   zoning+lot-size inference is now a FALLBACK for permits not covered by the
   direct PR-case match, tagged with lower confidence accordingly.
2. Fixed date-filter bug: PR case pull no longer restricts to applied_date >=
   HOME_PHASE1_DATE, since ~27 of the ground-truth misses were pre-2024
   applications that later opted into HOME under the city's own opt-in
   provision -- filtering by date excluded them incorrectly.
3. Added a unit-count sanity filter: housing_units > 10 with no
   total_new_add_sqft is very likely the BUILDING's total unit count on a
   repair/facade permit, not units actually added (confirmed via the 360
   Nueces St high-rise case -- 432 units, zero new sqft, description was a
   balcony repair). These are now excluded from the unit-adding permit set.
4. has_rezoning_case is now wired (previously stubbed) via the zoning cases
   dataset (edir-dcnf), completing the SB840 exclusion logic.
"""

import os
import re
import time
import pandas as pd
import requests
from rapidfuzz import fuzz, process

SOCRATA_BASE = "https://data.austintexas.gov/resource"


def _get_with_retry(url, params, max_retries=6, timeout=120):
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"  Request failed ({type(e).__name__}: {e}), retrying in {wait}s (attempt {attempt+1}/{max_retries})...")
            time.sleep(wait)


def normalize_address(addr):
    if pd.isna(addr) or not addr:
        return ""
    addr = str(addr).upper().strip()
    repl = {
        r"\bSTREET\b": "ST", r"\bAVENUE\b": "AVE", r"\bBOULEVARD\b": "BLVD",
        r"\bDRIVE\b": "DR", r"\bROAD\b": "RD", r"\bLANE\b": "LN",
        r"\bCOURT\b": "CT", r"\bCIRCLE\b": "CIR", r"\bPARKWAY\b": "PKWY",
        r"\bNORTH\b": "N", r"\bSOUTH\b": "S", r"\bEAST\b": "E", r"\bWEST\b": "W",
        r"\bBLDG\b.*$": "", r"\bBLK\b.*$": "",
        r"#\s*\w+.*$": "",
        r"[.,]": "",
    }
    for pat, sub in repl.items():
        addr = re.sub(pat, sub, addr)
    return re.sub(r"\s+", " ", addr).strip()


# ---------------------------------------------------------------------
# 1. PERMITS
# ---------------------------------------------------------------------
def pull_permits(start_date="2019-01-01", checkpoint_file="permits_checkpoint.csv"):
    """
    permittype = 'BP' only (excludes EP/MP/PP/DS trade sub-permits that copy
    housing_units metadata without adding units). No permit_class_mapped
    restriction (triplex/fourplex/apartments are coded Commercial in Austin's
    system, not Residential). housing_units > 0 is the core "adds units"
    signal, refined further downstream by the unit-count sanity filter.
    """
    url = f"{SOCRATA_BASE}/3syk-w9eu.json"
    params = {
        "$limit": 25000,
        "$select": (
            "permittype,permit_type_desc,permit_class_mapped,permit_class,work_class,"
            "housing_units,issue_date,calendar_year_issued,"
            "original_address1,original_zip,council_district,jurisdiction,"
            "latitude,longitude,description,total_new_add_sqft,"
            "total_job_valuation,tcad_id,status_current"
        ),
        "$where": (
            "permittype = 'BP' "
            "AND housing_units > 0 "
            "AND work_class NOT IN ('Demolition', 'Repair') "
            f"AND issue_date >= '{start_date}T00:00:00.000'"
        ),
        "$order": "issue_date",
    }

    rows = []
    offset = 0
    if os.path.exists(checkpoint_file):
        existing = pd.read_csv(checkpoint_file)
        rows = existing.to_dict("records")
        offset = len(rows)
        print(f"  Resuming from checkpoint: {offset} permits already saved")

    while True:
        params["$offset"] = offset
        try:
            resp = _get_with_retry(url, params)
        except requests.exceptions.RequestException:
            print(f"  Failed after all retries at offset {offset}. Progress saved to {checkpoint_file}.")
            pd.DataFrame(rows).to_csv(checkpoint_file, index=False)
            raise
        batch = resp.json()
        if not batch:
            break
        rows.extend(batch)
        offset += len(batch)
        print(f"  ...{offset} permits pulled so far")
        pd.DataFrame(rows).to_csv(checkpoint_file, index=False)
        if len(batch) < params["$limit"]:
            break

    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)

    df = pd.DataFrame(rows)
    for col in ["housing_units", "latitude", "longitude", "total_new_add_sqft", "total_job_valuation"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["issue_date"] = pd.to_datetime(df["issue_date"], errors="coerce")
    df["is_full_purpose"] = df["jurisdiction"].str.contains("FULL PURPOSE", na=False)

    # Unit-count sanity filter: a permit claiming >10 units with zero new square
    # footage almost certainly reports the BUILDING's total unit count (e.g. on a
    # repair/facade permit for an existing tower), not units it actually adds.
    # Confirmed on 360 Nueces St: housing_units=432, total_new_add_sqft=NaN,
    # description="Repairs to concrete balcony edges" -- clearly not unit-adding.
    before = len(df)
    suspicious = (df["housing_units"] > 10) & (df["total_new_add_sqft"].isna())
    print(f"  Excluding {suspicious.sum()} permits ({df.loc[suspicious, 'original_address1'].nunique()} unique addresses) "
          f"that report >10 units with no new square footage (likely building-total, not units-added)")
    df = df[~suspicious].copy()
    print(f"  Permits after sanity filter: {len(df)} (was {before})")

    return df


# ---------------------------------------------------------------------
# 2. ZONING (address-keyed, no spatial join needed)
# ---------------------------------------------------------------------
def pull_zoning_by_address():
    url = f"{SOCRATA_BASE}/nbzi-qabm.json"
    params = {"$limit": 25000}
    rows = []
    offset = 0
    while True:
        params["$offset"] = offset
        resp = _get_with_retry(url, params)
        batch = resp.json()
        if not batch:
            break
        rows.extend(batch)
        offset += len(batch)
        print(f"  ...{offset} zoning records pulled so far")
        if len(batch) < params["$limit"]:
            break

    df = pd.DataFrame(rows)
    df.columns = [c.lower() for c in df.columns]

    ztype_col = next((c for c in df.columns if "ztype" in c or ("zoning" in c and "type" in c)), None)
    base_col = next((c for c in df.columns if c == "base_zone"), None)
    if ztype_col is None or base_col is None:
        raise KeyError(f"Could not find expected zoning columns. Available columns: {list(df.columns)}")

    df["has_vmu"] = df[ztype_col].str.contains(r"-V(?:-|$)", regex=True, na=False)
    df["has_pud"] = df[ztype_col].str.contains("PUD", na=False)
    df["has_conditional_overlay"] = df[ztype_col].str.contains("-CO", na=False)
    df["has_overlay_or_pud"] = df["has_vmu"] | df["has_pud"] | df["has_conditional_overlay"]
    df = df.rename(columns={base_col: "BASE_ZONE", ztype_col: "ZONING_ZTYPE"})
    return df


def pull_zoning_cases():
    """Rezoning / CUP case history -- now actually wired into flag_sb840 exclusion."""
    url = f"{SOCRATA_BASE}/edir-dcnf.json"
    params = {"$limit": 25000}
    rows = []
    offset = 0
    while True:
        params["$offset"] = offset
        resp = _get_with_retry(url, params)
        batch = resp.json()
        if not batch:
            break
        rows.extend(batch)
        offset += len(batch)
        print(f"  ...{offset} zoning case records pulled so far")
        if len(batch) < params["$limit"]:
            break
    df = pd.DataFrame(rows)
    df.columns = [c.lower() for c in df.columns]
    print(f"  Zoning cases columns available: {list(df.columns)}")
    addr_col = next(
        (c for c in df.columns if any(kw in c for kw in ["address", "street", "location", "site", "project_addr"])),
        None
    )
    if addr_col is None:
        print(f"  WARNING: no address-like column found in zoning cases (see column list above). "
              f"has_rezoning_case will be all False -- SB840 exclusion logic will not filter anything out "
              f"until this is fixed with the real column name.")
        return pd.DataFrame(columns=["addr_norm"])
    print(f"  Using '{addr_col}' as the zoning case address column")
    # site_address is a compound field, e.g. "1804 ULIT AVENUE, TX, Austin, 78702" --
    # take only the street portion (before the first comma) so it can exact-match
    # against permits' plain "1804 ULIT AVENUE" style original_address1 after
    # normalization. Without this, isin() below would never match anything, since
    # the full compound string normalizes to something permits' address never equals.
    street_only = df[addr_col].astype(str).str.split(",").str[0]
    df["addr_norm"] = street_only.apply(normalize_address)
    return df


# ---------------------------------------------------------------------
# 3. HOME -- validated Plan Review Cases pull (PRIMARY source)
# ---------------------------------------------------------------------
HOME_DIRECT_MATCH_SUBTYPES = [
    "R- 103 Two Family Bldgs",          # duplex -- strong HOME Phase 1 signal
    "R- 104 Three & Four Family Bldgs", # triplex/fourplex -- strong HOME Phase 1 signal
]
# R- 101 Single Family Houses is deliberately EXCLUDED from direct address matching.
# It's the generic plan-review category used for EVERY new single-family home in
# Austin, not just HOME cases -- including it without a date filter caused a false-
# positive explosion (14,100 "matches" on a production run, versus the true ~264
# case ground truth). Phase 2 small-lot single-family cases are still covered via
# the lot-size-based flag_home_inferred() fallback instead, which requires an
# actual sub-pre-HOME-minimum lot size, not just the generic use category.


def pull_home_plan_review_cases():
    """
    Pulls only R-103 (duplex) and R-104 (triplex/fourplex) -- the two sub_types
    strong enough to use for direct address matching. R-101 (single family) is
    deliberately excluded: it's the generic category for every new SF home in
    Austin, and including it without a narrow date/context filter caused a
    14,100-record false-positive explosion on the first production run (true
    ground truth is ~264 cases). Phase 2 small-lot SF cases are handled by the
    TCAD-lot-size-based flag_home_inferred() fallback instead.

    Validated against 264 real KXAN/DSD-confirmed HOME cases: this narrower
    pull will have LOWER raw match count than the earlier 78% test (which used
    all 4 sub_types), but should have far higher precision. Re-validate against
    home_ground_truth.csv if you want the updated recall number.
    """
    url = f"{SOCRATA_BASE}/n8ck-xkda.json"
    subtype_clause = " OR ".join([f"sub_type = '{s}'" for s in HOME_DIRECT_MATCH_SUBTYPES])
    params = {"$where": subtype_clause, "$limit": 25000}

    rows = []
    offset = 0
    while True:
        params["$offset"] = offset
        resp = _get_with_retry(url, params)
        batch = resp.json()
        if not batch:
            break
        rows.extend(batch)
        offset += len(batch)
        print(f"  ...{offset} PR cases pulled so far")
        if len(batch) < params["$limit"]:
            break

    df = pd.DataFrame(rows)
    print(f"Total HOME-relevant (R-103/R-104) Plan Review Cases pulled: {len(df)}")
    if "project_name" in df.columns:
        df["addr_norm"] = df["project_name"].apply(normalize_address)
    return df


# ---------------------------------------------------------------------
# TCAD (fixed-width, from Legacy8.0.33-AppraisalExportLayout.xlsx)
# ---------------------------------------------------------------------
def parse_tcad_land_det(path):
    records = []
    with open(path, "r", encoding="latin-1") as f:
        for line in f:
            if len(line) < 97:
                continue
            prop_id = line[0:12].strip()
            size_acres_raw = line[69:83].strip()
            size_sqft_raw = line[83:97].strip()
            try:
                size_acres = int(size_acres_raw) / 10000 if size_acres_raw else None
                size_sqft = int(size_sqft_raw) if size_sqft_raw else None
            except ValueError:
                size_acres, size_sqft = None, None
            records.append({
                "prop_id": prop_id,
                "land_type_cd": line[28:38].strip(),
                "size_acres": size_acres,
                "size_square_feet": size_sqft,
            })
    df = pd.DataFrame(records)
    agg = df.groupby("prop_id", as_index=False).agg(
        total_lot_sq_ft=("size_square_feet", "sum"),
        total_lot_acres=("size_acres", "sum"),
    )
    return agg


def parse_tcad_prop(path):
    """geo_id (547-596) is THE join key to permits.tcad_id -- confirmed working,
    NOT address (TCAD's situs address has no house number in these positions)."""
    records = []
    with open(path, "r", encoding="latin-1") as f:
        for line in f:
            if len(line) < 1795:
                continue
            prop_id = line[0:12].strip()
            geo_id = line[546:596].strip()
            street = " ".join(filter(None, [
                line[1039:1049].strip(), line[1049:1099].strip(), line[1099:1109].strip()
            ]))
            legal_acreage_raw = line[1659:1675].strip()
            try:
                legal_acreage = int(legal_acreage_raw) / 10000 if legal_acreage_raw else None
            except ValueError:
                legal_acreage = None
            records.append({
                "prop_id": prop_id,
                "geo_id": geo_id,
                "situs_street": street,
                "situs_city": line[1109:1139].strip(),
                "situs_zip": line[1139:1149].strip(),
                "legal_acreage": legal_acreage,
                "abs_subdv_cd": line[1675:1685].strip(),
                "tract_or_lot": line[1745:1795].strip(),
            })
    return pd.DataFrame(records)


def build_tcad_lot_size_lookup(prop_path, land_det_path):
    prop = parse_tcad_prop(prop_path)
    land = parse_tcad_land_det(land_det_path)
    merged = prop.merge(land, on="prop_id", how="left")
    merged["likely_platted"] = merged["abs_subdv_cd"].str.strip().ne("")
    return merged.drop_duplicates("geo_id").set_index("geo_id")


# ---------------------------------------------------------------------
# 4. HOME / SB840 / SB15 FLAGGING
# ---------------------------------------------------------------------
HOME_PHASE1_DATE = pd.Timestamp("2024-02-05")
HOME_PHASE2_DATE = pd.Timestamp("2024-08-16")
SB840_DATE = pd.Timestamp("2025-09-01")

SB840_ELIGIBLE_DISTRICTS = {
    "NO", "LO", "GO", "CR", "LR", "GR", "L", "CBD", "DMU", "W/LO", "CS", "CH"
}
SF_DISTRICTS = {"SF-1", "SF-2", "SF-3"}

HOME_PHASE2_MIN_LOT = 2000
PRE_HOME_MIN_LOT = 5750
SB15_MIN_LOT = 1400


def flag_home_direct(row, pr_addr_set):
    """PRIMARY: direct match against validated Plan Review Cases.

    BUG FIXED (found via sanity-check against city-reported HOME numbers):
    this originally had NO date constraint, so it matched any permit at an
    address that EVER had an R-103/R-104 Plan Review Case on file -- including
    permits issued years before HOME existed (137 flagged in 2019, 88 in 2020,
    111 in 2021, etc., in one production run). Duplexes/triplexes could be
    built in some zones before HOME too; an address match alone doesn't mean
    THIS permit used HOME. Now requires issue_date >= HOME_PHASE1_DATE, which
    dropped a real run's direct-match count from 793 to 113 -- the difference
    was entirely false positives.
    """
    addr = row.get("addr_norm")
    if pd.isna(row.get("issue_date")) or row["issue_date"] < HOME_PHASE1_DATE:
        return None, None
    if addr and addr in pr_addr_set:
        return "HOME (matched to Plan Review Case)", "high"
    return None, None


def flag_home_inferred(row):
    """FALLBACK: zoning+lot-size inference, used only for permits the direct
    PR-case match didn't cover. Lower confidence than the direct match."""
    if row.get("base_zone") not in SF_DISTRICTS:
        return None, None
    if pd.isna(row["issue_date"]):
        return None, None
    if row["issue_date"] >= HOME_PHASE1_DATE and row.get("housing_units", 0) in (2, 3):
        return "HOME Phase 1 (inferred, 2-3 unit)", "medium"
    if row["issue_date"] >= HOME_PHASE2_DATE and row.get("housing_units", 0) == 1:
        lot = row.get("total_lot_sq_ft")
        if pd.notna(lot) and HOME_PHASE2_MIN_LOT <= lot < PRE_HOME_MIN_LOT:
            return "HOME Phase 2 (inferred, small lot)", "medium"
    return None, None


def flag_sb840(row):
    if row.get("base_zone") not in SB840_ELIGIBLE_DISTRICTS:
        return None, None
    if pd.isna(row["issue_date"]) or row["issue_date"] < SB840_DATE:
        return None, None
    if row.get("has_overlay_or_pud"):
        return "SB840 (possible, has overlay -- verify)", "medium"
    if row.get("has_rezoning_case"):
        return None, None
    lot_acres = row.get("total_lot_acres")
    units = row.get("housing_units", 0)
    if pd.notna(lot_acres) and lot_acres > 0 and units / lot_acres >= 36:
        return "SB840 (by-right, no overlay/case on record)", "high"
    return None, None


def flag_sb15(row):
    if row.get("likely_platted", True):
        return None, None
    if not row.get("total_lot_acres") or row["total_lot_acres"] < 5:
        return None, None
    lot_sqft = row.get("total_lot_sq_ft")
    if pd.notna(lot_sqft) and SB15_MIN_LOT <= lot_sqft < HOME_PHASE2_MIN_LOT:
        return "SB15 (unplatted-proxy, sub-HOME lot size) -- verify plat date", "medium"
    return None, None


def apply_flags(df, pr_cases):
    pr_addr_set = set(pr_cases["addr_norm"].dropna()) if "addr_norm" in pr_cases.columns else set()

    direct = df.apply(lambda r: pd.Series(flag_home_direct(r, pr_addr_set)), axis=1)
    direct.columns = ["home_flag", "home_confidence"]

    needs_fallback = direct["home_flag"].isna()
    if needs_fallback.any():
        fallback = df.loc[needs_fallback].apply(lambda r: pd.Series(flag_home_inferred(r)), axis=1)
        fallback.columns = ["home_flag", "home_confidence"]
        direct.loc[needs_fallback, ["home_flag", "home_confidence"]] = fallback

    df["home_flag"] = direct["home_flag"]
    df["home_confidence"] = direct["home_confidence"]

    df[["sb840_flag", "sb840_confidence"]] = df.apply(lambda r: pd.Series(flag_sb840(r)), axis=1)
    df[["sb15_flag", "sb15_confidence"]] = df.apply(lambda r: pd.Series(flag_sb15(r)), axis=1)
    return df


# ---------------------------------------------------------------------
# 5. FUZZY MATCH TO MLS
# ---------------------------------------------------------------------
def summarize_unmatched_permits(permits, merged, flag_col="home_flag"):
    """
    Reports how many flagged permits did NOT match to any MLS sale, broken
    out by issue year. This is deliberately NOT labeled "unsold" or
    "investment property held by builder" in the output: a permit with no
    matched sale could mean it hasn't resold yet (especially likely for
    recent permits, given normal construction timelines), is owner-occupied
    with no listing history, sold off-MLS, or simply failed the fuzzy address
    match. Breaking out by issue year makes the construction-lag effect
    visible: if the non-match rate is much higher for 2025/2026 permits than
    for 2019-2022 permits, that points to timing, not investment-holding, as
    the dominant explanation. This function does not attempt to assign a
    cause; it reports the plain match/non-match counts for the reader to
    interpret.
    """
    permits = permits.copy()
    permits["addr_norm"] = permits["original_address1"].apply(normalize_address)
    matched_keys = set(
        merged["original_address1"].astype(str) + "|" +
        merged["issue_date"].astype(str) + "|" +
        merged["housing_units"].astype(str)
    )
    permits["permit_key"] = (
        permits["original_address1"].astype(str) + "|" +
        permits["issue_date"].astype(str) + "|" +
        permits["housing_units"].astype(str)
    )
    permits["matched_to_mls"] = permits["permit_key"].isin(matched_keys)

    flagged = permits[permits[flag_col].notna()].copy()
    flagged["issue_year"] = pd.to_datetime(flagged["issue_date"]).dt.year

    print(f"\n=== {flag_col} permits: matched to an MLS sale vs. not, by issue year ===")
    print("(not matched != confirmed unsold -- see docstring for alternative explanations)")
    summary = flagged.groupby("issue_year")["matched_to_mls"].agg(["sum", "count"])
    summary["not_matched"] = summary["count"] - summary["sum"]
    summary["pct_matched"] = (summary["sum"] / summary["count"] * 100).round(1)
    print(summary.to_string())
    print(f"\nTotal {flag_col} permits: {len(flagged)}, matched: {flagged['matched_to_mls'].sum()}, "
          f"not matched: {(~flagged['matched_to_mls']).sum()}")

    # Does the city's own permit status explain the non-matched permits specifically?
    # This is the test that actually speaks to "these are under construction, not unsold":
    # status_current on the UNMATCHED subset, not the matched one. A permit already
    # showing in the matched (sold) data with a non-Final status is a different,
    # weaker signal (administrative lag after completion, not incomplete construction)
    # and should not be used to explain why OTHER permits haven't matched at all.
    if "status_current" in flagged.columns:
        unmatched = flagged[~flagged["matched_to_mls"]]
        print(f"\n=== {flag_col}: permit status among the {len(unmatched)} NOT-matched permits ===")
        print(unmatched["status_current"].value_counts())
        active_share = (unmatched["status_current"] == "Active").sum()
        print(f"\n{active_share} of {len(unmatched)} not-matched permits ({active_share/len(unmatched)*100:.1f}%) "
              f"show status 'Active', consistent with still being under construction. The remainder "
              f"show other statuses (commonly 'Final' or 'Expired'), meaning construction-timing status "
              f"alone does not explain the full gap; other explanations from the docstring above "
              f"(owner-occupied/never listed, off-MLS sale, address-match failure, data coverage gaps) "
              f"likely account for some of the rest.")

    return flagged[["original_address1", "issue_date", "issue_year", flag_col,
                     f"{flag_col.replace('_flag','')}_confidence", "matched_to_mls"]]


def export_all_flagged_permits(permits, csv_path="flagged_permits_all.csv", json_path="flagged_permits_all.json"):
    """
    Writes every HOME/SB840/SB15-flagged permit to its own file, matched to
    an MLS sale or not, with coordinates. permits_mls_merged_final.csv only
    contains permits that found a valid matched sale; this file is the
    complement needed to show flagged permits on a map even when no sale
    has happened yet, which is expected for most HOME/SB840 permits given
    how recent both policies are (see summarize_unmatched_permits).

    Writes both a CSV (for manual inspection) and a JSON (columnar format,
    matching permits_data.json) since index.html's dashboard fetches
    flagged_permits_all.json directly to show these as unsold-permit markers
    on the map.
    """
    import json
    import math

    flagged = permits[
        permits["home_flag"].notna() | permits["sb840_flag"].notna() | permits["sb15_flag"].notna()
    ].copy()
    cols = [
        "original_address1", "latitude", "longitude", "housing_units", "issue_date",
        "status_current", "home_flag", "home_confidence",
        "sb840_flag", "sb840_confidence", "sb15_flag", "sb15_confidence",
    ]
    flagged = flagged[[c for c in cols if c in flagged.columns]]
    flagged.to_csv(csv_path, index=False)

    # issue_date is a pandas Timestamp at this point (parsed earlier in
    # pull_permits), which json.dump cannot serialize on its own. Convert to
    # a plain date string before building the JSON rows, the same way
    # permits_data.json's export already does elsewhere in this file.
    if "issue_date" in flagged.columns:
        flagged["issue_date"] = pd.to_datetime(flagged["issue_date"], errors="coerce").dt.strftime("%Y-%m-%d")

    def _clean(v):
        if isinstance(v, float) and math.isnan(v):
            return None
        if isinstance(v, pd.Timestamp):
            return None if pd.isna(v) else v.strftime("%Y-%m-%d")
        return v

    columns = list(flagged.columns)
    rows = [[_clean(r[c]) for c in columns] for _, r in flagged.iterrows()]
    with open(json_path, "w") as f:
        json.dump({"columns": columns, "rows": rows}, f, separators=(",", ":"))

    print(f"\nWrote {len(flagged)} flagged permits (matched to a sale or not) to {csv_path} and {json_path}")
    return flagged


def summarize_forsale_vs_wholestructure(merged):
    """
    Classifies each UNIQUE permit (not each sale record) as condo, whole
    Single Family/Attached structure, or whole-building Multi-Family sale.
    Must be done at the permit level: a single condo building resells unit by
    unit over the years and can generate well over a hundred sale records
    tied to one original permit, while a whole-structure sale typically
    generates just one. Counting sale records directly overstates how much
    condo product actually exists relative to permits issued.

    A Single Family/Attached classification means the structure sold whole to
    one buyer, not that it's a rental: it doesn't distinguish an
    owner-occupant renting out one unit from an investor renting out the
    whole building. MLS property type can't make that distinction.
    """
    df = merged.copy()
    df["permit_key"] = (
        df["original_address1"].astype(str) + "|" +
        df["issue_date"].astype(str) + "|" +
        df["housing_units"].astype(str)
    )

    def bucket(u):
        if pd.isna(u) or u < 1:
            return None
        if u == 1:
            return "Single-family"
        if u <= 4:
            return "Middle housing (2-4)"
        return "Multifamily (5+)"

    df["unit_bucket"] = df["housing_units"].apply(bucket)

    permit_summary = df.groupby("permit_key").agg(
        unit_bucket=("unit_bucket", "first"),
        home_flag=("home_flag", lambda x: x.notna().any()),
        home_confidence=("home_confidence", lambda x: x.dropna().iloc[0] if x.notna().any() else None),
        property_types=("Property Type", lambda x: set(x)),
    ).reset_index()

    permit_summary["classification"] = permit_summary["property_types"].apply(
        lambda s: "Condo (for-sale)" if "Condo" in s
        else ("Whole-building (Multi-Family)" if "Multi-Family" in s
              else "Single Family / Attached (whole-structure)")
    )

    print("\n=== For-sale (condo) vs whole-structure sale, permit-level ===")
    mh = permit_summary[permit_summary["unit_bucket"] == "Middle housing (2-4)"]
    print(f"All middle housing permits (n={len(mh)}):")
    print((mh["classification"].value_counts(normalize=True) * 100).round(1))

    mh_home = mh[mh["home_flag"]]
    print(f"\nHOME-flagged middle housing permits (n={len(mh_home)}):")
    print((mh_home["classification"].value_counts(normalize=True) * 100).round(1))

    mh_home_high = mh_home[mh_home["home_confidence"] == "high"]
    print(f"\nHOME high-confidence (direct Plan Review Case match) only (n={len(mh_home_high)}):")
    print((mh_home_high["classification"].value_counts(normalize=True) * 100).round(1))

    return permit_summary


def add_price_per_unit(merged):
    """
    Computes price per dwelling unit from the matched MLS sale.

    MLS 'Property Type' determines how this is calculated:
      - 'Condo': the sale price already reflects ONE individually-deeded
        dwelling, confirmed empirically (Condo sale price and size don't
        scale with the matched permit's housing_units). Used directly, with
        no division.
      - 'Multi-Family', 'Single Family', 'Attached': these are whole-structure
        sales, one buyer purchasing the entire building represented by the
        permit, even when MLS files them under 'Single Family' or 'Attached'
        rather than 'Multi-Family'. Confirmed empirically: within the middle
        housing (2-4 unit) bucket, median sale square footage for 'Single
        Family' and 'Attached' listings scales with the permit's unit count
        the same way 'Multi-Family' does, not the way 'Condo' does. Divide by
        the permit's housing_units to get a true per-unit price.

    housing_units itself (from the permit) still determines the unit_type
    bucket (single-family / middle housing / multifamily) for classification
    purposes, independent of how a given unit within that building was later
    sold or bundled at resale.
    """
    def _price_per_unit(row):
        if row.get("Property Type") == "Condo":
            return row.get("Price")
        units = row.get("housing_units")
        if pd.notna(units) and units > 0:
            return row["Price"] / units
        return None

    merged = merged.copy()
    merged["price_per_unit"] = merged.apply(_price_per_unit, axis=1)
    return merged


def fuzzy_match_to_mls(permits, mls, threshold=90):
    """
    Matches permits to MLS sales by address, then keeps only sales dated ON
    OR AFTER the permit's issue_date.

    This date filter is required, not optional: address alone doesn't
    guarantee a sale reflects the permitted construction. A sale with a date
    before the permit was issued is necessarily a sale of whatever structure
    existed at that address BEFORE this construction, e.g. a teardown sold to
    a builder who then redeveloped it, not the new housing itself. In this
    dataset, 41% of address-matched sales predated their matched permit's
    issue date before this filter was added; those records were sales of a
    different, prior structure and cannot represent the price of the housing
    a permit describes.
    """
    permits = permits.copy()
    mls = mls.copy()
    mls["addr_norm"] = mls["Street"].apply(normalize_address)

    matches = []
    for zip_code, permit_group in permits.groupby("original_zip"):
        mls_block = mls[mls["Zip"].astype(str) == str(zip_code)]
        if mls_block.empty:
            continue
        choices = mls_block["addr_norm"].tolist()
        for idx, addr in permit_group["addr_norm"].items():
            if not addr:
                continue
            result = process.extractOne(addr, choices, scorer=fuzz.token_sort_ratio)
            if result and result[1] >= threshold:
                matches.append((idx, result[0], result[1]))

    match_df = pd.DataFrame(matches, columns=["permit_idx", "mls_addr_norm", "match_score"])
    permits = permits.merge(match_df, left_index=True, right_on="permit_idx", how="left")
    merged = permits.merge(mls, left_on="mls_addr_norm", right_on="addr_norm", how="inner", suffixes=("_permit", "_mls"))

    merged["sale_date_parsed"] = pd.to_datetime(merged["Date"], format="%m/%d/%y", errors="coerce")
    before_filter = len(merged)
    merged = merged[merged["sale_date_parsed"] >= merged["issue_date"]].copy()
    print(f"  Excluded {before_filter - len(merged)} sales dated before their matched permit's "
          f"issue_date (sales of a prior structure, not the permitted construction). "
          f"{len(merged)} of {before_filter} remain.")

    merged = add_price_per_unit(merged)
    return merged


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print("Pulling permits...")
    permits = pull_permits(start_date="2019-01-01")
    print(f"{len(permits)} building permits with net unit change (post sanity filter)")
    permits["addr_norm"] = permits["original_address1"].apply(normalize_address)

    print("Pulling validated HOME Plan Review Cases...")
    pr_cases = pull_home_plan_review_cases()

    print("Pulling address-keyed zoning + case data...")
    zoning = pull_zoning_by_address()
    zoning_cases = pull_zoning_cases()

    street_col = next((c for c in zoning.columns if "street" in c.lower() or "address" in c.lower()), None)
    if street_col is None:
        raise KeyError(f"Could not find a street/address column in zoning data. Columns: {list(zoning.columns)}")
    zoning["addr_norm"] = zoning[street_col].apply(normalize_address)
    zoning_lookup = zoning.drop_duplicates("addr_norm").set_index("addr_norm")
    permits["base_zone"] = permits["addr_norm"].map(zoning_lookup["BASE_ZONE"])
    permits["has_overlay_or_pud"] = permits["addr_norm"].map(zoning_lookup["has_overlay_or_pud"]).fillna(False).astype(bool)

    if "addr_norm" in zoning_cases.columns and len(zoning_cases):
        rezoning_addr_set = set(zoning_cases["addr_norm"].dropna())
        permits["has_rezoning_case"] = permits["addr_norm"].isin(rezoning_addr_set)
        print(f"  has_rezoning_case matched for {permits['has_rezoning_case'].sum()} permits")
    else:
        permits["has_rezoning_case"] = False

    print("Loading TCAD PROP + LAND_DET (fixed-width, from local export files)...")
    tcad_lookup = build_tcad_lot_size_lookup(prop_path="PROP.TXT", land_det_path="LAND_DET.TXT")
    permits["tcad_id_clean"] = permits["tcad_id"].astype(str).str.strip()
    permits["total_lot_sq_ft"] = permits["tcad_id_clean"].map(tcad_lookup["total_lot_sq_ft"])
    permits["total_lot_acres"] = permits["tcad_id_clean"].map(tcad_lookup["total_lot_acres"])
    permits["likely_platted"] = permits["tcad_id_clean"].map(tcad_lookup["likely_platted"]).fillna(True).astype(bool)
    print(f"  TCAD lot size matched for {permits['total_lot_sq_ft'].notna().sum()} / {len(permits)} permits")

    print("Applying HOME/SB840/SB15 flags...")
    permits = apply_flags(permits, pr_cases)
    print(f"  home_flag: {permits['home_flag'].notna().sum()} total "
          f"({(permits['home_confidence']=='high').sum()} high-confidence direct match, "
          f"{(permits['home_confidence']=='medium').sum()} medium-confidence inferred fallback)")
    print(f"  sb840_flag: {permits['sb840_flag'].notna().sum()} total "
          f"({(permits['sb840_confidence']=='high').sum()} high-confidence by-right, "
          f"{(permits['sb840_confidence']=='medium').sum()} medium-confidence needs-verify)")
    print(f"  sb15_flag: {permits['sb15_flag'].notna().sum()} total")

    print("Loading cleaned MLS data...")
    mls = pd.read_csv("mls_combined_all.csv")

    print("Fuzzy matching permits to MLS sales...")
    merged = fuzzy_match_to_mls(permits, mls)

    merged.to_csv("permits_mls_merged_final.csv", index=False)
    print(f"Done. {len(merged)} matched records written to permits_mls_merged_final.csv")

    summarize_unmatched_permits(permits, merged, flag_col="home_flag")
    summarize_unmatched_permits(permits, merged, flag_col="sb840_flag")
    summarize_forsale_vs_wholestructure(merged)
    export_all_flagged_permits(permits)
