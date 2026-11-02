# Security policy

CodeCrate runs untrusted code, so security reports are very welcome.

## Reporting a vulnerability

Please **don't open a public issue** for security problems. Instead, use GitHub's private reporting: go to the repository's **Security** tab and click **Report a vulnerability**.

Include what you found, how to reproduce it, and the impact you think it has. You should get a reply within a week.

## Scope

In scope: escaping the sandbox container, reaching the network or host filesystem from a run, getting around the time, memory, CPU or process limits, and attacks on the API itself.

Out of scope: the lack of authentication and rate limiting (documented in the README's Security section), and denial of service on a deployment you were not authorised to test.
