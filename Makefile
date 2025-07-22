# Makefile for Storage-in-OSeMOSYS Environment Management
# Author: Md Eliasinul Islam
# Description: This Makefile provides commands to create, update, and manage the conda environment for the Storage-in-OSeMOSYS project

# Variables
ENV_NAME = storage_osemosys
ENV_FILE = env/environment.yml
PYTHON_VERSION = 3.13
PROJECT_DIR = $(shell pwd)

# Colors for terminal output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

# Default target
.PHONY: help
help:
	@echo "$(BLUE)Storage-in-OSeMOSYS Environment Management$(NC)"
	@echo "=============================================="
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@echo "  $(YELLOW)make setup$(NC)          - Create and setup the conda environment from scratch"
	@echo "  $(YELLOW)make env-create$(NC)     - Create conda environment from environment.yml"
	@echo "  $(YELLOW)make env-update$(NC)     - Update existing environment from environment.yml"
	@echo "  $(YELLOW)make env-export$(NC)     - Export current environment to environment.yml"
	@echo "  $(YELLOW)make env-remove$(NC)     - Remove the conda environment"
	@echo "  $(YELLOW)make env-list$(NC)       - List all conda environments"
	@echo "  $(YELLOW)make env-info$(NC)       - Show environment information"
	@echo "  $(YELLOW)make install-deps$(NC)   - Install additional dependencies via pip"
	@echo "  $(YELLOW)make test-env$(NC)       - Test if all required packages are available"
	@echo "  $(YELLOW)make clean$(NC)          - Clean temporary files"
	@echo "  $(YELLOW)make run-main$(NC)       - Run the main.py script in the environment"
	@echo "  $(YELLOW)make activate$(NC)       - Show activation command"
	@echo ""
	@echo "$(GREEN)Documentation commands:$(NC)"
	@echo "  $(YELLOW)make docs-build$(NC)     - Build documentation with Sphinx"
	@echo "  $(YELLOW)make docs-serve$(NC)     - Serve documentation locally"
	@echo "  $(YELLOW)make docs-clean$(NC)     - Clean documentation build files"
	@echo "  $(YELLOW)make docs-deploy$(NC)    - Deploy documentation to GitHub Pages"
	@echo "  $(YELLOW)make docs-setup$(NC)     - Setup documentation dependencies"
	@echo "  $(YELLOW)make docs-check$(NC)     - Check documentation for errors"
	@echo "  $(YELLOW)make docs-autodoc$(NC)   - Auto-generate API documentation from source code"
	@echo "  $(YELLOW)make docs-full$(NC)      - Complete workflow: autodoc + build"
	@echo "  $(YELLOW)make docs-live$(NC)      - Live development server with auto-reload"
	@echo ""
	@echo "$(GREEN)Example workflow:$(NC)"
	@echo "  1. make setup         # First time setup"
	@echo "  2. make activate      # Activate environment"
	@echo "  3. make test-env      # Verify installation"
	@echo "  4. make run-main      # Run the main script"
	@echo ""
	@echo "$(GREEN)Documentation workflow:$(NC)"
	@echo "  1. make docs-setup    # Setup documentation tools"
	@echo "  2. make docs-autodoc  # Generate API docs from source"
	@echo "  3. make docs-build    # Build documentation"
	@echo "  4. make docs-serve    # Preview locally"
	@echo "  5. make docs-deploy   # Deploy to GitHub Pages"
	@echo ""

# Create and setup environment from scratch
.PHONY: setup
setup:
	@echo "$(GREEN)Setting up Storage-in-OSeMOSYS environment...$(NC)"
	@make env-create
	@make install-deps
	@make test-env
	@echo "$(GREEN)✓ Environment setup complete!$(NC)"
	@echo "$(YELLOW)To activate the environment, run: conda activate $(ENV_NAME)$(NC)"

