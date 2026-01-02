#!/bin/bash
set -e
source ./scripts/load_env.sh
./scripts/deploy.sh "hermes-dev" docker-compose.yml