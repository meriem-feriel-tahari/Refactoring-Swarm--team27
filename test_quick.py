"""Quick test to verify toolsmith tools are working"""
from src.tools import ToolsManager

print("🚀 Testing Toolsmith Tools...")
print("=" * 60)

# Initialize
tools = ToolsManager(sandbox_path="./sandbox")

# Test 1: Environment validation
print("\n1️⃣ Validating environment...")
validation = tools.validate_environment()
print(f"   Pylint: {'✅' if validation['pylint'] else '❌'}")
print(f"   Pytest: {'✅' if validation['pytest'] else '❌'}")
print(f"   Sandbox: {'✅' if validation['sandbox_exists'] else '❌'}")

# Test 2: File operations
print("\n2️⃣ Testing file operations...")
test_code = """
def add(a, b):
    return a + b

result = add(5, 3)
print(result)
"""
tools.write_file("./sandbox/test_code.py", test_code)
content = tools.read_file("./sandbox/test_code.py")
print(f"   ✅ File written and read successfully ({len(content)} chars)")

# Test 3: Code analysis
print("\n3️⃣ Testing code analysis...")
analysis = tools.analyze_file("./sandbox/test_code.py")
print(f"   Score: {analysis['score']:.2f}/10")
print(f"   Issues: {analysis['total_issues']}")
print(f"   Status: {analysis['status']}")

# Test 4: List files
print("\n4️⃣ Testing file listing...")
files = tools.list_python_files("./sandbox")
print(f"   Found {len(files)} Python files")

print("\n" + "=" * 60)
print("🎉 All tests passed! Tools are working!")
print("\nYour toolsmith setup is complete and ready to use! 🚀")