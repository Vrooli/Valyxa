#!/bin/bash
# NOTE 1: Run outside of Docker container, on production server
# NOTE 2: First run build.sh on development server
# NOTE 3: If docker-compose file was changed since the last build, you should prune the containers and images before running this script.
# Finishes up the deployment process, which was started by build.sh:
# 1. Runs git fetch and git pull to get the latest changes.
# 2. Runs setup.sh
# 3. Restarts docker containers
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "${HERE}/prettify.sh"

# Pull the latest changes from the repository.
info "Pulling latest changes from repository..."
git fetch
git pull
if [ $? -ne 0 ]; then
    error "Could not pull latest changes from repository. You likely have uncommitted changes."
    exit 1
fi

# Running setup.sh
info "Running setup.sh..."
"${HERE}/setup.sh" "${SETUP_ARGS[@]}" -p
if [ $? -ne 0 ]; then
    error "setup.sh failed"
    exit 1
fi

# Transfer and load Docker images
if [ -f "${BUILD_ZIP}/production-docker-images.tar.gz" ]; then
    info "Loading Docker images from ${BUILD_ZIP}/production-docker-images.tar.gz"
    docker load -i "${BUILD_ZIP}/production-docker-images.tar.gz"
    if [ $? -ne 0 ]; then
        error "Failed to load Docker images from ${BUILD_ZIP}/production-docker-images.tar.gz"
        exit 1
    fi
else
    error "Could not find Docker images archive at ${BUILD_ZIP}/production-docker-images.tar.gz"
    exit 1
fi

# Stop docker containers
info "Stopping docker containers..."
docker-compose --env-file ${BUILD_ZIP}/.env-prod down

# Restart docker containers.
info "Restarting docker containers..."
docker-compose --env-file ${BUILD_ZIP}/.env-prod -f ${HERE}/../docker-compose-prod.yml up -d

success "Done! You may need to wait a few minutes for the Docker containers to finish starting up."
info "Now that you've deployed, here are some next steps:"
info "- Manually check that Valyxa is working correctly"
info "- Let everyone on social media know that you've deployed a new version of Valyxa!"
