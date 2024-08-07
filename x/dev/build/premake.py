"""
https://premake.github.io/docs/What-Is-Premake

workspace "MyWorkspace"
   configurations { "Debug", "Release" }

project "MyProject"
   kind "ConsoleApp"
   language "C++"
   files { "**.h", "**.cpp" }

   filter { "configurations:Debug" }
      defines { "DEBUG" }
      symbols "On"

   filter { "configurations:Release" }
      defines { "NDEBUG" }
      optimize "On"
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


class Workspace(dc.Frozen, lang.Final, kw_only=True):
    name: str
    filename: str | None = None
    location: str | None = None
    configurations: ta.Sequence[str] = ()
    platforms: ta.Sequence[str] = ()


class Filter(dc.Frozen, lang.Final, kw_only=True):
    name: str
    defines: ta.Sequence[str] = ()
    symbols: bool = False
    flags: ta.Sequence[str] = ()
    system: str | None = None
    architecture: str | None = None
    kind: str | None = None


class Files(dc.Frozen, lang.Final, kw_only=True):
    include: ta.Sequence[str] = ()
    exclude: ta.Sequence[str] = ()


class Project(dc.Frozen, lang.Final, kw_only=True):
    name: str
    kind: str
    language: str
    location: str | None = None
    target_dir: str | None = None
    files: ta.Sequence[Files] = ()
    filters: ta.Sequence[Filter] = ()
    links: ta.Sequence[str] = ()
    remove_platforms: ta.Sequence[str] = ()
