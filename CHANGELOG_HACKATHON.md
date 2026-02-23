# Hackathon Change Log

Purpose: track procedural and data changes, the rationale, and the date for later analysis.

## 2026-02-21

### Checklist generator changes
- Added bulk generator script to create all required operation sets in one run, with dated output folders and standardized subfolder names.
  - Reason: enable fast multi-configuration generation and preserve consistent outputs across runs.
- Updated output folder timestamp format to YYYYMMDD_HHMM.
  - Reason: avoid folder name collisions when running multiple times in one day.
- Updated output subfolders to numbered naming convention (00-Json, 01-VLOS, 02-BVLOS_No_Vo, 03-BVLOS_Vo, 04-Night, 05-Swarm, 06-Multi-UAS).
  - Reason: enforce deterministic ordering and improve navigation.
- Renamed generated PDFs to match folder names with _checklist and _procedures suffixes.
  - Reason: improve traceability and reduce ambiguity when sharing files.

### JSON data ordering and structure
- Removed Operation Planning checklist from the dataset.
  - Reason: per updated scope and procedure set.
- Reordered JSON files to: ERP, Emergency, Contingency, First Flight, Subsequent Flight, In-Flight, Post-Flight, Pre-Operation, Packing, Post-Operation.
  - Reason: align document structure with the new operational flow.
- Added new ERP file (00_erp.json).
  - Reason: introduce a dedicated Emergency Response Plan section separate from emergency procedures.

### ERP alignment with provided guidance
- Rebuilt ERP content to match provided emergency matrix and contact list.
  - Reason: align with the documented emergency response framework and ensure all contacts are visible in checklist format.
- Added trigger-based entries and compact response actions for ERP emergency types.
  - Reason: improve readability and speed of use in emergencies.

### Checklist wording standardization
- Updated checklist entries across all operational JSON files to be concise and action-focused.
  - Reason: apply recognized checklist best practices for rapid scan and reduced cognitive load.
- Moved phone numbers into checklist entry text wherever calls are required.
  - Reason: ensure phone numbers appear in checklist PDFs (not only in procedures).
- Removed bush fire from Emergency Procedures and placed it under ERP fire response.
  - Reason: consolidate emergency response topics under ERP and avoid duplication.

### Checklist content refinements (round 2)
- Removed redundancy between checklist entry titles and descriptions.
  - Reason: improve scan speed and reduce cognitive load per CAA CAP 676 guidance.
- Rewrote "Fly-away" entry from "regain control" to specific actions: "orient antenna overhead, switch flight mode".
  - Reason: provide concrete, unambiguous actions rather than vague directives.
- Reorganized contingency procedures by risk level: aircraft/wildlife approaching first, then technical issues, then crew/weather.
  - Reason: align with emergency procedures and improve priority focus.
- Moved "controller outside window" from description to entry title for wildlife scenarios.
  - Reason: highlight critical safety action in checklist view.
- Added tourist proximity check (30+ seconds) in contingency procedures.
  - Reason: minimize disruption to conservancy visitor experience.
- Clarified GoPro entry to "GoPro: battery, time, settings, start recording, announce" (instead of just "verify").
  - Reason: be specific about what is being checked per checklist best practices.
- Moved weather assessment from operational environment to final checks (just before go/no-go).
  - Reason: conditions change rapidly in field; more relevant to check immediately before takeoff.
- Renamed operational environment check to "Topography hazards" (removed airspace/NOTAM check).
  - Reason: focus on immediate field hazards; NOTAMs are better checked in camp.
- Moved NOTAM check to pre-operation checklist with phrasing "Check NOTAMs".
  - Reason: NOTAMs do not change rapidly; checking in camp is more efficient and allows field safety officer to check once for all teams.
- Moved equipment section from first flight to after safety briefing.
  - Reason: improve workflow efficiency (crew briefed before handling equipment).
- Removed non-essential words per checklist best practices: "confirmed", "assigned", "monitored" where redundant.
  - Reason: per CAA/NASA guidance, checklists should be brief and free of filler; action verbs are sufficient.
- Consolidated controller mode check into "UAS on:" entry alongside failsafes/GPS/RSSI.
  - Reason: efficiency—controller checked while doing other UAS checks rather than requiring separate on/off cycle.
- Moved landing mat placement before "UAS on:" checks.
  - Reason: drone may need to be placed on mat before checking controller settings.
- Moved "team behind pilot" from landing mat entry to new entry just before takeoff announcement.
  - Reason: crew position is relevant to takeoff action, not mat placement.
- Removed IMSAFE from safety briefing section (kept only in final checks).
  - Reason: IMSAFE is more relevant immediately before takeoff, not during initial briefing.
- Applied all first-flight changes to subsequent-flight procedures where applicable.
  - Reason: consistency across flight types.

### Redundancy removal from descriptions (round 3)
- Systematically removed duplicate information from procedure descriptions that was already stated in checklist titles.
  - Reason: per CAA CAP 676 and NASA human factors guidance, descriptions should supplement titles, not repeat them; this reduces cognitive load and improves scanning speed.
  - Method: retained all titles; simplified descriptions to add only clarifying or procedural details not in the title.
