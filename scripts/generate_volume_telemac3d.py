"""
Copyright (C) 2022 ARTELIAGROUP

    Created by Félix Olart (felix.olart56@gmail.com)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.



    Standalone module to generate telemac3d volumes from Serafin files.
"""

import os
import sys

import time
import numpy as np
from math import ceil
import itertools as it
from numba import cuda
import pyopenvdb as vdb
from copy import deepcopy
from multiprocessing import Process, Manager, RawArray

# Custom imports
sys.path.insert(0, os.path.abspath("../nimphs/properties/telemac/"))
from serafin import Serafin


class Mesh():

    def __init__(self, path: str, plane_interp_steps: int = 0) -> None:
        """
        Init metohd of the class.

        Args:
            path (str): path to Serafin file
            plane_interp_steps (int, optional): interpolation steps for planes. Defaults to 0.
        """

        # Read file
        self.file = Serafin(path, read_time=True)
        self.file.get_2d()
        self.data = self.file.read(self.file.temps[0])

        # Get total number of planes (with interpolation)
        self.plane_interp_steps = plane_interp_steps
        self.nb_planes = (self.file.nplan - 1) * plane_interp_steps + self.file.nplan

        # Get mesh information
        self.nb_vertices = self.file.npoin2d
        self.x_coords = self.file.x[:self.nb_vertices]
        self.y_coords = self.file.y[:self.nb_vertices]
        self.z_coords = self.get_point_data(['ELEVATION Z', 'COTE Z'])

        # Get minimum values of coordinates (used in prepare voxels)
        self.minimum = [np.min(self.x_coords), np.min(self.y_coords), np.min(self.z_coords)]

        # Get mesh dimensions
        self.length = np.max(self.x_coords) - self.minimum[0]
        self.width = np.max(self.y_coords) - self.minimum[1]
        self.height = np.max(self.z_coords) - self.minimum[2]

    def set_time_point(self, time_point: int, time_interp_step: int = 0, time_steps: int = 0) -> None:
        """
        Update data according to the given time point. Linearly interpolates data in time if needed.

        Args:
            time_point (int): time point to read
            time_interp_step (int, optional): time step of interpolated time point. Defaults to 0.
            time_steps (int, optional): number of time steps between each time point. Defaults to 0.
        """

        if time_interp_step == 0:
            self.data = self.file.read(self.file.temps[time_point])
            self.z_coords = self.get_point_data(['ELEVATION Z', 'COTE Z'])
        else:
            # Linearly interpolate point data in time
            current_data = self.file.read(self.file.temps[time_point])
            next_data = self.file.read(self.file.temps[time_point + 1])
            percentage = time_interp_step / (time_steps + 1)
            difference = next_data - current_data
            self.data = current_data + percentage * difference

            self.z_coords = self.get_point_data(['ELEVATION Z', 'COTE Z'])

    def get_point_data(self, names: list[str]) -> np.ndarray:
        """
        Get point data if variable found in the given list of names.

        Args:
            names (list[str]): list of possible names

        Raises:
            NameError: if names not found in variables list

        Returns:
            np.ndarray: point data
        """

        for name, id in zip([name[:16] for name in self.file.nomvar], range(len(self.file.nomvar))):
            for subname in names:
                if subname in name:
                    if self.plane_interp_steps == 0:
                        return self.data[id]
                    else:
                        return self.interpolate_plane_data(self.data[id])

        raise NameError(f"Point data {names} not found in file.")

    def interpolate_plane_data(self, data: np.ndarray) -> np.ndarray:
        """
        Linearly interpolates given data to generate 'fake' planes.

        Args:
            data (np.ndarray): point data to interpolate.

        Returns:
            np.ndarray: interpolated data.
        """

        # Prepare data
        output = [0] * self.nb_planes
        for id in range(self.file.nplan):
            start = id * self.nb_vertices
            end = id * self.nb_vertices + self.nb_vertices
            output[id * self.plane_interp_steps + id] = deepcopy(data[start:end])

        # Linear iterpolation
        # [x, ., ., ., x, ., ., ., x, ., ., ., x, ., ., ., x]
        # 'x' is a knwon data, '.' is data to generate
        for id in range(1, self.file.nplan):
            end = id * (self.plane_interp_steps + 1)
            start = end - self.plane_interp_steps

            difference = np.array(output[end]) - np.array(output[start - 1])

            for interp_id in range(start, end, 1):
                percentage = interp_id / (self.plane_interp_steps + 1) - (id - 1)
                output[interp_id] = output[start - 1] + percentage * difference

        return np.array(output).flatten()

    def __str__(self) -> str:
        """
        Output this data structure as a string.

        Returns:
            str: output
        """

        output = "MESH:\n"
        output += f"DIMENSIONS: L = {self.length}, W = {self.width}, H = {self.height}\n"
        output += f"MINIMUM   : X = {self.minimum[0]}, Y = {self.minimum[1]}, Z = {self.minimum[2]}\n"
        output += f"VERTICES  : NB = {self.nb_vertices}\n"
        output += f"PLANES    : NB = {self.file.nplan}, INTERPOLATED = {self.plane_interp_steps}, TOTAL: {self.nb_planes}"

        return output


