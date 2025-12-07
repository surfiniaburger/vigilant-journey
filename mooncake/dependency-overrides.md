# Dependency Overrides

This document explains the reasons for the `overrides` configured in `package.json`.

## `js-yaml`

- **Package**: `js-yaml`
- **Override**: `^4.1.0`
- **Reason**: A security vulnerability was identified in versions of `js-yaml` below `4.1.0`. The `yaml.load()` function is unsafe and can lead to arbitrary code execution. To mitigate this risk across all transitive dependencies, we are enforcing a minimum version of `4.1.0`.

## `safer-buffer`

- **Package**: `safer-buffer`
- **Override**: `npm:safe-buffer@^5.2.1`
- **Reason**: The `safer-buffer` package is deprecated and was flagged by security scanners for containing potentially obfuscated code. We have overridden it with `safe-buffer`, which is the official and recommended replacement. This resolves the security warning and ensures we are not using a deprecated package.
