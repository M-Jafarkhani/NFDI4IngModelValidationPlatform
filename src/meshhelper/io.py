from pathlib import Path

import basix
import dolfinx as df
import numpy as np
import pyvista
import ufl

import dolfinx.cpp as _cpp

vtk_cell_to_basix = {
    5: basix.CellType.triangle,
    9: basix.CellType.quadrilateral,
    10: basix.CellType.tetrahedron,
    12: basix.CellType.hexahedron,
    13: basix.CellType.prism,
    14: basix.CellType.pyramid,
    69: basix.CellType.triangle,
}

vtk_cell_to_dolfinx_mesh = {
    5: df.mesh.CellType.triangle,
    9: df.mesh.CellType.quadrilateral,
    10: df.mesh.CellType.tetrahedron,
    12: df.mesh.CellType.hexahedron,
    13: df.mesh.CellType.prism,
    14: df.mesh.CellType.pyramid,
    69: df.mesh.CellType.triangle,
}

number_of_points_to_degree = {
    basix.CellType.triangle: {3: 1, 6: 2},
    basix.CellType.quadrilateral: {4: 1, 9: 2},
    basix.CellType.tetrahedron: {4: 1, 10: 2},
    basix.CellType.hexahedron: {8: 1, 27: 2},
}


def vtu_to_dolfinx(
    comm, file: str | Path, data: list[str] | None = None
) -> df.mesh.Mesh:
    assert Path(file).suffix == ".vtu", "File must have .vtu extension"
    mesh = pyvista.read(file)
    return pyvista_mesh_to_dolfinx(comm, mesh, data)

def pyvista_mesh_to_dolfinx(
    comm, mesh: pyvista.UnstructuredGrid, data: list[str] | None = None
) -> df.mesh.Mesh:
    points = np.array(mesh.points)
    points_per_cell: int = mesh.cells[0]
    df_cell_type = vtk_cell_to_dolfinx_mesh[mesh.celltypes[0]]
    basix_cell_type = vtk_cell_to_basix[mesh.celltypes[0]]
    degree = number_of_points_to_degree[basix_cell_type][points_per_cell]

    map_vtk = _cpp.io.perm_vtk(df_cell_type, points_per_cell) #tested: with other indices, the mesh is warped

    cells = np.array(mesh.cells.reshape(-1, points_per_cell + 1)[:, 1:])
    cells = cells[:, map_vtk]
    element = basix.ufl.element(
        basix.ElementFamily.P,
        vtk_cell_to_basix[mesh.celltypes[0]],
        degree,
        basix.LagrangeVariant.equispaced,
        shape=(2,),
    )
    ufl_mesh = ufl.Mesh(element)
    df_mesh = df.mesh.create_mesh(comm, cells, points, ufl_mesh)

    if data is None:
        return df_mesh

    dimensions = np.unique([mesh[data_].shape[1] for data_ in data])

    spaces = {
        dimension: df.fem.functionspace(df_mesh, ("CG", degree, (dimension,)))
        for dimension in dimensions
    }
    functions = {}
    for data_ in data:
        function_tmp = df.fem.Function(spaces[mesh[data_].shape[1]])
        indices_df = np.lexsort(
            [df_mesh.geometry.x[:, i] for i in range(df_mesh.geometry.x.shape[1])]
        )
        indices_pyvista = np.lexsort([points[:, i] for i in range(points.shape[1])])
        print(len(indices_pyvista), len(indices_df))
        df_reshaped = function_tmp.x.array.reshape(-1, mesh[data_].shape[1])
        df_reshaped[indices_df] = mesh[data_][indices_pyvista]
        functions[data_] = function_tmp
    return df_mesh, functions
