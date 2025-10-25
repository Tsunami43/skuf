# Skuf - Makefile for publishing

.PHONY: publish

# Publish to PyPI
publish:
	@echo "Building package..."
	python -m build
	@echo "Publishing to PyPI..."
	python -m twine upload dist/*
	@echo "✅ Package published successfully!"
