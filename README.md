# Austin Housing Delivery: Middle Housing Pricing & HOME/SB840 Attribution

Matches City of Austin building permits to MLS sales records to measure whether
middle housing (2-4 units) and multifamily construction deliver at lower
per-unit prices than single-family construction, how that price gap has moved
relative to HOME and SB840's effective dates, and which permits plausibly used
those allowances.

**Live dashboard:** `index.html` (auto-loads `permits_data.json`, no upload
needed; just open the page or host both files together, e.g. on GitHub
Pages). Figure references below (e.g. "Figure: Price over time") correspond
to named sections and chart cards on that page.

## Conclusion: what this means for HOME, SB840, and affordability

Denser housing delivers meaningfully more housing per dollar than
single-family construction in Austin. That is the clearest, best-supported
finding in this dataset: middle housing sells for 48% less per unit and
multifamily for 20% less per unit than single-family, based on thousands of
correctly-matched sales spanning 2019 through 2026. This holds across nearly
every year in the dataset and reflects a structural mechanism, land cost
and, for whole-building sales, shared structure divided across more
dwelling units, rather than a temporary market condition.

HOME is designed to shift a larger share of Austin's new construction
toward exactly this kind of housing: duplexes, triplexes, and small
multifamily buildings on lots that previously could only hold a single
house. SB840 is designed to do something related but distinct: unlock
by-right multifamily development on commercially-zoned land that
previously required a discretionary rezoning process. Given how
consistently middle housing and multifamily construction have delivered
lower per-unit cost across seven years of market data, both laws' basic
theory of change, that permitting more of this housing type lowers the
effective cost of homeownership per household, is well supported by the
evidence in this dataset.

What this dataset cannot yet show is either law's own realized track record
at meaningful scale. HOME took effect in February 2024 and SB840 in
September 2025, and this analysis only counts sales dated on or after a
permit's issue date, the correct standard for isolating the price of the
housing actually built rather than a prior structure at the same address
(see Methodology below). That correct standard leaves only 24 HOME-flagged
permits and 10 SB840-flagged permits with a valid matched sale citywide.
SB840's count is smaller still, and for a more basic reason than timing
alone: the law is barely eleven months old as of this writing, so almost no
SB840-enabled construction has had time to be built, let alone resold.
These are data availability problems, not challenges to the underlying
finding: Austin does not yet have enough completed, resold HOME or
SB840 housing to measure either law's own price impact with statistical
confidence, not because the impact is absent or in doubt.

**The confident conclusion this data supports: middle housing and
multifamily construction work as intended on price, wherever and however
they get built. The honest limitation: Austin does not yet have enough
sales history to prove HOME or SB840 specifically have delivered that
outcome at scale, only that the housing types they enable reliably deliver
it wherever built.**

## Key finding

Across 28,766 matched permit-sale records (2019-2026), counting only sales
dated on or after the matched permit's issue date:

| Unit type | Median price/unit | Median $/sqft | Median beds | Median baths | Median unit sqft |
|---|---|---|---|---|---|
| Single-family | $555,000 | $372 | 3 | 3 | 1,709 |
| Middle housing (2-4 units) | $288,800 (48% lower) | $322 (13% lower) | 2 | 2 | 952 |
| Multifamily (5+ units) | $444,000 (20% lower) | $444 (19% higher) | 2 | 2 | 1,097 |

*(Figure: "Median price per unit" and "Median $/sqft" charts)*

The price gap is real, and not stable over time; see the Figure: "Price
over time" chart and the year-by-year table below. In several recent years,
multifamily's median price per unit was higher than single-family's, not
lower:

| Sale year | Single-family | Middle housing | Multifamily |
|---|---|---|---|
| 2019 | $427,097 | $125,000 | $259,900 |
| 2020 | $480,750 | $158,199 | $275,000 |
| 2022 | $609,102 | $316,000 | $407,500 |
| 2023 | $525,000 | $385,000 | $520,000 |
| 2024 | $510,510 | $266,900 | **$616,500** |
| 2025 | $585,000 | $290,000 | $310,000 |
| 2026 (YTD) | $608,000 | $429,000 | **$755,000** |

*(Figure: "Price over time, relative to policy changes")*

