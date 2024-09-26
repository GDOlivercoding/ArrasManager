import os
os.chdir(os.path.dirname(__file__))

print("Downloading requirements...")
os.system("pip install -r requirements.txt")
input("Done!")