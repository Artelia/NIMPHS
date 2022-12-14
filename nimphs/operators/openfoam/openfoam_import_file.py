# <pep8 compliant>
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator, Context, Object
from bpy.props import StringProperty, PointerProperty, EnumProperty

import logging
log = logging.getLogger(__name__)

import time

from nimphs.operators.utils.mesh import OpenfoamMeshUtils
from nimphs.operators.utils.object import OpenfoamObjectUtils
from nimphs.properties.openfoam.file_data import OpenfoamFileData
from nimphs.properties.openfoam.import_settings import NIMPHS_OpenfoamImportSettings


def import_openfoam_menu_draw(self, context: Context) -> None:  # noqa: D417
    """
    Draw function which displays the import button in File > Import.

    Args:
        context (Context): context
    """

    prefs = context.preferences.addons["nimphs"].preferences.settings
    extensions = prefs.openfoam_extensions.replace("*", "")
    self.layout.operator(NIMPHS_OT_OpenfoamImportFile.bl_idname, text=f"OpenFOAM ({extensions})")


class NIMPHS_OT_OpenfoamImportFile(Operator, ImportHelper):
    """Import an OpenFOAM file."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "nimphs.import_openfoam_file"
    bl_label = "Import"
    bl_description = "Import an OpenFOAM file"

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

    #: bpy.props.StringProperty: List of allowed file extensions.
    filter_glob: StringProperty(
        default="*.foam",  # multiple allowed types: "*.foam;*.[];*.[]" etc ...
        options={"HIDDEN"}  # noqa: F821
    )

    #: bpy.props.StringProperty: Name to give to the imported object.
    name: StringProperty(
        name="Name",                    # noqa: F821
        description="Name to give to the imported object",
        default="OpenFOAM_preview",     # noqa: F821
    )

    #: NIMPHS_OpenfoamImportSettings: Import settings.
    import_settings: PointerProperty(type=NIMPHS_OpenfoamImportSettings)

    def execute(self, context: Context) -> set:
        """
        Import the selected file. Generates a preview object.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        start = time.time()

        try:
            file_data = OpenfoamFileData(self.filepath, self.import_settings)

            # Update point data local value ranges
            if self.mode != 'TEST':
                for name in file_data.vars.names:
                    file_data.update_var_range(name, data=file_data.get_point_data_from_raw(name))

        except BaseException:
            self.report({'WARNING'}, "An error occurred reading the file")
            return {'CANCELLED'}

        # Generate the preview mesh. This step is not present in the reload operator because
        # the preview mesh may already be loaded. Moreover, this step takes a while for large meshes.
        try:
            # Generate object
            vertices, file_data.mesh = OpenfoamMeshUtils.vertices(file_data)
            faces = OpenfoamMeshUtils.faces(file_data.mesh)
            obj = OpenfoamObjectUtils.generate(vertices, faces, self.name, new=True)
            # Setup and link generated object
            self.setup_generated_obj(context, obj, file_data)
            context.collection.objects.link(obj)
        except Exception:
            log.error("Something went wrong building the mesh", exc_info=1)
            self.report({'WARNING'}, "Something went wrong building the mesh. See logs.")
            return {'CANCELLED'}

        log.info("{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "File successfully imported")

        return {'FINISHED'}

    def draw(self, _context: Context) -> None:
        """
        UI layout of the operator.

        Args:
            _context (Context): context
        """

        # Import settings
        box = self.layout.box()
        row = box.row()
        row.label(text="Settings")

        row = box.row()
        row.prop(self.import_settings, "case_type", text="Case")
        row = box.row()
        row.prop(self.import_settings, "decompose_polyhedra", text="Decompose polyhedra")
        row = box.row()
        row.prop(self.import_settings, "skip_zero_time", text="Skip zero time")
        row = box.row()
        row.prop(self.import_settings, "triangulate", text="Triangulate")

        # Others
        box = self.layout.box()
        row = box.row()
        row.label(text="Others")

        row = box.row()
        row.prop(self, "name", text="Name")

    def setup_generated_obj(self, context: Context, obj: Object, file_data: OpenfoamFileData) -> None:
        """
        Copy import settings and setup needed 'nimphs' data for the generated object.

        Args:
            context (Context): context
            obj (Object): generated object
            file_data (NIMPHS_OpenfoamFileData): OpenFOAM file data
        """

        # Copy import settings
        io_settings = obj.nimphs.settings.openfoam.import_settings

        obj.nimphs.settings.file_path = self.filepath
        io_settings.case_type = self.import_settings.case_type
        io_settings.decompose_polyhedra = self.import_settings.decompose_polyhedra
        io_settings.skip_zero_time = self.import_settings.skip_zero_time
        io_settings.case_type = self.import_settings.case_type

        # Others
        obj.nimphs.module = 'OpenFOAM'

        # File data
        obj.nimphs.uid = str(time.time())
        context.scene.nimphs.file_data[obj.nimphs.uid] = file_data