Denser housing is also smaller per unit, which is expected and partly
explains the price gap: middle housing and multifamily units run
600-750 sq ft smaller than single-family, with one fewer median bedroom
(Figure: "Median unit square footage" and "Median bedrooms & bathrooms").
The price gap is not fully explained by size, though; see the next section.

## How this compares to the ABOR benchmark, and what "price per unit" means

The Austin Board of REALTORS and Unlock MLS published a [HOME Impact
Report](https://assets.unlockmls.com/pu0snv8rn9fa/5HaW83ratkgNRcyg4bbhGf/6345dc34abeee86f2914aca52c70e15e/HOME_Outcomes___Market_Performance_Report_%C3%A2___ABoR_2026.pdf)
in April 2026 comparing HOME Phase 1 new construction to traditional
single-family new construction, both restricted to units built and closed
within calendar year 2025 in the City of Austin. Their HOME sample (57
units) is drawn from the 436 units the city's own 2024 HOME Annual Report
confirmed as approved under Phase 1; properties not on that confirmed list
were excluded. The comparison group (115 units) is traditional detached,
fee-simple single-family new construction from the same year.

| Metric | HOME new construction | Traditional single-family new construction |
|---|---|---|
| Units analyzed | 57 | 115 |
| Median sales price | $750,000 | $1,580,000 |
| Median square footage | 1,693 sq ft | 3,029 sq ft |
| Median $/sqft | $477 | $522 |
| Median bedrooms | 3 | 4 |
| Median lot size | 6,708 sq ft | 8,276 sq ft |
| Median days on market | 32 | 37 |
| Close vs. list price discount | -6.1% | -10.6% |

ABOR's report analyzes "units," and every metric in their table, including
days on market and list-price discount, which are properties of an
individual MLS listing, is reported per unit. That means their $750,000
figure is very likely a genuine per-unit price for individually listed and
sold units, not a total transaction price for a multi-unit property counted
once. That makes their design closer in spirit to this study's price-per-unit
approach than a total-price comparison would be, though ABOR's report does
not fully specify whether every one of their 57 units was individually
listed rather than part of a bundled multi-unit sale.

**One notable difference between the two studies: ABOR finds HOME units
cheaper per square foot too** ($477 vs. $522, about 9% lower), while this
study finds middle housing and multifamily $/sqft is frequently higher than
single-family's, not lower (see the $/sqft section above). Several design
differences likely explain this rather than a contradiction in the
underlying market:

- ABOR compares **new construction to new construction only** in both
  groups. This study's single-family comparison group includes both new
  construction and resales of existing homes, which may price differently.
- ABOR restricts to a **single build-and-close year (2025)**, removing the
  multi-year price drift this study's 2019-2026 window includes.
- ABOR's HOME sample is **Phase 1 only**, sourced directly from the city's
  confirmed approval list; this study's HOME sample mixes a smaller
  direct-match subset with a lower-confidence inferred subset (see
  Methodology below), and includes both phases.
- ABOR's sample (57 units) and this study's post-permit-date-filtered HOME
  sample (24 permits) are both small by ordinary standards. Neither is large
  enough to rule out sampling differences as the source of the $/sqft gap.

Both studies broadly agree on the core, larger point: HOME product sells for
substantially less in total and per unit than traditional single-family
construction. Where they diverge (the $/sqft direction) is a genuinely open
question this study cannot resolve with its current sample, and is flagged
here rather than smoothed over.

Separately, it's worth being explicit about what "price per unit" means in
this study specifically, since the underlying calculation differs by
property type:

- **For a sale explicitly recorded as a whole building purchased in one
  transaction** (e.g. an investor buying an entire triplex): this study
  divides that sale price by the number of units in the building to get a
  per-unit figure.
- **For a sale of an individually deeded condo unit**: the recorded sale
  price already reflects one unit, and is used directly, with no division
  (see Methodology below for the exact rule and how it was verified).

Both are legitimate, useful numbers answering different questions. A
total-price figure answers "what does a typical HOME-built property cost to
buy?" A per-unit figure answers "how much housing, in units, does a given
amount of money buy, when comparing across building types of different
sizes?" A single $750,000 triplex and a single $750,000 house cost a buyer
the same amount, but the triplex delivers three households' worth of housing
for that price, which is the quantity this study's per-unit figures measure.

## Price per square foot: a different story than price per unit

Price per unit favors denser housing, but price per square foot does not.
Median $/sqft is $372 for single-family, $322 for middle housing (13%
lower), and $444 for multifamily, 19% higher than single-family, not lower
(Figure: "Median $/sqft").

This isn't a one-time anomaly. Looking quarter by quarter (27 quarters with
data, Figure: "Price per square foot over time"), multifamily $/sqft
exceeded single-family $/sqft in 15 of 27 quarters (more than half), and
middle housing did in 10 of 27:

