#!/usr/bin/env python3
"""
Startup script for Bitbucket MCP Server
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run server
from server import main
import asyncio

if __name__ == "__main__":
    print("=" * 60)
    print("Bitbucket MCP Server - Read-Only Repository Access")
    print("=" * 60)
    asyncio.run(main())
