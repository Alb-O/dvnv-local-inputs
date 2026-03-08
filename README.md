# Local Input Overrides

Reusable `devenv` module that generates `devenv.local.yaml` with local path overrides
for matching inputs in `devenv.yaml`.

## Includes

- `materializer.localInputOverrides.*` options
- Materialized file: `devenv.local.yaml` (configurable)
- Output: `outputs.materialized_local_input_overrides`

## Use

```yaml
inputs:
  env-local-overrides:
    url: github:Alb-O/env-local-overrides
    flake: false
imports:
  - env-local-overrides
```