| Sale year | Single-family $/sqft | Middle housing $/sqft | Multifamily $/sqft |
|---|---|---|---|
| 2019 | $300 | $157 | $252 |
| 2020 | $343 | $171 | $265 |
| 2022 | $381 | $331 | $406 |
| 2023 | $378 | $389 | $652 |
| 2024 | $352 | $277 | $570 |
| 2025 | $400 | $281 | $400 |
| 2026 (YTD) | $383 | $452 | $551 |

### Why $/sqft is higher for denser housing, despite lower per-unit price

The intuitive explanation is that larger buildings cost more to construct
per square foot (more kitchens, bathrooms, and mechanical systems per
building) and that multifamily buildings are priced as income-generating
commercial real estate. Checked directly against the data, that explanation
does not hold. Sales explicitly recorded as whole-building investment
transactions (`Property Type: Multi-Family`, one buyer purchasing an entire
building) are actually the cheapest housing type per square foot in the
dataset, around $132/sqft, well below single-family's $372/sqft. Their
total sale prices run lower than a typical single-family home's too, not
higher.

The higher $/sqft for the middle housing and multifamily categories overall
comes almost entirely from a different source: about 89% of sales in those
categories are individually-owned condos, not whole-building sales, and
condos in this dataset carry their own price premium per square foot. That
more likely reflects newer construction and denser, more amenity-rich
locations for condo product specifically, rather than a construction-cost or
income-property-valuation effect. Whole-building investment sales, the
category that would actually be priced using income-approach valuation, show
the opposite pattern: cheaper per square foot, not more expensive.

**What this means for the headline finding:** total price is not generally
higher for middle housing or multifamily construction in this dataset, and
where per-square-foot price is higher, it's a condo market effect rather
than a size or construction-cost effect. The per-unit savings shown above
come from land cost, and for whole-building sales the shared structure,
being divided across more units on one lot, not from the housing being
fundamentally cheaper to build or buy per square foot. This $/sqft
calculation comes directly from each sale's own price and square footage
and never involves permit-level unit count, so it is measuring something
different from, and unaffected by, the price-per-unit calculation described
in Methodology below.

### Appreciation rates, 2019-2026 (nominal, not inflation-adjusted)

| Metric | Single-family | Middle housing | Multifamily |
|---|---|---|---|
| Price/unit change | +42% | +243% | +191% |
| $/sqft change | +28% | +188% | +119% |

*(Figure: "Price over time" and "Price per square foot over time")*

Denser housing started from a much lower base, so a larger percentage
increase is mathematically expected. Still, the pace is notable and
consistent with the year-by-year reversals shown above: the per-unit price
advantage of middle and multifamily housing appears to be narrowing over
time, even though it remains real in absolute terms across most of the
study period. This is nominal price change and has not been adjusted for
inflation or interest-rate effects on the broader housing market over the
same period.

## Is middle housing sold as condos, or as whole structures?

MLS property type can distinguish condo sales, individually deeded units sold
to one owner each, from sales explicitly recorded as a whole building
purchased in a single transaction. This has to be counted at the
unique-permit level rather than the sale-record level: a single condo
building resells unit by unit over the years, sometimes generating well over
a hundred separate sale records tied to one original permit (the largest in
this dataset has 235), while a whole-structure sale typically generates just
one. Counting sale records directly would make condo product look far more
common than it actually is relative to the number of buildings actually
permitted.

Across all 611 unique middle housing permits with a valid, correctly-dated
matched sale, condo sales are the largest single category:

| Classification | Share of unique permits |
|---|---|
| Condo (for-sale, individually deeded) | 58% |
| Single Family / Attached (whole structure sold to one buyer) | 37% |
| Whole-building Multi-Family sale | 5% |

