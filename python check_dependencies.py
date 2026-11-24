
import sys
import flask
import pandas
import vaderSentiment
import yake
import dotenv

print("Python:", sys.version)
print("Flask:", flask.__version__ if hasattr(flask, "__version__") else "Installed")
print("Pandas:", pandas.__version__)
print("VADER: Installed")
print("YAKE: Installed")
print("python-dotenv: Installed")

print("\nAll dependencies imported successfully!")
