# -*- coding: utf-8 -*-
"""
Qt5 / Qt6 compatibility shim for the espace-collaboratif QGIS plugin.

QGIS 3.x bundles PyQt5 (Qt 5); QGIS 4.x bundles PyQt6 (Qt 6).
Both are exposed through the ``qgis.PyQt`` namespace, so the import
statement is the same — but the *enum access style* changed:

  Qt5 / PyQt5   →  flat enums   : Qt.Checked, QMessageBox.Yes, …
  Qt6 / PyQt6   →  scoped enums : Qt.CheckState.Checked, QMessageBox.StandardButton.Yes, …

This module provides:

1. **Named aliases** (guaranteed correct on *both* Qt versions) that any
   plugin file can import explicitly::

       from .qt_compat import ButtonBoxSave, MsgYes, CheckedState

2. **Monkey-patches** applied as a side-effect on import.  Importing this
   module once (e.g. in ``__init__.py``) patches all Qt classes so that
   *either* enum style works in the rest of the code::

       from . import qt_compat  # noqa: F401  # side-effect only

Usage in plugin modules::

    from .qt_compat import ButtonBoxSave, ButtonBoxCancel, MsgYes, MsgNo
    # or, for core/ sub-package:
    from ..qt_compat import ButtonBoxSave, …
"""

