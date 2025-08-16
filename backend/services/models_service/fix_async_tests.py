#!/usr/bin/env python3
"""
Fix pytest-asyncio decorators in test files
Replace @pytest_asyncio.async_test with @pytest.mark.asyncio
"""

import os
import re
from pathlib import Path

def fix_async_decorators():
    """Fix async test decorators in all test files"""
    test_dir = Path("tests")
    
    if not test_dir.exists():
        print("Tests directory not found")
        return
    
    files_fixed = 0
    total_replacements = 0
    
    for test_file in test_dir.glob("test_*.py"):
        print(f"Processing {test_file}")
        
        # Read file content
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Count occurrences before replacement
        before_count = content.count('@pytest_asyncio.async_test')
        
        # Replace the problematic decorator
        new_content = content.replace(
            '@pytest_asyncio.async_test',
            '@pytest.mark.asyncio'
        )
        
        # Count after replacement
        after_count = new_content.count('@pytest.mark.asyncio')
        replacements = before_count
        
        if replacements > 0:
            # Write back the file
            with open(test_file, 'w') as f:
                f.write(new_content)
            
            files_fixed += 1
            total_replacements += replacements
            print(f"  ✅ Fixed {replacements} decorators in {test_file}")
        else:
            print(f"  ⏭️  No changes needed in {test_file}")
    
    print(f"\n📊 Summary:")
    print(f"Files processed: {len(list(test_dir.glob('test_*.py')))}")
    print(f"Files fixed: {files_fixed}")
    print(f"Total decorators fixed: {total_replacements}")

if __name__ == "__main__":
    fix_async_decorators()
