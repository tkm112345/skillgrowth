# Security Policy

## Supported versions

skillgrowth is a single rolling release — there's no LTS or backport
policy. Security fixes land on `main` and go out in the next tagged
release. Only the latest release is supported; please upgrade before
reporting an issue that might already be fixed.

## Reporting a vulnerability

Please report security issues privately using [GitHub's private
vulnerability reporting](https://github.com/tkm112345/skillgrowth/security/advisories/new)
for this repository, rather than opening a public issue. If that isn't
available to you, open a regular [issue](https://github.com/tkm112345/skillgrowth/issues)
with as little sensitive detail as possible and ask to be contacted
privately.

Include what you'd include in any good bug report: the affected
version, steps to reproduce, and the impact you'd expect (e.g. what an
attacker could read, modify, or execute).

This is a single-maintainer project — there's no fixed SLA, but reports
are read and acknowledged as soon as possible.

## Scope

skillgrowth is meant to be run as a single-user, self-hosted instance
(see "Design choices" in `README.md`). Reports about the app's behavior
when deliberately exposed to multiple untrusted users, or about the
absence of authentication/multi-tenancy, are expected and out of scope
— that's a documented design choice, not a vulnerability. Reports about
things that go wrong even for the single trusted owner of an instance
(e.g. data exposure to that instance's own frontend, injection, path
traversal, unsafe file handling) are in scope.
