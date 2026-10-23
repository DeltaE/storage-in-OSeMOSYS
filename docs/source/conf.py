# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath('../..'))

# For Read the Docs compatibility
on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
    # Set up minimal environment for Read the Docs
    import warnings
    warnings.filterwarnings("ignore")
    
    # Add additional mock imports for Read the Docs
    additional_mocks = [
        'numba', 'dask', 'distributed', 'lxml', 'openpyxl', 'xlrd',
        'pyarrow', 'fastparquet', 'tables', 'bottleneck', 'numexpr'
    ]

project = 'Storage in OSeMOSYS'
copyright = '2025, Bruno Borba, Md Eliasinul Islam'
author = 'Bruno Borba, Md Eliasinul Islam'
release = '2025.07'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'autoapi.extension',
    "myst_parser",  # Markdown support
    "sphinx.ext.duration",
    "sphinx.ext.autodoc",  # Automatic documentation from docstrings
    "sphinx.ext.napoleon",  # Google-style docstrings
    "nbsphinx",  # Jupyter Notebook support
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",  # Links to source code
    "sphinxcontrib.mermaid",  # Mermaid diagrams
]

# MyST parser configuration
myst_enable_extensions = [
    "colon_fence",
    "html_admonition",
]

# MyST configuration for eval-rst
myst_fence_as_directive = ["eval-rst", "mermaid"]

templates_path = ['_templates']
exclude_patterns = ['**/.ipynb_checkpoints']

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://pydata-sphinx-theme.readthedocs.io/

html_theme = 'pydata_sphinx_theme'
html_title = 'Storage in OSeMOSYS'
html_static_path = ['_static']
html_css_files = ['custom.css']
html_js_files = ['header-buttons.js']
html_logo = '_static/storage_in_osemosys_icon.png'
html_favicon = '_static/favicon.png'
html_show_sourcelink = False

html_theme_options = {
    "logo": {"text": "Storage in OSeMOSYS"},
    # Top navbar = the four sections (Concept, Workflow, Results, API)
    "navbar_align": "left",
    "header_links_before_dropdown": 5,
    "navbar_start": ["navbar-logo", "home-button"],
    "navbar_end": ["search-button", "mode-button", "fullscreen-button", "icon-links"],
    "navbar_persistent": [],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/DeltaE/storage-in-OSeMOSYS",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
    ],
    "show_toc_level": 2,
    "secondary_sidebar_items": {"**": ["page-toc"], "index": []},
    "show_prev_next": True,
    "footer_start": ["copyright"],
    "footer_center": [],
    "footer_end": [],
    "use_edit_page_button": False,
}

# Opens in light mode; the header button switches to dark (choice is remembered)
html_context = {"default_mode": "light"}

# No left sidebar anywhere: the "On this page" panel on the right is the page index
html_sidebars = {"**": []}

autodoc_default_options = {
    'members': True,
    'undoc-members': False,
    'show-inheritance': True,
    'private-members': False,  # Exclude private members
    'special-members': False,  # Exclude special members (dunder methods)
}

# Suppress warnings and errors for Read the Docs compatibility
suppress_warnings = ['autodoc.import_error', 'autodoc', 'app.add_autodoc_attrgetter']
autodoc_inherit_docstrings = False

# NBSphinx configuration for Jupyter notebooks
nbsphinx_execute = 'never'  # Don't execute notebooks during build
nbsphinx_allow_errors = True  # Allow notebooks with errors to be included
nbsphinx_timeout = 60  # Timeout for notebook execution

# Additional NBSphinx settings for better compatibility
nbsphinx_kernel_name = 'python3'
nbsphinx_codecell_lexer = 'none'

# Function to skip documentation based on NODOC or :nodoc: markers
def skip_nodoc_members(app, what, name, obj, skip, options):
    """
    Skip documentation for members that contain NODOC or :nodoc: markers.
    Also automatically skip dunder methods (methods starting and ending with __).
    
    This function checks:
    1. Dunder methods (e.g., __init__, __str__, __repr__, etc.)
    2. Docstrings containing 'NODOC' or ':nodoc:' (case insensitive)
    3. Names containing 'NODOC' or ':nodoc:' 
    4. Module-level comments or attributes with these markers
    
    Args:
        app: The Sphinx application object
        what: The type of object being documented ('module', 'class', 'method', etc.)
        name: The fully qualified name of the object
        obj: The object itself
        skip: Current skip decision
        options: The options given to the directive
    
    Returns:
        bool: True to skip documentation, False to include it
    """
    if skip:  # If already marked to skip, respect that
        return True
    
    # Skip dunder methods (methods starting and ending with double underscores)
    if name and hasattr(obj, '__name__'):
        method_name = obj.__name__
        if method_name.startswith('__') and method_name.endswith('__'):
            # Allow some common dunder methods that might be useful in documentation
            allowed_dunder = ['__call__', '__iter__', '__len__', '__getitem__', '__setitem__']
            if method_name not in allowed_dunder:
                return True
    
    # Also check the qualified name for dunder methods
    if name:
        parts = name.split('.')
        if parts:
            last_part = parts[-1]
            if last_part.startswith('__') and last_part.endswith('__'):
                # Allow the same exceptions
                allowed_dunder = ['__call__', '__iter__', '__len__', '__getitem__', '__setitem__']
                if last_part not in allowed_dunder:
                    return True
    
    # Check the object's docstring for NODOC or :nodoc: markers
    docstring = getattr(obj, '__doc__', None)
    if docstring:
        docstring_lower = docstring.lower()
        if 'nodoc' in docstring_lower or ':nodoc:' in docstring_lower:
            return True
    
    # Check the object's name for NODOC markers
    if name:
        name_lower = name.lower()
        if 'nodoc' in name_lower:
            return True
    
    # Check for module-level NODOC markers
    if what == 'module' and hasattr(obj, '__all__'):
        # Check if NODOC is in __all__ (unlikely but possible)
        all_items = getattr(obj, '__all__', [])
        if any('nodoc' in str(item).lower() for item in all_items):
            return True
    
    # For classes and functions, check for NODOC in various attributes
    if hasattr(obj, '__name__'):
        obj_name_lower = obj.__name__.lower()
        if 'nodoc' in obj_name_lower:
            return True
    
    # Check for NODOC in module file path or module docstring
    if what == 'module' and hasattr(obj, '__file__'):
        module_file = getattr(obj, '__file__', '')
        if module_file and 'nodoc' in module_file.lower():
            return True
    
    return False

def setup(app):
    """
    Set up the Sphinx application with custom event handlers.
    """
    # Connect the skip function to the autodoc-skip-member event
    app.connect('autodoc-skip-member', skip_nodoc_members)
    
    return {
        'version': '1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }

# AutoAPI configuration
autoapi_dirs = ['../../src']
autoapi_type = 'python'
autoapi_template_dir = '_templates/autoapi'
autoapi_options = ['members', 'undoc-members', 'show-inheritance', 'show-module-summary', 'special-members', 'imported-members']
autoapi_python_class_content = 'both'
autoapi_member_order = 'bysource'
autoapi_add_toctree_entry = False  # linked from api.md instead
