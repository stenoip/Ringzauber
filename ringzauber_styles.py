"""
COPYRIGHT (C) 2026 STENOIP COMPANY. ALL RIGHTS RESERVED.
This source code is the intellectual property of Stenoip Company.
Unauthorized copying, modification, or distribution of this file 
is strictly prohibited.
"""

from PyQt6.QtWidgets import QApplication

def setup_app_styles(app: QApplication):
    """
    Sets the application-wide stylesheet for Ringzauber Browser 
    with a Frutiger Aero aesthetic.
    """
    
    # OMITTED: Specific Gradient stops and HEX value logic for the 
    # proprietary 'Ringzauber Glass' look.
    # REASON: Protects the unique visual brand of Stenoip Company.
    
    app.setStyleSheet("""
        /* --- GLOBAL FONT FIX --- */
        QWidget {
            font-family: 'Roboto';
        }
        
        /* --- GLOBAL/WINDOW ELEMENTS --- */
        QMainWindow, QDialog {
            border: 1px solid #b3e5fc;
        }
        
        /* --- TOOLBAR (Shiny/Glossy look) --- */
        QToolBar {
            /* Proprietary gloss gradient removed */
            border-bottom: 2px solid #039be5;
            padding: 5px;
            border-radius: 12px;
            margin: 5px;
        }
        
        /* --- URL BAR/LINE EDIT --- */
        QLineEdit {
            /* Glassy pill-shape logic */
            border: 1px solid #03a9f4;
            border-radius: 18px;
            padding: 6px 18px;
            font-weight: bold;
        }

        /* --- TABS (Glassy) --- */
        QTabWidget::pane {
            border: 1px solid #81d4fa;
            border-radius: 10px;
            background-color: transparent; 
        }

        QTabBar::tab {
            /* Floating tab gradient removed */
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            min-width: 120px;
            padding: 8px 15px;
        }

        /* --- BUTTONS (Vibrant Glossy Orbs) --- */
        QPushButton {
            /* Signature Cyan-Teal Orb gradient removed */
            border-radius: 15px;
            font-weight: bold;
        }
        
        /* --- STATUS BAR --- */
        QStatusBar {
            background-color: #b3e5fc;
            border-top: 1px solid #81d4fa;
        }
    """)
