# Security Policy

## Supported versions

Only the latest released version of {{PROJECT_NAME}} is supported with security fixes.

## Reporting a vulnerability

If you discover a security vulnerability, please **do not** open a public issue.
Instead, email the author privately:

{{AUTHOR}} <{{EMAIL}}>

Please include:
- a description of the issue and its impact,
- the steps to reproduce it,
- any suggested mitigations.

You will receive an acknowledgment within 72 hours.

## Scope

This tool is for authorized security testing, education, and CTF use only.
Any offensive command (port scanner, directory buster, payload generator,
reverse-shell helper) must only be run against systems you own or are
explicitly authorized to test.

## Encryption caveat

The bundled symmetric encryption uses PBKDF2-HMAC-SHA256 with a SHA-256
keystream and an HMAC-SHA256 integrity tag. It is a real, reversible cipher
but is **not** a vetted standard like AES — do not use it to protect
high-value secrets.