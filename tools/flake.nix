{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { nixpkgs, ... }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in {
    devShells.${system}.default = pkgs.mkShell {
      packages = with pkgs; [
        stdenv.cc.cc.lib
        (python3.withPackages (ps: with ps; [
          virtualenv
        ]))

        (rstudioWrapper.override { packages = with rPackages; [
          plyr
          shiny
          dplyr
          rjson
          ggplot2
          plotly
          data_table
          DT
          tidyr
          scales
          flexdashboard
        ]; })
      ];

      # Without this, jupyter-notebook complains about stdlibc++.so.6
      LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
    };
  };
}
