#!/usr/bin/env python3
"""
AI Avatar System - Main Runner
Run this file to start the server
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.main import main

if __name__ == "__main__":
    print("=" * 50)
    print("AI Avatar System Starting...")
    print("=" * 50)
    print("\nMake sure you have installed requirements:")
    print("pip install -r requirements.txt")
    print("\nStarting server...")
    print("-" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all requirements are installed")
        print("2. Check if port 8765 is available")
        print("3. Run with: python run.py")