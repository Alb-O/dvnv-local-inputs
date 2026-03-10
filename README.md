# Local Input Overrides

Reusable `devenv` module that generates `devenv.local.yaml` with local path overrides
for inputs in `devenv.yaml` whose remote repo name matches a local directory name
under `composer.localInputOverrides.reposRoot`.

It also walks local repos transitively. If repo `A` imports local repo `B`, and
`B` imports local repo `C`, then `A`'s generated `devenv.local.yaml` will include
overrides for both `B` and `C`.

## Includes

- `composer.localInputOverrides.*` options
- Materialized file: `devenv.local.yaml` (configurable)
- Output: `outputs.local_input_overrides`

## Notes

- Recursive scanning reuses the same `sourcePath` inside each local repo.
- That works best with the default `devenv.yaml`, or another repo-relative path
  shared across the repos in your polyrepo.
- Existing stale `devenv.local.yaml` files still need one refresh before the new
  transitive overrides can affect evaluation.

## Use

```yaml
inputs:
  dvnv-local-inputs:
    url: github:Alb-O/dvnv-local-inputs
    flake: false
imports:
  - dvnv-local-inputs
```
