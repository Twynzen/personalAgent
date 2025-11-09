"""
Configuration File Parsers

Parse project configuration files for different project types:
- package.json (Node.js)
- pyproject.toml (Python)
- Cargo.toml (Rust)
- go.mod (Go)
- pom.xml (Java/Maven)
- And more...
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional

from sendell.projects.types import ProjectConfig
from sendell.utils.logger import get_logger

logger = get_logger(__name__)


def parse_package_json(path: Path) -> Optional[ProjectConfig]:
    """
    Parse Node.js package.json file.

    Args:
        path: Path to package.json

    Returns:
        ProjectConfig or None if parsing fails
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return ProjectConfig(
            name=data.get("name"),
            version=data.get("version"),
            description=data.get("description"),
            dependencies=data.get("dependencies", {}),
            dev_dependencies=data.get("devDependencies", {}),
            scripts=data.get("scripts", {}),
            author=data.get("author"),
            license=data.get("license"),
            repository=data.get("repository", {}).get("url") if isinstance(data.get("repository"), dict) else data.get("repository"),
            node_version=data.get("engines", {}).get("node") if "engines" in data else None,
        )
    except Exception as e:
        logger.error(f"Failed to parse package.json at {path}: {e}")
        return None


def parse_pyproject_toml(path: Path) -> Optional[ProjectConfig]:
    """
    Parse Python pyproject.toml file.

    Args:
        path: Path to pyproject.toml

    Returns:
        ProjectConfig or None if parsing fails
    """
    try:
        # Use tomli for Python <3.11, tomllib for 3.11+
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib

        with open(path, "rb") as f:
            data = tomllib.load(f)

        # Different structures for Poetry, PDM, setuptools, etc.
        config = ProjectConfig()

        # Poetry format
        if "tool" in data and "poetry" in data["tool"]:
            poetry = data["tool"]["poetry"]
            config.name = poetry.get("name")
            config.version = poetry.get("version")
            config.description = poetry.get("description")
            config.dependencies = poetry.get("dependencies", {})
            config.dev_dependencies = poetry.get("dev-dependencies", {})
            config.author = ", ".join(poetry.get("authors", []))
            config.license = poetry.get("license")
            config.repository = poetry.get("repository")
            config.python_version = poetry.get("dependencies", {}).get("python")

        # PEP 621 format (modern standard)
        elif "project" in data:
            project = data["project"]
            config.name = project.get("name")
            config.version = project.get("version")
            config.description = project.get("description")
            config.dependencies = {dep: "*" for dep in project.get("dependencies", [])}
            config.license = project.get("license", {}).get("text") if isinstance(project.get("license"), dict) else project.get("license")

            if "authors" in project and len(project["authors"]) > 0:
                config.author = project["authors"][0].get("name")

            if "requires-python" in project:
                config.python_version = project["requires-python"]

        return config if config.name else None

    except Exception as e:
        logger.error(f"Failed to parse pyproject.toml at {path}: {e}")
        return None


def parse_cargo_toml(path: Path) -> Optional[ProjectConfig]:
    """
    Parse Rust Cargo.toml file.

    Args:
        path: Path to Cargo.toml

    Returns:
        ProjectConfig or None if parsing fails
    """
    try:
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib

        with open(path, "rb") as f:
            data = tomllib.load(f)

        package = data.get("package", {})

        return ProjectConfig(
            name=package.get("name"),
            version=package.get("version"),
            description=package.get("description"),
            dependencies={k: str(v) for k, v in data.get("dependencies", {}).items()},
            dev_dependencies={k: str(v) for k, v in data.get("dev-dependencies", {}).items()},
            author=", ".join(package.get("authors", [])),
            license=package.get("license"),
            repository=package.get("repository"),
            rust_edition=package.get("edition"),
        )

    except Exception as e:
        logger.error(f"Failed to parse Cargo.toml at {path}: {e}")
        return None


