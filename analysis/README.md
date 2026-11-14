# Swing plane versus attack angle by pitch height

Prepared for Pat Burgess, November 12, 2026.

## Question
Within the same hitter, is the swing plane flatter on higher pitches while the bat's direction at impact changes less?

## Finding
Yes for the flatter swing plane. The adjusted high-minus-low difference in swing-path tilt was -9.64 degrees (95% confidence interval -9.84 to -9.43). Attack angle changed less, but was not identical: +1.84 degrees (95% CI +1.38 to +2.29), meaning slightly more upward at impact on high pitches.

This supports the distinction between the plane of the approach and the instantaneous direction at impact. It does not prove that flattening the approach causes a particular impact angle, or that any verbal coaching cue is effective.

## Descriptive medians (degrees)

| Batting side | Pitch height | Swing-path tilt | Attack angle |
|---|---|---:|---:|
| Right | Low | 36.91 | +6.24 |
| Right | Middle | 32.28 | +7.46 |
| Right | High | 26.87 | +8.59 |
| Left | Low | 37.77 | +7.13 |
| Left | Middle | 33.22 | +7.62 |
| Left | High | 27.92 | +7.92 |

These are pooled medians, not adjusted individual changes. Read the within-hitter results separately.

## Data and quality checks

Fresh Baseball Savant downloads retrieved in 14 date batches for the 2024 and 2025 regular seasons. Four-seam fastballs resulting in singles, doubles, triples or home runs only. Downloaded 24,224 unique pitch records; no duplicate game/at-bat/pitch keys. Of 18,986 hits whose pitch centers were within the specified strike zone, 17,660 had both angle metrics (705 distinct hitters). Missing angle measurements excluded 1,326 in-zone hits (7.0%). No angle values were imputed. The adjusted model used 17,384 observations from 625 hitters with within-unit pitch-height variation and available controls.

The fresh cohort is not identical to the prior atlas snapshot: this analysis explicitly restricts to regular-season games and complete paired angle measurements and does not require contact depth in the primary comparison. Do not overwrite prior cohort counts with these counts.

## Definitions

- Attack angle: vertical direction of the bat sweet spot at impact relative to horizontal; positive is upward.
- Swing-path tilt: orientation of the plane approximated by the barrel path over the 40 milliseconds before contact; a lower value is flatter. It is not a signed instruction to swing upward or downward.
- Pitch height: (plate_z - sz_bot) / (sz_top - sz_bot), split into equal low, middle and high thirds.
- Horizontal pitch-center bounds: +/- 17/24 ft. Horizontal comparisons are mirrored so positive inches indicate inside for either batting side.
- Contact depth: forward distance relative to batter center of mass; not distance forward of home plate.

## Within-hitter analysis

Primary descriptive regression: separate fixed intercepts for each hitter-season-batting-side combination. High and middle pitch-height indicators use low pitches as reference. Controls: horizontal location and its square, pitch velocity, and pitcher handedness. Confidence intervals use a cluster-robust covariance estimator by hitter with finite-sample adjustment and a t distribution with number-of-hitters minus one degrees of freedom. Combined and separate right/left models are in output/within_hitter_results.csv.

Sensitivity checks:
- Adding contact depth: tilt -9.78 degrees; attack angle +2.75 degrees. Depth may be part of the movement/timing response, so this is secondary, not a causal correction.
- Matching high and low pitches within hitter-season-side and horizontal third, requiring at least three hits at each height: 154 hitters contributed 235 paired strata. Hitter-weighted mean difference of stratum medians: tilt -10.01 degrees (bootstrap 95% CI -10.43 to -9.57); attack +2.50 degrees (1.54 to 3.46).
- Requiring at least five hits per high/low stratum retained only 18 hitters. Tilt remained -10.28 degrees; attack-angle uncertainty included zero. No strata met the 10-hit minimum, so no estimate was reported for that threshold. Thresholds describe precision sensitivity, not performance standards.

## Limits and interpretation

Successful hits alone are a selected subset of swings. This cannot establish optimal technique, explain misses, evaluate batting average, or prove the effectiveness of a "swing down" cue. Missing tracking could be systematic. Differences are observational and depend on the specified model; individual responses vary. Statistical differences do not establish practical importance. No equivalence margin was specified, so do not claim attack angles were statistically equivalent or exactly the same. This is not a reconstruction of each barrel's trajectory.

The supported wording is: "On successful four-seam hits, hitters used a substantially flatter swing plane higher in the zone while maintaining a modestly upward attack angle at contact. The approach and the direction at impact are different measurements."

## Reproduction and verification

Run `python analyze.py` with numpy, pandas, scipy and matplotlib installed. The original 14 downloads are represented by a single compressed CSV in raw/ retaining all 24,224 records and every field used by this analysis. Unused source columns were removed; measurement values were not changed. Download coverage is in manifest.json. The script accepts CSV and CSV.gz inputs. Outputs include eligible records, audits, pooled medians, adjusted contrasts, sensitivity results and the figure. Seed 20261112 makes bootstrap calculations repeatable. Raw-file counts and medians were independently recomputed with Python's csv/statistics libraries. Primary coefficients were independently verified using a sparse full-dummy fixed-effects regression.

## Official sources

- https://baseballsavant.mlb.com/statcast_search
- https://baseballsavant.mlb.com/csv-docs
- https://baseballsavant.mlb.com/leaderboard/bat-tracking/swing-path-attack-angle
- https://www.mlb.com/glossary/statcast/swing-path-tilt
- https://www.mlb.com/glossary/statcast/attack-angle

Data source: MLB Statcast / Baseball Savant. Independent exploratory analysis; not endorsed by MLB. Raw source data remains subject to provider terms.
