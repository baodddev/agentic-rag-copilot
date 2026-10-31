from pathlib import Path

# Currrent working directoy
root = Path(".")

# Folders to create 
folders = [
    "app/api",
    "app/core",
    "app/rag",
    "app/services",
    "data",
    "templates",
    "static",
    "uploads",
    "tests",
]

# Fies to create
files = [
    "app/main.py",
    "ingest_sample_kb.py",
    "requirements.txt",
    "run.py",
    ".env",
]

# create folder
for folder in folders:
    (root/folder).mkdir(parents=True,exist_ok=True)

# create files
for file in files:
    (root/file).touch(exist_ok=True)


print("Project structure created sucessfully")