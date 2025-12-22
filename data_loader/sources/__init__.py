"""
Data source implementations.

This package contains loaders for various data sources.
Currently supports:
- Local files

Future sources can be added by extending BaseLoader:
- GitHub
- SharePoint
- Azure services
- And more...
"""

# Import loaders
from .local import LocalFileLoader

# Future sources (to be added):
# from .github import GitHubLoader
# from .sharepoint import SharePointLoader
# from .azure import AzureLoader

__all__ = [
    'LocalFileLoader',
    # Add future loaders here as they are implemented
]

