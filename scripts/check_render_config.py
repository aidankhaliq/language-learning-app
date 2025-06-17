#!/usr/bin/env python3
"""
Render Configuration Checker
This script helps diagnose persistent storage issues on Render
"""

import os
import sys

def check_render_environment():
    """Check if we're running on Render"""
    render_vars = {
        'RENDER': os.getenv('RENDER'),
        'RENDER_SERVICE_ID': os.getenv('RENDER_SERVICE_ID'),
        'PORT': os.getenv('PORT'),
    }
    
    print("=== Render Environment Check ===")
    for var, value in render_vars.items():
        status = "✅" if value else "❌"
        print(f"{status} {var}: {value}")
    
    is_render = any(render_vars.values())
    print(f"\nRender detected: {'✅ YES' if is_render else '❌ NO'}")
    return is_render

def check_data_directory():
    """Check /data directory status"""
    print("\n=== /data Directory Check ===")
    
    # Check if directory exists
    exists = os.path.exists('/data')
    print(f"Directory exists: {'✅ YES' if exists else '❌ NO'}")
    
    if not exists:
        print("❌ ISSUE: /data directory does not exist")
        print("   This means persistent disk is not mounted")
        return False
    
    # Check if it's a directory
    is_dir = os.path.isdir('/data')
    print(f"Is directory: {'✅ YES' if is_dir else '❌ NO'}")
    
    # Check permissions
    readable = os.access('/data', os.R_OK)
    writable = os.access('/data', os.W_OK)
    executable = os.access('/data', os.X_OK)
    
    print(f"Readable: {'✅ YES' if readable else '❌ NO'}")
    print(f"Writable: {'✅ YES' if writable else '❌ NO'}")
    print(f"Executable: {'✅ YES' if executable else '❌ NO'}")
    
    # Try to write a test file
    try:
        test_file = '/data/test_write.tmp'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✅ Write test: SUCCESS")
        return True
    except Exception as e:
        print(f"❌ Write test: FAILED - {e}")
        return False

def check_database_location():
    """Check current database location"""
    print("\n=== Database Location Check ===")
    
    possible_locations = [
        '/data/database.db',
        'database.db',
        './database.db',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database.db')
    ]
    
    for location in possible_locations:
        abs_path = os.path.abspath(location)
        exists = os.path.exists(abs_path)
        size = os.path.getsize(abs_path) if exists else 0
        
        status = "✅" if exists else "❌"
        print(f"{status} {location}")
        print(f"    Absolute path: {abs_path}")
        print(f"    Size: {size} bytes")
        print()

def provide_solutions():
    """Provide solutions for common issues"""
    print("\n=== Solutions ===")
    print("If /data directory doesn't exist or isn't writable:")
    print()
    print("1. Go to your Render Dashboard")
    print("2. Navigate to your service")
    print("3. Go to Settings tab")
    print("4. Scroll to 'Disks' section")
    print("5. Click 'Add Disk' if no disk exists, or check existing disk")
    print("6. Configure:")
    print("   - Name: sqlite-data")
    print("   - Mount Path: /data")
    print("   - Size: 1 GB (or larger)")
    print("7. Save and redeploy your service")
    print()
    print("Alternative: Check your render.yaml file contains:")
    print("```yaml")
    print("disk:")
    print("  name: sqlite-data")
    print("  mountPath: /data")
    print("  sizeGB: 1")
    print("```")

def main():
    print("🔍 Render Persistent Storage Diagnostic Tool")
    print("=" * 50)
    
    is_render = check_render_environment()
    data_ok = check_data_directory()
    check_database_location()
    
    print("\n=== Summary ===")
    if is_render and data_ok:
        print("✅ Persistent storage is configured correctly!")
    elif is_render and not data_ok:
        print("❌ Persistent storage is NOT configured correctly!")
        provide_solutions()
    else:
        print("ℹ️  Not running on Render - this is normal for local development")

if __name__ == "__main__":
    main() 