class Volume():

    def __init__(self, mesh: Mesh, nb_threads: int, use_cuda: bool = False, vx_size: float = 0.5,
                 dimensions: tuple[float] = (0.0, 0.0, 0.0)) -> None:
        """
        Init method of the class.

        Args:
            mesh (Mesh): mesh information
            nb_threads (int): number of threads to use for parallel computation
            use_cude (boo, option): indicate whether to use CUDA
            vx_size (float, optional): voxel size. Defaults to 0.5.
            dimensions (tuple[float], optional). Defaults to (0.0, 0.0, 0.0).
        """

        # Indicate use of CUDA for volume computation
        self.use_cuda = use_cuda

        # If no dimensions provided, use the given size to generate 'cubic' voxels
        if dimensions == (0.0, 0.0, 0.0):

            # Set voxel size
            self.vx_size = (vx_size, vx_size, vx_size)

            # Compute raw dimensions of the volume
            self.raw_dim_x = mesh.length / vx_size
            self.raw_dim_y = mesh.width / vx_size
            self.raw_dim_z = mesh.height / vx_size

            # Save dimensions
            self.dim = (int(np.rint(self.raw_dim_x)), int(np.rint(self.raw_dim_y)), int(np.rint(self.raw_dim_z)))

            # Compute offset due to error of discretization
            self.offset = [
                abs(self.dim[0] - self.raw_dim_x) * 0.5,
                abs(self.dim[1] - self.raw_dim_y) * 0.5,
                abs(self.dim[2] - self.raw_dim_z) * 0.5,
            ]

        else:
            self.dim = dimensions
            self.vx_size = (mesh.length / dimensions[0], mesh.width / dimensions[1], mesh.height / dimensions[2])
            self.raw_dim_x = dimensions[0]
            self.raw_dim_y = dimensions[1]
            self.raw_dim_z = dimensions[2]
            self.offset = [0, 0, 0]

        # Array information
        self.zmin = None
        self.zmax = None
        # This array contains 'z columns' (vertices in the bounds of each voxel along the z axis)
        self.zcols: list[np.ndarray] = list()

        self.nb_voxels = self.dim[0] * self.dim[1] * self.dim[2]
        self.nb_threads = nb_threads

        # Allocate memory for volume data
        data = np.zeros(self.dim)
        if self.use_cuda:
            self.data = data.flatten()
        else:
            self.data = make_shared_array(data, 'd', self.dim)
            # Generate voxel indices
            self.vxids = list(it.product(*[range(n) for n in self.dim]))
            self.xyids = np.repeat(np.arange(self.dim[0] * self.dim[1]), self.dim[2])

    def prepare_voxels(self, mesh: Mesh) -> None:
        """
        Prepare voxels information (compute zcols, zmin, zmax).

        Args:
            mesh (Mesh): mesh information
        """

        # Compute min/max coordinates
        start = time.time()

        x_world = np.array(mesh.minimum[0] - self.offset[0] + np.arange(self.dim[0]) * self.vx_size[0])
        y_world = np.array(mesh.minimum[1] - self.offset[1] + np.arange(self.dim[1]) * self.vx_size[1])
        z_world = np.array(mesh.minimum[2] - self.offset[2] + np.arange(self.dim[2]) * self.vx_size[2])

        xmin, xmax = np.array(x_world - self.vx_size[0] * 1.0), np.array(x_world + self.vx_size[0] * 1.0)
        ymin, ymax = np.array(y_world - self.vx_size[1] * 1.0), np.array(y_world + self.vx_size[1] * 1.0)
        zmin, zmax = np.array(z_world - self.vx_size[2] * 1.0), np.array(z_world + self.vx_size[2] * 1.0)

        plane_indices = np.arange(0, mesh.nb_planes, 1)

        if SHOW_DETAILS:
            print(f"| Compute min/max coordinates: {time.time() - start}s")

        start = time.time()

        # Prepare voxels information
        if self.use_cuda:
            self.prepare_voxels_for_gpu(xmin, xmax, ymin, ymax, plane_indices, mesh, mode='SEQUENTIAL')
            self.zmin = zmin
        else:
            self.prepare_voxels_for_cpu(xmin, xmax, ymin, ymax, plane_indices, mesh, mode='SEQUENTIAL')
            # Allocate shared memory for zmin and zmax
            self.zmin = zmin
            self.zmax = zmax

        if SHOW_DETAILS:
            print(f"| Prepare voxels information: {time.time() - start}s")

    def prepare_voxels_for_cpu(self, xmin, xmax, ymin, ymax, plane_indices, mesh: Mesh, mode: str = 'SEQUENTIAL'):
        """
        Prepare voxels information to be computed using the CPU.

        Args:
            xmin (np.ndarray): min x coordinates of voxels
            xmax (np.ndarray): max x coordinates of voxels
            ymin (np.ndarray): min y coordinates of voxels
            ymax (np.ndarray): max y coordinates of voxels
            plane_indices (np.ndarray): plane indices
            mesh (Mesh): mesh
            mode (str, optional): execution mode, enum in ['SEQUENTIAL', 'PARALLEL_CPU', 'PARALLEL_GPU'].\
                                  Defaults to 'SEQUENTIAL'.
        """

        if mode == 'SEQUENTIAL':

            for x in range(self.dim[0]):
                for y in range(self.dim[1]):

                    # Get vertices which validated the X and Y conditions (Z column)
                    x_condition = np.logical_and(xmin[x] <= mesh.x_coords, mesh.x_coords <= xmax[x])
                    y_condition = np.logical_and(ymin[y] <= mesh.y_coords, mesh.y_coords <= ymax[y])

                    mesh_vertices = np.array(np.where(x_condition & y_condition)[0])
                    offsets = np.repeat(plane_indices * x_condition.shape[0], mesh_vertices.shape[0])

                    self.zcols.append(np.array(np.tile(mesh_vertices, mesh.nb_planes) + offsets))

        elif mode == 'PARALLEL_CPU':

            # TODO: /!\ All the zcols are shuffeld
            # Using such a data structure is unefficient.
            # All the threads are "sort of trying to write at the same location". --> race condition?
            # TODO: maybe find another data structure that would best fit the issue

            # Prepare processes information
            size = self.dim[0] * self.dim[1]
            # zcols = np.empty((size,), dtype='object')
            size_per_thread = ceil(size / self.nb_threads)
            processes: list[Process] = list()
            manager = Manager()
            shared_list = manager.list()

            # Run as many processes as chosen threads
            for id in range(self.nb_threads):

                start, end = id * size_per_thread, min((id + 1) * size_per_thread, size)
                process = Process(
                    target=prepare_voxels_cpu,
                    args=(shared_list, xmin, xmax, ymin, ymax, mesh.x_coords, mesh.y_coords, plane_indices, start, end,
                          self.dim))
                process.start()
                processes.append(process)

            # Wait for all processes to finish
            for process in processes:
                process.join()

            self.zcols = shared_list

        elif mode == 'PARALLEL_GPU':
            pass

    def prepare_voxels_for_gpu(self, xmin, xmax, ymin, ymax, plane_indices, mesh: Mesh, mode: str = 'SEQUENTIAL'):
        """
        Prepare voxels information to be computed using the GPU.

        Args:
            xmin (np.ndarray): min x coordinates of voxels
            xmax (np.ndarray): max x coordinates of voxels
            ymin (np.ndarray): min y coordinates of voxels
            ymax (np.ndarray): max y coordinates of voxels
            plane_indices (np.ndarray): plane indices
            mesh (Mesh): mesh
            mode (str, optional): execution mode, enum in ['NORMAL', 'PARALLEL_CPU', 'PARALLEL_GPU'].\
                                  Defaults to 'SEQUENTIAL'.
        """

        if mode == 'SEQUENTIAL':

            vertex_indices = list()
            start_id = self.dim[0] * self.dim[1] * 2

            for x in range(self.dim[0]):
                for y in range(self.dim[1]):

                    # Get vertices which validated the X and Y conditions (Z column)
                    x_condition = np.logical_and(xmin[x] <= mesh.x_coords, mesh.x_coords <= xmax[x])
                    y_condition = np.logical_and(ymin[y] <= mesh.y_coords, mesh.y_coords <= ymax[y])

                    mesh_vertices = np.array(np.where(x_condition & y_condition)[0])
                    offsets = np.repeat(plane_indices * x_condition.shape[0], mesh_vertices.shape[0])

                    zcol = np.array(np.tile(mesh_vertices, mesh.nb_planes) + offsets)

                    self.zcols.append(start_id)
                    self.zcols.append(zcol.size)
                    vertex_indices.append(zcol)
                    start_id += zcol.size

            # Concatenate zcols information with mesh vertices
            self.zcols = np.concatenate((self.zcols, np.hstack(vertex_indices)))

        elif mode == 'PARALLEL_CPU':
            # TODO: is it possible to compute it with CPU parallelization?
            pass
        elif mode == 'PARALLEL_GPU':
            # TODO: is it possible to compute it with GPU parallelization?
            pass

    def fill(self, mesh: Mesh, point_data: list[str]) -> None:
        """
        Set the density of each voxel using the given data.

        Args:
            mesh (Mesh): mesh data
            point_data (list[str]): name of point data to use as density
        """

        start = time.time()
        data = mesh.get_point_data(point_data)

        if self.use_cuda:
            self.fill_with_gpu(data, mesh)
        else:
            self.fill_with_cpu(data, mesh)

        if SHOW_DETAILS:
            print(f"| Fill volume: {time.time() - start}s")

    def fill_with_cpu(self, data: np.ndarray, mesh: Mesh):
        """
        Set density of each voxel using an algorithm with runs on the CPU.

        Args:
            data (np.ndarray): point data
            mesh (Mesh): mesh information
        """

        # Prepare processes information
        size_per_thread = ceil(self.nb_voxels / self.nb_threads)
        processes: list[Process] = list()

        # Run as many processes as chosen threads
        for id in range(self.nb_threads):

            # Compute start / end indices so each thread know on which data to work
            start, end = id * size_per_thread, min((id + 1) * size_per_thread, self.nb_voxels)

            process = Process(
                target=fill_volume_cpu,
                args=(self.data, data, self.vxids, self.xyids, mesh.z_coords, self.zcols, self.zmin, self.zmax,
                      start, end, self.dim))
            process.start()
            processes.append(process)

        # Wait for all processes to finish
        for process in processes:
            process.join()

    def fill_with_gpu(self, data: np.ndarray, mesh: Mesh):
        """
        Set density of each voxel using an algorithm with runs on the GPU.

        Args:
            data (np.ndarray): point data
            mesh (Mesh): mesh information
        """

        start = time.time()

        # Copy data from host to device, D_xxx = data on device
        D_volume = cuda.to_device(np.zeros(self.nb_voxels))
        D_data = cuda.to_device(data)
        D_z_coords = cuda.to_device(mesh.z_coords)
        D_zcols = cuda.to_device(self.zcols)
        D_zmin = cuda.to_device(self.zmin)

        if SHOW_DETAILS:
            print(f"  | Copy to device: {time.time() - start}s")

        start = time.time()

        # Compute density of voxels
        fill_volume_gpu.forall(self.nb_voxels)(D_volume, D_data, D_z_coords, D_zcols, D_zmin, self.vx_size[2], self.dim)

        if SHOW_DETAILS:
            print(f"  | Launch threads: {time.time() - start}s")

        start = time.time()

        # Copy data from device to host
        self.data = D_volume.copy_to_host()

        if SHOW_DETAILS:
            print(f"  | Copy to host: {time.time() - start}s")

    def export_time_point(self, mesh: Mesh, point_data: list[str], file_name: str) -> None:
        """
        Generate and export volume for the current time point.

        Args:
            mesh (Mesh): mesh
            point_data (list[str]): point data to use as density
            file_name (str): file name
        """

        # Fill volume
        self.fill(mesh, point_data)

        # Save volume
        self.save_as_vdb(point_data[0], file_name)
        self.clear_data()

    def clear_data(self) -> None:
        """Clear volume data and allocate new memory."""

        # Clear volume data (set all cells to 0.0)
        if self.use_cuda:
            self.data.fill(0.0)
        else:
            np.frombuffer(self.data).fill(0.0)

    def save_as_vdb(self, grid_name: str, file_name: str) -> None:
        """
        Save volume data as .vdb file.

        Args:
            grid_name (str): name of variable to export
            file_name (str): file name
        """

        grid = vdb.FloatGrid()

        if not self.use_cuda:
            grid.copyFromArray(np.frombuffer(self.data).reshape(self.dim))
        else:
            grid.copyFromArray(self.data.reshape(self.dim))

        grid.name = grid_name

        vdb.write(f"{file_name}.vdb", grids=grid)

    def __str__(self) -> str:
        """
        Output this data structure as a string.

        Returns:
            str: output
        """

        output = "VOLUME:\n"
        output += f"Use CUDA: {self.use_cuda}\n"
        output += f"RAW DIM: X = {self.raw_dim_x}, Y = {self.raw_dim_y}, Z = {self.raw_dim_z}\n"
        output += f"VOL DIM: X = {self.dim[0]}, Y = {self.dim[1]}, Z = {self.dim[2]}\n"
        output += f"OFFSET : X = {self.offset[0]}, Y = {self.offset[1]}, Z = {self.offset[2]}\n"
        output += f"VOXELS : NB = {self.dim[0] * self.dim[1] * self.dim[2]}, SIZE = {self.vx_size}"

        return output


