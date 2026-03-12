{ lib, ... }:

{
  options.composer.localInputOverrides = {
    reposRoot = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      default = null;
      description = "Base directory containing local repos used for generated overrides. When null, defaults to `builtins.dirOf config.devenv.root`.";
    };

    sourcePath = lib.mkOption {
      type = lib.types.str;
      default = "devenv.yaml";
      description = "Source devenv YAML file to scan for inputs and URLs.";
    };

    outputPath = lib.mkOption {
      type = lib.types.str;
      default = "devenv.local.yaml";
      description = "Output path for generated local input override YAML.";
    };

    urlScheme = lib.mkOption {
      type = lib.types.enum [ "path" "git+file" ];
      default = "path";
      description = "URL scheme used for generated local repo overrides.";
    };
  };

  imports = [ ./nix/local-input-overrides ];
}
