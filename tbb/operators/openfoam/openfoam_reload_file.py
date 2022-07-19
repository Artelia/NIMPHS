# <pep8 compliant>
from bpy.props import EnumProperty
from bpy.types import Operator, Context

import logging
log = logging.getLogger(__name__)

import time

from tbb.panels.utils import get_selected_object
from tbb.properties.utils.point_data import PointDataManager
from tbb.properties.openfoam.file_data import TBB_OpenfoamFileData


class TBB_OT_OpenfoamReloadFile(Operator):
    """Operator to reload file data of the selected OpenFOAM object."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.reload_openfoam_file"
    bl_label = "Reload"
    bl_description = "Reload file data of the selected OpenFOAM object"

    #: bpy.props.EnumProperty: Indicate which mode to use for this operator. Enum in ['NORMAL', 'TEST'].
    mode: EnumProperty(
        name="Mode",  # noqa: F821
        description="Indicate which mode to use for this operator. Enum in ['NORMAL', 'TEST']",
        items=[
            ('NORMAL', "Normal", "Run normal"),  # noqa: F821
            ('TEST', "Test", "Run for unit tests"),  # noqa: F821
        ],
        options={'HIDDEN'},  # noqa F821
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
        io_settings = obj.tbb.settings.openfoam.import_settings

        # Generate new file data
        try:
            file_data = TBB_OpenfoamFileData(obj.tbb.settings.file_path, io_settings)
        except BaseException:
            self.report({'WARNING'}, "An error occurred reading the file")
            return {'CANCELLED'}

        # Make sure the object still have an identifier
        if obj.tbb.uid == "":
            obj.tbb.uid = str(time.time())

        # Load saved information
        context.scene.tbb.file_data[obj.tbb.uid] = file_data
        if obj.tbb.settings.point_data.save != "":
            context.scene.tbb.file_data[obj.tbb.uid].vars = PointDataManager(obj.tbb.settings.point_data.save)

        # Update point data local value ranges
        if self.mode != 'TEST':
            for name in file_data.vars.names:
                file_data.update_var_range(name, data=file_data.get_point_data_from_raw(name))

        log.info("{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "Reload successful")

        return {'FINISHED'}