def make_shared_array(data: np.ndarray, ctype: str, shape: tuple[int]):
    """
    Make raw shared array from given data and information.

    Args:
        data (np.ndarray): data to put in the array
        ctype (str): ctype. Enum in ['i', 'd'].
        shape (int): shape of the array

    Returns:
        RawArray: shared array
    """

    # Compute size of the array using the given shape
    size = 1
    for element in shape:
        size *= element

    array = RawArray(ctype, int(size))
    if ctype == 'i':
        NP_array = np.frombuffer(array, dtype='int32').reshape(shape)
    else:
        NP_array = np.frombuffer(array).reshape(shape)

    np.copyto(NP_array, data)

    return array


def prepare_voxels_cpu(zcols, xmin: np.ndarray, xmax: np.ndarray, ymin: np.ndarray, ymax: np.ndarray,
                       x_coords: np.ndarray, y_coords: np.ndarray, plane_indices: np.ndarray, start: int,
                       end: int, dim: tuple[float, float, float]) -> None:
    """
    Prepare voxels information (runs for one thread).

    Args:
        zcols (?): z columns (destination array)
        xmin (np.ndarray): min x coordinates of voxels
        xmax (np.ndarray): max x coordinates of voxels
        ymin (np.ndarray): min y coordinates of voxels
        ymax (np.ndarray): max y coordinates of voxels
        x_coords (np.ndarray): x vertices coordinates
        y_coords (np.ndarray): y vertices coordinates
        plane_indices (np.ndarray): indices of all available planes
        start (int): start index
        end (int): end index
        dim (tuple[float, float, float]): volume dimensions
    """

    for xyid in range(start, end, 1):
        x, y = xyid // dim[0], xyid % dim[1]

        # Get vertices which validated the X and Y conditions (Z column)
        x_condition = np.logical_and(xmin[x] <= x_coords, x_coords <= xmax[x])
        y_condition = np.logical_and(ymin[y] <= y_coords, y_coords <= ymax[y])

        mesh_vertices = np.array(np.where(x_condition & y_condition)[0])
        offsets = np.repeat(plane_indices * x_condition.shape[0], mesh_vertices.shape[0])

        zcols.append(np.array(np.tile(mesh_vertices, plane_indices.size) + offsets))


