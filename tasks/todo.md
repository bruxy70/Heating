# Heating assessment — 2026-10-09

Read-only assessment of deployed controls and history. No heating settings, services, or deployments will change.

- [x] Verify earlier low-temperature experiments and emitter limitations.
- [x] Capture today's room comfort, boiler flow/return, burner and demand history.
- [x] Separate seasonal startup, maintenance/DHW, burner cycling and controller shutdowns.
- [x] Save a baseline and repeatable 48–72 hour review criteria.

Verification: use dated live states and history, cross-check counters against burner transitions and controller logs, and distinguish measurements from inferred demand/efficiency.

## Follow-up action items — 11–12 October 2026

- [ ] Confirm battery replacements are complete and room/valve readings are fresh, especially WC.
- [ ] Export the next 48–72 hours of history and exclude maintenance, service mode, DHW and unavailable periods from normal-heating comparisons.
- [ ] Assess living-room comfort against **22°C daytime using the independent room sensor**, preserving calibrated TRV offsets.
- [ ] Compare room recovery, time below target, evening/night comfort and overshoot; assess gallery and bedroom separately.
- [ ] Compare heating-specific starts, burner runtime and short runs with actual flow/return, minimum modulation, outdoor conditions and solar gains.
- [ ] Decide whether the current automatic low-flow operation maintains comfort before proposing any settings change; change one variable at a time if a later trial is justified.

The user will request the follow-up; no reminder or scheduled job has been created.

## Review

Saved `heating-assessment-2026-10-09.md` and timestamped live-state/history JSON. Cross-checked burner starts, gas transitions, DHW/service codes, controller state and room data freshness. Multi-day comfort and normal cycling remain open for follow-up; no live mutations made.

User confirmed 22°C living-room daytime comfort. Reviewed deployed offset addition and distinct flow-controller threshold; recorded safeguards against offset misinterpretation in `lessons.md` and updated baseline interpretation. No live settings changed.
