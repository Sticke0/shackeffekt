{
  description = "Schackeffekt – statisk webbplats";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        site = pkgs.stdenv.mkDerivation {
          name = "schackeffekt";
          src = ./src;
          buildInputs = with pkgs; [ minify python3 ];
          buildPhase = ''
            python3 build.py
            minify -o "$out/index.html" index.html
            minify -o "$out/stylesheet.css" stylesheet.css
            cp -r images "$out/"
          '';
          installPhase = "true";
        };

        buildScript = pkgs.writeShellScriptBin "build" ''
          set -e
          python3 src/build.py --out dist
          ${pkgs.minify}/bin/minify -o dist/index.html dist/index.html
          ${pkgs.minify}/bin/minify -o dist/stylesheet.css src/stylesheet.css
          cp -r src/images dist/
          echo "Built to ./dist/"
        '';
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            miniserve
            minify
            python3
            entr
            nixpkgs-fmt
            buildScript
          ];

          shellHook = ''
            echo "🏁 Schackeffekt dev shell"
            echo ""
            echo "  build   → minifiera HTML+CSS till ./dist/"
            echo "  serve   → python3 -m http.server 8000"
            echo "  dev     → nix run .  (miniserve)"
            echo ""
          '';
        };

        packages.default = site;

        apps.default = let
          devServer = pkgs.writeShellScript "dev-server"
            "${pkgs.miniserve}/bin/miniserve src -p 8000";
        in {
          type = "app";
          program = "${devServer}";
        };
      }
    );
}
