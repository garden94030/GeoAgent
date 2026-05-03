"""Startup-path tests for the OpenGeoAgent QGIS plugin."""

from __future__ import annotations

import importlib
import sys
import types


def test_plugin_package_import_does_not_import_dependency_manager() -> None:
    """Importing the plugin package should not run dependency checks."""
    for module_name in list(sys.modules):
        if module_name == "open_geoagent" or module_name.startswith("open_geoagent."):
            sys.modules.pop(module_name, None)

    importlib.import_module("open_geoagent")

    assert "open_geoagent.deps_manager" not in sys.modules


def test_all_dependencies_met_uses_lightweight_spec_checks(monkeypatch) -> None:
    """The chat-open dependency gate must not import provider packages."""
    from open_geoagent import deps_manager

    monkeypatch.setattr(
        deps_manager,
        "CORE_RUNTIME_PACKAGES",
        [("geoagent", "GeoAgent[providers]>=1.4.1"), ("strands", "strands-agents")],
    )
    monkeypatch.setattr(deps_manager, "ensure_venv_packages_available", lambda: True)

    checked: list[str] = []

    def fake_find_spec(import_name: str):
        checked.append(import_name)
        return types.SimpleNamespace(name=import_name)

    def fail_import_module(import_name: str):
        raise AssertionError(f"unexpected import of {import_name}")

    monkeypatch.setattr(deps_manager.importlib.util, "find_spec", fake_find_spec)
    monkeypatch.setattr(deps_manager.importlib, "import_module", fail_import_module)

    assert deps_manager.all_dependencies_met() is True
    assert checked == ["geoagent", "strands"]


def test_ensure_venv_packages_available_processes_pth_files(
    monkeypatch, tmp_path
) -> None:
    """Editable installs should work when QGIS adds the plugin venv later."""
    from open_geoagent import deps_manager

    source_dir = tmp_path / "editable_source"
    site_packages = tmp_path / "site-packages"
    source_dir.mkdir()
    site_packages.mkdir()
    (site_packages / "editable-test.pth").write_text(
        f"{source_dir}\n", encoding="utf-8"
    )

    monkeypatch.setattr(deps_manager, "venv_exists", lambda: True)
    monkeypatch.setattr(
        deps_manager, "get_venv_site_packages", lambda: str(site_packages)
    )
    if str(source_dir) in sys.path:
        sys.path.remove(str(source_dir))
    if str(site_packages) in sys.path:
        sys.path.remove(str(site_packages))

    assert deps_manager.ensure_venv_packages_available() is True

    assert str(source_dir) in sys.path


def test_required_dependencies_include_core_runtime_packages() -> None:
    """Dependency gate should catch partial GeoAgent installs."""
    from open_geoagent.deps_manager import REQUIRED_PACKAGES

    assert ("geoagent", "GeoAgent[providers]>=1.4.1") in REQUIRED_PACKAGES
    assert ("strands", "strands-agents>=1.37") in REQUIRED_PACKAGES
    assert ("pydantic", "pydantic>=2.0") in REQUIRED_PACKAGES


def test_dependency_groups_include_optional_workflow_packages() -> None:
    """Optional workflow stacks should be grouped instead of globally required."""
    from open_geoagent.deps_manager import DEPENDENCY_GROUPS, REQUIRED_PACKAGES

    assert ("whitebox", "whitebox>=2.3.6") not in REQUIRED_PACKAGES
    assert ("whitebox", "whitebox>=2.3.6") in DEPENDENCY_GROUPS["WhiteboxTools"]
    assert ("pystac_client", "pystac-client>=0.8") in DEPENDENCY_GROUPS["STAC"]
    assert ("gee_data_catalogs", "gee-data-catalogs") not in DEPENDENCY_GROUPS[
        "GEE Data Catalogs"
    ]
    assert ("ee", "earthengine-api>=1.0") in DEPENDENCY_GROUPS["GEE Data Catalogs"]


def test_python_runtime_error_mentions_required_version(monkeypatch) -> None:
    """The installer should fail clearly on unsupported QGIS Python versions."""
    from open_geoagent import deps_manager

    monkeypatch.setattr(deps_manager, "MIN_PYTHON_VERSION", (99, 0))

    assert deps_manager.python_runtime_supported() is False
    assert "Python 99.0 or newer" in deps_manager.python_runtime_error()


def test_find_python_executable_detects_macos_qgis_python(monkeypatch, tmp_path) -> None:
    """macOS QGIS should use the bundled Python binary, not the app binary."""
    from open_geoagent import deps_manager

    app_root = tmp_path / "QGIS.app" / "Contents"
    qgis_binary = app_root / "MacOS" / "QGIS"
    python_binary = app_root / "MacOS" / "python3.12"
    qgis_binary.parent.mkdir(parents=True)
    qgis_binary.write_text("#!/bin/sh\n", encoding="utf-8")
    python_binary.write_text("#!/bin/sh\n", encoding="utf-8")

    monkeypatch.setattr(deps_manager.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(deps_manager.sys, "executable", str(qgis_binary))

    assert deps_manager._find_python_executable() == str(python_binary)


def test_clean_env_preserves_macos_qgis_pythonhome(monkeypatch, tmp_path) -> None:
    """QGIS's macOS Python needs PYTHONHOME pointing at Contents/Frameworks."""
    from open_geoagent import deps_manager

    app_root = tmp_path / "QGIS.app" / "Contents"
    qgis_binary = app_root / "MacOS" / "QGIS"
    frameworks_dir = app_root / "Frameworks"
    qgis_binary.parent.mkdir(parents=True)
    frameworks_dir.mkdir(parents=True)
    qgis_binary.write_text("#!/bin/sh\n", encoding="utf-8")

    monkeypatch.setattr(deps_manager.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(deps_manager.sys, "executable", str(qgis_binary))
    monkeypatch.setenv("PYTHONHOME", "/unrelated")

    env = deps_manager._get_clean_env()

    assert env["PYTHONHOME"] == str(frameworks_dir)
