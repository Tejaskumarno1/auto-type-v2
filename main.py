#!/usr/bin/env python3
"""
Auto Typer Pro v2.0 — Senior Dev Edition
Entry point.
"""
import sys
import os
import logging

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(name)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

from ui.app import AutoTyperPro


def main():
    app = AutoTyperPro()
    app.mainloop()


if __name__ == "__main__":
    main()
