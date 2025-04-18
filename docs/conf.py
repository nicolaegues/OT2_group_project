# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'OptoBot'
copyright = '2025, Akthar Uzzaman, Hanxuan Sheng, Hodan Abdi, Nicola Egues Muhlberger, Pavan Ponupureddi, Sebastian Parkin'
author = 'Akthar Uzzaman, Hanxuan Sheng, Hodan Abdi, Nicola Egues Muhlberger, Pavan Ponupureddi, Sebastian Parkin'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']
