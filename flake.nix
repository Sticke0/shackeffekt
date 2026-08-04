{
  description = "Schackeffekt – statisk webbplats";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };

        minifySite = dir: ''
          find "${dir}" -type f \( -name '*.html' -o -name '*.css' \) -exec ${pkgs.minify}/bin/minify -i '{}' \;
        '';

        site = pkgs.stdenv.mkDerivation {
          name = "schackeffekt";
          src = ./src;
          buildInputs = with pkgs; [ minify ];
          buildPhase = ''
            mkdir -p "$out"
            cp -r . "$out/"
            ${minifySite "$out"}
          '';
          installPhase = "true";
        };

        buildScript = pkgs.writeShellScriptBin "build" ''
          set -e
          rm -rf dist
          mkdir -p dist
          cp -r src/. dist/
          ${minifySite "dist"}
          echo "Built to ./dist/"
        '';
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            miniserve
            minify
            entr
            buildScript
          ];

          shellHook = ''
            echo "🏁 Schackeffekt dev shell"
            echo ""
            echo "  build   → minifiera HTML+CSS till ./dist/"
            echo "  serve   → (cd src && python3 -m http.server 8000)"
            echo "  dev     → nix run .  (miniserve ./src)"
            echo ""
          '';
        };

        packages.default = site;

        apps.default =
          let
            devServer = pkgs.writeShellScript "dev-server" "${pkgs.miniserve}/bin/miniserve ./src -p 8000 --index index.html";
          in
          {
            type = "app";
            program = "${devServer}";
          };
      }
    );
}