# Create conda environment from environment.yml
.PHONY: env-create
env-create:
	@echo "$(GREEN)Creating conda environment '$(ENV_NAME)' from $(ENV_FILE)...$(NC)"
	@if conda env list | grep -q "^$(ENV_NAME) "; then \
		echo "$(YELLOW)Environment '$(ENV_NAME)' already exists. Use 'make env-update' to update it.$(NC)"; \
	else \
		conda env create -f $(ENV_FILE) -n $(ENV_NAME); \
		echo "$(GREEN)✓ Environment '$(ENV_NAME)' created successfully!$(NC)"; \
	fi

# Update existing environment
.PHONY: env-update
env-update:
	@echo "$(GREEN)Updating conda environment '$(ENV_NAME)'...$(NC)"
	@if conda env list | grep -q "^$(ENV_NAME) "; then \
		conda env update -f $(ENV_FILE) -n $(ENV_NAME) --prune; \
		echo "$(GREEN)✓ Environment updated successfully!$(NC)"; \
	else \
		echo "$(RED)Environment '$(ENV_NAME)' does not exist. Use 'make env-create' first.$(NC)"; \
		exit 1; \
	fi

# Export current environment
.PHONY: env-export
env-export:
	@echo "$(GREEN)Exporting environment '$(ENV_NAME)' to $(ENV_FILE)...$(NC)"
	@if conda env list | grep -q "^$(ENV_NAME) "; then \
		conda env export -n $(ENV_NAME) > $(ENV_FILE); \
		echo "$(GREEN)✓ Environment exported to $(ENV_FILE)$(NC)"; \
	else \
		echo "$(RED)Environment '$(ENV_NAME)' does not exist.$(NC)"; \
		exit 1; \
	fi

# Remove conda environment
.PHONY: env-remove
env-remove:
	@echo "$(RED)Removing conda environment '$(ENV_NAME)'...$(NC)"
	@read -p "Are you sure you want to remove the environment '$(ENV_NAME)'? [y/N]: " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		conda env remove -n $(ENV_NAME); \
		echo "$(GREEN)✓ Environment '$(ENV_NAME)' removed.$(NC)"; \
	else \
		echo "$(YELLOW)Environment removal cancelled.$(NC)"; \
	fi

# List all conda environments
.PHONY: env-list
env-list:
	@echo "$(GREEN)Available conda environments:$(NC)"
	@conda env list

# Show environment information
.PHONY: env-info
env-info:
	@echo "$(GREEN)Environment Information:$(NC)"
	@echo "Environment Name: $(ENV_NAME)"
	@echo "Environment File: $(ENV_FILE)"
	@echo "Python Version: $(PYTHON_VERSION)"
	@echo "Project Directory: $(PROJECT_DIR)"
	@echo ""
	@if conda env list | grep -q "^$(ENV_NAME) "; then \
		echo "$(GREEN)Environment Status: EXISTS$(NC)"; \
		echo "$(GREEN)Installed packages:$(NC)"; \
		conda list -n $(ENV_NAME) | head -20; \
		echo "... (showing first 20 packages)"; \
	else \
		echo "$(RED)Environment Status: NOT FOUND$(NC)"; \
	fi

# Install additional dependencies
.PHONY: install-deps
install-deps:
	@echo "$(GREEN)Installing additional dependencies...$(NC)"
	@if conda env list | grep -q "^$(ENV_NAME) "; then \
		conda run -n $(ENV_NAME) pip install otoole colorama; \
		echo "$(GREEN)✓ Additional dependencies installed!$(NC)"; \
	else \
		echo "$(RED)Environment '$(ENV_NAME)' does not exist. Create it first.$(NC)"; \
		exit 1; \
	fi