- Examples of changes:
  - "Aircraft approaching: lower altitude below 30m AGL" → description changed from "Lower the drone to a safe altitude (below 30m AGL)." to "This maintains safe separation."
  - "Crew unwell: RTH" → description changed from "RTH. Keep calm and communicate clearly." to "Keep calm and communicate clearly."
  - "Weather assessed" → description changed from "Confirm no high winds, good visibility, no incoming rain, no low clouds." to "Verify no high winds, good visibility, no incoming rain, no low clouds."
  - "GoPro: battery, time, settings, start recording, announce details" → description now focuses on settings and what to announce, not repeating the checklist action items.
- Applied across all 10 JSON files: ERP, Emergency, Contingency, First Flight, Subsequent Flight, In-Flight, Post-Flight, Pre-Operation, Packing, Post-Operation.
- Validation: all 10 JSON files verified for syntax correctness; PDF generation tested successfully for all 6 operation configurations.

### Workflow optimization and section reorganization (round 4)
- Updated GoPro checklist title from "battery, time, settings..." to "battery, SD card space, settings...".
  - Reason: clarify that "space" refers to storage capacity, not time on SD card; more precise and actionable.
- Updated GoPro description to explicitly check "sufficient battery and SD card space remaining".
  - Reason: make storage verification a primary action item, not secondary.
- Removed "confirm mode" from "Controller on" entry; controller mode check is now in "UAS on:" entry only.
  - Reason: avoid redundancy; mode confirmation grouped with other UAS checks for efficiency.
- Reorganized first flight and subsequent flight sections: Safety Briefing now comes BEFORE Equipment.
  - Previous order: GoPro → Operational Environment → Equipment → Safety Briefing → Final Checks
  - New order: GoPro → Operational Environment → Safety Briefing → Equipment → Final Checks
  - Reason: crew briefing and hazard awareness before handling equipment improves workflow logic.
- Moved landing mat checks to occur BEFORE "UAS on:" checks within Equipment section.
  - Reason: mat must be placed before powered-on checks; drone may need to be positioned on mat.
- Removed duplicate standalone "IMSAFE" entry from Final Checks section.
  - Reason: IMSAFE already part of the go/no-go decision; removing redundancy per checklist best practices.
- Updated "Go/no-go" title to "Go/no-go: ground/air risks, IMSAFE" (shorter, more scannable format).
  - Reason: clarify that IMSAFE is included in go/no-go criteria; matches compact title style throughout.
- Applied all changes to subsequent-flight.json to match first-flight organization.
  - Reason: consistency across flight types ensures crew familiarity.

### Vertical separation safety enhancement
- Added RTH altitude preset requirement to vertical separation check.
  - Current description: "Coordinate vertical separation with other UAS and set maximum altitude accordingly. RTH must be set to preset altitude (not optimal) to maintain vertical separation during RTH and prevent mid-air collisions."
  - Reason: critical safety measure for swarm and multi-UAS operations. Setting RTH to preset altitude ensures drones maintain assigned vertical separation during RTH; optimal RTH setting can cause altitude changes and risk mid-air collisions.
  - Applies to: first_flight.json only (applies only to MULTIPLE and SWARM drone configurations)

### Simplified checklist language (round 5)
- Removed redundant controller mode check from subsequent-flight UAS on entry.
  - Reason: controller mode is already verified in first flight; no need to duplicate in subsequent flights.
- Removed unnecessary qualifier words from checklist titles per CAA guidance on brevity.
  - Removed: "confirmed", "assessed", "checked" from titles (kept only in descriptions where necessary)
  - Examples:
    - "Weather assessed" → "Weather"
    - "Vertical separation confirmed" → "Vertical separation"
    - "Mission plan and team briefing confirmed" → "Mission plan and team briefing"
    - "NOTAMs checked" → "NOTAMs"
    - "Comms and VHF checked" → "Comms and VHF"
### Removed action verbs from in-flight checklist (round 6)
- Simplified in-flight entries by removing action verbs (Watch, Check) for brevity.
  - "Watch weather (wind, rain, visibility)" → "Weather (wind, rain, visibility)"
  - "Watch UAS (battery, RSSI, GPS, altitude)" → "UAS (battery, RSSI, GPS, altitude)"
  - "Check transmitter battery" → "Transmitter battery"
  - "Watch air traffic (124.3 MHz, FlightRadar24)" → "Air traffic (124.3 MHz, FlightRadar24)"
  - "'LANDING' announced" (unchanged)
  - Reason: Action verbs in titles are redundant; descriptions convey the continuous monitoring action. Titles now focus on the subject matter for faster scanning.
- Moved "preset-altitude RTH" from description to title for vertical separation (swarm/multi-UAS).
  - "Vertical separation" → "Vertical separation: RTH altitude, RTH mode: preset"
  - Reason: Critical safety requirement belongs in the title for swarm/multi-UAS operations to prevent mid-air collisions.  - Reason: titles should be action-oriented and concise; verbs in titles (assess, confirm, check) create cognitive load; descriptions provide context when needed.
  - Exception: "Review contingency and emergency procedures" retained as-is (action verb "review" is essential to title).
- Applied across: first_flight.json, subsequent_flight.json, pre_operation.json

- data/json/00_erp.json
- data/json/01_emergency_procedures.json
- data/json/02_contingency_procedures.json
- data/json/03_first_flight.json
- data/json/04_subsequent_flight.json
- data/json/05_in_flight.json
- data/json/06_post_flight.json
- data/json/07_pre_operation.json
- data/json/08_packing.json
- data/json/09_post_operation.json
