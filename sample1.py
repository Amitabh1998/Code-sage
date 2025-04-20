import os

def crawl_directory(path, level=0):
    indent = "  " * level
    print(f"{indent}📁 {os.path.basename(path)}")

    try:
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                crawl_directory(full_path, level + 1)
            else:
                print(f"{indent}  📄 {entry}")
    except PermissionError:
        print(f"{indent}  ❌ Permission denied")

def count_files_and_folders(path):
    file_count = 0
    folder_count = 0

    for root, dirs, files in os.walk(path):
        folder_count += len(dirs)
        file_count += len(files)

    return {
        "files": file_count,
        "folders": folder_count
    }

def get_total_size(path):
    total_size = 0

    for entry in os.scandir(path):
        try:
            if entry.is_file():
                total_size += entry.stat().st_size
            elif entry.is_dir():
                total_size += get_total_size(entry.path)
        except PermissionError:
            continue

    return total_size

def main():
    path = input("Enter directory path to analyze: ")
    if not os.path.isdir(path):
        print("❌ Invalid directory.")
        return

    print("\n🔍 Crawling directory structure...")
    crawl_directory(path)

    print("\n📊 Counting files and folders...")
    stats = count_files_and_folders(path)
    print(f"📄 Files: {stats['files']}")
    print(f"📁 Folders: {stats['folders']}")

    print("\n📦 Calculating total size...")
    size = get_total_size(path)
    print(f"🧮 Total Size: {size / 1024:.2f} KB")

if __name__ == "__main__":
    main()
