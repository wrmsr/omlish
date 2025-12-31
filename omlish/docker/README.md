# Overview

Docker and OCI (Open Container Initiative) utilities for working with containers, images, registries, and docker-compose.
Provides programmatic access to Docker functionality without requiring the full Docker SDK.

# Key Features

- **Docker CLI wrapper** - Programmatic interface to `docker` command-line tool.
- **Docker Hub integration** - Query Docker Hub for image information.
- **OCI manifest handling** - Parse and manipulate OCI image manifests.
- **Docker Compose** - Parse and work with docker-compose.yml files.
- **Container detection** - Detect if code is running inside a container.
- **Port allocation** - Utilities for allocating and managing container ports.
- **Namespace utilities** - Work with container namespaces.
- **Timebomb containers** - Create containers that self-destruct after a timeout (useful for tests).

# Notable Modules

- **[cli](https://github.com/wrmsr/omlish/blob/master/omlish/docker/cli.py)** - Docker CLI wrapper for executing docker
  commands programmatically.
- **[hub](https://github.com/wrmsr/omlish/blob/master/omlish/docker/hub.py)** - Docker Hub API integration for querying
  image information.
- **[oci](https://github.com/wrmsr/omlish/blob/master/omlish/docker/oci)** - OCI image manifest parsing and
  manipulation.
- **[manifests](https://github.com/wrmsr/omlish/blob/master/omlish/docker/manifests.py)** - Docker manifest handling.
- **[compose](https://github.com/wrmsr/omlish/blob/master/omlish/docker/compose.py)** - docker-compose.yml parsing and
  manipulation.
- **[detect](https://github.com/wrmsr/omlish/blob/master/omlish/docker/detect.py)** - Container environment detection
  (am I running in a container?).
- **[ports](https://github.com/wrmsr/omlish/blob/master/omlish/docker/ports.py)** - Port allocation and management for
  containers.
- **[ns1](https://github.com/wrmsr/omlish/blob/master/omlish/docker/ns1.py)** - Container namespace utilities.
- **[timebomb](https://github.com/wrmsr/omlish/blob/master/omlish/docker/timebomb.py)** - Self-destructing containers
  for testing.

# Example Usage

```python
from omlish.docker import cli, detect

# Check if running in a container
if detect.is_in_container():
    print("Running in a container!")

# Execute docker commands
result = cli.docker_run(['alpine', 'echo', 'hello'])
print(result.stdout)

# Query Docker Hub
from omlish.docker import hub
tags = hub.get_image_tags('library/python')
print(tags)
```

# Design Philosophy

Docker utilities should:
- **Not require Docker SDK** - Use CLI and APIs instead to minimize dependencies.
- **Be lightweight** - Thin wrappers over existing tools rather than reimplementing Docker.
- **Support testing** - Provide utilities like timebomb containers for test isolation.
- **Handle both Docker and OCI** - Work with standard OCI formats, not just Docker-specific formats.

This package is useful for:
- Orchestration scripts that need to interact with Docker.
- Testing frameworks that spin up containers.
- CI/CD pipelines that build and push images.
- Tools that need to detect container environments.
