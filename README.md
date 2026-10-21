# GitHub evidence to DKG Working Memory

A small Python CLI that imports a reviewed public GitHub issue JSON export into a named Knowledge Asset in an existing local DKG Context Graph. It preserves source URL, author, timestamps and a versioned SHA256 identifier. Source text is treated as untrusted evidence.

## Scope

One-shot local import over the public HTTP API. No GitHub polling, automatic SHARE/PUBLISH, chain transaction, model API or runtime third-party network request. Public visibility metadata must be independently reviewed by the operator. Python3.9+, no runtime dependencies. This is an early integration candidate, not an accepted bounty or production-audited product.

## Install and prepare

From a reviewed local source checkout:

    python3 -m venv .venv
    .venv/bin/python -m pip install .
    .venv/bin/dkg-prepare-issue issue.json --context-graph EXACT_GRAPH_ID

The JSON needs html_url, title, body, created_at, updated_at, user.login and repository.full_name/private=false. Input limit256KiB. Use synthetic or verified public data only.

## Import

Start your own authorized local DKG node, create a Context Graph, verify its identity and provide its token in DKG_AUTH_TOKEN without printing it. Then:

    .venv/bin/dkg-import-issue issue.json --context-graph EXACT_GRAPH_ID --expected-author EXPECTED_AGENT_ADDRESS --journal new-operation.json --node-url http://127.0.0.1:19240

Each run requires a new journal; do not delete/recreate journals to bypass a failed operation. Conflicting assets, partial writes, lost responses and mismatched read-back stop execution. See RECOVERY.md. This tool does not install or initialize a DKG node or obtain tokens/funding.

## Validation

    python3 -m unittest discover -v

Thirteen local tests cover input handling and HTTP failure boundaries. Installed wheel0.1.1 was tested outside the source directory against real DKG10.0.23 with embedded storage and mock chain: exact eight-quad read-back passed. See installed-cli-validation-0.1.1.json. demo-0.1.1.cast is an actual asciicast-v2 terminal recording. Neither proves peer replication, mainnet verification, committee acceptance or payment.

See SECURITY.md and DESIGN.md for authority and provenance limitations. No maintainer identity or long-term service promise is assigned by this local publication candidate; those require separate approval before submission. MIT license is proposed for the public release. No package registry release exists yet.
