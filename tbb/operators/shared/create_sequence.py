# <pep8 compliant>
from bpy.types import Operator, Context, RenderSettings
from bpy.props import EnumProperty, PointerProperty

import time

from tbb.operators.utils import setup_streaming_sequence_object
from tbb.operators.telemac.utils import generate_telemac_streaming_sequence_obj
from tbb.panels.utils import get_selected_object
from tbb.properties.shared.module_scene_settings import TBB_ModuleSceneSettings
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

    #: bpy.props.EnumProperty: Type of the sequence to create. Enum in ['MESH', 'STREAMING']
    type: EnumProperty(
        name="Type",  # noqa: F821
        description="Type of the sequence to create. Enum in ['MESH', 'STREAMING']",
        items=[
            ('MESH', "Mesh", "TODO"),  # noqa: F821
            ('STREAMING', "Streaming", "TODO"),  # noqa: F821
        ],
        options={'HIDDEN'},
    )

    #: TBB_PointDataSettings: Point data settings.
    point_data: PointerProperty(type=TBB_PointDataSettings)

    #: str: JSON strigified list of point data to import as vertex colors.
    list: str = VariablesInformation().dumps()

    #: str: Unique identifier.
    uid: str = str(time.time())

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

    def execute(self, settings: TBB_ModuleSceneSettings, context: Context, module: str) -> set:
        """
        Create a sequence.

        Args:
            settings (TBB_ModuleSceneSettings): scene settings
            context (Context): context
            module (str): name of the module, enum in ['OpenFOAM', 'TELEMAC']

        Returns:
            set: state of the operator
        """

        wm = context.window_manager

        if settings.sequence_type == "mesh_sequence":
            # Create timer event
            self.timer = wm.event_timer_add(time_step=1e-6, window=context.window)
            wm.modal_handler_add(self)

            # Setup prograss bar
            context.scene.tbb.progress_label = "Create sequence"
            context.scene.tbb.progress_value = -1.0

            # Setup for creating the sequence
            self.start_time_point = settings.get("start_time_point", 0)
            self.current_time_point = settings.get("start_time_point", 0)
            self.end_time_point = settings.get("end_time_point", 1)
            self.current_frame = context.scene.frame_current
            self.user_sequence_name = settings.sequence_name

            context.scene.tbb.create_sequence_is_running = True

            if self.mode == 'MODAL':
                return {'RUNNING_MODAL'}
            elif self.mode == 'NORMAL':
                return {'NORMAL'}  # custom value to run the process without modal mode (used in tests)
            else:
                print("WARNING::TBB_CreateSequence: undefined operator mode '" + str(self.mode) + "', running\
                       modal by default.")
                return {'RUNNING_MODAL'}

        elif settings.sequence_type == "streaming_sequence":
            from tbb.operators.openfoam.utils import generate_openfoam_streaming_sequence_obj
            # Warn the user when the selected start frame may be "weird"
            if settings.frame_start < context.scene.frame_start or settings.frame_start > context.scene.frame_end:
                self.report({"WARNING"}, "Frame start is not in the selected time frame.")

            if module == 'OpenFOAM':
                obj = generate_openfoam_streaming_sequence_obj(context, settings.sequence_name)
                sequence = obj.tbb.settings.openfoam.s_sequence
            if module == 'TELEMAC':
                obj = generate_telemac_streaming_sequence_obj(context, settings.sequence_name)
                sequence = obj.tbb.settings.telemac.s_sequence

            setup_streaming_sequence_object(obj, sequence, settings.tmp_data.nb_time_points, settings, module)

            context.scene.collection.objects.link(obj)

            # As mentioned here, lock the interface because the custom handler will alter data on frame change
            # https://docs.blender.org/api/current/bpy.app.handlers.html?highlight=app%20handlers#module-bpy.app.handlers
            RenderSettings.use_lock_interface = True

            self.report({'INFO'}, "Sequence successfully created")

            return {'FINISHED'}

        else:
            self.report({'ERROR'}, "Unknown sequence type (type = " + str(settings.sequence_type) + ")")
            return {'FINISHED'}

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
