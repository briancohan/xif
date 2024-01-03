#!/usr/bin/env just --justfile

# Setup
install:
    @poetry install

# Publish to github
push:
    @git push --set-upstream origin `git rev-parse --abbrev-ref HEAD`

# Create a new release
build:
    @rm -Rf dist
    @poetry build

# Install locally
pipx: build
    pipx install --force `find ./dist -name "*.whl" | sort | tail -n 1`
