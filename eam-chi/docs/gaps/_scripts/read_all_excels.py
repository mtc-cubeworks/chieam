import openpyxl

files = {
    'Maintenance Management': '/Users/macbookair/dev_projects/enhanced-ueml/system-generation/eam-fast-api/docs/PAN/Maintenance_Management_Data_Validated.xlsx20250702-v4.xlsx',
    'Purchasing & Stores': '/Users/macbookair/dev_projects/enhanced-ueml/system-generation/eam-fast-api/docs/PAN/Purchasing_And_Stores_Data.xlsx',
    'Core EAM': '/Users/macbookair/dev_projects/enhanced-ueml/system-generation/eam-fast-api/docs/PAN/Core_EAM_Data.xlsx',
}

for label, path in files.items():
    try:
        wb = openpyxl.load_workbook(path, read_only=True)
        print(f"\n=== {label} ===")
        for i, name in enumerate(wb.sheetnames, 1):
            print(f"  {i}. {name}")
        wb.close()
    except Exception as e:
        print(f"\n=== {label} === ERROR: {e}")