def fill_volume_cpu(volume: np.ndarray, data: np.ndarray, vxids: np.ndarray, xyids: np.ndarray, z_coords: np.ndarray,
                    zcols: np.ndarray, zmin: np.ndarray, zmax: np.ndarray, start: int, end: int,
                    dim: tuple[float, float, float]) -> None:
    """
    Fill volume density using given data (runs for one CPU thread).

    Args:
        volume (np.ndarray): volume (destination array)
        data (np.ndarray): point data to use as density
        vxids (np.ndarray): voxel '(x, y, z)' indices
        xyids (np.ndarray): voxel 'xy' indices
        z_coords (np.ndarray): z vertices coordinates
        zcols (np.ndarray): z columns
        zmin (np.ndarray): min z coordinates of voxels
        zmax (np.ndarray): max z coordinates of voxels
        start (int): start index
        end (int): end index
        dim (tuple[float, float, float]): volume dimensions
    """

    # Retrieve data from RawArrays (T_xxx is data for the current thread)
    T_volume = np.frombuffer(volume).reshape(dim)

    for vxid, xyid in zip(vxids[start:end], xyids[start:end]):
        zcol = zcols[xyid]
        z_coords_column = z_coords[zcol]
        z_condition = np.logical_and(zmin[vxid[2]] <= z_coords_column, z_coords_column <= zmax[vxid[2]])
        mesh_vertices = list(zcol[z_condition])

        # Set data
        if len(mesh_vertices) > 0:
            T_volume[vxid[0], vxid[1], vxid[2]] = np.sum(data[mesh_vertices]) / len(mesh_vertices)


