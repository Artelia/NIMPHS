from bpy.types import Operator

class TBB_OT_CreateSequence(Operator):
    bl_idname="tbb.create_sequence"
    bl_label="Create sequence"
    bl_description="Create a mesh sequence using the selected parameters"

    timer = None

    def execute(self, context):
        wm = context.window_manager
        self.timer = wm.event_timer_add(time_step=0.001, window=context.window)
        wm.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == "ESC":
            print("Cancel")
            return {"CANCELLED"}

        if event.type == "TIMER":
            print("Computing...")

        return {"PASS_THROUGH"}
    
    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self.timer)
        self.timer = None

