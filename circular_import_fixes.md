# Circular Import Fixes

## Overview

This document outlines the fixes applied to resolve circular import issues in the Tower of Temptation PvP Statistics Discord Bot models.

## Problem

Several circular import dependencies existed between models:

1. `models/event.py` imported `models/player.py` but Player also needed Event data
2. `models/faction.py` imported `models/player.py` but Player also needed Faction data
3. `models/event.py` had a self-import issue with the Connection class referencing Event

## Approach

Rather than creating complex import structures or using lazy imports, we've applied a more robust solution:

1. Remove problematic imports entirely
2. Use direct database operations for cross-model functionality
3. Return dictionaries instead of model instances when retrieving related data
4. Use string type annotations where appropriate

## Changes Applied

### 1. Fixed models/event.py

- Removed `from models.player import Player` import
- Replaced `Player.create_or_update()` with direct database operations
- Replaced `from models.event import Event` self-import with direct database query
- Access `db.players` collection directly instead of through Player model

### 2. Fixed models/faction.py

- Removed `from models.player import Player` import
- Updated method signatures to return `dict` instead of `Player` where appropriate
- Replaced player access in the following methods:
  - `create`: Update players collection directly to set faction ID
  - `add_member`: Update players collection directly
  - `remove_member`: Update players collection directly
  - `delete`: Update all members' faction ID directly
  - `get_members`: Fetch player data directly from database
  - `get_admins`: Fetch player data directly from database
  - `get_owner`: Fetch owner data directly from database
- Updated `get_stats()` to use dictionary access with `.get()` method and default values

## Testing

A new test script `test_circular_import_fixes.py` was created to verify that all models can be imported correctly without circular reference errors.

## Benefits

1. **Improved Code Robustness**: Eliminated fragile import dependencies
2. **Better Performance**: Direct database access is more efficient than nested model instantiation
3. **Type Safety**: Added proper type hints for returned dictionaries
4. **Explicit Error Handling**: Added default values to handle missing fields
5. **Maintainability**: Easier to understand code structure

## Potential Future Improvements

1. Consider using a factory pattern for model creation
2. Implement an ORM-style relationship system
3. Add data validation for dictionary access