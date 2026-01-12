"""Demo: Analyze messy code"""
from src.tools import ToolsManager

# Initialize
tools = ToolsManager()

print("🔍 Analyzing messy code...")
print("=" * 60)

# Analyze the messy code
result = tools.analyze_file('./badcode/bad.py')

print(f"\n📊 Analysis Results:")
print(f"   - Score: {result['score']:.2f}/10 ({result['percentage']:.1f}%)")
print(f"   - Total Issues: {result['total_issues']}")
print(f"   - Errors: {len(result['errors'])}")
print(f"   - Warnings: {len(result['warnings'])}")
print(f"   - Conventions: {len(result['conventions'])}")

if result['errors']:
    print(f"\n❌ Errors found:")
    for error in result['errors'][:3]:  # Show first 3
        print(f"   Line {error['line']}: {error['message']}")

if result['conventions']:
    print(f"\n📏 Style issues:")
    for conv in result['conventions'][:3]:  # Show first 3
        print(f"   Line {conv['line']}: {conv['message']}")

print("\n" + "=" * 60)
print("💡 This code needs refactoring!")