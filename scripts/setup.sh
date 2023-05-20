#!/bin/bash
# Sets up NPM, Yarn, global dependencies, and anything else
# required to get the project up and running.
#
# Arguments (all optional):
# -r: Run on remote server (y/N) - If set to "y", will run additional commands to set up the remote server
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "${HERE}/prettify.sh"

# Read arguments
ON_REMOTE=""
ENVIRONMENT="dev"
for arg in "$@"; do
    case $arg in
    -r | --remote)
        ON_REMOTE="${2}"
        shift
        shift
        ;;
    -p | --prod)
        ENVIRONMENT="prod"
        shift
        ;;
    -h | --help)
        echo "Usage: $0 [-h HELP] [-f FORCE] [-r REMOTE]"
        echo "  -h --help: Show this help message"
        echo "  -r --remote: (Y/n) True if this script is being run on the remote server"
        echo "  -p --prod: If set, will skip steps that are only required for development"
        exit 0
        ;;
    esac
done

header "Checking for package updates"
sudo apt-get update
header "Running upgrade"
RUNLEVEL=1 sudo apt-get -y upgrade

# If this script is being run on the remote server, enable PasswordAuthentication
if [ -z "${ON_REMOTE}" ]; then
    prompt "Is this script being run on the remote server? (Y/n)"
    read -n1 -r ON_REMOTE
    echo
fi
if [ "${ON_REMOTE}" = "y" ] || [ "${ON_REMOTE}" = "Y" ] || [ "${ON_REMOTE}" = "yes" ] || [ "${ON_REMOTE}" = "Yes" ]; then
    header "Enabling PasswordAuthentication"
    sudo sed -i 's/#\?PasswordAuthentication .*/PasswordAuthentication yes/g' /etc/ssh/sshd_config
    sudo sed -i 's/#\?PubkeyAuthentication .*/PubkeyAuthentication yes/g' /etc/ssh/sshd_config
    sudo sed -i 's/#\?AuthorizedKeysFile .*/AuthorizedKeysFile .ssh\/authorized_keys/g' /etc/ssh/sshd_config
    chmod 700 ~/.ssh
    chmod 600 ~/.ssh/authorized_keys
    # Try restarting service. Can either be called "sshd" or "ssh"
    sudo service sshd restart
    # If sshd fails, try to restart ssh
    if [ $? -ne 0 ]; then
        echo "Failed to restart sshd, trying ssh..."
        sudo systemctl restart ssh
        # If ssh also fails, exit with an error
        if [ $? -ne 0 ]; then
            echo "Failed to restart ssh. Exiting with error."
            exit 1
        fi
    fi
else
    # Otherwise, make sure mailx is installed. This may be used by some scripts which
    # track errors on the remote server and notify the developer via email.
    header "Installing mailx"
    # TODO - Not working for some reason
    # info "Select option 2 (Internet Site) then enter \"http://mirrors.kernel.org/ubuntu\" when prompted."
    #sudo apt-get install -y mailutils
    # While we're here, also check if .env and .env-prod exist. If not, create them using .env-example.
    if [ ! -f "${HERE}/../.env" ]; then
        header "Creating .env file"
        cp "${HERE}/../.env-example" "${HERE}/../.env"
        warning "Please update the .env file with your own values."
    fi
    if [ ! -f "${HERE}/../.env-prod" ]; then
        header "Creating .env-prod file"
        cp "${HERE}/../.env-example" "${HERE}/../.env-prod"
        warning "Please update the .env-prod file with your own values."
    fi
fi

if ! command -v docker &>/dev/null; then
    info "Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    trap 'rm -f get-docker.sh' EXIT
    sudo sh get-docker.sh
    # Check if Docker installation failed
    if ! command -v docker &>/dev/null; then
        echo "Error: Docker installation failed."
        exit 1
    fi
else
    info "Detected: $(docker --version)"
fi

if ! command -v docker-compose &>/dev/null; then
    info "Docker Compose is not installed. Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod a+rx /usr/local/bin/docker-compose
    # Check if Docker Compose installation failed
    if ! command -v docker-compose &>/dev/null; then
        echo "Error: Docker Compose installation failed."
        exit 1
    fi
else
    info "Detected: $(docker-compose --version)"
fi

info "Done! You may need to restart your editor for syntax highlighting to work correctly."
info "If you haven't already, copy .env-example to .env and edit it to match your environment."