# Test environment
.PHONY: test-env
test-env:
	@echo "$(GREEN)Testing environment setup...$(NC)"
	@if conda env list | grep -q "^$(ENV_NAME) "; then \
		echo "$(GREEN)Testing Python and core packages...$(NC)"; \
		conda run -n $(ENV_NAME) python -c "import sys; print(f'Python version: {sys.version}')"; \
		conda run -n $(ENV_NAME) python -c "import numpy as np; print(f'NumPy version: {np.__version__}')"; \
		conda run -n $(ENV_NAME) python -c "import pandas as pd; print(f'Pandas version: {pd.__version__}')"; \
		conda run -n $(ENV_NAME) python -c "import matplotlib; print(f'Matplotlib version: {matplotlib.__version__}')"; \
		conda run -n $(ENV_NAME) python -c "import sklearn; print(f'Scikit-learn version: {sklearn.__version__}')"; \
		conda run -n $(ENV_NAME) python -c "import yaml; print('PyYAML: OK')"; \
		conda run -n $(ENV_NAME) python -c "import openpyxl; print('OpenPyXL: OK')"; \
		conda run -n $(ENV_NAME) python -c "import src.utilities as utils; print('Utilities: OK')"; \
		conda run -n $(ENV_NAME) python -c "import src; print('Source modules: OK')"; \
		conda run -n $(ENV_NAME) python -c "import otoole; print('OtoOle: OK')"; \
		conda run -n $(ENV_NAME) python -c "import colorama; print('Colorama: OK')"; \
		conda run -n $(ENV_NAME) which glpsol > /dev/null && echo "GLPSOL: OK" || echo "$(RED)GLPSOL: NOT FOUND$(NC)"; \
		echo "$(GREEN)✓ Environment test completed!$(NC)"; \
	else \
		echo "$(RED)Environment '$(ENV_NAME)' does not exist.$(NC)"; \
		exit 1; \
	fi

# Run main script
.PHONY: run-main
run-main:
	@echo "$(GREEN)Running main.py in $(ENV_NAME) environment...$(NC)"
	@if conda env list | grep -q "^$(ENV_NAME) "; then \
		conda run -n $(ENV_NAME) python main.py; \
	else \
		echo "$(RED)Environment '$(ENV_NAME)' does not exist. Create it first.$(NC)"; \
		exit 1; \
	fi

# Show activation command
.PHONY: activate
activate:
	@echo "$(GREEN)To activate the environment, run:$(NC)"
	@echo "$(YELLOW)conda activate $(ENV_NAME)$(NC)"
	@echo ""
	@echo "$(GREEN)To deactivate, run:$(NC)"
	@echo "$(YELLOW)conda deactivate$(NC)"

# Clean temporary files
.PHONY: clean
clean:
	@echo "$(GREEN)Cleaning temporary files...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup completed!$(NC)"

# Development targets
.PHONY: dev-setup
dev-setup: setup
	@echo "$(GREEN)Setting up development environment...$(NC)"
	@conda run -n $(ENV_NAME) pip install black flake8 pytest
	@echo "$(GREEN)✓ Development tools installed!$(NC)"

# Quick environment recreation
.PHONY: recreate
recreate:
	@echo "$(GREEN)Recreating environment...$(NC)"
	@make env-remove
	@make env-create
	@make install-deps
	@echo "$(GREEN)✓ Environment recreated!$(NC)"

# Backup environment
.PHONY: backup
backup:
	@echo "$(GREEN)Creating environment backup...$(NC)"
	@mkdir -p backups
	@conda env export -n $(ENV_NAME) > backups/environment_backup_$(shell date +%Y%m%d_%H%M%S).yml
	@echo "$(GREEN)✓ Environment backed up to backups/ directory$(NC)"

# Show environment size
.PHONY: env-size
env-size:
	@echo "$(GREEN)Environment disk usage:$(NC)"
	@if conda env list | grep -q "^$(ENV_NAME) "; then \
		ENV_PATH=$$(conda env list | grep "^$(ENV_NAME) " | awk '{print $$2}'); \
		du -sh $$ENV_PATH 2>/dev/null || echo "Could not determine size"; \
	else \
		echo "$(RED)Environment '$(ENV_NAME)' does not exist.$(NC)"; \
	fi

