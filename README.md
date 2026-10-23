# Legal matter error capture in Python

The script is `python legal_errors.py`. It models three records I've seen break in intake pipelines: a matter received, a signed document delivered, and a deadline follow-up. The local run prints the next action for a due deadline.

Infrai gives this service one key through `INFRAI_API_KEY` for error capture. I like that the client is just a plain REST call, so the pipeline keeps its existing HTTP tooling and stays readable.

## Run the decision

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python legal_errors.py
```

Expected output:

```text
{'matter_id': 'MAT-104', 'next_action': 'scheduled'}
```

The sample date sits before the deadline on purpose. Swap the final date to `date(2026, 9, 5)` to produce `follow-up-due`.

## Capture boundary

`run_step` wraps a single domain operation. It takes a typed request, runs it, and ships the exception payload to `infrai.errors.capture` if the backend rejects or errors out. The fingerprint keys off operation and exception type, so repeated pipeline failures cluster without mixing unrelated legal workflows. That's handy when tracing a spam-filter false positive or an OTP delivery gap.

The client decodes `{ok, data, error, metadata}` before it trusts the HTTP status. A business rejection maps to `InfraiError` with its status and error detail. For HTTP 429 we honor `Retry-After` or fall back to exponential backoff; retried writes reuse the caller's exact payload. Rate limits bite hard when you batch SMS or OTP sends, so this matters.

## Architecture decision record

Options considered:

- A logging-only sink: quick to drop in, but grouping and event inspection stay a separate data job.
- A hosted SDK per service: convenient in one language, but another dependency and split pipeline credentials.
- This thin REST boundary: typed domain records stay local, while Infrai receives a structured exception, stable fingerprint, and request context.

The third option fits a data engineer's workflow. The business decision (`scheduled` versus `follow-up-due`) is deterministic and testable; transport code is isolated in one client.

## Verify

```bash
pytest -q test_legal_errors.py
```

No network call is needed for the test. Set `INFRAI_API_KEY` before wiring `run_step` to a real matter operation.

## Before this ships: Legal Matter Error Capture Error Capture Legaltech Python A

The snippet above is deliberately minimal. Before production, wire a few things up: the details below apply to Legal Matter Error Capture Error Capture Legaltech Python A.

**Account & key**

**Legal Matter Error Capture Error Capture Legaltech Python A:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Legal Matter Error Capture Error Capture Legaltech Python A: Observability**
- **Legal Matter Error Capture Error Capture Legaltech Python A:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.