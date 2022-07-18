# <pep8 compliant>
import bpy
from bpy.types import Operator, Context
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, PointerProperty

import logging
log = logging.getLogger(__name__)

import time

from tbb.operators.utils.object import TelemacObjectUtils
from tbb.properties.telemac.file_data import TBB_TelemacFileData
from tbb.properties.telemac.import_settings import TBB_TelemacImportSettings


def import_telemac_menu_draw(self, context: Context) -> None:  # noqa D417
    """
    Draw function which displays the import button in File > Import.

    Args:
        context (Context): context
    """

    prefs = context.preferences.addons["tbb"].preferences.settings
    extensions = prefs.telemac_extensions.replace("*", "")
    self.layout.operator(TBB_OT_TelemacImportFile.bl_idname, text=f"TELEMAC ({extensions})")


class TBB_OT_TelemacImportFile(Operator, ImportHelper):
    """Operator to import a TELEMAC file."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.import_telemac_file"
    bl_label = "Import"
    bl_description = "Import a TELEMAC file"

    #: bpy.props.StringProperty: List of allowed file extensions.
    filter_glob: StringProperty(
        default="*.slf",  # multiple allowed types: "*.slf;*.[];*.[]" etc ...
        options={"HIDDEN"}  # noqa: F821
    )

    #: bpy.props.StringProperty: Name to give to the imported object.
    name: StringProperty(
        name="Name",  # noqa F821
        description="Name to give to the imported object",
        default="TBB_TELEMAC_preview",  # noqa F821
    )

    #: TBB_TelemacImportSettings: Import settings.
    import_settings: PointerProperty(type=TBB_TelemacImportSettings)

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
            file_data = TBB_TelemacFileData(self.filepath)
        except BaseException:
            self.report({'WARNING'}, "An error occurred reading the file")
            return {'CANCELLED'}

        # Generate parent object
        obj = bpy.data.objects.new(self.name, object_data=None)
        context.scene.collection.objects.link(obj)
        # Setup common settings
        obj.tbb.module = 'TELEMAC'
        obj.tbb.uid = str(time.time())
        obj.tbb.settings.file_path = self.filepath
        context.scene.tbb.file_data[obj.tbb.uid] = file_data

        # Generate objects
        children = TelemacObjectUtils.base(file_data, self.name)
        # Link generated objects to main 'Null' object
        for child in children:
            context.scene.collection.objects.link(child)
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
