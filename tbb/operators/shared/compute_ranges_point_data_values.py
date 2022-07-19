# <pep8 compliant>
from bpy.props import PointerProperty
from bpy.types import Operator, Context, Event, Object

import logging
log = logging.getLogger(__name__)

import numpy as np

from tbb.properties.utils.point_data import PointDataManager
from tbb.panels.utils import draw_point_data, get_selected_object
from tbb.operators.shared.modal_operator import TBB_ModalOperator
from tbb.properties.shared.point_data_settings import TBB_PointDataSettings


class TBB_OT_ComputeRangesPointDataValues(Operator, TBB_ModalOperator):
    """Operator to compute ranges of point data values."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.compute_ranges_point_data_values"
    bl_label = "Compute ranges of point data values"
    bl_description = "Compute ranges of point data values"

    #: TBB_PointDataSettings: Point data settings.
    point_data: PointerProperty(type=TBB_PointDataSettings)
    #: int: Identifier of the last time point
    end: int = 0
    #: int: Current time point
    time_point: int = 0
    #: list: List of minima for each selected variable
    minima: list = []
    #: list: List of maxima for each selected variable
    maxima: list = []
    #: Object: Selected object
    obj: Object = None

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, locks the button of the operator.

        Args:
            context (Context): context

        Returns:
            bool: state of the operator
        """

        obj = get_selected_object(context)
        if obj is None:
            return False

        if context.scene.tbb.m_op_running:
            return False

        if obj.tbb.module not in ['OpenFOAM', 'TELEMAC']:
            return False

        return True

    def invoke(self, context: Context, _event: Event) -> set:
        """
        Prepare operator settings. Function triggered before the user can edit settings.

        Args:
            context (Context): context
            _event (Event): event

        Returns:
            set: state of the operator
        """

        self.obj = get_selected_object(context)
        if self.obj is None:
            return {'CANCELLED'}

        if context.scene.tbb.file_data.get(self.obj.tbb.uid, None) is None:
            self.report({'ERROR'}, "Reload file data first")
            return {'CANCELLED'}

        # "Copy" file data information
        context.scene.tbb.file_data["ops"] = context.scene.tbb.file_data[self.obj.tbb.uid]

        # Used for unit tests
        if self.mode == 'TEST':
            self.time_point = 0
            self.end = context.scene.tbb.file_data["ops"].nb_time_points - 1
            return {'FINISHED'}

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: Context) -> None:
        """
        Layout of the popup window.

        Args:
            context (Context): context
        """

        file_data = context.scene.tbb.file_data["ops"]

        # Import point data
        box = self.layout.box()
        row = box.row()
        row.label(text="Variables")

        # Update list of chosen point data from this operator. Ugly but it works.
        self.point_data.list = context.scene.tbb.op_vars.dumps()

        draw_point_data(box, self.point_data, show_remap=False, show_range=False, edit=True, src='OPERATOR')

        row = box.row()
        op = row.operator("tbb.add_point_data", text="Add", icon='ADD')
        op.available = file_data.vars.dumps()
        op.chosen = self.point_data.list
        op.source = 'OPERATOR'

    def execute(self, context: Context) -> set:
        """
        Compute ranges of point data values ('GLOBAL' scope).

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        # Clear data
        self.minima.clear()
        self.maxima.clear()

        # Add chosen point data in minima and maxima dictionaries
        if self.mode == 'TEST':
            self.point_data.list = self.test_data
        else:
            self.point_data.list = context.scene.tbb.op_vars.dumps()

        vars = PointDataManager(self.point_data.list)

        # If no data selected, do nothing
        if vars.length() <= 0:
            return {'CANCELLED'}

        # Setup minima and maxima lists
        for id in range(vars.length()):
            self.minima.append([])
            self.maxima.append([])

        if self.mode == 'MODAL':
            self.time_point = 0
            self.end = context.scene.tbb.file_data["ops"].nb_time_points - 1
            super().prepare(context, "Computing...")
            return {'RUNNING_MODAL'}

        # -------------------------------- #
        # /!\ For testing purpose only /!\ #
        # -------------------------------- #
        if self.mode == 'TEST':
            state = self.invoke(context, None)
            if state != {'FINISHED'}:
                return state

            for i in range(self.end + 2):
                state = self.modal(context, None)
                if state != {'PASS_THROUGH'}:
                    return state

        return {'CANCELLED'}

    def modal(self, context: Context, event: Event) -> set:
        """
        Run one step of the 'compute ranges point data values' process.

        Args:
            context (Context): context
            event (Event): event

        Returns:
            set: state of the operator
        """

        if event is not None and event.type == 'ESC':
            super().stop(context, canceled=True)
            return {'CANCELLED'}

        if self.mode == 'TEST' or (event is not None and event.type == 'TIMER'):

            vars = PointDataManager(self.point_data.list)

            if self.time_point <= self.end:

                file_data = context.scene.tbb.file_data["ops"]
                file_data.update_data(self.time_point)

                # Compute local minima and maxima
                for name, id in zip(vars.names, range(vars.length())):

                    data = file_data.get_point_data(name)
                    self.minima[id].append(float(np.min(data)))
                    self.maxima[id].append(float(np.max(data)))

            else:
                file_data = context.scene.tbb.file_data.get(self.obj.tbb.uid, None)

                if file_data is None:
                    self.report({'ERROR'}, "File data not found. Can't update.")
                    super().stop(context)
                    return {'CANCELLED'}

                # Compute global minima and maxima from list of local values
                for name, id in zip(vars.names, range(vars.length())):

                    mini = float(np.min(self.minima[id]))
                    maxi = float(np.max(self.maxima[id]))

                    # Update point data information
                    file_data.update_var_range(name, scope='GLOBAL', data={"min": mini, "max": maxi})

                self.report({'INFO'}, "Compute ranges finished")
                super().stop(context)
                return {'FINISHED'}

            self.update_progress(context, self.time_point, self.end)
            self.time_point += 1

        return {'PASS_THROUGH'}
