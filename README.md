# Hermes Active Sessions Plugin

Portable plugin for listing active sessions in the current Hermes profile.

Commands:

```text
hermes sessions-active
hermes sessions-active --json
/sessions-active
/sessions-active json
```

It reads the selected profile's `runtime/active_sessions.json` and optionally reads `$HERMES_HOME/busytime.json` when the busytime plugin is installed. Missing busytime data is reported as zero.

The exact nested spelling `hermes sessions active` requires a separate core alias patch because the current public plugin API registers top-level commands only.
