# Earnings forecast task

Research exactly one company using the frozen local corpus under `challenge/offline-data/` and return the requested JSON object. Do not edit any files.

## Required method

1. Read the company metadata and identify the exact period, metric labels and units.
2. Start with the newest relevant company index entries, filings, earnings-call presentation/Q&A and slides. Prefer primary reported figures and management guidance.
3. Verify each critical number in its cited document. Keep quarterly versus annual, GAAP versus adjusted, percentage points versus decimals, and pence versus pounds separate.
4. For every requested metric, establish a comparable baseline and calculate the forecast. Do not merely assert a number. State a compact arithmetic formula that connects the baseline and adjustments to the final value.
5. Cross-check the three forecasts for economic consistency. Use restrained assumptions when evidence is weak.
6. Include bear and bull values around the selected point forecast. `bear` must be less than or equal to `value`, which must be less than or equal to `bull`.
7. Cite local source paths, publication dates, public source URLs when present in the document header, and short supporting excerpts. Every forecast must reference evidence IDs that exist.

## Quality bar

- Use the exact metric labels and units supplied in the task.
- The requested period is an upcoming or not-yet-reported period; never substitute an already reported period.
- Prefer recent directly comparable periods and explicit company guidance over generic macro commentary.
- Treat search matches as leads, not verified evidence.
- Record uncertainty and specific risks honestly.
- Output only the schema-conforming result.
