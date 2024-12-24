#!/usr/bin/env just --justfile
set dotenv-load := true

# Show all available recipes
default:
  @just --list --unsorted

#####################
# Lektor management #
#####################

# Install dependencies into the current environment
install:
    @pipx --version || (echo "pipx is not installed. Please install it using 'python3 -m pip install --user pipx'." && exit 1)
    pipx install lektor

# Build the site
build:
    lektor build

# Run the site
up:
    lektor serve

alias serve := up

# Clean the environment
clean:
    lektor clean

# Deploy the site
deploy:
    @just build
    lektor deploy ghpages

##################
# Other commands #
##################

# Generate the program pages (talks & speakers)
generate-program:
    @python3 scripts/init_program.py




