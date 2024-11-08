{
  description = "Generate changelog from git log with convencional commits.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    pyproject-nix.url = "github:nix-community/pyproject.nix";
    pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, pyproject-nix, }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pypkgs = pkgs.python3Packages;
        python = pkgs.python3.override {
          packageOverrides = self: super: {
            hatch = pkgs.hatch;
            ruff = pkgs.ruff;
            mypy = pkgs.mypy;
            black = pkgs.black;
          };
        };
        project =
          pyproject-nix.lib.project.loadPyproject { projectRoot = ./.; };

      in {
        packages = {
          mkchangelog = let
            # Returns an attribute set that can be passed to `buildPythonPackage`.
            attrs = project.renderers.buildPythonPackage {
              inherit python;
              extras = [ ];
            };
            # Pass attributes to buildPythonPackage.
            # Here is a good spot to add on any missing or custom attributes.
          in python.pkgs.buildPythonPackage (attrs // {
            # Because we're following main, use the git rev as version
            version = "0.0.0.dev+local";
            # version = if (self ? rev) then self.shortRev else self.dirtyShortRev;
          });
          default = self.packages.${system}.mkchangelog;
        };
        devShells = {
          default = let
            # Returns a function that can be passed to `python.withPackages`
            arg = project.renderers.withPackages {
              inherit python;
              extras = [ ];
            };

            # Returns a wrapped environment (virtualenv like) with all our packages
            pythonEnv = python.withPackages arg;

            # Create a devShell like normal.
          in pkgs.mkShell {
            packages = [
              self.packages.${system}.mkchangelog
              pythonEnv
              pkgs.black
              pkgs.curl
              pkgs.gnumake
              pkgs.hatch
              pkgs.jq
              pkgs.mypy
              pkgs.ruff
              pypkgs.hatch-vcs
              pypkgs.keyrings-alt
              pypkgs.pip
            ];
            shellHook = ''
              export PYTHONPATH="$(pwd):$PYTHONPATH"
            '';
          };
        };
      });
}
