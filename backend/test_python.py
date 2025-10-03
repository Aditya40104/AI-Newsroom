import sys
print("Python path:", sys.executable)
print("Python version:", sys.version)

try:
    import openai
    print("OpenAI imported successfully!")
    print("OpenAI version:", openai.__version__)
except ImportError as e:
    print("Failed to import openai:", e)
    
print("Python paths:")
for path in sys.path:
    print(" -", path)