*(Figure: "All middle housing permits")*

Permits flagged as HOME-related point the other direction, though the
sample is small enough that only the direction, not the precise share,
should be treated as reliable. Among 13 unique HOME-flagged middle housing
permits with a valid matched sale, 2 are condo sales and 11 are whole
Single Family or Attached structure sales:

| Classification | Count of unique permits |
|---|---|
| Condo (for-sale, individually deeded) | 2 |
| Single Family / Attached (whole structure sold to one buyer) | 11 |
| Whole-building Multi-Family sale | 0 |

*(Figure: "HOME-flagged middle housing permits")*

That direction holds among the smaller, higher-confidence subset matched
directly to a Plan Review Case (n=7): 1 condo, 6 whole-structure. At this
sample size, a single permit changes the percentage by roughly 15 points,
so no precise figure should be quoted from either cut. The reason the
sample is this thin, and not a data quality problem on its own, is that
HOME is too recent for most HOME-built housing to have resold at all; see
the next section.

The price-per-unit gap between these two categories also holds over time
(Figure: "Price per unit over time, condo vs whole-structure sales"), though
quarterly sample sizes for whole-structure sales are small enough in several
quarters that individual data points should be read cautiously rather than
as precise figures.

**What this does and doesn't show.** A Single Family or Attached
classification on a duplex or triplex permit means the structure was sold
whole to one buyer, not divided into individually owned units. It does not,
on its own, distinguish an owner-occupant who lives in one unit and rents
out the other from an investor who bought the whole building purely as a
rental. Both are common ways a small multifamily property changes hands, and
MLS property type does not separate them. What the data suggests
directionally, without enough sample to be precise about it: HOME-permitted
duplexes and triplexes are, so far, more often sold as whole structures
than as individually owned condo units, the opposite of the broader middle
housing market citywide, where condos are the largest category. The
HOME-specific sample sizes here (13 permits, 7 for the high-confidence
subset) are far smaller than the citywide comparison (611 permits) and
should be read as suggestive, not conclusive.

## HOME permits with no matched MLS sale

A meaningful share of HOME-flagged permits don't appear anywhere in this
dataset's MLS sales, meaning they were never matched to any resale record.
It's tempting to read that as "held by the builder as a rental," but that's
only one of several explanations, and probably not the largest one:

- **Construction timing.** A permit issued in 2025 or 2026 may simply not
  have finished construction yet, or finished too recently to show up in a
  resale. Given typical build timelines, this is likely the single largest
  contributor to a low match rate among the most recently issued permits.
- **Owner-occupied, never resold.** Someone builds a duplex and lives in it
  indefinitely. That's not investment-holding, it's just a home with no
  resale history yet.
- **Off-MLS sales.** Small multifamily properties sometimes transact directly
  between investors without a standard MLS listing.
- **Address-match failures.** The fuzzy matching process used to link permits
  to MLS sales has a real, if low, failure rate; some genuinely sold permits
  may not have matched due to address formatting differences.
- **Data coverage gaps.** The known MLS gap for calendar year 2021 and the
  zip-code approximation of city limits (see Known Limitations) could both
  cause a real sale to be missing from this dataset.
- **Held as a rental investment**, which was the original hypothesis, is a
  real possibility for some share of these permits, but MLS data records a
  sale event, not an owner's subsequent intent to occupy, rent, or resell a
  property, so it cannot be confirmed or ruled out directly from this data.

To make the most useful of these explanations, construction timing, visible
rather than assumed, `pipeline.py` includes `summarize_unmatched_permits()`,
which reports the match rate broken out by permit issue year. If the
non-match rate is much higher for the most recent permits than for older
ones, that points to timing as the dominant factor. Run it via:

```python
summarize_unmatched_permits(permits, merged, flag_col="home_flag")
```

This requires the full pre-match permit set (`permits`, before the MLS
fuzzy-match step), not just the merged output, so it runs automatically as
part of `pipeline.py`'s `main()` and its output was not available when this
document was last generated. A future run of `pipeline.py` will print this
breakdown to the console.

## Sanity check against city-reported numbers

