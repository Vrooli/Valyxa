#!/bin/bash
# NOTE: Run outside of Docker container
# Prepares project for deployment to VPS:
# 1. Builds all Docker containers, making sure to include environment variables and post-build commands.
# 2. Copies the tarballs for the React app and Docker containers to the VPS.
#
# Arguments (all optional):
# -d: Deploy to VPS (y/N)
# -h: Show this help message
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "${HERE}/prettify.sh"

# Read arguments
while getopts "d:h" opt; do
    case $opt in
    d)
        DEPLOY=$OPTARG
        ;;
    h)
        echo "Usage: $0 [-v VERSION] [-d DEPLOY] [-h]"
        echo "  -d --deploy: Deploy to VPS (y/N)"
        echo "  -h --help: Show this help message"
        exit 0
        ;;
    \?)
        echo "Invalid option: -$OPTARG" >&2
        exit 1
        ;;
    :)
        echo "Option -$OPTARG requires an argument." >&2
        exit 1
        ;;
    esac
done

# Load variables from .env file
if [ -f "${HERE}/../.env" ]; then
    source "${HERE}/../.env"
else
    error "Could not find .env file. Exiting..."
    exit 1
fi

# Check for required variables
check_var() {
    if [ -z "${!1}" ]; then
        error "Variable ${1} is not set. Exiting..."
        exit 1
    fi
}
check_var REDIS_URL
check_var OPENAI_API_KEY

# Build Docker images
cd ${HERE}/..
info "Building (and Pulling) Docker images..."
docker-compose --env-file .env -f docker-compose-prod.yml build
docker pull postgres:13-alpine
docker pull redis:7-alpine

# Save and compress Docker images
info "Saving Docker images..."
docker save -o production-docker-images.tar valyxa-python:prod redis:7-alpine
if [ $? -ne 0 ]; then
    error "Failed to save Docker images"
    exit 1
fi
trap "rm production-docker-images.tar*" EXIT
info "Compressing Docker images..."
gzip -f production-docker-images.tar
if [ $? -ne 0 ]; then
    error "Failed to compress Docker images"
    exit 1
fi

# Copy build to VPS
if [ -z "$DEPLOY" ]; then
    prompt "Build successful! Would you like to send the build to the production server? (y/N)"
    read -n1 -r DEPLOY
    echo
fi

if [ "${DEPLOY}" = "y" ] || [ "${DEPLOY}" = "Y" ] || [ "${DEPLOY}" = "yes" ] || [ "${DEPLOY}" = "Yes" ]; then
    source "${HERE}/keylessSsh.sh"
    BUILD_DIR="${SITE_IP}:/var/tmp/valyxa/"
    prompt "Going to copy to ${BUILD_DIR}. Press any key to continue..."
    read -n1 -r -s
    rsync -ri --info=progress2 production-docker-images.tar.gz .env-prod root@${BUILD_DIR}
    if [ $? -ne 0 ]; then
        error "Failed to copy files to ${BUILD_DIR}"
        exit 1
    fi
    success "Files copied to ${BUILD_DIR}! To finish deployment, run deploy.sh on the VPS."
else
    BUILD_DIR="/var/tmp/valyxa"
    info "Copying locally to ${BUILD_DIR}."
    # Make sure to create missing directories
    mkdir -p "${BUILD_DIR}"
    cp -p production-docker-images.tar.gz ${BUILD_DIR}
    if [ $? -ne 0 ]; then
        error "Failed to copy files to ${BUILD_DIR}"
        exit 1
    fi
    # If building locally, use .env and rename it to .env-prod
    cp -p .env ${BUILD_DIR}/.env-prod
    if [ $? -ne 0 ]; then
        error "Failed to copy .env to ${BUILD_DIR}/.env-prod"
        exit 1
    fi
fi

success "Build process completed successfully! Now run deploy.sh on the VPS to finish deployment, or locally to test deployment."
