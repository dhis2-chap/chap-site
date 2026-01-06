.PHONY: fetch-docs serve build clean help

help:
	@echo "Available targets:"
	@echo "  fetch-docs  - Fetch external documentation from configured repos"
	@echo "  serve       - Fetch docs and start local development server"
	@echo "  build       - Fetch docs and build the site"
	@echo "  clean       - Remove build artifacts and temp directories"
	@echo "  help        - Show this help message"

fetch-docs:
	python scripts/fetch-external-docs.py

serve: fetch-docs
	mkdocs serve

build: fetch-docs
	mkdocs build

clean:
	rm -rf site/
	rm -rf .modeling-app-temp/
