# Security and authority

This prototype accepts a reviewed local GitHub export and writes only to local DKG Working Memory. It does not fetch GitHub, execute issue text, call SHARE/PUBLISH, fund wallets, or provide chain verification. Public visibility flags are supplied metadata, not independently verified proof. Operators must inspect source data before importing.

## Credentials and network

The only credential is DKG_AUTH_TOKEN in process environment; it is not written to the operation journal or printed. The expected caller identity must be provided and checked before mutations. The HTTP origin must use literal loopback (127.0.0.1 or ::1); proxies and redirects are refused. A malicious local service can still impersonate an endpoint if the operator selects the wrong port: use only an owned, authenticated node. DKG's own peer/chain behavior is separate from the importer and must be configured by its operator.

No third-party network egress is performed by the importer. Node HTTP calls: GET /api/agent/identity, POST /api/knowledge-assets, POST /api/knowledge-assets/{name}/wm/write, GET /api/knowledge-assets/{name}/wm/quads. Source exports capped at 256 KiB; responses capped at 1 MiB; request timeout 20 seconds. This is not a comprehensive denial-of-service guarantee.

## Mutation and recovery

Every run requires a new exclusive journal path. The journal records source hash, Context Graph, local node origin, expected author, asset name and last phase. Before a mutation, its outcome is durably marked unknown. Repeated journal use, conflicting existing assets, partial responses, malformed counts and read-back mismatch stop the run. No mutation is automatically retried. See RECOVERY.md before repeating any failed operation.

## Known limitations

No production security audit, crash-injection testing, untrusted local filesystem defense, end-to-end permission matrix or full automated coverage measurement. Tests with synthetic HTTP failures are distinct from real-node tests. No signed-export authentication. No seamless update/delete or resume workflow. The proof-of-concept must not be treated as an unattended ingestion daemon.

Private node state, tokens, keys, wallet files, local journals and raw daemon logs are excluded from review/publication archives. Reported local validation used mock chain, not mainnet or actual consensus verification. Maintainer identity and disclosure contact are not assigned yet; they must be chosen before publication.
