from bpy.types import Operator

class TBB_OT_CreateSequence(Operator):
    bl_idname="tbb.create_sequence"
    bl_label="Create sequence"
    bl_description="Create a mesh sequence using the selected parameters"

    timer = None
    progress = 0.0

    @classmethod
    def poll(cls, context):
        return not context.scene.tbb_settings.create_sequence_is_running

    def execute(self, context):
        wm = context.window_manager
        context.scene.tbb_settings.create_sequence_is_running = True
        # Create timer event
        self.timer = wm.event_timer_add(time_step=1e-3, window=context.window)
        wm.modal_handler_add(self)

        # Setup prograss bar
        context.scene.tbb_progress_label = "Create sequence"
        context.scene.tbb_progress_value = -1.0

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == "ESC":
            self.cancel(context)
            return {"CANCELLED"}

        if event.type == "TIMER":
            self.progress += .1
            context.scene.tbb_progress_value = self.progress

        return {"PASS_THROUGH"}
    
    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self.timer)
        self.timer = None
        context.scene.tbb_settings.create_sequence_is_running = False
        context.scene.tbb_progress_value = -1.0
        self.report({"INFO"}, "Create sequence cancelled")
