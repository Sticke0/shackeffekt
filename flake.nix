{
  description = "Schackeffekt – statisk webbplats";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
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

        site = pkgs.stdenv.mkDerivation {
          name = "schackeffekt";
          src = pkgs.lib.cleanSourceWith {
            src = ./.;
            filter =
              path: type:
              let
                base = builtins.baseNameOf path;
              in
              !(pkgs.lib.hasPrefix "." base)
              && base != "result"
              && base != "flake.nix"
              && base != "flake.lock";
          };
          buildInputs = with pkgs; [ minify ];
          buildPhase = ''
            mkdir -p "$out"
            minify -o "$out/index.html" index.html
            minify -o "$out/stylesheet.css" stylesheet.css
            cp -r images "$out/"
          '';
          installPhase = "true";
        };

        buildScript = pkgs.writeShellScriptBin "build" ''
          set -e
          mkdir -p dist
          ${pkgs.minify}/bin/minify -o dist/index.html index.html
          ${pkgs.minify}/bin/minify -o dist/stylesheet.css stylesheet.css
          cp -r images dist/
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
            echo "  serve   → python3 -m http.server 8000"
            echo "  dev     → nix run .  (miniserve)"
            echo ""
          '';
        };

        packages.default = site;

        apps.default =
          let
            devServer = pkgs.writeShellScript "dev-server" "${pkgs.miniserve}/bin/miniserve . -p 8000 --index index.html";
          in
          {
            type = "app";
            program = "${devServer}";
          };
      }
    );
}