def parse_go_mod(path: Path) -> Optional[ProjectConfig]:
    """
    Parse Go go.mod file.

    Args:
        path: Path to go.mod

    Returns:
        ProjectConfig or None if parsing fails
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        config = ProjectConfig()
        dependencies = {}

        for line in content.splitlines():
            line = line.strip()

            # Module name
            if line.startswith("module "):
                config.name = line.replace("module ", "").strip()

            # Go version
            elif line.startswith("go "):
                config.go_version = line.replace("go ", "").strip()

            # Dependencies
            elif line.startswith("require "):
                # Single-line require
                if not line.endswith("("):
                    dep = line.replace("require ", "").strip()
                    if " " in dep:
                        name, version = dep.rsplit(" ", 1)
                        dependencies[name] = version

            # Multi-line require block
            elif line and not line.startswith(")") and "=>" not in line and len(line.split()) == 2:
                parts = line.split()
                if len(parts) == 2:
                    dependencies[parts[0]] = parts[1]

        config.dependencies = dependencies
        return config if config.name else None

    except Exception as e:
        logger.error(f"Failed to parse go.mod at {path}: {e}")
        return None


def parse_pom_xml(path: Path) -> Optional[ProjectConfig]:
    """
    Parse Java Maven pom.xml file.

    Args:
        path: Path to pom.xml

    Returns:
        ProjectConfig or None if parsing fails
    """
    try:
        tree = ET.parse(path)
        root = tree.getroot()

        # Maven uses XML namespace
        ns = {"mvn": "http://maven.apache.org/POM/4.0.0"}

        config = ProjectConfig()

        # Basic info
        config.name = root.findtext("mvn:artifactId", namespaces=ns)
        config.version = root.findtext("mvn:version", namespaces=ns)
        config.description = root.findtext("mvn:description", namespaces=ns)

        # Dependencies
        dependencies = {}
        deps = root.find("mvn:dependencies", namespaces=ns)
        if deps is not None:
            for dep in deps.findall("mvn:dependency", namespaces=ns):
                group_id = dep.findtext("mvn:groupId", namespaces=ns)
                artifact_id = dep.findtext("mvn:artifactId", namespaces=ns)
                version = dep.findtext("mvn:version", namespaces=ns)

                if group_id and artifact_id:
                    key = f"{group_id}:{artifact_id}"
                    dependencies[key] = version or "latest"

        config.dependencies = dependencies

        # License
        license_elem = root.find("mvn:licenses/mvn:license", namespaces=ns)
        if license_elem is not None:
            config.license = license_elem.findtext("mvn:name", namespaces=ns)

        return config if config.name else None

    except Exception as e:
        logger.error(f"Failed to parse pom.xml at {path}: {e}")
        return None


def parse_gemfile(path: Path) -> Optional[ProjectConfig]:
    """
    Parse Ruby Gemfile (basic parsing).

    Args:
        path: Path to Gemfile

    Returns:
        ProjectConfig or None if parsing fails
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        config = ProjectConfig()
        dependencies = {}

        for line in content.splitlines():
            line = line.strip()

            # gem 'name', 'version'
            if line.startswith("gem "):
                parts = line.replace("gem ", "").replace("'", '"').split(",")
                if len(parts) >= 1:
                    name = parts[0].strip().strip('"')
                    version = parts[1].strip().strip('"') if len(parts) > 1 else "*"
                    dependencies[name] = version

        config.dependencies = dependencies

        # Try to infer name from parent directory
        config.name = path.parent.name

        return config if dependencies else None

    except Exception as e:
        logger.error(f"Failed to parse Gemfile at {path}: {e}")
        return None


def parse_composer_json(path: Path) -> Optional[ProjectConfig]:
    """
    Parse PHP composer.json file.

    Args:
        path: Path to composer.json

    Returns:
        ProjectConfig or None if parsing fails
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return ProjectConfig(
            name=data.get("name"),
            version=data.get("version"),
            description=data.get("description"),
            dependencies=data.get("require", {}),
            dev_dependencies=data.get("require-dev", {}),
            license=data.get("license"),
        )

    except Exception as e:
        logger.error(f"Failed to parse composer.json at {path}: {e}")
        return None


# Mapping of config files to parser functions
CONFIG_PARSERS = {
    "package.json": parse_package_json,
    "pyproject.toml": parse_pyproject_toml,
    "Cargo.toml": parse_cargo_toml,
    "go.mod": parse_go_mod,
    "pom.xml": parse_pom_xml,
    "Gemfile": parse_gemfile,
    "composer.json": parse_composer_json,
}


def parse_project_config(config_file: Path) -> Optional[ProjectConfig]:
    """
    Parse project configuration file automatically based on filename.

    Args:
        config_file: Path to configuration file

    Returns:
        ProjectConfig or None if no parser available or parsing fails
    """
    filename = config_file.name

    parser = CONFIG_PARSERS.get(filename)
    if parser:
        return parser(config_file)

    logger.warning(f"No parser available for config file: {filename}")
    return None