# Check for updates
.PHONY: check-updates
check-updates:
	@echo "$(GREEN)Checking for package updates...$(NC)"
	@if conda env list | grep -q "^$(ENV_NAME) "; then \
		conda run -n $(ENV_NAME) conda list --outdated; \
	else \
		echo "$(RED)Environment '$(ENV_NAME)' does not exist.$(NC)"; \
	fi

# ============================================================================
# DOCUMENTATION TARGETS
# ============================================================================

# Documentation variables
DOCS_DIR = docs
DOCS_SOURCE_DIR = $(DOCS_DIR)/source
DOCS_BUILD_DIR = $(DOCS_DIR)/build
DOCS_HTML_DIR = $(DOCS_BUILD_DIR)/html
GH_PAGES_BRANCH = gh-pages

# Setup documentation dependencies
.PHONY: docs-setup
docs-setup:
	@echo "$(GREEN)Setting up documentation dependencies...$(NC)"
	@if conda env list | grep -q "^$(ENV_NAME) "; then \
		conda run -n $(ENV_NAME) pip install sphinx sphinx-book-theme myst-parser nbsphinx ghp-import sphinx-autodoc-typehints sphinx-autoapi; \
		echo "$(GREEN)✓ Documentation tools installed!$(NC)"; \
	else \
		echo "$(RED)Environment '$(ENV_NAME)' does not exist. Run 'make setup' first.$(NC)"; \
		exit 1; \
	fi

# Build documentation
.PHONY: docs-build
docs-build:
	@echo "$(GREEN)Building documentation...$(NC)"
	@if conda env list | grep -q "^$(ENV_NAME) "; then \
		if [ ! -d "$(DOCS_DIR)" ]; then \
			echo "$(RED)Documentation directory not found. Please ensure docs/ exists.$(NC)"; \
			exit 1; \
		fi; \
		cd $(DOCS_DIR) && conda run -n $(ENV_NAME) sphinx-build -b html source build/html --keep-going; \
		echo "$(GREEN)✓ Documentation built successfully!$(NC)"; \
		echo "$(YELLOW)Documentation available at: $(DOCS_HTML_DIR)/index.html$(NC)"; \
	else \
		echo "$(RED)Environment '$(ENV_NAME)' does not exist.$(NC)"; \
		exit 1; \
	fi

# Serve documentation locally
.PHONY: docs-serve
docs-serve:
	@echo "$(GREEN)Starting documentation server...$(NC)"
	@if [ ! -d "$(DOCS_HTML_DIR)" ]; then \
		echo "$(YELLOW)Documentation not built yet. Building now...$(NC)"; \
		make docs-build; \
	fi
	@echo "$(GREEN)Serving documentation at http://localhost:8000$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop the server$(NC)"
	@cd $(DOCS_HTML_DIR) && conda run -n $(ENV_NAME) python -m http.server 8000

# Clean documentation build files
.PHONY: docs-clean
docs-clean:
	@echo "$(GREEN)Cleaning documentation build files...$(NC)"
	@if [ -d "$(DOCS_BUILD_DIR)" ]; then \
		rm -rf $(DOCS_BUILD_DIR); \
		echo "$(GREEN)✓ Documentation build files cleaned!$(NC)"; \
	else \
		echo "$(YELLOW)No documentation build files to clean.$(NC)"; \
	fi

# Check documentation for errors
.PHONY: docs-check
docs-check:
	@echo "$(GREEN)Checking documentation for errors...$(NC)"
	@if conda env list | grep -q "^$(ENV_NAME) "; then \
		if [ ! -d "$(DOCS_DIR)" ]; then \
			echo "$(RED)Documentation directory not found.$(NC)"; \
			exit 1; \
		fi; \
		cd $(DOCS_DIR) && conda run -n $(ENV_NAME) sphinx-build -b html source build/html -E; \
		echo "$(GREEN)✓ Documentation check completed!$(NC)"; \
	else \
		echo "$(RED)Environment '$(ENV_NAME)' does not exist.$(NC)"; \
		exit 1; \
	fi

