# <pep8 compliant>
import bpy
from bpy.types import Operator, Context
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, PointerProperty

import logging
log = logging.getLogger(__name__)

import time

from nimphs.operators.utils.object import TelemacObjectUtils
from nimphs.properties.telemac.file_data import TelemacFileData
from nimphs.properties.telemac.import_settings import NIMPHS_TelemacImportSettings


def import_telemac_menu_draw(self, context: Context) -> None:  # noqa: D417
    """
    Draw function which displays the import button in File > Import.

    Args:
        context (Context): context
    """

    prefs = context.preferences.addons["nimphs"].preferences.settings
    extensions = prefs.telemac_extensions.replace("*", "")
    self.layout.operator(NIMPHS_OT_TelemacImportFile.bl_idname, text=f"TELEMAC ({extensions})")


class NIMPHS_OT_TelemacImportFile(Operator, ImportHelper):
    """Operator to import a TELEMAC file."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "nimphs.import_telemac_file"
    bl_label = "Import"
    bl_description = "Import a TELEMAC file"

    #: bpy.props.StringProperty: List of allowed file extensions.
    filter_glob: StringProperty(
        default="*.slf",  # multiple allowed types: "*.slf;*.[];*.[]" etc ...
        options={"HIDDEN"}  # noqa: F821
    )

    #: bpy.props.StringProperty: Name to give to the imported object.
    name: StringProperty(
        name="Name",                # noqa: F821
        description="Name to give to the imported object",
        default="TELEMAC_preview",  # noqa: F821
    )

    #: NIMPHS_TelemacImportSettings: Import settings.
    import_settings: PointerProperty(type=NIMPHS_TelemacImportSettings)

    def execute(self, context: Context) -> set:
        """
        Import the selected file.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        start = time.time()

        try:
            file_data = TelemacFileData(self.filepath)
        except BaseException:
            self.report({'WARNING'}, "An error occurred reading the file")
            return {'CANCELLED'}

        # Generate parent object
        obj = bpy.data.objects.new(self.name, object_data=None)
        context.collection.objects.link(obj)
        # Setup common settings
        obj.nimphs.module = 'TELEMAC'
        obj.nimphs.uid = str(time.time())
        obj.nimphs.settings.file_path = self.filepath
        context.scene.nimphs.file_data[obj.nimphs.uid] = file_data

        # Generate objects
        children = TelemacObjectUtils.base(file_data, self.name)
        # Link generated objects to main 'Null' object
        for child in children:
            context.collection.objects.link(child)
            child.parent = obj

        log.info("{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "File successfully imported")

        return {'FINISHED'}

    def draw(self, _context: Context) -> None:
        """
        UI layout of the operator.

        Args:
            _context (Context): context
        """

        # Others
        box = self.layout.box()
        row = box.row()
        row.label(text="Others")

        row = box.row()
        row.prop(self, "name", text="Name")
