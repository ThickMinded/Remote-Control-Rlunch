{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.pip
    pkgs.xorg.libX11
    pkgs.xorg.libXtst
    pkgs.xorg.libXext
    pkgs.xorg.libXrandr
    pkgs.tk
    pkgs.tcl
    pkgs.xdotool
    pkgs.xvfb-run
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.xorg.libX11
      pkgs.xorg.libXtst
      pkgs.xorg.libXext
      pkgs.xorg.libXrandr
    ];
    DISPLAY = ":99";
  };
}
