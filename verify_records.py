import json
import os
import glob
import sys
try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("Error: jsonschema module not found. Please install via 'pip install jsonschema'")
    sys.exit(1)

def validate_isaac_records():
    # Load Schema
    schema_path = "schema/isaac_record_v1.json"
    if not os.path.exists(schema_path):
        print(f"❌ Schema not found at {schema_path}")
        return False
        
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    print(f"✅ Loaded Schema: {schema['title']}")
    
    # Load Examples
    example_files = glob.glob("examples/*.json")
    if not example_files:
        print("❌ No examples found in examples/")
        return False
        
    all_passed = True
    print(f"\n🔍 validating {len(example_files)} Golden Records...")
    print("-" * 50)
    
    for example_file in example_files:
        filename = os.path.basename(example_file)
        try:
            with open(example_file, 'r') as f:
                data = json.load(f)
            
            # 1. JSON Schema Validation
            validate(instance=data, schema=schema)
            
            # 2. Logic Checks (Wiki Rules)
            # Check Measurement Series
            if 'measurement' in data:
                if 'series' not in data['measurement']:
                    raise ValidationError("Measurement block missing 'series'")
                for s in data['measurement']['series']:
                    if 'independent_variables' not in s: 
                         raise ValidationError(f"Series {s.get('series_id')} missing 'independent_variables'")
                    if 'channels' not in s:
                         raise ValidationError(f"Series {s.get('series_id')} missing 'channels'")

            # Check System Configuration Flatness
            if 'system' in data:
                conf = data['system'].get('configuration', {})
                for k, v in conf.items():
                    if isinstance(v, (dict, list)):
                        raise ValidationError(f"System configuration must be flat. Key '{k}' contains nested {type(v)}")

            print(f"✅ PASS: {filename}")
            
        except ValidationError as e:
            print(f"❌ FAIL: {filename}")
            print(f"   Reason: {e.message}")
            if len(e.path) > 0:
                print(f"   Path: {' -> '.join(str(p) for p in e.path)}")
            all_passed = False
        except json.JSONDecodeError:
            print(f"❌ FAIL: {filename} (Invalid JSON syntax)")
            all_passed = False
        except Exception as e:
            print(f"❌ FAIL: {filename} (Unexpected Parsing Error)")
            print(f"   {str(e)}")
            all_passed = False

    print("-" * 50)
    if all_passed:
        print("🎉 SUCCESS: All records are 100% v1.0 Compliant")
        return True
    else:
        print("⚠️  FAILURE: Consistency checks failed")
        return False

if __name__ == "__main__":
    if validate_isaac_records():
        sys.exit(0)
    else:
        sys.exit(1)
