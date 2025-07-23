import json
import subprocess
import pytest
from pytest import LogCaptureFixture
from pytest_mock import MockerFixture
from pathlib import Path

from pullsar.parse_operators_catalog import (
    render_operator_catalog,
    create_repository_paths_maps,
)


def test_render_catalog_success(mocker: MockerFixture, tmp_path: Path) -> None:
    """
    Test that the opm command is called correctly and its output is written to a file.
    """
    mock_process = mocker.Mock()
    mock_process.stdout = '{"schema": "olm.bundle"}'
    mock_run = mocker.patch("subprocess.run", return_value=mock_process)

    output_file = tmp_path / "catalog.json"
    catalog_image = "my-image:latest"

    is_success = render_operator_catalog(catalog_image, str(output_file))

    expected_command = ["opm", "render", catalog_image, "-o", "json"]
    mock_run.assert_called_once_with(
        expected_command, capture_output=True, text=True, check=True
    )
    assert is_success is True
    assert output_file.read_text() == '{"schema": "olm.bundle"}'


def test_render_catalog_opm_not_found(
    mocker: MockerFixture, caplog: LogCaptureFixture
) -> None:
    """
    Test that a FileNotFoundError is raised and logged if opm is not installed.
    """
    mock_run = mocker.patch("subprocess.run", side_effect=FileNotFoundError)

    with pytest.raises(FileNotFoundError):
        render_operator_catalog("my-image:latest", "output.json")

    mock_run.assert_called_once()
    assert "'opm' command not found" in caplog.text


def test_render_catalog_opm_fails(
    mocker: MockerFixture, caplog: LogCaptureFixture
) -> None:
    """
    Test that errors from a failed opm command are logged.
    """
    error = subprocess.CalledProcessError(
        returncode=1, cmd=["opm", "..."], stderr="something went wrong"
    )
    mocker.patch("subprocess.run", side_effect=error)

    is_success = render_operator_catalog("my-image:latest", "output.json")

    assert is_success is False
    assert "Rendering of catalog image failed" in caplog.text
    assert "something went wrong" in caplog.text


def test_render_catalog_generic_exception(
    mocker: MockerFixture, caplog: LogCaptureFixture
) -> None:
    """
    Covers the generic 'except Exception' block in render_operator_catalog.
    """
    mocker.patch("subprocess.run", side_effect=Exception("A generic opm error"))

    is_success = render_operator_catalog("my-image:latest", "output.json")

    assert is_success is False
    assert "An unexpected error occurred during opm render" in caplog.text


@pytest.fixture
def fake_jq_output() -> str:
    """A fixture that provides sample multi-line JSON output like jq -c."""
    bundle1 = {"name": "op-a.v1", "package": "op-a", "image": "quay.io/org-a/repo:v1"}
    bundle2 = {"name": "op-a.v2", "package": "op-a", "image": "quay.io/org-a/repo:v2"}
    bundle3 = {
        "name": "op-b.v1",
        "package": "op-b",
        "image": "quay.io/org-b/repo@sha256:abc",
    }
    # bundle with registry.connect proxy should be in non-quay map
    bundle4 = {
        "name": "op-c.v1",
        "package": "op-c",
        "image": "registry.connect.redhat.com/org-c/repo:v1",
    }

    return (
        "\n".join(
            [
                json.dumps(bundle1),
                json.dumps(bundle2),
                json.dumps(bundle3),
                json.dumps(bundle4),
            ]
        )
        + "\n\n"
    )  # empty line to skip


def test_create_maps_success(
    mocker: MockerFixture, fake_jq_output: str, tmp_path: Path
) -> None:
    """
    Test the happy path where jq output is parsed and maps are created correctly.
    """
    mock_process = mocker.Mock()
    mock_process.stdout = fake_jq_output
    mocker.patch("subprocess.run", return_value=mock_process)
    catalog_file = tmp_path / "catalog.json"

    all_map, missing_digest_map, not_quay_map = create_repository_paths_maps(
        str(catalog_file), {}
    )

    assert len(all_map) == 2  # two repo paths: org-a/repo and org-b/repo
    assert len(all_map["org-a/repo"]) == 2  # two bundles for this repo
    assert all_map["org-a/repo"][0].name == "op-a.v1"
    assert all_map["org-a/repo"][1].name == "op-a.v2"
    assert all_map["org-b/repo"][0].digest == "sha256:abc"

    assert len(missing_digest_map) == 1
    assert len(missing_digest_map["org-a/repo"]) == 2
    assert "org-b/repo" not in missing_digest_map

    assert len(not_quay_map) == 1
    assert len(not_quay_map["org-c/repo"]) == 1
    assert not_quay_map["org-c/repo"][0].registry == "registry.connect.redhat.com"


def test_create_maps_jq_not_found(
    mocker: MockerFixture, caplog: LogCaptureFixture
) -> None:
    """
    Test that a FileNotFoundError is raised and logged if jq is not installed.
    """
    mock_run = mocker.patch("subprocess.run", side_effect=FileNotFoundError)

    with pytest.raises(FileNotFoundError):
        create_repository_paths_maps("catalog.json", {})

    mock_run.assert_called_once()
    assert "'jq' command not found" in caplog.text


def test_create_maps_jq_fails(mocker: MockerFixture, caplog: LogCaptureFixture) -> None:
    """
    Test that the function returns empty dicts if the jq command fails.
    """
    error = subprocess.CalledProcessError(returncode=1, cmd=["jq", "..."])
    mocker.patch("subprocess.run", side_effect=error)

    all_map, missing_digest_map, not_quay_map = create_repository_paths_maps(
        "catalog.json", {}
    )

    assert all_map == {}
    assert missing_digest_map == {}
    assert not_quay_map == {}
    assert "Error running jq command" in caplog.text


def test_create_maps_malformed_json_line(
    mocker: MockerFixture, caplog: LogCaptureFixture, tmp_path: Path
) -> None:
    """
    Test that a malformed line in the jq output is skipped with a warning.
    """
    malformed_output = '{"name": "op-a.v1"}\nnot-json\n{"name": "op-b.v1"}'
    mock_process = mocker.Mock()
    mock_process.stdout = malformed_output
    mocker.patch("subprocess.run", return_value=mock_process)
    catalog_file = tmp_path / "catalog.json"

    create_repository_paths_maps(str(catalog_file), {})

    assert "Could not decode JSON" in caplog.text
    assert "Problematic line content: not-json" in caplog.text


def test_create_maps_generic_exception(
    mocker: MockerFixture, caplog: LogCaptureFixture
) -> None:
    """
    Covers the generic 'except Exception' block in create_repository_paths_maps.
    """
    mocker.patch("subprocess.run", side_effect=Exception("A generic jq error"))

    all_map, missing_digest_map, not_quay_map = create_repository_paths_maps(
        "catalog.json", {}
    )

    assert all_map == {}
    assert missing_digest_map == {}
    assert not_quay_map == {}
    assert "An unexpected error occurred during jq processing" in caplog.text
