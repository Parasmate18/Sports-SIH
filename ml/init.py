"""Compatibility module for the requested ``ml/init.py`` file.

Python uses ``ml/__init__.py`` to mark this directory as a package. This file
keeps the requested project structure while exposing the same public constants.
"""

from ml import MODEL_VERSION, RANDOM_STATE

__all__ = ["MODEL_VERSION", "RANDOM_STATE"]
