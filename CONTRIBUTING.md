# Contributing

OBCS is a community proposal. Changes to normative terms or geometry should be
proposed in an issue before editing SPEC.md. Include a rationale, compatibility
impact, and tests for the reference implementation. Run `uv run ruff check`,
`uv run pytest`, `uv run obcs validate examples/*.yaml`, and
`uv run obcs check-generated` before submitting.

## Measurements

Contributors may submit a measurement issue using the repository form or a
pull request with a YAML record. Identify the exact frame size and BSD, measured
width and rim width, fender and drivetrain conditions, method, instruments,
resolution, date, repeats, uncertainty, and photos. Report observed values,
not inferred clearances, and remove photo location metadata.

All contributions are dedicated to the public domain under CC0 1.0 Universal.

## Name-use policy

Modified versions must not call themselves “OBCS” or claim OBCS conformance
unless they pass the reference test suite. The name may identify the unmodified
specification or reference implementation.
