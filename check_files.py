# Create a file called check_files.py
import os

def check_training_files():
    path = r"C:\Users\DELL\Downloads\TRAINING_SAMPLES\TRAINING_SAMPLES"
    
    if not os.path.exists(path):
        print(f"❌ Path does not exist: {path}")
        return
    
    files = os.listdir(path)
    print(f"📁 Files in {path}:")
    for i, file in enumerate(files, 1):
        file_path = os.path.join(path, file)
        file_size = os.path.getsize(file_path) if os.path.isfile(file_path) else "DIR"
        print(f"  {i}. {file} ({file_size})")

if __name__ == "__main__":
    check_training_files()