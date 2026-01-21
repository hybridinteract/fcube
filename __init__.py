"""
FCube CLI - FastAPI Module Generator

A modern CLI tool for generating modular FastAPI applications following
the Korab Backend architecture patterns.

Features:
- Clean Architecture with layered design
- Dependency Injection pattern
- Role-based access control (RBAC)
- Proper folder structure (models/, schemas/, crud/, services/, routes/)
- Integration facades for cross-module communication
- Transaction management following "No Commit in CRUD" pattern
"""

__version__ = "1.0.0"
__author__ = "Amal Babu"
__author_email__ = "amalbabu1200@gmail.com"
__github__ = "https://github.com/amal-babu-git"

from .cli import app

__all__ = ["app"]
