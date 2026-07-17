import os

def identify_and_fix_excel(file_path, output_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    file_size = os.path.getsize(file_path)
    print(f"File Size: {file_size} bytes")
    
    if file_size == 0:
        print("Error: The file is empty (0 bytes). It cannot be recovered.")
        return

    # Read the first few bytes (the "magic number") to identify the real file type
    with open(file_path, "rb") as f:
        header = f.read(8)
    
    print(f"File Header Hex: {header.hex().upper()}")

    # 1. Check for True Modern Excel / Zip (PK..)
    if header.startswith(b"PK\x03\x04"):
        print("Diagnosis: This IS a valid zip structure. If openpyxl failed, the zip directory might be corrupted.")
        return

    # 2. Check for Old Excel 97-2003 (D0 CF 11 E0 ...)
    elif header.startswith(b"\xd0\xcf\x11\xe0"):
        print("Diagnosis: This is an old Excel 97-2003 binary file (.xls) renamed to .xlsx!")
        print("Attempting legacy parsing and protection removal...")
        try:
            import xlrd
            # open_workbooks automatically ignores sheet protection flags when reading raw data
            wb = xlrd.open_workbook(file_path, formatting_info=False)
            print(f"✓ Successfully opened legacy file. Found {wb.nsheets} sheets.")
            
            # Since xlrd is read-only, we would normally rebuild it. 
            # But if it opens here, you can just rename 'R.xlsx' to 'R.xls' on your desktop and open it!
            print("\n[ACTION REQUIRED]: Simply rename your file from 'R.xlsx' to 'R.xls' in Windows Explorer.")
            print("Excel will then open it natively without the Zip error.")
            
        except Exception as e:
            print(f"Failed to parse legacy structure: {e}")

    # 3. Completely unrecognized or corrupted
    else:
        print("Diagnosis: The file headers match neither modern nor legacy Excel formats.")
        print("The file appears to be corrupted, unfinalized, or a different file type entirely.")

# Configuration
INPUT_PATH = r"D:\excel-recovery\R.xlsx"
OUTPUT_PATH = r"D:\excel-recovery\R_fixed.xls"

identify_and_fix_excel(INPUT_PATH, OUTPUT_PATH)