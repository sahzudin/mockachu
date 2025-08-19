# Makefile for Mockachu
# Cross-platform build automation

.PHONY: help install install-dev install-gui install-build test lint clean build build-dev release

# Default target
help:
	@echo "Mockachu - Build Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install         Install package only"
	@echo "  install-gui     Install package with GUI support"
	@echo "  install-dev     Install package with development tools"
	@echo "  install-build   Install package with build tools"
	@echo ""
	@echo "Development Commands:"
	@echo "  test            Run tests"
	@echo "  lint            Run linting"
	@echo "  clean           Clean build artifacts"
	@echo ""
	@echo "Build Commands:"
	@echo "  build           Build executable for current platform"
	@echo "  build-enhanced  Build with enhanced anti-virus settings (Windows)"
	@echo "  build-test      Test build configuration"
	@echo ""
	@echo "Release Commands:"
	@echo "  release-patch   Create patch release (x.x.X)"
	@echo "  release-minor   Create minor release (x.X.x)"
	@echo "  release-major   Create major release (X.x.x)"
	@echo ""

# Installation targets
install:
	pip install -e .

install-gui:
	pip install -e ".[gui]"

install-dev:
	pip install -e ".[dev]"

install-build:
	pip install -e ".[gui,build]"

# Development targets
test:
	pytest tests/ --cov=mockachu --cov-report=term-missing

lint:
	black mockachu/ tests/ --check
	flake8 mockachu/ tests/

clean:
	rm -rf dist/ build/ *.egg-info/
	rm -rf .pytest_cache/ .coverage htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build targets
build: install-build
	@echo "Building executable for current platform..."
	@if [ "$$(uname)" = "Darwin" ] || [ "$$(uname)" = "Linux" ]; then \
		./scripts/build.sh; \
	else \
		echo "Use 'scripts\\build.bat' on Windows"; \
	fi

build-enhanced: install-build
	@echo "Building with enhanced anti-virus settings..."
	python build_enhanced.py

build-test: install-build
	python scripts/test_build.py

# Release targets  
release-patch:
	python scripts/release.py create --patch

release-minor:
	python scripts/release.py create --minor

release-major:
	python scripts/release.py create --major

# Platform detection
ifeq ($(OS),Windows_NT)
    PLATFORM := windows
    SHELL_EXT := .bat
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
        PLATFORM := linux
    endif
    ifeq ($(UNAME_S),Darwin)
        PLATFORM := macos
    endif
    SHELL_EXT := .sh
endif
