"""
Fix server validation function calls in the codebase

This script updates references from the deprecated check_server_existence
to the new standardized check_server_exists function from server_utils.py.

It correctly updates the parameter order and references to match the new signature:
- check_server_exists(db, guild_id, server_id)
"""
import os
import re


def update_file(file_path, dry_run=False):
    """
    Update server validation function calls in a file
    
    Args:
        file_path: Path to the file to update
        dry_run: If True, don't actually write changes
    
    Returns:
        Tuple of (file_updated, changes_made)
    """
    print(f"Processing {file_path}")
    
    if not os.path.isfile(file_path):
        print(f"  Error: File {file_path} not found")
        return False, 0
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the pattern - looking for check_server_existence function call
    pattern = r'check_server_existence\s*\(\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*\)'
    
    # Find all occurrences
    matches = re.findall(pattern, content)
    if not matches:
        print(f"  No occurrences found in {file_path}")
        return False, 0
    
    print(f"  Found {len(matches)} occurrences in {file_path}")
    
    # Replace each occurrence with correct parameter order
    changes_made = 0
    for match in matches:
        guild_var, server_id_var, db_var = match
        # Look for the pattern with the specific variables
        specific_pattern = f'check_server_existence\\s*\\(\\s*{guild_var}\\s*,\\s*{server_id_var}\\s*,\\s*{db_var}\\s*\\)'
        replacement = f'check_server_exists({db_var}, {guild_var}.id, {server_id_var})'
        
        # Replace this specific occurrence
        new_content = re.sub(specific_pattern, replacement, content)
        
        if new_content != content:
            content = new_content
            changes_made += 1
    
    if changes_made > 0 and not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Updated {changes_made} occurrences in {file_path}")
    elif changes_made > 0:
        print(f"  Would update {changes_made} occurrences in {file_path} (dry run)")
    
    return changes_made > 0, changes_made
    
    
def add_imports(file_path, dry_run=False):
    """
    Add import for check_server_exists if not present
    
    Args:
        file_path: Path to the file to update
        dry_run: If True, don't actually write changes
    
    Returns:
        Boolean indicating if file was updated
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the import is already present
    if 'from utils.server_utils import' in content:
        # Check if check_server_exists is imported
        if 'from utils.server_utils import' in content and 'check_server_exists' not in content:
            # Add check_server_exists to the existing import
            content = re.sub(
                r'from utils\.server_utils import (.*)',
                r'from utils.server_utils import \1, check_server_exists',
                content
            )
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            return True
    else:
        # Add new import line
        import_line = 'from utils.server_utils import check_server_exists\n'
        # Find a good place to insert (after other imports)
        lines = content.split('\n')
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_index = i + 1
            elif line and not line.startswith('#') and not insert_index:
                # First non-import, non-comment line
                break
        
        lines.insert(insert_index, import_line)
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
        return True
    
    return False


def main():
    """
    Update all files with server validation function calls
    """
    print("Fixing server validation function calls...")
    
    # Define files to check
    cog_files = [
        'cogs/bounties.py',
        'cogs/stats.py',
        'cogs/setup.py',
        'cogs/admin.py',
        'cogs/economy.py',
        'cogs/events.py',
        'cogs/killfeed.py',
        'cogs/player_links.py'
    ]
    
    files_updated = 0
    total_changes = 0
    
    # Update each file
    for file_path in cog_files:
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            continue
            
        updated, changes = update_file(file_path)
        if updated:
            add_imports(file_path)
            files_updated += 1
            total_changes += changes
    
    print(f"Updated {files_updated} files with {total_changes} changes")


if __name__ == "__main__":
    main()