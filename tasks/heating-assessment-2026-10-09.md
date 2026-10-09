# Heating baseline — 9 October 2026

Scope: read-only assessment. Captured HA REST live state and recorder history at approximately 11:46 Europe/Prague. Read deployed AppDaemon configuration, source and mounted logs. No live settings, code or services changed. Raw evidence: `heating-states-2026-10-09.json`, `heating-history-2026-10-09.json`.

## Today's evidence

- Heating mode changed Léto → Doma at 08:00:02; heating enabled at 08:00:05. Initial burner operation was domestic hot water (08:00–08:20); space heating began 08:23:37.
- The controller requested 44–46°C during initial space heating, 40°C at 10:01, 38°C at 10:53 and 36°C at 11:03. Log `Flow` is requested flow, not actual measured flow. Boiler selected-flow history also includes DHW/service overrides (84°C/70°C); these must not be interpreted as ordinary heating-curve requests.
- Snapshot: outdoors 8.5°C, actual flow 36.4°C, independently measured return 34.6°C, burner modulation 10%, water flow 1,091 L/h, pump modulation 83%, pressure 1.5 bar. These are a snapshot, not a daily efficiency measurement.
- `switch.heating_activated` has no recorded off transition after activation; two unavailable intervals exist. `sensor.heating_system_state` remained active. No evidence of repeated controller shutdown/restart cycling in the observed interval.
- Burner starts increased 4,260 → 4,270; heating-specific starts 2,314 → 2,320. Do not report all ten as normal heating cycles. Four starts coincide with DHW periods. The maintenance cluster contains service code 208 at 10:21 and 10:28, 70°C selected-flow overrides, and boiler data outages at 10:04–10:12 and 10:17. It cannot establish steady-state short cycling.
- The first space-heating on segment was 08:23–10:04, interrupted by telemetry loss rather than a recorded off state. It was on again at 10:12. A clean later run lasted 10:29:45–11:11:26 (~42 minutes). DHW then ran until 11:17; heating resumed at 11:39. The 11:17–11:39 pause may include DHW recovery/boiler anti-cycle behavior; observe further before assigning a cause.

| Room | Temperature at baseline | Day schedule helper | Caveat |
|---|---:|---:|---|
| Living room | 21.99°C | 22°C | No recorder changes until 10:01 after the midnight seed; morning warm-up rate cannot be inferred |
| Gallery | 23.5°C | 22°C | Hourly readings; 21.3°C at 08:01 and 23.6°C at 10:01 |
| Bedroom | 21.64°C | 23°C | 20.58°C at 08:05; warming, below day helper |
| Office | 20.91°C | 21°C | Active TRV target is 19°C, differs from day helper |
| Jakub | 23.01°C | 22°C | Above day helper |
| Klára | 23.10°C | 22°C | Active TRV target is 20°C, differs from day helper |

User confirmed the living-room daytime comfort target is **22°C**. Compare the independent living-room sensor directly against 22°C. Preserve measured per-valve calibration: deployed TRV code adds each valve's configured offset to the desired room temperature. Compensated TRV targets and the flow controller's separate fixed 2.5°C subtraction must not redefine the occupant's comfort target or justify repeated temperature reductions. Other room targets still need interpretation against schedules and occupants' experience. See `lessons.md`. Solar radiation was 178 W/m² at capture; gallery warming cannot be attributed solely to heating.

## Control and measurement limits

Deployed `apps.yaml` minimum flow is 33°C (comment: previously 30°C, raised for recovery). Boiler heating-curve endpoints currently read 38°C and 53°C. Controller publishes base 44.6°C, weather −0.3°C, room adjustment −8.6°C and active system state. Requested 36°C follows those components with rounding/hysteresis.

Live curve values subsequently verified: +16°C outdoor → 38°C base flow; −1°C outdoor → 53°C base flow. Linear extrapolation raises flow by approximately 0.88°C for each 1°C outdoor drop. The controller applies weather/room adjustments and a 33°C minimum. The live boiler maximum heating temperature is 70°C; 53°C is a curve pivot, not the maximum. No curve or limit changes were made.

