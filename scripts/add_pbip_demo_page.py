#!/usr/bin/env python3
"""Deprecated entry point - use add_pbip_walkthrough_page.py."""
from add_pbip_walkthrough_page import build_walkthrough_page, main

__all__ = ["build_walkthrough_page", "main"]

# Legacy alias used by rebuild_all_pbip_pages.py imports.
build_demo_page = build_walkthrough_page

if __name__ == "__main__":
    main()
