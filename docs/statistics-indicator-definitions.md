# Statistics and Annual Reporting Definitions

The API registry at `GET /api/v1/statistics/indicators` and the Statistics screen expose the live indicator configuration. Unless an entry says otherwise, calculations exclude soft-deleted source records. Hierarchical scopes first resolve the selected archdiocese or deanery to its parishes, then roll those rows up to the configured grouping.

## Registered indicators

| Indicator | Source and value | Reporting period | Inclusion rule | Aggregation scope |
| --- | --- | --- | --- | --- |
| `faithful_by_deanery` | `Faithful` row count | Current registry snapshot | One non-deleted profile per person; all canonical statuses, including deceased, are counted. | Deanery |
| `land_value_by_vicariate` | Sum of `LandParcel.estimated_value_rwf` | Current registry snapshot | Non-deleted parcels with an estimated value; unvalued parcels contribute no amount. | Vicariate (deanery) |
| `donations_trend_by_parish` | Sum of `Donation.amount` | Month of `donation_date` | All donation and payment categories; soft-deleted entries excluded. Currency values are not converted, so callers should scope this to one currency before interpreting a total. | Parish and month |
| `documents_by_parish` | `Document` row count | Current repository snapshot | Non-deleted documents linked to a parish. Documents scoped only to a deanery or archdiocese appear in an unassigned parish bucket. | Parish |
| `documents_by_type` | `Document` row count | Current repository snapshot | Non-deleted documents grouped by `document_type_id`; untyped documents have an unassigned type bucket. | Document type |
| `retention_review_backlog` | `Document` row count | Current repository snapshot | Non-deleted documents with disposition status `DUE_FOR_REVIEW`. | Parish |
| `ocr_completion_rate` | Non-null `ScannedPage.ocr_raw_text` share | Current repository snapshot | Completed pages have non-null OCR text; all non-deleted scanned pages are the denominator. | Parish owning the ledger book |
| `annual_catholic_population_by_parish` | Sum of reported Catholic population | `report_year` | Latest parish return for each parish and year. | Parish, then archdiocese/deanery rollup |
| `annual_infant_baptisms_by_parish` | Sum of reported infant baptisms | `report_year` | Latest parish return for each parish and year. | Parish, then archdiocese/deanery rollup |
| `annual_adult_baptisms_by_parish` | Sum of reported adult baptisms | `report_year` | Latest parish return for each parish and year. | Parish, then archdiocese/deanery rollup |
| `annual_confirmations_by_parish` | Sum of reported confirmations | `report_year` | Latest parish return for each parish and year. | Parish, then archdiocese/deanery rollup |
| `annual_marriages_both_catholic_by_parish` | Sum of reported marriages with both spouses Catholic | `report_year` | Latest parish return for each parish and year. | Parish, then archdiocese/deanery rollup |
| `annual_marriages_mixed_religion_by_parish` | Sum of reported mixed-religion marriages | `report_year` | Latest parish return for each parish and year. | Parish, then archdiocese/deanery rollup |

## Annual parish returns

Returns cover a calendar year and contain the parish-submitted totals shown in the entry form. Counts must be non-negative and the reporting year must be between 1900 and 2200. Submitting the same parish and year again replaces the current values; an immutable audit event records the actor, year, and old/new values for changed fields. The API and Annuario aggregation return one latest record per parish/year, even if older duplicate rows already exist.

Register reconciliation compares annual return totals with non-deleted sacramental records whose `celebration_date` falls inside the calendar year. It reports baptism total (infant + adult), confirmations, first communions, marriages (both categories combined), and Christian funerals. A mismatch is a review cue; the parish return remains the submitted figure until an authorized user corrects and resubmits it. Population, families, schools, students, health centers, and catechumens do not have an equivalent dated operational register in this repository and are not register-reconciled.

The Annuario Pontificio report counts non-deleted parishes as of computation time, active-duty diocesan and religious priests as of computation time, and the annual-return totals for the selected year. Parish and clergy counts are current snapshots, not historical counts for that year.
