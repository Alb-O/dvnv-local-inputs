{ pkgs }:

let
  pythonWithYaml = pkgs.python3.withPackages (ps: [ ps.pyyaml ]);
  localInputOverridesScript = ../../dvnv-local-inputs.py;
in
(
  {
    cfg,
    repoNames,
    repoSources,
    reposRoot,
    sourcePath,
  }:
  if builtins.pathExists sourcePath then
    builtins.readFile (
      pkgs.runCommand "local-input-overrides.yaml" {
        nativeBuildInputs = [ pythonWithYaml ];
        passAsFile = [
          "sourceYaml"
          "repoNamesJson"
          "repoSourcesJson"
        ];
        # Pass larger YAML/JSON payloads via files instead of shell-escaped env.
        sourceYaml = builtins.readFile sourcePath;
        repoNamesJson = builtins.toJSON repoNames;
        repoSourcesJson = builtins.toJSON repoSources;
        reposRoot = reposRoot;
        urlScheme = cfg.urlScheme;
      } ''
        python3 ${localInputOverridesScript} \
          "$sourceYamlPath" \
          "$repoNamesJsonPath" \
          "$repoSourcesJsonPath" \
          "$reposRoot" \
          "$urlScheme" \
          > "$out"
      ''
    )
  else
    ""
)
