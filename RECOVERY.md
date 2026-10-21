# Inspect a stopped import without duplicating writes

Do not delete a failed journal and rerun the importer with another journal to bypass a conflict. Inspect the last phase, source hash, intended caller, node origin, Context Graph and asset name. Keep tokens out of screenshots and support requests.

- `prepared`: no request is recorded as sent, but an operator must inspect state before reuse.
- `create-outcome-unknown`: creation may have committed. Inspect the named asset with GET; do not blindly POST again.
- `created`: draft creation returned success; no write is recorded as attempted yet.
- `write-outcome-unknown`: data may be present despite lost/partial response. Read the existing asset's WM quads and compare exact evidence against the original export and hash. Do not append or create a replacement merely to get a green result.
- `written-readback-pending`: returned write count matched, but exact read-back was not verified. Perform read-only inspection; absence of an error is not proof of content.
- `verified`: exact read-back matched at that time; it is not perpetual integrity, chain verification, sharing, committee acceptance or payment.

Use the installed node's documented read-only API and exact Context Graph. A mismatch, 401/403, missing asset, malformed response or changed source requires diagnosis; do not broaden permissions or change the source silently. This version deliberately has no automatic resume. Manual reconciliation must record what was observed and which further action was explicitly chosen.
