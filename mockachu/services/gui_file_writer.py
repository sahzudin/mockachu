import csv
import xml.etree.ElementTree as ET
import secrets
import zipfile
import ujson
import os
import pandas as pd
from pathlib import Path
from datetime import datetime

from ..generators.generator import GeneratorFormats


def write_for_gui(data, format, zip_file=False, custom_path=None, batch_size=1000):
    """
    Write data for GUI application with user-friendly file locations

    Args:
        data: The data to write
        format: GeneratorFormats enum value  
        zip_file: Whether to compress the output
        custom_path: Optional custom file path

    Returns:
        str: Full path to the created file
    """

    if custom_path:
        output_dir = Path(custom_path).parent
        filename_base = Path(custom_path).stem
    else:
        possible_dirs = [
            Path.home() / "Documents" / "Mockachu",
            Path.home() / "Downloads" / "Mockachu",
            Path.cwd() / "exports"
        ]

        output_dir = None
        for dir_path in possible_dirs:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                test_file = dir_path / "test_write.tmp"
                test_file.touch()
                test_file.unlink()
                output_dir = dir_path
                break
            except (PermissionError, OSError):
                continue

        if not output_dir:
            output_dir = Path.cwd()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_base = f"mock_data_{timestamp}"

    file_extension = format.name.lower()
    file_path = output_dir / f"{filename_base}.{file_extension}"

    if format == GeneratorFormats.JSON:
        _write_json(data, file_path)
    elif format == GeneratorFormats.XML:
        _write_xml(data, file_path)
    elif format == GeneratorFormats.CSV:
        _write_csv(data, file_path)
    elif format == GeneratorFormats.HTML:
        _write_html(data, file_path)
    elif format == GeneratorFormats.SQL:
        _write_sql(data, file_path, batch_size=batch_size)
    else:
        raise ValueError(f"Unsupported format: {format}")

    if zip_file:
        zip_path = file_path.with_suffix('.zip')
        _compress_file(file_path, zip_path)
        file_path.unlink()
        return str(zip_path)

    return str(file_path)


def _write_json(data, file_path):

    with open(file_path, "w", encoding='utf-8') as f:
        ujson.dump(data, f, indent=2, ensure_ascii=False)


def _write_xml(data, file_path):

    root = ET.Element("dataset")
    root.set("generated_at", datetime.now().isoformat())
    root.set("record_count", str(len(data)))

    for i, record in enumerate(data):
        record_elem = ET.SubElement(root, "record")
        record_elem.set("id", str(i + 1))

        for key, value in record.items():
            field_elem = ET.SubElement(record_elem, "field")
            field_elem.set("name", str(key))
            field_elem.text = str(value) if value is not None else ""

    ET.indent(root, space="  ", level=0)
    tree = ET.ElementTree(root)

    with open(file_path, "wb") as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)


def _write_csv(data, file_path):

    if not data:
        with open(file_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["No data generated"])
        return

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding='utf-8')


def _write_html(data, file_path):

    if not data:
        with open(file_path, "w", encoding='utf-8') as f:
            f.write("<!DOCTYPE html>\n<html>\n<head>\n<title>Mock Data</title>\n")
            f.write("<style>\n")
            f.write("table { border-collapse: collapse; width: 100%; }\n")
            f.write(
                "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n")
            f.write("th { background-color: #f2f2f2; font-weight: bold; }\n")
            f.write("tr:nth-child(even) { background-color: #f9f9f9; }\n")
            f.write("</style>\n</head>\n<body>\n")
            f.write("<h2>Mock Data Table</h2>\n")
            f.write("<p>No data generated</p>\n")
            f.write("</body>\n</html>")
        return

    with open(file_path, "w", encoding='utf-8') as f:
        f.write("<!DOCTYPE html>\n<html>\n<head>\n")
        f.write("<title>Mock Data</title>\n")
        f.write("<style>\n")
        f.write("table { border-collapse: collapse; width: 100%; }\n")
        f.write(
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n")
        f.write("th { background-color: #f2f2f2; font-weight: bold; }\n")
        f.write("tr:nth-child(even) { background-color: #f9f9f9; }\n")
        f.write("</style>\n</head>\n<body>\n")
        f.write("<h2>Mock Data Table</h2>\n")
        f.write("<table>\n")

        columns = list(data[0].keys())
        f.write("  <thead>\n    <tr>\n")
        for col in columns:
            f.write(f"      <th>{col}</th>\n")
        f.write("    </tr>\n  </thead>\n")

        f.write("  <tbody>\n")
        for row in data:
            f.write("    <tr>\n")
            for col in columns:
                value = row.get(col)
                cell_value = str(value) if value is not None else ""
                cell_value = cell_value.replace("&", "&amp;").replace(
                    "<", "&lt;").replace(">", "&gt;")
                f.write(f"      <td>{cell_value}</td>\n")
            f.write("    </tr>\n")
        f.write("  </tbody>\n</table>\n</body>\n</html>")


def _write_sql(data, file_path, batch_size=1000, table_name="mock_data"):

    if not data:
        with open(file_path, "w", encoding='utf-8') as f:
            f.write("-- No data generated\n")
        return

    with open(file_path, "w", encoding='utf-8') as f:
        f.write(f"-- Mock Data SQL Export\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n")
        f.write(f"-- Record count: {len(data)}\n")
        f.write(f"-- Batch size: {batch_size}\n\n")

        columns = list(data[0].keys())
        column_names = ", ".join(f"`{col}`" for col in columns)

        f.write(f"-- CREATE TABLE IF NOT EXISTS `{table_name}` (\n")
        for col in columns:
            f.write(f"--   `{col}` TEXT,\n")
        f.write("-- );\n\n")

        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]

            f.write(f"-- Batch {i // batch_size + 1}\n")
            f.write(f"INSERT INTO `{table_name}` ({column_names}) VALUES\n")

            for j, record in enumerate(batch):
                values = []
                for col in columns:
                    value = record.get(col)
                    if value is None:
                        values.append("NULL")
                    elif isinstance(value, str):
                        escaped_value = value.replace("'", "''")
                        values.append(f"'{escaped_value}'")
                    else:
                        values.append(f"'{value}'")

                value_str = f"  ({', '.join(values)})"

                if j == len(batch) - 1:  # Last item in batch
                    f.write(f"{value_str};\n\n")
                else:
                    f.write(f"{value_str},\n")


def _compress_file(input_file_path, output_zip_path):

    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        zipf.write(input_file_path, Path(input_file_path).name)


def _compress_multiple_files(input_file_paths, output_zip_path):

    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for file_path in input_file_paths:
            zipf.write(file_path, Path(file_path).name)


def get_default_export_directory():

    possible_dirs = [
        Path.home() / "Documents" / "Mockachu",
        Path.home() / "Downloads" / "Mockachu",
        Path.cwd() / "exports"
    ]

    for dir_path in possible_dirs:
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            return str(dir_path)
        except (PermissionError, OSError):
            continue

    return str(Path.cwd())


def get_recent_exports(limit=10):

    export_dir = Path(get_default_export_directory())
    if not export_dir.exists():
        return []

    files = []
    for pattern in ["*.json", "*.csv", "*.xml", "*.sql", "*.zip"]:
        files.extend(export_dir.glob(pattern))

    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    return [str(f) for f in files[:limit]]