The controller computes room error from **TRV target minus a fixed 2.5°C**, rather than directly comparing room temperature to the day helper. It reports +3.17°C weighted warmth while the bedroom remains below its 23°C helper. Office and WC are omitted from its eight area-weighted entries. Living-room TRV targets currently differ (21°C, 21°C, 23.5°C), and TRV current temperatures are null. Valve opening is not measured by these climate entities. A high TRV target, inferred demand or throttling score does not prove physical valve travel.

WC radiator battery is reported at 10%; its room temperature 20.97°C has not updated since 8 October 07:33 local. Treat it as stale until it reports again. Battery replacement in progress is a confounder: compare stable operation after replacements, not maintenance/recovery periods.

`sensor.heating_efficiency` is a formula-based score, not measured boiler efficiency. The daily energy/gas-counter ratio reads 118.3%; do not accept it as calibrated efficiency. Prefer measured return, counters over longer matched periods, and cycle/runtime data. The estimated return sensor is unnecessary for this baseline because an actual return sensor is available.

## Previous research verification

The deployed guide records a 4 February experiment: approximately 0°C outside, 46–52°C flow, open-space TRV targets set to 28°C for four hours. Living room changed 19.8→20.0°C and gallery 20.6→20.7°C. This supports limited response to raising TRV targets under those conditions. It does not prove that 30–40°C fails in mild October weather, nor verify actual full valve opening. Source: `/Volumes/config/docs/heating-flow-temperature-control-guide.md`, lines 628–648.

The guide's equilibrium and required-flow conclusions are stronger than the experiment establishes. Its regression text also conflicts with its flow-dominance claim and contains inconsistent arithmetic (lines 683–691). Do not reuse the claimed required 52–55°C flow as an established comfort threshold.

Documentation names KORATHERM radiators and a floor convector, rather than a verified bathroom-only model inventory. KORADO markets KORATHERM for living spaces. Actual model, dimensions, water temperatures and room heat loss are needed to establish emitter capacity. A capacity limitation remains plausible, not proven.

## Follow-up in 48–72 hours

Existing recorder logging already captures the required signals. No additional live automation or scheduled job was installed. Export the next history before retention expires when the user requests follow-up.

1. Analyse stable periods after boiler service/battery replacement. Separate startup, day/night, away, DHW, service mode, outages and fireplace use.
2. Compare room measurements with agreed comfort targets: time below target minus 0.5°C, hours to recover, temperature trend and overshoot. Track living room separately from gallery and bedrooms; flag stale data.
3. Count heating-specific starts per valid observation hour, burner-on/off durations, median runtime and completed runs under five minutes. Cross-check gas transitions, heating-active signal, DHW exclusions and cumulative counters; do not bridge outages as known state.
4. Compare requested/actual flow, actual return, minimum modulation, pump and water flow during heating-only periods. Persistent short runs at minimum modulation suggest low heat absorption relative to boiler minimum output; this does not alone identify excessive flow temperature.
5. Relate comfort/cycles to outdoor temperature, solar gains and room/house modes. First assess whether automatic 33–40°C operation maintains living-room comfort over evenings/nights. A later controlled flow adjustment should change one variable at a time and preserve comfort, without repeating unsupported historical assumptions.

Sources: [Worcester Bosch on return temperature and condensing](https://www.worcester-bosch.co.uk/professional/news/how-to-ensure-boilers-condense-what-installers-need-to-know), [KORADO living-room radiators](https://www.korado.com/living-room), [KORADO output selection](https://www.korado.com/koralux-standard?operation_mode=2).

Conclusion: baseline established. Lower-temperature operation is already occurring and living-room temperature is currently around the 22°C scheduled target. Today is insufficient to establish sustained comfort, normal cycle rate, emitter sizing or comparative gas savings. Leave settings unchanged pending stable multi-day evidence.