# Auto-generate API documentation from source code
.PHONY: docs-autodoc
docs-autodoc:
	@echo "$(GREEN)Auto-generating API documentation from source code...$(NC)"
	@if conda env list | grep -q "^$(ENV_NAME) "; then \
		if [ ! -d "$(DOCS_DIR)" ]; then \
			echo "$(RED)Documentation directory not found.$(NC)"; \
			exit 1; \
		fi; \
		if [ ! -d "src" ]; then \
			echo "$(RED)Source directory 'src' not found.$(NC)"; \
			exit 1; \
		fi; \
		echo "$(YELLOW)Installing sphinx-autodoc dependencies...$(NC)"; \
		conda run -n $(ENV_NAME) pip install sphinx-autodoc-typehints sphinx-autoapi; \
		echo "$(YELLOW)Generating module documentation...$(NC)"; \
		mkdir -p source/api; \
		cd $(DOCS_DIR) && conda run -n $(ENV_NAME) sphinx-apidoc -f -o source/api ../src --separate; \
		echo "$(YELLOW)Creating comprehensive API index...$(NC)"; \
		echo "# API Documentation" > source/api/index.rst; \
		echo "" >> source/api/index.rst; \
		echo "This section contains auto-generated documentation from the source code." >> source/api/index.rst; \
		echo "" >> source/api/index.rst; \
		echo "## Modules" >> source/api/index.rst; \
		echo "" >> source/api/index.rst; \
		echo ".. toctree::" >> source/api/index.rst; \
		echo "   :maxdepth: 2" >> source/api/index.rst; \
		echo "   :caption: Source Code Documentation" >> source/api/index.rst; \
		echo "" >> source/api/index.rst; \
		for file in source/api/src.*.rst; do \
			if [ -f "$$file" ]; then \
				basename "$$file" .rst >> source/api/index.rst; \
			fi; \
		done; \
		echo "$(YELLOW)Updating main documentation index...$(NC)"; \
		if ! grep -q "api/index" source/index.md; then \
			sed -i '/notes\/api_reference/a api/index' source/index.md; \
		fi; \
		echo "$(YELLOW)Creating module overview file...$(NC)"; \
		echo "# Module Overview" > source/api/modules.rst; \
		echo "" >> source/api/modules.rst; \
		echo "This page provides an overview of all modules in the Storage-in-OSeMOSYS framework." >> source/api/modules.rst; \
		echo "" >> source/api/modules.rst; \
		echo ".. autosummary::" >> source/api/modules.rst; \
		echo "   :toctree: _autosummary" >> source/api/modules.rst; \
		echo "   :caption: All Modules" >> source/api/modules.rst; \
		echo "   :template: module.rst" >> source/api/modules.rst; \
		echo "   :recursive:" >> source/api/modules.rst; \
		echo "" >> source/api/modules.rst; \
		echo "   src" >> source/api/modules.rst; \
		echo "$(YELLOW)Updating Sphinx configuration for autodoc...$(NC)"; \
		if [ -f "source/conf.py" ]; then \
			if ! grep -q "sphinx.ext.autodoc" source/conf.py; then \
				sed -i "/extensions = \[/a\\    'sphinx.ext.autodoc'," source/conf.py; \
			fi; \
			if ! grep -q "sphinx.ext.autosummary" source/conf.py; then \
				sed -i "/extensions = \[/a\\    'sphinx.ext.autosummary'," source/conf.py; \
			fi; \
			if ! grep -q "sphinx.ext.viewcode" source/conf.py; then \
				sed -i "/extensions = \[/a\\    'sphinx.ext.viewcode'," source/conf.py; \
			fi; \
			if ! grep -q "autoapi" source/conf.py; then \
				sed -i "/extensions = \[/a\\    'autoapi.extension'," source/conf.py; \
				echo "" >> source/conf.py; \
				echo "# AutoAPI configuration" >> source/conf.py; \
				echo "autoapi_dirs = ['../../src']" >> source/conf.py; \
				echo "autoapi_type = 'python'" >> source/conf.py; \
				echo "autoapi_template_dir = '_templates/autoapi'" >> source/conf.py; \
				echo "autoapi_options = ['members', 'undoc-members', 'show-inheritance', 'show-module-summary', 'special-members', 'imported-members']" >> source/conf.py; \
				echo "autoapi_python_class_content = 'both'" >> source/conf.py; \
				echo "autoapi_member_order = 'bysource'" >> source/conf.py; \
			fi; \
		fi; \
		echo "$(GREEN)✓ API documentation auto-generated successfully!$(NC)"; \
		echo "$(YELLOW)Generated files in: source/api/$(NC)"; \
		echo "$(YELLOW)Run 'make docs-build' to build the updated documentation$(NC)"; \
	else \
		echo "$(RED)Environment '$(ENV_NAME)' does not exist.$(NC)"; \
		exit 1; \
	fi