@cuda.jit
def fill_volume_gpu(D_volume: np.ndarray, D_data: np.ndarray, D_z_coords: np.ndarray, D_zcols: np.ndarray,
                    D_zmin: np.ndarray, vx_size_z: float, dim: tuple[float, float, float]):
    """
    Fill volume density using given data (runs for one GPU thread).

    Args:
        D_volume (np.ndarray): volume (destination array)
        D_data (np.ndarray): point data to use as density
        D_z_coords (np.ndarray): z vertices coordinates
        D_zcols (np.ndarray): z columns
        D_zmin (np.ndarray): min z coordinates of voxels
        vx_size_z (float): voxel size along z axis
        dim (tuple[float, float, float]): volume dimensions
    """

    # Thread id corresponds to voxel id
    thid = cuda.grid(1)

    # Make sure the thread id corresponds to a voxel
    if thid < dim[0] * dim[1] * dim[2]:
        xyid = thid // dim[2]
        start, end = D_zcols[xyid * 2], D_zcols[xyid * 2] + D_zcols[xyid * 2 + 1]
        zcol = D_zcols[start:end]

        value, count = 0.0, 0
        for vtid in zcol:

            plane_id = thid % dim[2]

            z, zmin, zmax = D_z_coords[vtid], D_zmin[plane_id], D_zmin[plane_id] + 2.0 * vx_size_z
            if zmin <= z and z <= zmax:
                value += D_data[vtid]
                count += 1

        D_volume[thid] = value / count if count > 0 else 0.0


