# SwingLab — Fastball Contact Atlas

An interactive 3D statistical view of pitch location, contact depth and attack angle, developed by Pat Burgess from questions raised while coaching hitters.

## Explore the project

- [Contact Atlas source](contact-atlas/)
- [Methods, definitions and findings](CONTACT-ATLAS.md)
- [Graph data: summaries and sampled hits](contact-atlas/data/contact-map.json)
- [Data builder](scripts/build_contact_map.py)

The blue-and-white atlas includes separate left/right-handed groups, 35 location cells per side, individual-hit samples, selectable depth and attack-angle colors, and high/middle/low pitch comparisons.

## Run locally

No JavaScript build or package installation is required. With Python installed, run from the repository root:

```sh
python -m http.server 8000 --directory contact-atlas
```

Open http://localhost:8000 in your browser. Serve the files over HTTP rather than opening index.html directly, so the graph can load its JSON data.

## What the data shows

The included snapshot summarizes 17,963 eligible successful four-seam hits from imported 2024–2025 MLB Statcast records. All eligible observations contribute to summaries; the individual-hit display contains 1,400 sampled records per batting side.

Inside pitches show farther-forward median contact relative to hitter center of mass than outside pitches. Higher pitches show slightly more upward median attack angles in this pooled successful-hit cohort. These observations do not establish optimal technique or prove the effectiveness of an up/down mental cue.

Pitch width and normalized height are measured at the plate; contact depth is relative to hitter center of mass. This is a statistical graph, not a reconstructed physical swing or contact position over home plate. Attack angle is distinct from launch angle and swing-plane tilt.

## Data source and reproduction

Source: MLB Statcast / Baseball Savant. [Metric definitions](https://baseballsavant.mlb.com/csv-docs).

This public repository includes the derived visualization snapshot, processing code and measurement notes. It does not include the full raw import. To regenerate, supply matching Statcast CSV gzip files under `data/raw/statcast/`, then run:

```sh
python scripts/build_contact_map.py
cp data/visualization/contact-map.json contact-atlas/data/contact-map.json
python scripts/verify-contact-map.py
```

Raw source data remains subject to its provider's terms; this repository does not claim ownership of MLB data. The visualization is independent and is not endorsed by MLB.