# Deploy documentation to GitHub Pages
.PHONY: docs-deploy
docs-deploy:
	@echo "$(GREEN)Deploying documentation to GitHub Pages...$(NC)"
	@if conda env list | grep -q "^$(ENV_NAME) "; then \
		if ! command -v git >/dev/null 2>&1; then \
			echo "$(RED)Git is not installed or not in PATH.$(NC)"; \
			exit 1; \
		fi; \
		if ! git status >/dev/null 2>&1; then \
			echo "$(RED)Not in a git repository.$(NC)"; \
			exit 1; \
		fi; \
		echo "$(YELLOW)Building documentation...$(NC)"; \
		make docs-build; \
		echo "$(YELLOW)Deploying to GitHub Pages...$(NC)"; \
		conda run -n $(ENV_NAME) ghp-import -n -p -f $(DOCS_HTML_DIR); \
		echo "$(GREEN)✓ Documentation deployed to GitHub Pages!$(NC)"; \
		echo "$(YELLOW)Documentation will be available at: https://$(shell git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\)\/\([^/.]*\).*/\1.github.io\/\2/')$(NC)"; \
	else \
		echo "$(RED)Environment '$(ENV_NAME)' does not exist.$(NC)"; \
		exit 1; \
	fi

# Force rebuild and deploy documentation
.PHONY: docs-redeploy
docs-redeploy:
	@echo "$(GREEN)Force rebuilding and deploying documentation...$(NC)"
	@make docs-clean
	@make docs-build
	@make docs-deploy

# Live documentation development
.PHONY: docs-live
docs-live:
	@echo "$(GREEN)Starting live documentation development server...$(NC)"
	@if conda env list | grep -q "^$(ENV_NAME) "; then \
		conda run -n $(ENV_NAME) pip install sphinx-autobuild; \
		echo "$(GREEN)Starting live reload server at http://localhost:8000$(NC)"; \
		echo "$(YELLOW)Documentation will auto-rebuild on changes. Press Ctrl+C to stop.$(NC)"; \
		cd $(DOCS_DIR) && conda run -n $(ENV_NAME) sphinx-autobuild source build/html --host 0.0.0.0 --port 8000; \
	else \
		echo "$(RED)Environment '$(ENV_NAME)' does not exist.$(NC)"; \
		exit 1; \
	fi

# Create documentation backup
.PHONY: docs-backup
docs-backup:
	@echo "$(GREEN)Creating documentation backup...$(NC)"
	@if [ -d "$(DOCS_HTML_DIR)" ]; then \
		mkdir -p backups; \
		tar -czf backups/docs_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz $(DOCS_HTML_DIR); \
		echo "$(GREEN)✓ Documentation backup created in backups/ directory$(NC)"; \
	else \
		echo "$(YELLOW)No built documentation to backup. Run 'make docs-build' first.$(NC)"; \
	fi

