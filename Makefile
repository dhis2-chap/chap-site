.PHONY: fetch-docs serve build clean help

# Default target
help:
	@echo "Available targets:"
	@echo "  fetch-docs  - Fetch external documentation from configured repos"
	@echo "  serve       - Fetch docs and start local development server"
	@echo "  build       - Fetch docs and build the site"
	@echo "  clean       - Remove build artifacts and temp directories"
	@echo "  help        - Show this help message"

# Fetch external documentation
fetch-docs:
	python scripts/fetch-external-docs.py

# Serve locally (fetches docs first)
serve: fetch-docs
	mkdocs serve

# Build the site (fetches docs first)
build: fetch-docs
	mkdocs build

# Clean up build artifacts and temp directories
clean:
	rm -rf site/
	rm -rf .modeling-app-temp/
