from data_loader import get_loader, load_data, load_data_config
from data_loader.utils.config_loader import get_data_config_path
from pathlib import Path

source_name = "csv_data"  # Replace with your actual source name

print("=== load_data() Debugging ===\n")

# 1. Check what load_data will use
print("1. Config file contents:")
try:
    config_file_path = get_data_config_path()
    print(f"   Config file: {config_file_path}")
    
    data_config = load_data_config()
    source_config = data_config['sources'][source_name]
    file_path = source_config.get('pattern') or source_config.get('path')
    
    print(f"   Source name: {source_name}")
    print(f"   Source path/pattern from config: {file_path}")
    print(f"   Full source config: {source_config}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# 2. Check the loader that load_data creates
print("\n2. Loader created by load_data():")
try:
    # This is what load_data does internally
    from data_loader.factory import get_loader
    loader = get_loader()
    
    print(f"   loader.base_directory: {loader.base_directory}")
    print(f"   loader.config_file_path: {loader.config_file_path}")
    print(f"   loader.config: {loader.config}")
    
    # Test validate_source with the actual file_path from config
    print(f"\n3. Testing validate_source with config path/pattern:")
    print(f"   Testing: {file_path}")
    result = loader.validate_source(file_path)
    print(f"   validate_source result: {result}")
    
    if not result:
        print("\n   ⚠️  validate_source returned False!")
        print("   This is why load_data() is failing.")
        
        # Try to resolve the path manually
        print("\n4. Manual path resolution:")
        from data_loader.utils.file_finder import resolve_file_path
        try:
            resolved = resolve_file_path(
                file_path,
                base_directory=loader.base_directory,
                config_file_path=loader.config_file_path,
                match_strategy="first"
            )
            print(f"   ✓ Resolved path: {resolved}")
            print(f"   Exists: {resolved.exists()}")
            print(f"   Is file: {resolved.is_file()}")
        except Exception as e:
            print(f"   ✗ Resolution failed: {e}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# 3. Actually try load_data
print("\n5. Actually calling load_data():")
try:
    data = load_data(source_name)
    print(f"   ✓ Success! Loaded {len(data)} rows")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n=== End Debugging ===")