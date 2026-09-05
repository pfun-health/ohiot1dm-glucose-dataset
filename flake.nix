{
  description = "OhioT1DM glucose dataset — LSTM and CMA model dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
        pythonVersion = pkgs.python312;
      in
      {
        devShells.default = pkgs.mkShell {
          name = "ohiot1dm-glucose-dataset";

          packages = [
            pkgs.uv
            pythonVersion

            # System libraries required by some Python packages
            pkgs.stdenv.cc.cc
            pkgs.zlib
            pkgs.libffi
            pkgs.openssl
          ];

          shellHook = ''
            echo "OhioT1DM Glucose Dataset — dev shell"
            echo "Python: $(python3 --version)"
            echo "uv: $(uv --version)"
            echo ""
            echo "Run 'uv sync --dev' to install all dependencies."
            echo "Run 'uv run jupyter lab notebooks/' to launch Jupyter Lab."
            echo ""

            # Prevent uv from downloading its own Python; use the nixpkgs one.
            export UV_PYTHON_PREFERENCE="only-system"
            export UV_PYTHON="${pythonVersion}/bin/python3"

            # Silence the numba threading layer warnings that arise on some
            # systems when importing pfun-cma-model without a GPU.
            export NUMBA_THREADING_LAYER="workqueue"

            # manylinux torch wheels need libstdc++ from the nix toolchain
            export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"
          '';
        };
      }
    );
}
