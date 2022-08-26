# <pep8 compliant>
from bpy.props import EnumProperty
from bpy.types import Operator, Context

import logging
log = logging.getLogger(__name__)

import time

from nimphs.panels.utils import get_selected_object
from nimphs.properties.utils.point_data import PointDataManager
from nimphs.properties.openfoam.file_data import OpenfoamFileData


class NIMPHS_OT_OpenfoamReloadFile(Operator):
    """Operator to reload file data of the selected OpenFOAM object."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "nimphs.reload_openfoam_file"
    bl_label = "Reload"
    bl_description = "Reload file data of the selected OpenFOAM object"

    #: bpy.props.EnumProperty: Indicate which mode to use for this operator. Enum in ['NORMAL', 'TEST'].
    mode: EnumProperty(
        name="Mode",                                    # noqa: F821
        description="Indicate which mode to use for this operator. Enum in ['NORMAL', 'TEST']",
        items=[
            ('NORMAL', "Normal", "Run normal"),         # noqa: F821
            ('TEST', "Test", "Run for unit tests"),     # noqa: F821
        ],
        options={'HIDDEN'},                             # noqa: F821
    )

    def execute(self, context: Context) -> set:
        """
        Reload file data of the selected OpenFOAM object.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        start = time.time()

        obj = get_selected_object(context)
        io_settings = obj.nimphs.settings.openfoam.import_settings

        # Generate new file data
        try:
            file_data = OpenfoamFileData(obj.nimphs.settings.file_path, io_settings)
        except BaseException:
            self.report({'WARNING'}, "An error occurred reading the file")
            return {'CANCELLED'}

        # Make sure the object still have an identifier
        if obj.nimphs.uid == "":
            obj.nimphs.uid = str(time.time())

        # Load saved information
        context.scene.nimphs.file_data[obj.nimphs.uid] = file_data
        if obj.nimphs.settings.point_data.save != "":
            context.scene.nimphs.file_data[obj.nimphs.uid].vars = PointDataManager(obj.nimphs.settings.point_data.save)

        # Update point data local value ranges
        if self.mode != 'TEST':
            for name in file_data.vars.names:
                file_data.update_var_range(name, data=file_data.get_point_data_from_raw(name))

        log.info("{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "Reload successful")

        return {'FINISHED'}
