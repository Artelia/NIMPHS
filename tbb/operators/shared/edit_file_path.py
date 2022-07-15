# <pep8 compliant>
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator, Context, Event

import logging
log = logging.getLogger(__name__)

from tbb.panels.utils import get_selected_object
from tbb.properties.openfoam.file_data import TBB_OpenfoamFileData
from tbb.properties.telemac.file_data import TBB_TelemacFileData


class TBB_OT_EditFilePath(Operator, ImportHelper):
    """Operator to edit the file path of the selected object."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.edit_file_path"
    bl_label = "Edit"
    bl_description = "Edit file path of the selected object"

    #: bpy.props.StringProperty: List of allowed file extensions.
    filter_glob: StringProperty(
        default="",
        options={"HIDDEN"},  # noqa: F821
    )

    def invoke(self, context: Context, _event: Event) -> set:
        """
        Initialize the operator (update the list of allowed extensions).

        Args:
            context (Context): context
            _event (Event): event

        Returns:
            set: state of the operator
        """

        # Get the list of allowed files extensions
        obj = get_selected_object(context)
        if obj is None or obj.tbb.module not in ['TELEMAC', 'OpenFOAM']:
            log.error("Object is None or not a TELEMAC/OpenFOAM file.")
            return {'CANCELLED'}

        prefs = context.preferences.addons["tbb"].preferences
        if obj.tbb.module == 'OpenFOAM':
            self.filter_glob = prefs.settings.openfoam_extensions
        if obj.tbb.module == 'TELEMAC':
            self.filter_glob = prefs.settings.telemac_extensions

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context: Context) -> set:
        """
        Update file path property.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        obj = get_selected_object(context)
        if obj is None or obj.tbb.module not in ['TELEMAC', 'OpenFOAM']:
            log.error("Object is None or not a TELEMAC/OpenFOAM file.")
            return {'CANCELLED'}

        # Update file_path property
        obj.tbb.settings.file_path = self.filepath

        try:

            if obj.tbb.module == 'OpenFOAM':
                file_data = TBB_OpenfoamFileData(self.filepath, obj.tbb.settings.openfoam.import_settings)

            if obj.tbb.module == 'TELEMAC':
                file_data = TBB_TelemacFileData(self.filepath)

        except BaseException:
            self.report({'WARNING'}, "An error occurred reading the new file")
            return {'CANCELLED'}

        # Update file data
        file_data.copy(context.scene.tbb.file_data[obj.tbb.uid])
        context.scene.tbb.file_data[obj.tbb.uid] = file_data

        if context.area is not None:
            context.area.tag_redraw()

        self.report({'INFO'}, "Path successfully updated")
        return {'FINISHED'}
