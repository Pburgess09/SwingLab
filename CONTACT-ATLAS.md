# Fastball Contact Atlas

A rotatable three-dimensional statistical graph inspired by a ball-grid hitting-zone display. It does not reconstruct ball positions over home plate.

## Data contract
- Existing imported MLB Statcast 2024–2025 rows; no new acquisition required.
- Four-seam only: `pitch_type == FF`.
- Successful hits only: single, double, triple, home_run; `description == hit_into_play`.
- Pitch center within ±17/24 ft and the batter's recorded vertical strike zone.
- Missing depth is excluded, never imputed.
- X: plate_x in inches, mirrored into positive-inside coordinates for aggregation, then displayed from the pitcher's perspective for each side.
- Y: normalized pitch height `(plate_z - sz_bot)/(sz_top - sz_bot)`.
- Z: `intercept_ball_minus_batter_pos_y_inches`, ahead of hitter COM. It is NOT depth ahead of the plate. Source data contains only batter-relative intercept X/Y fields, not an absolute plate-registered contact XYZ.

These three quantities form a statistical plot. The plate icon is an orientation key only. Pitch location and actual contact location are different measurements.

## Cohort and results
1,451,540 imported rows examined. 24,688 four-seam hits; 5,347 outside the plotted zone. Of 19,341 in-zone hits, 1,378 lack contact depth, leaving 17,963 tracked hits.

| Batting side | Hits | Outside median | Middle median | Inside median |
|---|---:|---:|---:|---:|
| Right | 9,528 | 25.244 in | 27.477 in | 28.745 in |
| Left | 8,435 | 24.860 in | 27.963 in | 29.165 in |

The three bands split plate width into equal thirds. These are observation-weighted distributions across hitters and heights, not a same-hitter causal comparison. Positive inside-minus-outside differences are observed, not imposed.

Grid summaries use five horizontal by seven vertical bands for each batting side. All eligible hits contribute to medians/IQR. Individual-hit display uses a deterministic random sample of up to 1,400 per side; dates, event, exit velocity, batter ID and pitch key are retained. Color defaults to attack angle, with a depth-color option; neither represents hit probability. Successful hits alone cannot provide a batting-average denominator or evaluate cue effectiveness.

## Reproduce and run
`python scripts/build_contact_map.py` processes existing `data/raw/statcast/**/*.csv.gz` and writes `data/visualization/contact-map.json`. The published snapshot was generated from the original project's imported records. The full raw import and its workflow are not included in this public repository; see README.md for reproduction requirements.

The self-contained `contact-atlas/` source can be served as static files. Copy a refreshed `data/visualization/contact-map.json` to `contact-atlas/data/contact-map.json` when updating. The Motion Study navigation link has been removed.

## Verification
Cohort totals, all 70 grid cells, quantile order, allowed hit outcomes and uniqueness/bounds of 2,800 sampled records checked. JS syntax checked. Browser checks cover batting-side changes, median/point modes, camera views and data selection. No WebGL is required; the canvas projects and depth-sorts actual 3D graph coordinates.

The coaching section separates reported cue from measured movement and outcome. No mental cue or hand/barrel path is inferred from this graph.

## Attack angle by pitch height
Measured `attack_angle` is the vertical direction of the bat sweet spot at impact relative to horizontal. It is distinct from ball launch angle and swing-plane tilt. Positive values mean upward. All 17,963 depth-eligible records have attack angles. Separate depth and angle medians do not reconstruct one swing.

| Batting side | High third | Middle third | Low third |
|---|---:|---:|---:|
| Right | +8.639° | +7.472° | +6.226° |
| Left | +7.920° | +7.598° | +7.197° |

These pooled successful-hit medians do not support the proposed lower-pitch/more-upward ordering. They mix hitters, dates and horizontal locations and do not establish optimal technique or cue effects. The high/low cards use thirds of each pitch's normalized strike zone. A selected cell supplies a more specific location summary and IQR. The arrows use the actual vertical angle with equal horizontal/vertical scale, independent of graph depth expansion; they are not full bat paths. Missing values, if present in a refresh, remain unavailable with explicit coverage counts.

Official metric definition: https://baseballsavant.mlb.com/csv-docs#attack_angle
