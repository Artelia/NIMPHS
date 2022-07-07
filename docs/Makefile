# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build
MODULE        = tbb


# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile
	
# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).

# Rename tbb/__init__.py to avoid problems if a python module is not found
# Comment '@persistent' decorator because fake-bpy-module defines it at 'None', which is not callable and causes errors during 'sphinx-build'
%: Makefile
	mv ../$(MODULE)/__init__.py ../$(MODULE)/___init__.py
	find ../$(MODULE)/ -type f -name "*.py" -exec sed -i 's/@persistent/#@persistent/g' {} +
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	find ../$(MODULE)/ -type f -name "*.py" -exec sed -i 's/#@persistent/@persistent/g' {} +
	mv ../$(MODULE)/___init__.py ../$(MODULE)/__init__.py