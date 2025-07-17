import subprocess
import json
from typing import List, Dict, Tuple

from pullsar.operator_bundle_model import OperatorBundle
from pullsar.config import logger

RepositoryMap = Dict[str, List[OperatorBundle]]


def render_operator_catalog(catalog_image: str, output_file: str) -> bool:
    """
    Renders the OLM catalog image to a local JSON file using opm.
    Requires 'opm' to be installed and accessible in PATH,
    and appropriate registry authentication (e.g., via podman login).

    Args:
        catalog_image (str): Operators catalog image pullspec
        output_file (str): Name of a file to be generated, containing
        the rendered JSON catalog.

    Returns:
        bool: True if render was successful, else False
    """
    command = ["opm", "render", catalog_image, "-o", "json"]

    logger.info(f"Executing: {' '.join(command)} > {output_file}")
    logger.info("Might take up to a few minutes...")
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=True)

        with open(output_file, "w") as file:
            file.write(process.stdout)

        logger.info(f"Successfully rendered catalog to {output_file}")
        return True

    except FileNotFoundError:
        logger.error(
            f"'{command[0]}' command not found. Please, add it to your PATH. Terminating..."
        )
        raise
    except subprocess.CalledProcessError as error:
        logger.error(
            f"Rendering of catalog image failed (Exit Code: {error.returncode}):"
        )
        logger.error(f"Command: {' '.join(error.cmd)}")
        logger.debug(f"Stdout:\n{error.stdout}")
        logger.error(f"Stderr:\n{error.stderr}")
        logger.info(f"Skipping catalog {catalog_image}...")
        return False
    except Exception as exception:
        logger.error(f"An unexpected error occurred during opm render: {exception}")
        logger.info(f"Skipping catalog {catalog_image}...")
        return False


def create_repository_paths_maps(
    catalog_json_file: str,
) -> Tuple[RepositoryMap, RepositoryMap]:
    """
    Parses rendered JSON operators catalog and creates mappings between
    all the Quay repository paths and lists of the operator bundle versions
    that are tied with these repositories.

    Args:
        catalog_json_file (str): Rendered JSON catalog of operators.

    Returns:
        Tuple[RepositoryMap, RepositoryMap]: Two dictionaries with key-value pairs,
        key being a Quay repository path e.g. org/repo and value being a list
        of OperatorBundle objects, images of which are available in these repositories.
        First dictionary contains all repositories with all of their operator bundles
        Second dictionary contains only repositories and their operator bundles with undefined digests
        (digests for these need to be looked up using Quay API before moving on).
    """
    repository_paths_map: RepositoryMap = {}
    repository_paths_map_missing_digest: RepositoryMap = {}

    # select all bundle objects and make the output compact (-c ... one line, one item)
    # so we can easily process the output line by line, item by item and create
    # an OperatorBundle object for each item
    jq_command = ["jq", "-c", '. | select(.schema == "olm.bundle")', catalog_json_file]

    logger.info(f"Executing: {' '.join(jq_command)}")
    try:
        process = subprocess.run(jq_command, capture_output=True, text=True, check=True)

        for line_num, line in enumerate(process.stdout.splitlines(), 1):
            if not line.strip():
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError as e:
                logger.warning(
                    f"Could not decode JSON from jq output on line {line_num}: {e}"
                )
                logger.warning(f"Problematic line content: {line.strip()}")
                continue

            if "name" in item and "package" in item and "image" in item:
                operator = OperatorBundle(
                    name=item["name"], package=item["package"], image=item["image"]
                )

                quay_repo_path = operator.repo_path
                if quay_repo_path:
                    repository_paths_map.setdefault(quay_repo_path, []).append(operator)
                    if operator.digest is None:
                        repository_paths_map_missing_digest.setdefault(
                            quay_repo_path, []
                        ).append(operator)
            else:
                logger.warning(
                    f"Item on line {line_num} is missing some of the attributes "
                    "(expected: name, package, image). Skipping item..."
                )

        logger.info(
            f"Successfully identified {len(repository_paths_map)} repository paths "
            "and a list of their operator bundles from jq output."
        )
        return (repository_paths_map, repository_paths_map_missing_digest)

    except FileNotFoundError:
        logger.error(
            f"'{jq_command[0]}' command not found. Please, add it to your PATH. Terminating..."
        )
        raise
    except subprocess.CalledProcessError as error:
        logger.error(f"Error running jq command (Exit Code: {error.returncode}):")
        logger.error(f"Command: {' '.join(error.cmd)}")
        logger.debug(f"Stdout:\n{error.stdout}...")
        logger.error(f"Stderr:\n{error.stderr}")
        logger.info(f"Skipping catalog {catalog_json_file}...")
        return ({}, {})

    except Exception as exception:
        logger.error(
            f"An unexpected error occurred during jq processing or operator creation: {exception}"
        )
        logger.info(f"Skipping catalog {catalog_json_file}...")
        return ({}, {})
