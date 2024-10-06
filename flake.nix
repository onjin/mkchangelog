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
            mkchangelog = mkchangelog;
            hatch = pkgs.hatch;
            ruff = pkgs.ruff;
            mypy = pkgs.mypy;
            black = pkgs.black;
          };
        };
        project =
          pyproject-nix.lib.project.loadPyproject { projectRoot = ./.; };

        mkchangelog = python.pkgs.buildPythonPackage rec {
          pname = "mkchangelog";
          version = "2.4.0";

          src = python.pkgs.fetchPypi {
            inherit pname version;
            sha256 = "";
          };

          doCheck = false;
          checkInputs = [ ];
          propagatedBuildInputs = [ pypkgs.feedparser ];

          meta = with pkgs.lib; {
            homepage = "https://github.com/onjin/mkchangelog";
            description =
              "Generate changelog from git log with convencional commits.";
            license = licenses.mit;
          };
        };

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
            version =
              if (self ? rev) then self.shortRev else self.dirtyShortRev;
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
              pkgs.gnumake
              pkgs.hatch
              pkgs.ruff
              pkgs.mypy
              pkgs.black
              pypkgs.keyrings-alt
            ];
            shellHook = ''
              export PYTHONPATH="$(pwd):$PYTHONPATH"
            '';
          };
        };
      });
}