if __name__ == '__main__':

    SHOW_DETAILS = True
    OUTPUT_PATH = "/tmp"
    DIMENSIONS = (100, 100, 40)
    VOXEL_SIZE = .1
    VAR = 'ELEVATION Z'
    TIME_INTERP_STEPS = 0
    PLANE_INTERP_STEPS = 5
    NB_THREADS = 12
    VERSION = 16
    USE_CUDA = True
    FILE_NAME = f"{OUTPUT_PATH}/TEST_V{VERSION}{'_GPU' if USE_CUDA else ''}"

    start_global = time.time()

    # ELEVATION Z: 0.0, 4.773
    mesh = Mesh("../data/telemac_3d/telemac_3d.slf", plane_interp_steps=PLANE_INTERP_STEPS)

    NB_TIME_POINTS = mesh.file.nb_pdt
    # NB_TIME_POINTS = 10

    volume = Volume(mesh, NB_THREADS, use_cuda=USE_CUDA, vx_size=VOXEL_SIZE, dimensions=DIMENSIONS)

    print("-------------------------")
    print(mesh)
    print("-------------------------")

    # Prepare volume
    start = time.time()
    print("PREPARE VOLUME -----------------------------")
    volume.prepare_voxels(mesh)
    if SHOW_DETAILS:
        print(f"Total: {time.time() - start}s")

    print(volume)
    print("-------------------------")

    counter = 0

    for time_point in range(NB_TIME_POINTS):
        print(f"TIME POINT: {time_point} ------------------------------")

        start_tp = time.time()

        # Update data
        start = time.time()
        mesh.set_time_point(time_point)
        if SHOW_DETAILS:
            print(f"Set time point: {time.time() - start}s")

        # Export volume at current time point
        volume.export_time_point(mesh, [VAR], f"{FILE_NAME}_{counter}")
        counter += 1

        # Generate interpolated time steps
        if time_point != NB_TIME_POINTS - 1:
            for interp_time_point in range(1, TIME_INTERP_STEPS + 1):
                mesh.set_time_point(time_point, interp_time_point, TIME_INTERP_STEPS)
                volume.export_time_point(mesh, [VAR], f"{FILE_NAME}_{counter}")
                counter += 1

        if SHOW_DETAILS:
            print(f"Total: {time.time() - start_tp}s")

    print(f"TOTAL PROGRAM: {time.time() - start_global}s")