from qgis.PyQt.QtCore import (
    Qt,
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
)
from qgis.PyQt.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from qgis.PyQt.QtWidgets import (
    QAbstractButton,
    QAbstractItemView,
    QAbstractScrollArea,
    QApplication,
    QCalendarWidget,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGroupBox,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QTextEdit,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

# ---------------------------------------------------------------------------
# Aliases — try Qt6 scoped enums, fall back to Qt5 flat enums.
# ---------------------------------------------------------------------------
try:
    # ── Qt namespace ─────────────────────────────────────────────────────
    WindowStaysOnTopHint    = Qt.WindowType.WindowStaysOnTopHint
    ApplicationModal        = Qt.WindowModality.ApplicationModal
    Horizontal              = Qt.Orientation.Horizontal
    Vertical                = Qt.Orientation.Vertical

    AlignLeft               = Qt.AlignmentFlag.AlignLeft
    AlignRight              = Qt.AlignmentFlag.AlignRight
    AlignHCenter            = Qt.AlignmentFlag.AlignHCenter
    AlignTop                = Qt.AlignmentFlag.AlignTop
    AlignBottom             = Qt.AlignmentFlag.AlignBottom
    AlignVCenter            = Qt.AlignmentFlag.AlignVCenter
    AlignLeading            = Qt.AlignmentFlag.AlignLeading

    CheckedState            = Qt.CheckState.Checked
    UncheckedState          = Qt.CheckState.Unchecked

    ItemIsEnabled           = Qt.ItemFlag.ItemIsEnabled
    ItemIsUserCheckable     = Qt.ItemFlag.ItemIsUserCheckable
    ItemIsSelectable        = Qt.ItemFlag.ItemIsSelectable
    ItemIsEditable          = Qt.ItemFlag.ItemIsEditable

    MatchCaseSensitive      = Qt.MatchFlag.MatchCaseSensitive
    MatchExactly            = Qt.MatchFlag.MatchExactly
    MatchContains           = Qt.MatchFlag.MatchContains

    ToolButtonTextOnly      = Qt.ToolButtonStyle.ToolButtonTextOnly
    ToolButtonIconOnly      = Qt.ToolButtonStyle.ToolButtonIconOnly
    ToolButtonTextBesideIcon = Qt.ToolButtonStyle.ToolButtonTextBesideIcon

    ScrollBarAlwaysOff      = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    ScrollBarAlwaysOn       = Qt.ScrollBarPolicy.ScrollBarAlwaysOn
    ScrollBarAsNeeded       = Qt.ScrollBarPolicy.ScrollBarAsNeeded

    PenStyleNoPen           = Qt.PenStyle.NoPen
    PenStyleSolid           = Qt.PenStyle.SolidLine

    BusyCursor              = Qt.CursorShape.BusyCursor
    ArrowCursor             = Qt.CursorShape.ArrowCursor
    WaitCursor              = Qt.CursorShape.WaitCursor

    SortAscending           = Qt.SortOrder.AscendingOrder
    SortDescending          = Qt.SortOrder.DescendingOrder

    UserRole                = Qt.ItemDataRole.UserRole
    DisplayRole             = Qt.ItemDataRole.DisplayRole
    DecorationRole          = Qt.ItemDataRole.DecorationRole
    CheckStateRole          = Qt.ItemDataRole.CheckStateRole

    # ── QMessageBox ───────────────────────────────────────────────────────
    MsgYes                  = QMessageBox.StandardButton.Yes
    MsgNo                   = QMessageBox.StandardButton.No
    MsgOk                   = QMessageBox.StandardButton.Ok
    MsgCancel               = QMessageBox.StandardButton.Cancel
    MsgWarning              = QMessageBox.Icon.Warning
    MsgCritical             = QMessageBox.Icon.Critical
    MsgInformation          = QMessageBox.Icon.Information
    MsgQuestion             = QMessageBox.Icon.Question

    # ── QDialogButtonBox ─────────────────────────────────────────────────
    ButtonBoxOk             = QDialogButtonBox.StandardButton.Ok
    ButtonBoxSave           = QDialogButtonBox.StandardButton.Save
    ButtonBoxCancel         = QDialogButtonBox.StandardButton.Cancel
    ButtonBoxClose          = QDialogButtonBox.StandardButton.Close
    ButtonBoxApply          = QDialogButtonBox.StandardButton.Apply

    # ── QToolButton ───────────────────────────────────────────────────────
    ToolButtonInstantPopup  = QToolButton.ToolButtonPopupMode.InstantPopup

    # ── QSizePolicy ───────────────────────────────────────────────────────
    SizePolicyExpanding     = QSizePolicy.Policy.Expanding
    SizePolicyPreferred     = QSizePolicy.Policy.Preferred
    SizePolicyFixed         = QSizePolicy.Policy.Fixed
    SizePolicyMinimum       = QSizePolicy.Policy.Minimum
    SizePolicyMaximum       = QSizePolicy.Policy.Maximum

    # ── QAbstractItemView ─────────────────────────────────────────────────
    ScrollPerItem           = QAbstractItemView.ScrollMode.ScrollPerItem
    ScrollPerPixel          = QAbstractItemView.ScrollMode.ScrollPerPixel
    MultiSelection          = QAbstractItemView.SelectionMode.MultiSelection
    SingleSelection         = QAbstractItemView.SelectionMode.SingleSelection
    ExtendedSelection       = QAbstractItemView.SelectionMode.ExtendedSelection
    NoSelection             = QAbstractItemView.SelectionMode.NoSelection

except AttributeError:
    # ── Qt5 flat enums ────────────────────────────────────────────────────
    WindowStaysOnTopHint    = Qt.WindowStaysOnTopHint          # type: ignore[attr-defined]
    ApplicationModal        = Qt.ApplicationModal              # type: ignore[attr-defined]
    Horizontal              = Qt.Horizontal                    # type: ignore[attr-defined]
    Vertical                = Qt.Vertical                      # type: ignore[attr-defined]

    AlignLeft               = Qt.AlignLeft                     # type: ignore[attr-defined]
    AlignRight              = Qt.AlignRight                    # type: ignore[attr-defined]
    AlignHCenter            = Qt.AlignHCenter                  # type: ignore[attr-defined]
    AlignTop                = Qt.AlignTop                      # type: ignore[attr-defined]
    AlignBottom             = Qt.AlignBottom                   # type: ignore[attr-defined]
    AlignVCenter            = Qt.AlignVCenter                  # type: ignore[attr-defined]
    AlignLeading            = Qt.AlignLeading                  # type: ignore[attr-defined]

    CheckedState            = Qt.Checked                       # type: ignore[attr-defined]
    UncheckedState          = Qt.Unchecked                     # type: ignore[attr-defined]

    ItemIsEnabled           = Qt.ItemIsEnabled                 # type: ignore[attr-defined]
    ItemIsUserCheckable     = Qt.ItemIsUserCheckable           # type: ignore[attr-defined]
    ItemIsSelectable        = Qt.ItemIsSelectable              # type: ignore[attr-defined]
    ItemIsEditable          = Qt.ItemIsEditable                # type: ignore[attr-defined]

    MatchCaseSensitive      = Qt.MatchCaseSensitive            # type: ignore[attr-defined]
    MatchExactly            = Qt.MatchExactly                  # type: ignore[attr-defined]
    MatchContains           = Qt.MatchContains                 # type: ignore[attr-defined]

    ToolButtonTextOnly      = Qt.ToolButtonTextOnly            # type: ignore[attr-defined]
    ToolButtonIconOnly      = Qt.ToolButtonIconOnly            # type: ignore[attr-defined]
    ToolButtonTextBesideIcon = Qt.ToolButtonTextBesideIcon     # type: ignore[attr-defined]

    ScrollBarAlwaysOff      = Qt.ScrollBarAlwaysOff            # type: ignore[attr-defined]
    ScrollBarAlwaysOn       = Qt.ScrollBarAlwaysOn             # type: ignore[attr-defined]
    ScrollBarAsNeeded       = Qt.ScrollBarAsNeeded             # type: ignore[attr-defined]

    PenStyleNoPen           = Qt.NoPen                         # type: ignore[attr-defined]
    PenStyleSolid           = Qt.SolidLine                     # type: ignore[attr-defined]

    BusyCursor              = Qt.BusyCursor                    # type: ignore[attr-defined]
    ArrowCursor             = Qt.ArrowCursor                   # type: ignore[attr-defined]
    WaitCursor              = Qt.WaitCursor                    # type: ignore[attr-defined]

    SortAscending           = Qt.AscendingOrder                # type: ignore[attr-defined]
    SortDescending          = Qt.DescendingOrder               # type: ignore[attr-defined]

    UserRole                = Qt.UserRole                      # type: ignore[attr-defined]
    DisplayRole             = Qt.DisplayRole                   # type: ignore[attr-defined]
    DecorationRole          = Qt.DecorationRole                # type: ignore[attr-defined]
    CheckStateRole          = Qt.CheckStateRole                # type: ignore[attr-defined]

    MsgYes                  = QMessageBox.Yes                  # type: ignore[attr-defined]
    MsgNo                   = QMessageBox.No                   # type: ignore[attr-defined]
    MsgOk                   = QMessageBox.Ok                   # type: ignore[attr-defined]
    MsgCancel               = QMessageBox.Cancel               # type: ignore[attr-defined]
    MsgWarning              = QMessageBox.Warning              # type: ignore[attr-defined]
    MsgCritical             = QMessageBox.Critical             # type: ignore[attr-defined]
    MsgInformation          = QMessageBox.Information          # type: ignore[attr-defined]
    MsgQuestion             = QMessageBox.Question             # type: ignore[attr-defined]

    ButtonBoxOk             = QDialogButtonBox.Ok              # type: ignore[attr-defined]
    ButtonBoxSave           = QDialogButtonBox.Save            # type: ignore[attr-defined]
    ButtonBoxCancel         = QDialogButtonBox.Cancel          # type: ignore[attr-defined]
    ButtonBoxClose          = QDialogButtonBox.Close           # type: ignore[attr-defined]
    ButtonBoxApply          = QDialogButtonBox.Apply           # type: ignore[attr-defined]

    ToolButtonInstantPopup  = QToolButton.InstantPopup         # type: ignore[attr-defined]

    SizePolicyExpanding     = QSizePolicy.Expanding            # type: ignore[attr-defined]
    SizePolicyPreferred     = QSizePolicy.Preferred            # type: ignore[attr-defined]
    SizePolicyFixed         = QSizePolicy.Fixed                # type: ignore[attr-defined]
    SizePolicyMinimum       = QSizePolicy.Minimum              # type: ignore[attr-defined]
    SizePolicyMaximum       = QSizePolicy.Maximum              # type: ignore[attr-defined]

    ScrollPerItem           = QAbstractItemView.ScrollPerItem  # type: ignore[attr-defined]
    ScrollPerPixel          = QAbstractItemView.ScrollPerPixel # type: ignore[attr-defined]
    MultiSelection          = QAbstractItemView.MultiSelection # type: ignore[attr-defined]
    SingleSelection         = QAbstractItemView.SingleSelection # type: ignore[attr-defined]
    ExtendedSelection       = QAbstractItemView.ExtendedSelection # type: ignore[attr-defined]
    NoSelection             = QAbstractItemView.NoSelection    # type: ignore[attr-defined]

# ---------------------------------------------------------------------------
# Monkey-patches (side-effects) — patch flat Qt5 names onto Qt6 classes so
# any code still using old-style names works without changes.
# Each block is independent; a failure in one does not affect the others.
# ---------------------------------------------------------------------------
def _patch(cls, name, val):
    """Set ``cls.name = val`` only if the attribute is not already present."""
    if not hasattr(cls, name):
        try:
            setattr(cls, name, val)
        except (AttributeError, TypeError):
            pass


# Qt namespace — flat aliases
for _n, _v in (
    ('WindowStaysOnTopHint',    WindowStaysOnTopHint),
    ('ApplicationModal',        ApplicationModal),
    ('Horizontal',              Horizontal),
    ('Vertical',                Vertical),
    ('AlignLeft',               AlignLeft),
    ('AlignRight',              AlignRight),
    ('AlignHCenter',            AlignHCenter),
    ('AlignTop',                AlignTop),
    ('AlignBottom',             AlignBottom),
    ('AlignVCenter',            AlignVCenter),
    ('AlignLeading',            AlignLeading),
    ('Checked',                 CheckedState),
    ('Unchecked',               UncheckedState),
    ('ItemIsEnabled',           ItemIsEnabled),
    ('ItemIsUserCheckable',     ItemIsUserCheckable),
    ('ItemIsSelectable',        ItemIsSelectable),
    ('ItemIsEditable',          ItemIsEditable),
    ('MatchCaseSensitive',      MatchCaseSensitive),
    ('MatchExactly',            MatchExactly),
    ('MatchContains',           MatchContains),
    ('ToolButtonTextOnly',      ToolButtonTextOnly),
    ('ToolButtonIconOnly',      ToolButtonIconOnly),
    ('ScrollBarAlwaysOff',      ScrollBarAlwaysOff),
    ('ScrollBarAlwaysOn',       ScrollBarAlwaysOn),
    ('ScrollBarAsNeeded',       ScrollBarAsNeeded),
    ('NoPen',                   PenStyleNoPen),
    ('SolidLine',               PenStyleSolid),
    ('BusyCursor',              BusyCursor),
    ('ArrowCursor',             ArrowCursor),
    ('WaitCursor',              WaitCursor),
    ('AscendingOrder',          SortAscending),
    ('DescendingOrder',         SortDescending),
    ('UserRole',                UserRole),
    ('DisplayRole',             DisplayRole),
    ('DecorationRole',          DecorationRole),
    ('CheckStateRole',          CheckStateRole),
):
    _patch(Qt, _n, _v)

# QMessageBox
for _n, _v in (
    ('Yes',         MsgYes),
    ('No',          MsgNo),
    ('Ok',          MsgOk),
    ('Cancel',      MsgCancel),
    ('Warning',     MsgWarning),
    ('Critical',    MsgCritical),
    ('Information', MsgInformation),
    ('Question',    MsgQuestion),
):
    _patch(QMessageBox, _n, _v)

# QDialogButtonBox
for _n, _v in (
    ('Ok',      ButtonBoxOk),
    ('Save',    ButtonBoxSave),
    ('Cancel',  ButtonBoxCancel),
    ('Close',   ButtonBoxClose),
    ('Apply',   ButtonBoxApply),
):
    _patch(QDialogButtonBox, _n, _v)

# QToolButton
_patch(QToolButton, 'InstantPopup', ToolButtonInstantPopup)

# QSizePolicy
try:
    for _n, _v in (
        ('Expanding', SizePolicyExpanding),
        ('Preferred', SizePolicyPreferred),
        ('Fixed',     SizePolicyFixed),
        ('Minimum',   SizePolicyMinimum),
        ('Maximum',   SizePolicyMaximum),
    ):
        _patch(QSizePolicy, _n, _v)
except AttributeError:
    pass

# QAbstractItemView
try:
    for _n, _v in (
        ('ScrollPerItem',       ScrollPerItem),
        ('ScrollPerPixel',      ScrollPerPixel),
        ('MultiSelection',      MultiSelection),
        ('SingleSelection',     SingleSelection),
        ('ExtendedSelection',   ExtendedSelection),
        ('NoSelection',         NoSelection),
    ):
        _patch(QAbstractItemView, _n, _v)
except AttributeError:
    pass

# QFrame
try:
    _patch(QFrame, 'NoFrame', QFrame.Shape.NoFrame)
    _patch(QFrame, 'Box',     QFrame.Shape.Box)
    _patch(QFrame, 'Panel',   QFrame.Shape.Panel)
except AttributeError:
    pass

# QPalette
try:
    for _n, _v in (
        ('Active',      QPalette.ColorGroup.Active),
        ('Inactive',    QPalette.ColorGroup.Inactive),
        ('Disabled',    QPalette.ColorGroup.Disabled),
        ('Base',        QPalette.ColorRole.Base),
        ('Window',      QPalette.ColorRole.Window),
        ('WindowText',  QPalette.ColorRole.WindowText),
        ('Text',        QPalette.ColorRole.Text),
        ('Button',      QPalette.ColorRole.Button),
        ('ButtonText',  QPalette.ColorRole.ButtonText),
    ):
        _patch(QPalette, _n, _v)
except AttributeError:
    pass

del _patch, _n, _v