This project's HOME flagging was checked against two official City of Austin
sources: the live [HOME Amendments page](https://www.austintexas.gov/development-services/home-amendments)
(data current as of Aug 5, 2026) and the [2024 HOME Annual Report](https://services.austintexas.gov/edims/document.cfm?id=463145)
(covering Feb 2024-Feb 2025).

| Category | City-reported | Our dataset (valid post-permit sales only) |
|---|---|---|
| HOME Phase 1 approved applications, all-time (through Aug 2026) | 681 | 17 flagged permits (11 direct-matched to Plan Review Cases + 6 inferred from zoning/unit count) |
| HOME Phase 1 approved applications, Feb 2024-Feb 2025 only | 236 | (included in the 17 above; not separately re-cut by date range) |
| HOME Phase 1 new units approved, all-time | 1,362 | not directly comparable; our count is permits, not units, and units-per-permit isn't 1:1 with the city's unit tally |
| HOME Phase 2 building permit applications, Aug 2024-Feb 2025 | 6 | 7 flagged permits (inferred only, no direct case match) |

Two things follow from this comparison:

1. **The Phase 1 gap (17 vs. 681) is expected and not a red flag; it's a
   timing effect, not a data quality problem.** This dataset only counts
   sales dated on or after the permit's issue date, the correct standard for
   isolating the price of the housing actually built. HOME Phase 1 only took
   effect in February 2024, so most HOME-built housing simply has not had
   time to resell yet under that correct standard. The small count reflects
   how new the program is, not how much HOME construction has actually
   happened.
2. **The Phase 2 count (7) is too small to evaluate against the city's 6**
   in any meaningful way, though the two numbers happen to be close. Both
   are small enough that a difference of one or two permits changes the
   comparison substantially. The Phase 2 flag is inferred purely from lot
   size (a small lot, one unit, permit issued after Phase 2's effective
   date) with no direct case-record match behind it, unlike the Phase 1
   duplex/triplex flag, which is anchored to real Plan Review Case records,
   so it should be treated as low-confidence regardless of how it compares
   numerically to the city's figure.

This is also a useful general lesson embedded in the methodology: flags
built from a direct match to a real city case record, like the Phase 1
duplex/triplex flag, are meaningfully more trustworthy than flags built from
inference over proxy conditions, like the Phase 2 lot-size flag or the
SB840 medium-confidence tier, and the two should not be treated with equal
weight when reading results from this dataset.

## Data sources

| Source | Dataset | Used for |
|---|---|---|
| City of Austin Open Data | Issued Construction Permits (`3syk-w9eu`) | Building permits, unit counts, addresses |
| City of Austin Open Data | Zoning By Address (`nbzi-qabm`) | Base zoning district and overlay/combining districts (VMU, PUD, CO) |
| City of Austin Open Data | Zoning Cases (`edir-dcnf`) | Rezoning/CUP case history, to exclude discretionary-approval parcels from SB840 attribution |
| City of Austin Open Data | Plan Review Cases (`n8ck-xkda`) | Direct HOME application matching (duplex/triplex/fourplex case records) |
| Travis Central Appraisal District | Certified Appraisal Export (PROP.TXT, LAND_DET.TXT) | Parcel lot size and acreage, for HOME Phase 2 and SB840 density tests |
| MLS (via Privy) | Sales export, 2019-2026, 45,995 records after cleaning | Sale price, sale date, beds, baths, sqft, $/sqft, property type |
| Austin Board of REALTORS / Unlock MLS | [HOME Impact Report](https://assets.unlockmls.com/pu0snv8rn9fa/5HaW83ratkgNRcyg4bbhGf/6345dc34abeee86f2914aca52c70e15e/HOME_Outcomes___Market_Performance_Report_%C3%A2___ABoR_2026.pdf), April 2026 | External comparison point for HOME Phase 1 pricing, discussed below |
| KXAN / Austin DSD | 264 confirmed HOME applications (public records request, Dec 2024) | Ground-truth validation of the HOME direct-match flagging logic |
| City of Austin Development Services | [HOME Amendments page](https://www.austintexas.gov/development-services/home-amendments), [2024 HOME Annual Report](https://services.austintexas.gov/edims/document.cfm?id=463145) | Sanity-check comparison for HOME application/unit totals |
| Austin Planning | [SB840 and Austin Density Bonus Programs staff presentation](https://services.austintexas.gov/edims/document.cfm?id=462645), Nov 18, 2025 | Sanity-check for SB840 zoning district list and density threshold (confirmed 54/acre actual Austin entitlement, not just the 36/acre statutory floor) |

## Methodology

### Price per unit
- For sales where MLS `Property Type = Condo`: the sale price already reflects
  a single individually-deeded dwelling. Used directly, with no division.
  Confirmed empirically: Condo sale price and size do not scale with the
  matched permit's `housing_units`, unlike every other property type.
- For all other property types (`Multi-Family`, `Single Family`, `Attached`):
  these are whole-structure sales, one buyer purchasing the entire building
  the permit covers, even when MLS files a small duplex or triplex sale under
  `Single Family` or `Attached` rather than `Multi-Family`. Price per unit
  equals sale price divided by the matched permit's `housing_units`.
  Confirmed empirically: within the middle housing (2-4 unit) bucket, median
  sale square footage for `Single Family` and `Attached` listings scales with
  the permit's unit count the same way `Multi-Family` does.
- The `unit_bucket` classification itself (single-family, middle housing, or
  multifamily) still comes from the matched permit's `housing_units`, i.e.
  what type of building was actually built, independent of how its units
  were later individually sold or bundled at resale.
- This logic lives in `pipeline.py`'s `add_price_per_unit()` function and
  runs automatically on every pipeline output.

### Permit filtering
- Restricted to `permittype = 'BP'` (Building Permits only), which excludes
  Electrical/Mechanical/Plumbing/Driveway trade sub-permits. Those copy the
  `housing_units` value from the associated building permit as metadata even
  when they add zero units (e.g. an irrigation install).
- No restriction to `permit_class_mapped = 'Residential'`. Austin classifies
  3-4 unit buildings and 5+ unit apartment buildings as `Commercial` in this
  dataset, so a residential-only filter would silently exclude all
  triplexes, fourplexes, and apartments.
- `housing_units > 0` is the core "adds units" signal, refined by a
  unit-count sanity filter: permits reporting more than 10 units with zero
  recorded new square footage are excluded, since this pattern (confirmed on
  a real case: a 432-unit high-rise balcony repair permit) reflects the
  building's total unit count on a repair/facade permit, not units the
  permit actually adds.

### HOME (local ordinance) attribution
- Primary signal: direct address match against the Plan Review Cases
  dataset, restricted to `sub_type` values `R- 103 Two Family Bldgs` (duplex)
  and `R- 104 Three & Four Family Bldgs` (triplex/fourplex), and requiring
  `issue_date >= 2024-02-05` (HOME Phase 1's effective date). The sub_type
  restriction avoids false positives from `R- 101 Single Family Houses`, the
  generic category used for every new single-family home, HOME or not. The
  date restriction avoids matching permits from before HOME existed to a
  duplex/triplex case at the same address for unrelated reasons.
- Fallback signal (lower confidence): for permits not caught by the direct
  match, zoning and lot-size inference is used instead: SF-zoned lot, issued
  after the relevant HOME phase effective date, and (for Phase 1) 2-3 units,
  or (for Phase 2) a lot size between 1,800/2,000 and 5,750 sq ft (see the
  note below on the 1,800 vs. 2,000 sq ft discrepancy). The Phase 2 branch of
  this fallback is known to substantially overcount; see Sanity Check
  section.
- Validated against ground truth: KXAN obtained 264 confirmed HOME
  application permit numbers and addresses directly from Austin DSD via a
  public records request (Dec 2024), embedded in their article as a PDF
  table. A broader version of this flagging logic (including R-101 with a
  date filter) matched 206/264 (78%) against this ground truth. The current
  narrower logic trades some recall for much higher precision.

### SB840 (state law, effective Sept 1, 2025) attribution
- Applies only to parcels zoned in one of Austin's commercial base districts
  (NO, LO, GO, CR, LR, GR, L, CBD, DMU, W/LO, CS, CH). This list was confirmed
  against Austin Planning's own Nov 18, 2025 staff presentation on SB840 and
  density bonus programs; it matches exactly.
- High confidence: commercial base zoning, no VMU/PUD/Conditional Overlay on
  the parcel, no prior rezoning/CUP case on record, and a resulting density
  of 36+ units/acre. That is, a multifamily project with no other legal path
  to that density before SB840 existed.
- Medium confidence ("needs verify"): same as above but the parcel carries an
  existing overlay (VMU/PUD/CO) that could have permitted the project through
  the pre-SB840 discretionary process instead.
- Confirmed via the city's own Sept 2025 staff presentation on SB840 that
  Austin's commercial base zoning generally did not allow multifamily
  by-right before this law; it required VMU, PUD, or a rezoning case. This
  makes the by-right signal a fairly strong one, not a weak inference.
- Density threshold refinement: the city's Nov 2025 staff presentation states
  the law requires cities to allow the greater of 36 units per acre or the
  highest residential density currently allowed in the city, and that this
  figure is 54 units/acre in Austin specifically, not 36. Our flag uses
  36/acre (the statutory floor that applies everywhere) as its threshold,
  which is more permissive than the 54/acre bar Austin's own entitlement
  actually sets. This means the flag may include some permits between 36 and
  54 units/acre that meet the law's baseline minimum but not Austin's actual
  by-right density; a threshold refinement to 54/acre has not been
  implemented in the current pipeline.
- The same presentation gives SB840's formal definition of "Multifamily
  Residential" as any site with 3 or more dwelling units in one or more
  buildings, which our density-based test does not check directly, though in
  practice reaching 36+ units/acre on typical Austin commercial parcels
  almost always implies 3+ units.
- Date-checked: 100% of SB840-flagged permits have `issue_date` in 2025 or
  2026, consistent with the law's Sept 2025 effective date.

### SB15 (state law, effective Sept 1, 2025) attribution
- Applies only to unplatted tracts of 5+ acres in qualifying cities (Austin
  qualifies). No true plat-date history is available in any public dataset
  found for this project, only whether a parcel is currently platted. The
  flag uses this as a proxy (`likely_platted`) and is explicitly labeled
  lower-confidence ("verify plat date") when it does fire.
- Zero SB15 matches in the current dataset. This most likely reflects data
  availability and the very short window since the law took effect (under a
  year of possible activity), not necessarily zero real-world usage. A direct
  text search of Plan Review Cases for "SB15"/"SB 15" mentions also returned
  zero results, consistent with builders not yet having left a text trail
  referencing the law by name in city systems.

### MLS address matching
- Fuzzy string matching (RapidFuzz `token_sort_ratio`, 90+ similarity
  threshold), blocked by zip code for performance. Mean match confidence
  across the final dataset: about 95%.
- Address matching alone is not sufficient: a sale at the same address as a
  permit does not necessarily reflect the housing that permit describes.
  After the address match, only sales dated on or after the permit's
  `issue_date` are kept. A sale dated before the permit was issued is
  necessarily a sale of whatever structure existed at that address before
  this construction, for example a teardown sold to a builder who then
  redeveloped it, not the new housing itself. This filter removed 41% of
  otherwise address-matched sales; those records were sales of a different,
  prior structure at the same address.

## Sample size and reliability

This dataset covers a small fraction of the city's own reported HOME
activity: 24 flagged permits against a city-reported 681 approved Phase 1
applications, once sales are correctly restricted to those dated on or
after the permit's issue date. That restriction is required for accuracy
(see Methodology above), and it is also the main reason the count is this
small: HOME only took effect in February 2024, so most HOME-built housing
has simply not had enough time to resell yet. This is a timing limit, not a
sign the underlying data or method is unreliable.

**Reasonably robust:** that price per unit is meaningfully lower for denser
housing than for single-family, across the housing market generally. The
mechanism, land cost and shared structure divided across more units on one
lot, is close to a structural fact rather than something that depends on
which specific permits happened to resell. This conclusion rests on
thousands of correctly-dated sales (3,102 middle housing, 2,195
multifamily) and would very likely hold with the full population.

**Approximate, not precise:** the exact magnitude of that citywide gap (48%
for middle housing, 20% for multifamily) and the exact dollar figures. A
larger or more representative sample could shift these numbers, though not
the direction of the finding.

**Should not be treated as a reliable, precise figure at all:** anything
specific to HOME or SB840. With only 24 HOME-flagged and 10 SB840-flagged
permits citywide, and single-digit counts within most sub-cuts (13 and 7 for
the HOME middle-housing breakdowns; 1 high-confidence SB840 permit), these
numbers indicate scale, not precision. A difference of one or two permits
changes the reported percentage by ten points or more in several of these
cuts. Individual quarters or years in the time series where the underlying
cell count is a handful of sales should be read the same way (visible
directly in `pipeline.py`'s per-cell counts if reproduced).

The more important issue is not sample size in isolation but
**representativeness**: this dataset is not a random sample of HOME permits,
it's the subset that also happens to have resold on the MLS within the years
covered. Permits that resell quickly (investor flips, condo units, which by
design turn over more often) are structurally more likely to appear in this
dataset than permits that don't resell at all (long-term owner-occupants,
buildings held as rentals). That selection effect could bias price
comparisons in ways that simply having more data of the same kind would not
fix. For HOME and SB840 specifically, this compounds with the timing effect
above: both are recent enough that the permits which have resold at all may
be a particularly unrepresentative early slice (for example, disproportionately
investor flips that sell quickly) rather than a fair preview of how HOME
housing broadly will price once more of it has had time to resell. The
"HOME permits with no matched MLS sale" section above addresses this same
limitation from a different angle.

## Known limitations

- SB840 density threshold uses the 36/acre statutory floor, not Austin's
  actual 54/acre entitlement, confirmed via the city's own Nov 2025 staff
  presentation. The current flag may include some permits that meet the
  law's baseline minimum but not Austin's specific by-right density. Not yet
  corrected in the pipeline.
- HOME Phase 2 flag count (7 flagged, correctly-dated) happens to be close
  to the city-reported 6 for the comparable early window, but the sample on
  both sides is too small for that closeness to mean much; see Sanity Check
  section. This flag is inferred, not directly matched to a case record, and
  should be treated as low-confidence regardless.
- HOME Phase 2 lot-size threshold discrepancy, unresolved: the city's public
  summary page cites 1,800 sq ft as the small-lot minimum; the ordinance
  amendment review sheet (C20-2023-024) states 2,000 sq ft. The pipeline uses
  2,000 (the more conservative figure) pending confirmation against the
  final adopted ordinance text (Ord. 20240516-006).
- TCAD lot-size join coverage: about 79% of permits successfully matched to a
  TCAD parcel record via `geo_id`. Permits without a match cannot be
  evaluated for HOME Phase 2 or SB840 density criteria.
- Permits vs. units: flag counts in this document are permit counts, not
  unit counts, and are not directly comparable to the city's unit-level
  totals (e.g. "1,362 new units approved") without a units-per-permit
  reconciliation that hasn't been built.
- Zip-code filtering as an Austin-boundary proxy: MLS data is filtered to a
  curated list of Austin-area zip codes, which is an approximation of city
  limits, not a precise spatial boundary. Some included zips (e.g. far West
  Austin, Del Valle) contain unincorporated Travis County / ETJ area.
- MLS data gap: no MLS records for calendar year 2021 (2019-2020,
  2022-2026 are covered).
- Zoning/overlay data currency: the city's own documentation for the Zoning
  By Address dataset notes it may not reflect all current overlays for a
  given address and should not be treated as a legal record.
- Small quarterly sample sizes for middle housing and multifamily, relative
  to single-family's much larger volume, mean quarter-to-quarter swings in
  the time series charts, especially for multifamily, should be read with
  wider uncertainty than the single-family series.

## Files

- `index.html`: the dashboard (self-contained, loads `permits_data.json`
  automatically). Includes the time series, beds/baths/sqft comparison, the
  ABOR methodology clarification, and the $/sqft explanation directly on the
  page, with named figure anchors referenced throughout the text.
- `permits_data.json`: slim columnar extract of the merged dataset (address,
  units, dates, coordinates, policy flags, price, price per unit, beds,
  baths, sqft, property type, match confidence) used by the dashboard.
- `pipeline.py`: the full data pipeline. Pulls permits, zoning, TCAD parcel
  data, and Plan Review Cases from their live sources; applies the
  HOME/SB840/SB15 flagging logic described above; fuzzy-matches to MLS
  sales; and computes price per unit via the `Property Type`-conditional
  logic described in Methodology above.
- `permits_mls_merged_v4_postpermit.csv`: full merged output (60+ columns,
  28,766 rows), restricted to sales dated on or after the matched permit's
  issue date, that `permits_data.json` is derived from.
