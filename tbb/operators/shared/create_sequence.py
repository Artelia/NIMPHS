# <pep8 compliant>
from bpy.types import Operator, Context, Object
from bpy.props import EnumProperty, PointerProperty

import time

from tbb.panels.utils import get_selected_object
from tbb.properties.shared.point_data_settings import TBB_PointDataSettings
from tbb.properties.utils import VariablesInformation


class TBB_CreateSequence(Operator):
    """Base class of the 'CreateSequence' operators."""

    register_cls = False
    is_custom_base_cls = True

    #: bpy.props.EnumProperty: Indicates whether the operator should run modal or not. Enum in ['MODAL', 'NORMAL']
    mode: EnumProperty(
        name="Mode",  # noqa: F821
        description="Indicates whether the operator should run modal or not. Enum in ['MODAL', 'NORMAL']",
        items=[
            ('MODAL', "Modal", "TODO"),  # noqa: F821
            ('NORMAL', "Normal", "TODO"),  # noqa: F821
        ],
        options={'HIDDEN'},
    )

    #: TBB_PointDataSettings: Point data settings.
    point_data: PointerProperty(type=TBB_PointDataSettings)

    #: str: JSON strigified list of point data to import as vertex colors.
    list: str = VariablesInformation().dumps()

    #: bpy.types.Object: Selected object
    obj: Object = None

    @classmethod
    def poll(self, context: Context) -> bool:
        """
        If false, locks the UI button of the operator.

        Args:
            context (Context): context

        Returns:
            bool: state of the operator
        """

        csir = context.scene.tbb.create_sequence_is_running  # csir = create sequence is running
        obj = get_selected_object(context)
        if obj is None:
            return False

        return obj.tbb.module in ['OpenFOAM', 'TELEMAC'] and not csir

    def draw(self, context: Context) -> None:
        """
        UI layout of the operator.

        Args:
            context (Context): context
        """

        layout = self.layout
        tmp_data = context.scene.tbb.tmp_data["ops"]

        # Import point data
        box = layout.box()
        row = box.row()
        row.prop(self.point_data, "import_data", text="Import point data")

        if self.point_data.import_data:

            row = box.row()
            row.prop(self.point_data, "remap_method", text="Method")

            # Display selected point data
            data = VariablesInformation(self.list)
            for name, unit, values, type, dim in zip(data.names, data.units, data.ranges, data.types, data.dimensions):
                subbox = box.box()
                row = subbox.row()

                if values is not None:
                    if self.point_data.remap_method == 'LOCAL':
                        if values["local"]["min"] is not None and values["local"]["max"] is not None:
                            if type == 'SCALAR':
                                info = "[" + "{:.4f}".format(values["local"]["min"]) + " ; "
                                info += "{:.4f}".format(values["local"]["max"]) + "]"
                            if type == 'VECTOR':
                                info = ""
                                for i in range(dim):
                                    info += "[" + "{:.4f}".format(values["local"]["min"][i]) + " ; "
                                    info += "{:.4f}".format(values["local"]["max"][i]) + "]"
                        else:
                            info = "None"
                    elif self.point_data.remap_method == 'GLOBAL':
                        if values["global"]["min"] is not None and values["global"]["max"] is not None:
                            if type == 'SCALAR':
                                info = "[" + "{:.4f}".format(values["global"]["min"]) + " ; "
                                info += "{:.4f}".format(values["global"]["max"]) + "]"
                            if type == 'VECTOR':
                                info = ""
                                for i in range(dim):
                                    info += "[" + "{:.4f}".format(values["global"]["min"][i]) + " ; "
                                    info += "{:.4f}".format(values["global"]["max"][i]) + "]"
                        else:
                            info = "None"
                    else:
                        info = "None"
                else:
                    info = "None"

                op = row.operator("tbb.remove_point_data", text="", icon='REMOVE')
                op.var_name = name
                op.source = 'OPERATOR'
                row.label(text=(name + ", (" + unit + ")") if unit != "" else name + ",  " + info)

            row = box.row()
            op = row.operator("tbb.add_point_data", text="Add", icon='ADD')
            op.available = tmp_data.vars_info.dumps()
            op.chosen = self.list
            op.source = 'OPERATOR'

    def stop(self, context: Context, cancelled: bool = False) -> None:
        """
        Stop the 'create sequence' process.

        Common stop function for OpenFOAM and TELEMAC 'create sequence' operators.

        Args:
            context (Context): context
            cancelled (bool, optional): ask to report 'create sequence cancelled'. Defaults to False.
        """

        # Reset timer if it was running modal
        if self.timer is not None:
            wm = context.window_manager
            wm.event_timer_remove(self.timer)
            self.timer = None

        context.scene.tbb.create_sequence_is_running = False
        context.scene.tbb.progress_value = -1.0

        if cancelled:
            self.report({'INFO'}, "Create sequence cancelled")
