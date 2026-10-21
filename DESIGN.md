# Design brief

## Problem and target user

Research/coding agents lose issue evidence across sessions. An operator can import a reviewed public issue export into a project Context Graph, retaining traceable text rather than relying on a previous model summary. No existing customer/user adoption is claimed.

## Working Memory and primitives

Each source revision becomes a named Knowledge Asset with an Entity IRI based on the canonical issue URL and content hash. Context Graph ID is provided explicitly. The importer consumes only the public HTTP API and uses no internal DKG packages. Author metadata is source attribution, distinct from the authenticated local writer. Public source metadata is operator supplied and is not a signed authenticity assertion.

## LLM-Wiki/research fit

The capability is durable attributable evidence capture for later authorized retrieval. Agent workflows can invoke the one-shot CLI; autonomous GitHub monitoring and a full agent-framework adapter are not implemented. Imported issue text never authorizes tool actions. A later agent must treat it as source claims rather than verified truth.

## Promotion path

The current importer writes only Working Memory. It retains source revision hash, URL and timestamps for future Curator-controlled selection into Shared or Verifiable Memory. SHARE/PUBLISH, endorsement and chain verification are not implemented or implied by storage. A future promotion component should preserve named asset linkage and let oracle consumers distinguish source evidence from conclusions; this is a design direction, not a shipped oracle feature.

## Operations and security

Explicit loopback origin, no proxies/redirects, expected caller verification, bounded exports/responses and exclusive durable operation journal. Exact read-back is required for verified status, which means content equality at that moment, not verification of the claims. Mutations are never automatically retried; recovery is documented and manual. No direct runtime external egress beyond the selected local node; the node has its own separately configured network behavior.

## Evidence and limitations

Thirteen automated tests, installed0.1.1 wheel validation on real local DKG10.0.23/mock-chain and actual terminal recording. No production audit, on-chain proof or full crash-injection coverage. Package compatibility and recording format remain questions in OriginTrail/dkg-integrations#36. Candidate has not been submitted for an award. Six-month maintainer and publication identities must be explicitly agreed before any registry undertaking.
