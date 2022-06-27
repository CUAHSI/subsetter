import xarray as xr
import pyproj

from .types import BoundingBox


def geo_grid_proj(geo_em: xr.Dataset) -> str:
    def get_attr_helper(ds: xr.Dataset, attr: str) -> str:
        value = ds.attrs.get(attr, None)
        if value is None:
            error_message = f"Global attribute: {attr}, not found in {ds}"
            raise AttributeError(error_message)
        return value

    map_proj = get_attr_helper(geo_em, "MAP_PROJ")

    if map_proj != 1:
        error_message = f"Only MAP_PROJ=1, Lambert Conformal Conic, is supported. MAP_PROJ={map_proj}"
        raise ValueError(error_message)

    cen_lat = get_attr_helper(geo_em, "CEN_LAT")
    cen_lon = get_attr_helper(geo_em, "STAND_LON")
    truelat1 = get_attr_helper(geo_em, "TRUELAT1")
    truelat2 = get_attr_helper(geo_em, "TRUELAT2")

    return f"+proj=lcc +lat_1={truelat1} +lat_2={truelat2} +lat_0={cen_lat} +lon_0={cen_lon} +x_0=0 +y_0=0 +a=6370000 +b=6370000 +units=m +no_defs"


def geo_grid_proj_as_Proj(geo_em: xr.Dataset) -> pyproj.Proj:
    def get_attr_helper(ds: xr.Dataset, attr: str) -> str:
        value = ds.attrs.get(attr, None)
        if value is None:
            error_message = f"Global attribute: {attr}, not found in {ds}"
            raise AttributeError(error_message)
        return str(value)

    map_proj = get_attr_helper(geo_em, "MAP_PROJ")

    if map_proj != "1":
        error_message = f"Only MAP_PROJ=1, Lambert Conformal Conic, is supported. MAP_PROJ={map_proj}"
        raise ValueError(error_message)

    cen_lat = get_attr_helper(geo_em, "CEN_LAT")
    moad_cen_lat = get_attr_helper(geo_em, "MOAD_CEN_LAT")
    cen_lon = get_attr_helper(geo_em, "STAND_LON")
    truelat1 = get_attr_helper(geo_em, "TRUELAT1")
    truelat2 = get_attr_helper(geo_em, "TRUELAT2")

    # source: https://fabienmaussion.info/2018/01/06/wrf-projection/
    return pyproj.Proj(
        proj="lcc",  # projection type: Lambert Conformal Conic
        lat_1=truelat1,
        lat_2=truelat2,  # Cone intersects with the sphere
        lat_0=moad_cen_lat,
        lon_0=cen_lon,  # Center point
        a=6370000,
        b=6370000,
    )


def estimate_geogrid_corners(ds: xr.Dataset) -> BoundingBox:
    # TODO: should this return a SimpleBoundingBox instead?

    # reference: http://amps-backup.ucar.edu/information/configuration/wrf_grid_structure.html
    # wrf geogrid uses an Arakawa C-grid staggering as show below.

    # Mass grid
    #   Mass-related quantities such as pressure, temperature, humidity, etc. are computed at the
    #   center of a grid cell, at points indicated by "x". Collectively, these "x" points are
    #   referred to as the "mass grid".
    # U grid
    #   The u-component of the horizontal wind is computed at the center of the left and right sides
    #   of a grid cell, at points indicated by the "u". Collectively, these points are
    #   referred to as the "U grid". The U grid has the same number of points in the y direction as
    #   the mass grid, and one more point in the x direction.
    # V grid
    #   The v-component of the horizontal wind is computed at the center of the top and bottom sides
    #   of a grid cell, at points indicated by the "v". Collectively, these points are referred to
    #   as the "V grid". The V grid has the same number of points in the x direction as the mass grid,
    #   and one more point in the y direction.
    # Staggered grid
    #   The points defining the corners of the mass grid cells are indicated by "+" in the
    #   schematic. Collectively, these points are referred to as the "staggered grid". The WRF
    #   staggered grid has one additional point in each direction beyond the dimensions of the mass
    #   grid.

    # + - -v- - +
    # |         |
    # u    x    u
    # |         |
    # + - -v- - +

    # wrf's geogrid files uses a cartesian grid to store values with the bottom left most grid cell
    # at [0, 0, 0] (the zeroth dimension is time).
    # bottom left, bottom right, top left, top right
    y_idx = (0, 0, -1, -1)
    x_idx = (0, -1, 0, -1)

    # to estimate the "staggered" corner lats the u and v components are used. given that the u
    # component is the nearest west to the staggered grid and the v component is the nearest south
    # to the staggered grid, the corner ys (lats) from the u component and the corner xs (longs)
    # from the v component are paired to get an estimated staggered grid corner point.
    u_xs = ds.XLONG_U.values[0, y_idx, x_idx]
    v_ys = ds.XLAT_V.values[0, y_idx, x_idx]

    return BoundingBox(
        bottom_left=(u_xs[0], v_ys[0]),
        bottom_right=(u_xs[1], v_ys[1]),
        top_left=(u_xs[2], v_ys[2]),
        top_right=(u_xs[3], v_ys[3]),
    )


def distance_factor(origin: float, grid_spacing: float, location: float):
    return (origin - location) / grid_spacing
