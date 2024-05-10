{ pkgs ? import <nixpkgs> {} }:
let
  my-python-packages = ps: with ps; [
    # find-libpython
    # dbus-python
      psycopg2
      pyparsing
      sqlparse

      ipykernel

      notebook
      jupyter-core
      # jupyter-contrib-core

    # jupyter-lab
        jupyter-server

  ];
  my-python = pkgs.python3.withPackages my-python-packages;
# in my-python.env
in pkgs.mkShell {
  packages = [
      my-python
      pkgs.nodePackages.pyright
  ];
}
