{
  description = "Upkeep";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    pyproject-nix = {
      url = "github:nix-community/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:adisbladis/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, uv2nix, pyproject-nix, pyproject-build-systems, ... }:
    let
      inherit (nixpkgs) lib;
      forAllSystems = lib.genAttrs lib.systems.flakeExposed;

      wsgiApp = "config.wsgi:application";
      settingsModules = {
        prod = "config.settings";
      };

      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

      overlay = workspace.mkPyprojectOverlay {
        sourcePreference = "wheel";
      };

      editableOverlay = workspace.mkEditablePyprojectOverlay {
        root = "$REPO_ROOT";
      };

      # Python sets grouped per system
      pythonSets = forAllSystems
        (
          system:
          let
            pkgs = nixpkgs.legacyPackages.${system};
            inherit (pkgs) stdenv;

            # Base Python package set from pyproject.nix
            baseSet = pkgs.callPackage pyproject-nix.build.packages {
              python = pkgs.python312;
            };

            # An overlay of build fixups & test additions
            pyprojectOverrides = final: prev: {

              # upkeep is the name of our example package
              upkeep = prev.upkeep.overrideAttrs (old: {

                passthru = old.passthru // {
                  tests =
                    (old.tests or { }) //
                      {

                        mypy =
                          let
                            venv = final.mkVirtualEnv "upkeep-typing-env" {
                              upkeep = [ "typing" ];
                            };
                          in
                          stdenv.mkDerivation {
                            name = "${final.upkeep.name}-mypy";
                            inherit (final.upkeep) src;
                            nativeBuildInputs = [ venv ];
                            dontConfigure = true;
                            dontInstall = true;
                            buildPhase = ''
                              export MYPYPATH=apps
                              mypy . --junit-xml $out/junit.xml
                            '';
                          };

                        pytest =
                          let
                            venv = final.mkVirtualEnv "upkeep-pytest-env" {
                              upkeep = [ "test" ];
                            };
                          in
                          stdenv.mkDerivation {
                            name = "${final.upkeep.name}-pytest";
                            inherit (final.upkeep) src;
                            nativeBuildInputs = [
                              venv
                            ];

                            dontConfigure = true;

                            buildPhase = ''
                              pytest --junit-xml=$out/junit.xml
                            '';
                          };
                      } // lib.optionalAttrs stdenv.isLinux {
                      #
                      nixos =
                        let
                          venv = final.mkVirtualEnv "upkeep-nixos-test-env" workspace.deps.default;
                          secrets = pkgs.writeText "upkeep-test-secrets" ''
                            DEBUG=false
                            DJANGO_DATABASE_URL="sqlite:///tmp/db.sqlite3"
                          '';
                        in
                        pkgs.nixosTest {
                          name = "upkeep-nixos-test";

                          nodes.machine = { ... }:
                            {
                              imports = [
                                self.nixosModules.default
                              ];

                              services.upkeep = {
                                enable = true;
                                inherit venv;
                                secrets = [ secrets ];
                                port = 8001;
                              };

                              system.stateVersion = "24.11";
                            };

                          testScript = ''
                            with subtest("Check upkeep app comes up"):
                              machine.wait_for_unit("upkeep.service")
                              machine.wait_for_open_port(8001)

                            with subtest("Staticfiles are generated"):
                              machine.succeed("curl -sf http://localhost:8001/static/ui/main.css")

                            with subtest("Home page is live"):
                              machine.succeed("curl -sLf http://localhost:8001/ | grep 'Upkeep'")
                          '';
                        };
                    };
                };
              });

            };

          in
          baseSet.overrideScope (
            lib.composeManyExtensions [
              pyproject-build-systems.overlays.default
              overlay
              pyprojectOverrides
            ]
          )
        );

      # Django static roots grouped per system
      staticRoots = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          inherit (pkgs) stdenv;

          pythonSet = pythonSets.${system};

          venv = pythonSet.mkVirtualEnv "upkeep-env" workspace.deps.default;

        in
        stdenv.mkDerivation {
          name = "upkeep-static";
          inherit (pythonSet.upkeep) src;

          dontConfigure = true;
          dontBuild = true;

          nativeBuildInputs = [
            venv
          ];

          installPhase = ''
            export DJANGO_STATIC_ROOT="$out"
            upkeep-manage collectstatic
          '';
        }
      );

    in
    {
      checks = forAllSystems
        (
          system:
          let
            pythonSet = pythonSets.${system};
          in
          # Inherit tests from passthru.tests into flake checks
          pythonSet.upkeep.passthru.tests
        );

      nixosModules = {
        default = { config, lib, pkgs, ... }:
          let
            cfg = config.services.upkeep;
            inherit (pkgs) system;

            pythonSet = pythonSets.${system};

            inherit (lib.options) mkOption;
            inherit (lib.modules) mkIf;
          in
          {
            options.services.upkeep = {
              enable = mkOption {
                type = lib.types.bool;
                default = false;
                description = ''
                  Enable Upkeep
                '';
              };

              port = lib.mkOption {
                type = lib.types.port;
                description = "Proxy port";
                default = 8000;
              };

              settings-module = mkOption {
                type = lib.types.str;
                default = settingsModules.prod;
                description = ''
                  Django settings module for Upkeep
                '';
              };

              venv = mkOption {
                type = lib.types.package;
                default = pythonSet.mkVirtualEnv "upkeep-env" workspace.deps.default;
                description = ''
                  Upkeep virtual environment package
                '';
              };

              static-root = mkOption {
                type = lib.types.package;
                default = staticRoots.${system};
                description = ''
                  Upkeep static root
                '';
              };

              secrets = lib.mkOption {
                type = with lib.types; listOf path;
                description = ''
                  A list of files containing the various secrets. Should be in the format
                  expected by systemd's `EnvironmentFile` directory.
                '';
                default = [ ];
              };
            };

            config = mkIf cfg.enable {
              systemd.services.upkeep = {
                description = "upkeep server";

                environment = {
                  DJANGO_SETTINGS_MODULE = cfg.settings-module;
                  DJANGO_STATIC_ROOT = cfg.static-root;
                };

                serviceConfig = {
                  EnvironmentFile = cfg.secrets;
                  ExecStartPre = "${cfg.venv}/bin/upkeep-manage migrate --no-input";
                  ExecStart = ''
                    ${cfg.venv}/bin/gunicorn --bind 127.0.0.1:${toString cfg.port} ${wsgiApp}
                  '';
                  Restart = "on-failure";

                  DynamicUser = true;
                  StateDirectory = "upkeep";
                  RuntimeDirectory = "upkeep";

                  BindReadOnlyPaths = [
                    "${
                      config.environment.etc."ssl/certs/ca-certificates.crt".source
                    }:/etc/ssl/certs/ca-certificates.crt"
                    builtins.storeDir
                    "-/etc/resolv.conf"
                    "-/etc/nsswitch.conf"
                    "-/etc/hosts"
                    "-/etc/localtime"
                  ];

                  RestrictAddressFamilies = "AF_UNIX AF_INET";
                  CapabilityBoundingSet = "";
                  SystemCallFilter = [ "@system-service" "~@privileged @setuid @keyring" ];
                };

                wantedBy = [ "multi-user.target" ];
              };
            };

          };

      };

      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pythonSet = pythonSets.${system};
        in
        {
          default =
            let
              venv = pythonSet.mkVirtualEnv "upkeep-env" workspace.deps.default;
            in
            pkgs.writeShellApplication {
              name = "manage";
              text = ''
                if [ "$UID" -ne 0 ]; then
                    echo "error: run this command as root."
                    exit 1
                fi
                sudo -u upkeep env DJANGO_DATABASE_URL=postgres:///upkeep ${venv}/bin/upkeep-manage "$@"
              '';
            };

          static = staticRoots.${system};
        } //
        lib.optionalAttrs pkgs.stdenv.isLinux {
          # Expose Docker container in packages
          docker =
            let
              venv = pythonSet.mkVirtualEnv "upkeep-env" workspace.deps.default;
            in
            pkgs.dockerTools.buildLayeredImage {
              name = "upkeep";
              contents = [ pkgs.cacert ];
              config = {
                Cmd = [
                  "${venv}/bin/gunicorn"
                  wsgiApp
                ];
                Env = [
                  "DJANGO_SETTINGS_MODULE=${settingsModules.prod}"
                  "DJANGO_STATIC_ROOT=${staticRoots.${system}}"
                ];
              };
            };
        }
      );

      apps = forAllSystems
        (
          system: {
            default = {
              type = "app";
              program = "${self.packages.${system}.default}/bin/manage";
            };
          }
        );

      # Use an editable Python set for development.
      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          editablePythonSet = pythonSets.${system}.overrideScope editableOverlay;
          venv = editablePythonSet.mkVirtualEnv "upkeep-dev-env" workspace.deps.all;
          uv = uv2nix.packages.${system}.uv-bin;
          packages = [
            pkgs.just
            pkgs.nodejs
            pkgs.pre-commit
            uv
          ];
        in
        {
          impure = pkgs.mkShell {
            inherit packages;
          };

          default = pkgs.mkShell {
            packages = packages ++ [ venv ];
            shellHook = ''
              unset PYTHONPATH
              export REPO_ROOT=$(git rev-parse --show-toplevel)
              export UV_NO_SYNC=1
            '';
          };
        }
      );
    };
}
