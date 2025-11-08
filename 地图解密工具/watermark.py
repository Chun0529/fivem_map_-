import os
import argparse

def watermark(path, content):
    try:
        for current_folder, subfolders, files in os.walk(path):
            readme_path = os.path.join(current_folder, "kook.txt")
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(content)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a watermark in all folders")
    parser.add_argument("-d", "--directory", required=True, help="Target directory")
    args = parser.parse_args()

    content = """
    https://kook.vip/1mUKyN 
    https://kook.vip/1mUKyN
    https://kook.vip/1mUKyN
    https://kook.vip/1mUKyN
    https://kook.vip/1mUKyN
    """
    watermark(args.directory, content) 