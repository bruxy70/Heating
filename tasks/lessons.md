# Heating assessment lessons

## 2026-10-09 — Preserve calibrated TRV offsets

User confirmed 22°C daytime living-room comfort and recalled earlier offset misinterpretation causing repeated temperature reductions.

- Assess comfort using the independent room sensor against the occupant's actual target (living room: 22°C daytime).
- Keep three quantities distinct: desired room temperature, compensated TRV command, and the flow controller's internal comfort/error threshold.
- Deployed TRV code adds the configured per-valve calibration offset to the room target. A higher compensated TRV setpoint is not evidence that the desired room temperature is higher or that the room is overheating.
- Do not subtract calibration offsets from independent room measurements, apply compensation twice, or lower targets/flow solely because compensated TRV commands or internal weighted error appear high.
- The deployed flow controller's fixed 2.5°C comfort subtraction is distinct from per-valve offsets. Trace the complete live calculation before recommending any change; do not assume that subtraction is itself a bug or recalibrate offsets from a snapshot.
- Previous measurements/configuration are evidence leads. Verify the active schedule, actual device command and fresh independent temperature; battery replacement, overrides and sleepy-device reports can confound comparisons.
- Keep all live settings unchanged during this baseline assessment. Evaluate sustained comfort and cycling together before proposing optimization.

Evidence reviewed: deployed `heating-control.py` lines 258–259 and 310–333; `apps.yaml` per-valve offsets; flow-controller calculation lines 829–870; guide calibration section lines 493–511. The exact historical reduction incident was not found in the searched troubleshooting/analysis notes, so retain the user's account explicitly rather than claiming a reconstructed root cause.
