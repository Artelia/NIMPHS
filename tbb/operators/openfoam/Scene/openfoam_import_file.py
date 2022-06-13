# <pep8 compliant>
from bpy.props import StringProperty, PointerProperty
from bpy.types import Operator, Context, Object
from bpy_extras.io_utils import ImportHelper

import time
import logging
log = logging.getLogger(__name__)
from typing import Union
from pyvista import OpenFOAMReader, POpenFOAMReader

from tbb.properties.openfoam.import_settings import TBB_OpenfoamImportSettings
from tbb.operators.openfoam.utils import load_openfoam_file, generate_mesh_data
from tbb.properties.openfoam.utils import encode_value_ranges, encode_scalar_names
from tbb.operators.utils import generate_object_from_data, get_collection, update_scene_settings_dynamic_props
from tbb.properties.openfoam.temporary_data import TBB_OpenfoamTemporaryData


def import_openfoam_menu_draw(self, _context: Context):
    """
    Draw function which displays the import button in File > Import.

    Args:
        _context (Context): context
    """
    self.layout.operator(TBB_OT_OpenfoamImportFile.bl_idname, text="OpenFOAM")


class TBB_OT_OpenfoamImportFile(Operator, ImportHelper):
    """Import an OpenFOAM file. This operator manages the file browser and its filtering options."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.import_openfoam_file"
    bl_label = "Import"
    bl_description = "Import an OpenFOAM file"

    #: bpy.props.StringProperty: List of allowed file extensions.
    filter_glob: StringProperty(
        default="*.foam",  # multiple allowed types: "*.foam;*.[];*.[]" etc ...
        options={"HIDDEN"}  # noqa: F821
    )

    #: bpy.props.StringProperty: Name to give to the imported object.
    name: StringProperty(
        name="Name",
        description="Name to give to the imported object",
        default="TBB_OpenFOAM_preview",
    )

    #: TBB_OpenfoamImportSettings: Import settings.
    import_settings: PointerProperty(type=TBB_OpenfoamImportSettings)

    def execute(self, context: Context) -> set:
        """
        Import the selected file. Generates the object.

        Args:
            _context (Context): context

        Returns:
            set: state of the operator
        """

        start = time.time()

        settings = self.import_settings
        success, file_reader = load_openfoam_file(self.filepath, settings.case_type, settings.decompose_polyhedra)

        if not success:
            self.report({'ERROR'}, "The chosen file does not exist")
            return {'FINISHED'}

        # Generate the preview mesh. This step is not present in the reload operator because
        # the preview mesh may already be loaded. Moreover, this step takes a while for large meshes.
        try:
            vertices, faces, mesh = generate_mesh_data(file_reader, 0, triangulate=settings.triangulate)
            obj = generate_object_from_data(vertices, faces, self.name, new=True)
            self.setup_generated_obj(obj, file_reader)
            context.scene.collection.objects.link(obj)
        except Exception:
            log.error("Something went wrong building the mesh", exc_info=1)
            self.report({'ERROR'}, "Something went wrong building the mesh. See logs.")
            return {'FINISHED'}

        log.info("{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "File successfully imported")

        return {'FINISHED'}

    def draw(self, context: Context) -> None:
        """
        UI layout of the operator.

        Args:
            context (Context): context
        """

        layout = self.layout

        # Import settings
        box = layout.box()
        row = box.row()
        row.label(text="Settings")

        row = box.row()
        row.prop(self.import_settings, "case_type", text="Case")
        row = box.row()
        row.prop(self.import_settings, "decompose_polyhedra", text="Decompose polyhedra")
        row = box.row()
        row.prop(self.import_settings, "triangulate", text="Triangulate")

        # Others
        box = layout.box()
        row = box.row()
        row.label(text="Others")

        row = box.row()
        row.prop(self, "name", text="Name")

    def setup_generated_obj(self, obj: Object, file_reader: Union[OpenFOAMReader, POpenFOAMReader]) -> None:
        """
        Copy import settings and setup needed 'tbb' data for the generated object.

        Args:
            obj (Object): generated object
            file_reader (Union[OpenFOAMReader, POpenFOAMReader]): OpenFOAM file reader
        """

        # Copy import settings
        import_settings = obj.tbb.settings.openfoam.s_sequence.import_settings

        obj.tbb.settings.file_path = self.filepath
        import_settings.case_type = self.import_settings.case_type
        import_settings.decompose_polyhedra = self.import_settings.decompose_polyhedra
        import_settings.case_type = self.import_settings.case_type

        # Others
        obj.tbb.uid = str(time.time())

        # Temporary data
        obj.tbb.tmp_data[obj.tbb.uid] = TBB_OpenfoamTemporaryData()
        obj.tbb.tmp_data[obj.tbb.uid].update(file_reader, time_point=0)