# Check documentation dependencies
.PHONY: docs-deps-check
docs-deps-check:
	@echo "$(GREEN)Checking documentation dependencies...$(NC)"
	@if conda env list | grep -q "^$(ENV_NAME) "; then \
		conda run -n $(ENV_NAME) python -c "import sphinx; print(f'Sphinx: {sphinx.__version__}')"; \
		conda run -n $(ENV_NAME) python -c "import myst_parser; print('MyST Parser: OK')"; \
		conda run -n $(ENV_NAME) python -c "import nbsphinx; print('nbsphinx: OK')"; \
		conda run -n $(ENV_NAME) python -c "try: import sphinx_autodoc_typehints; print('Autodoc TypeHints: OK'); except ImportError: print('$(YELLOW)Autodoc TypeHints: NOT FOUND$(NC)')"; \
		conda run -n $(ENV_NAME) python -c "try: import autoapi; print('AutoAPI: OK'); except ImportError: print('$(YELLOW)AutoAPI: NOT FOUND$(NC)')"; \
		conda run -n $(ENV_NAME) which ghp-import > /dev/null && echo "ghp-import: OK" || echo "$(YELLOW)ghp-import: NOT FOUND (run 'make docs-setup')$(NC)"; \
		echo "$(GREEN)✓ Documentation dependencies check completed!$(NC)"; \
	else \
		echo "$(RED)Environment '$(ENV_NAME)' does not exist.$(NC)"; \
		exit 1; \
	fi

# Complete documentation workflow - autodoc + build + serve
.PHONY: docs-full
docs-full:
	@echo "$(GREEN)Running complete documentation workflow...$(NC)"
	@make docs-autodoc
	@make docs-build
	@echo "$(GREEN)✓ Complete documentation workflow finished!$(NC)"
	@echo "$(YELLOW)Run 'make docs-serve' to preview or 'make docs-deploy' to publish$(NC)"

# Show documentation status
.PHONY: docs-status
docs-status:
	@echo "$(GREEN)Documentation Status:$(NC)"
	@echo "Documentation Directory: $(DOCS_DIR)"
	@echo "Source Directory: $(DOCS_SOURCE_DIR)"
	@echo "Build Directory: $(DOCS_BUILD_DIR)"
	@echo "HTML Output: $(DOCS_HTML_DIR)"
	@echo ""
	@if [ -d "$(DOCS_DIR)" ]; then \
		echo "$(GREEN)Source Status: EXISTS$(NC)"; \
		echo "Source files:"; \
		find $(DOCS_SOURCE_DIR) -name "*.md" -o -name "*.rst" | head -10; \
	else \
		echo "$(RED)Source Status: NOT FOUND$(NC)"; \
	fi
	@echo ""
	@if [ -d "$(DOCS_HTML_DIR)" ]; then \
		echo "$(GREEN)Build Status: EXISTS$(NC)"; \
		echo "Built: $$(date -r $(DOCS_HTML_DIR)/index.html 2>/dev/null || echo 'Unknown')"; \
		echo "Size: $$(du -sh $(DOCS_HTML_DIR) 2>/dev/null | cut -f1 || echo 'Unknown')"; \
	else \
		echo "$(RED)Build Status: NOT BUILT$(NC)"; \
	fi
	@echo ""
	@if git show-ref --verify --quiet refs/heads/gh-pages; then \
		echo "$(GREEN)GitHub Pages Branch: EXISTS$(NC)"; \
		echo "Last commit: $$(git log gh-pages -1 --format='%h %s' 2>/dev/null || echo 'Unknown')"; \
	else \
		echo "$(YELLOW)GitHub Pages Branch: NOT FOUND$(NC)"; \
	fi
