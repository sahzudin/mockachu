#!/usr/bin/env python3
"""
Mockachu - Desktop Application Entry Point
A modern cross-platform GUI for generating mock data using PyQt6
"""

import sys
from pathlib import Path

# Add the package to path for development mode
package_root = Path(__file__).parent
if str(package_root) not in sys.path:
    sys.path.insert(0, str(package_root))


def main():
    """Main entry point for the desktop application."""
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QIcon
        from mockachu.ui.main_window import MainWindow

        app = QApplication(sys.argv)

        # Set application metadata - this helps with proper app identification
        app.setApplicationName("Mockachu")
        app.setApplicationDisplayName("Mockachu")
        app.setOrganizationName("Mockachu")
        app.setOrganizationDomain("mockdatagenerator.org")

        # Additional properties for better OS integration
        app.setDesktopFileName("Mockachu")

        # Import version from package
        try:
            from mockachu.version import __version__
            app.setApplicationVersion(__version__)
        except ImportError:
            app.setApplicationVersion("1.0.0")

        # Set up application icon
        icon_paths = [
            package_root / "ui" / "res" / "logo_app.png",
            package_root / "ui" / "res" / "logo_rounded_1024x1024.png",
            package_root / "ui" / "res" / "logo_rounded_512x512.png",
            package_root / "ui" / "res" / "logo_rounded_256x256.png",
            package_root / "ui" / "res" / "logo_rounded_128x128.png",
            package_root / "ui" / "res" / "logo_rounded_64x64.png",
            package_root / "ui" / "res" / "logo_rounded_32x32.png",
            package_root / "ui" / "res" / "logo_rounded_16x16.png"
        ]

        app_icon = QIcon()
        for icon_path in icon_paths:
            if icon_path.exists():
                app_icon.addFile(str(icon_path))

        if not app_icon.isNull():
            app.setWindowIcon(app_icon)
            QApplication.setWindowIcon(app_icon)
            print(
                f"✅ Application icon set with {len([p for p in icon_paths if p.exists()])} sizes")
        else:
            print("❌ Could not load application icon")

        # macOS specific settings
        if sys.platform == "darwin":
            app.setAttribute(
                Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)

        window = MainWindow()
        window.show()

        sys.exit(app.exec())

    except ImportError as e:
        print(f"Import Error: {e}")
        print("\nMake sure you have PyQt6 installed:")
        print("pip install 'mockachu[gui]'")
        print("or")
        print("pip install PyQt6 qdarkstyle")
        sys.exit(1)

    except Exception as e:
        print(f"Application Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
