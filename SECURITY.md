# Security Policy

## Supported Versions

The following versions of the Physiology Video Translator are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a potential security vulnerability in this project, please report it by opening an issue with the [Security] prefix or by emailing the project maintainers.

We will acknowledge your report within 48 hours and provide an estimated timeline for a fix if necessary. Please do not disclose the vulnerability publicly until a fix is released.

## Dependency Security
This project relies on several third-party AI and multimedia libraries. We use `uv.lock` to pin dependencies and reduce the risk of supply chain attacks. It is recommended to keep your environment synchronized using `uv sync`.
