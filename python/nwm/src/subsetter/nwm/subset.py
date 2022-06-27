import xarray as xr
import pyproj
import warnings

# local imports
from .types import SimpleBoundingBox, SimpleBoundingBoxIndices
from .utilities import geo_grid_proj_as_Proj


def iget_intersecting_bbox(
    ds: xr.Dataset, bb: SimpleBoundingBox
) -> SimpleBoundingBoxIndices:
    # (lat, lon, (lat, lon))
    # (y, x, (y, x))
    # lon_lat_grid = np.dstack((ds.XLAT_M.values[0, :, :], ds.XLONG_M.values[0, :, :]))
    # determine x corners indices
    # determine y corner indices using x corner indices

    lcc_proj = geo_grid_proj_as_Proj(ds)
    wgs_proj = pyproj.Proj(proj="latlong", datum="WGS84")
    wgs_to_lcc_transformer = pyproj.Transformer.from_proj(wgs_proj, lcc_proj)

    dx = ds.DX
    half_dx = dx // 2

    mass_grid_bottom_left_corner_coords = (
        # dims (time, south_north, west_east)
        ds.XLONG_M.values[0, 0, 0],  # x axis
        ds.XLAT_M.values[0, 0, 0],  # y axis
    )

    mass_grid_min_x_lcc, mass_grid_min_y_lcc = wgs_to_lcc_transformer.transform(
        *mass_grid_bottom_left_corner_coords
    )

    target_xs_lcc, target_ys_lcc = wgs_to_lcc_transformer.transform(*bb.as_array())

    target_xs_lcc_mod = target_xs_lcc % dx
    target_ys_lcc_mod = target_ys_lcc % dx

    x_factor = (target_xs_lcc_mod <= half_dx).astype(int)
    y_factor = (target_ys_lcc_mod <= half_dx).astype(int)

    mg_x_factor = (
        mass_grid_min_x_lcc // dx != (mass_grid_min_x_lcc - half_dx) // dx
    ).astype(int)

    # mg_x_lcc_diff = np.abs(target_xs_lcc - mass_grid_min_x_lcc)

    # TODO: add why this is being done
    # mg_x_lcc_diff = mg_x_lcc_diff - half_dx

    # mg_x_idxs = mg_x_lcc_diff // dx
    # mg_x_idxs = np.abs((target_xs_lcc // dx) - (mass_grid_min_x_lcc // dx))
    mg_x_idxs = np.abs((target_xs_lcc - mass_grid_min_x_lcc) // dx)
    mg_x_idxs = mg_x_idxs.astype(int)

    # TODO: add why add 2
    mg_x_idxs = mg_x_idxs  # + mg_x_factor + x_factor

    mg_x_min_idx, mg_x_max_idx = mg_x_idxs

    mg_bottom_target_x_cols = (
        # dims (time, south_north, west_east)
        ds.XLONG_M.values[0, 0, (mg_x_min_idx, mg_x_max_idx)],  # x axis
        ds.XLAT_M.values[0, 0, (mg_x_min_idx, mg_x_max_idx)],  # y axis
    )

    _, mg_bottom_target_x_cols_lcc = wgs_to_lcc_transformer.transform(
        *mg_bottom_target_x_cols
    )

    mg_y_factor = 1
    # mg_y_factor = (
    #     mg_bottom_target_x_cols_lcc // dx
    #     != (mg_bottom_target_x_cols_lcc - half_dx) // dx
    # ).astype(int)

    # mg_y_lcc_diff = np.abs(mg_bottom_target_x_cols_lcc - target_ys_lcc)

    # TODO: add why this is being done
    # mg_y_lcc_diff = mg_y_lcc_diff - half_dx

    # mg_y_idxs = mg_y_lcc_diff // dx
    # mg_y_idxs = np.abs((target_xs_lcc // dx) - (mass_grid_min_x_lcc // dx))

    # mg_y_idxs = np.abs((mg_bottom_target_x_cols_lcc // dx) - (target_ys_lcc // dx))
    mg_y_idxs = np.abs((mg_bottom_target_x_cols_lcc - target_ys_lcc) // dx)
    mg_y_idxs = mg_y_idxs.astype(int)

    # TODO: add why add 2
    # mg_y_idxs = mg_y_idxs + mg_y_factor + y_factor

    # TODO: add why this
    # mg_y_idxs = len(ds.south_north) - mg_y_idxs

    # # NOTE: min switches to max b.c. grid was flipped top to bottom
    # mg_y_max_idx, mg_y_min_idx = mg_y_idxs

    # NOTE: min switches to max b.c. grid was flipped top to bottom
    mg_y_min_idx, mg_y_max_idx = mg_y_idxs

    return SimpleBoundingBoxIndices(
        top=mg_y_max_idx, right=mg_x_max_idx, bottom=mg_y_min_idx, left=mg_x_min_idx
    )


def subset_geo_em(ds: xr.Dataset, wrf_bb: SimpleBoundingBoxIndices) -> xr.Dataset:
    #  system(paste0("ncks -O -d west_east,", geo_w-1, ",", geo_e-1, " -d south_north,", geo_s-1, ",", geo_n-1,
    #               " -d west_east_stag,", geo_w-1, ",", geo_e, " -d south_north_stag,",geo_s-1, ",", geo_n, " ",
    #               fullGeoFile, " ", subGeoFile))
    # corner_lats <- c()
    # for (latName in c('XLAT_M', 'XLAT_U', 'XLAT_V', 'XLAT_C')) {
    #     if (latName %in% var_names(subGeoFile)) {
    #     a = RNetCDF::var.get.nc(RNetCDF::open.nc(subGeoFile), latName)
    #     corners = c(a[1,1], a[1, ncol(a)], a[nrow(a), ncol(a)], a[nrow(a), 1])
    #     }else{
    #     corners = c(0,0,0,0)
    #     }
    #     corner_lats = c(corner_lats, corners)
    # }

    # corner_lons <- c()
    # for (lngName in c('XLONG_M', 'XLONG_U', 'XLONG_V', 'XLONG_C')) {
    #     if (lngName %in% var_names(subGeoFile)) {
    #     a = RNetCDF::var.get.nc(RNetCDF::open.nc(subGeoFile), lngName)
    #     corners = c(a[1,1], a[1, ncol(a)], a[nrow(a), ncol(a)], a[nrow(a), 1])
    #     }else{
    #     corners = c(0,0,0,0)
    #     }
    #     corner_lons = c(corner_lons, corners)
    # }

    # # Attribute updates
    # system(paste0("ncatted -h -a WEST-EAST_GRID_DIMENSION,global,o,l,", geo_e-geo_w+2, " ", subGeoFile))
    # system(paste0("ncatted -h -a SOUTH-NORTH_GRID_DIMENSION,global,o,l,", geo_n-geo_s+2, " ", subGeoFile))
    # system(paste0("ncatted -h -a WEST-EAST_PATCH_END_UNSTAG,global,o,l,", geo_e-geo_w+1, " ", subGeoFile))
    # system(paste0("ncatted -h -a SOUTH-NORTH_PATCH_END_UNSTAG,global,o,l,", geo_n-geo_s+1, " ", subGeoFile))
    # system(paste0("ncatted -h -a WEST-EAST_PATCH_START_STAG,global,d,,, ", subGeoFile))
    # system(paste0("ncatted -h -a SOUTH-NORTH_PATCH_START_STAG,global,d,,, ", subGeoFile))
    # system(paste0("ncatted -h -a WEST-EAST_PATCH_END_STAG,global,d,,, ", subGeoFile))
    # system(paste0("ncatted -h -a SOUTH-NORTH_PATCH_END_STAG,global,d,,, ", subGeoFile))
    # system(paste0("ncatted -h -a i_parent_end,global,o,l,", geo_e-geo_w+2, " ", subGeoFile))
    # system(paste0("ncatted -h -a j_parent_end,global,o,l,", geo_n-geo_s+2, " ", subGeoFile))
    # system(paste0("ncatted -O -a corner_lons,global,o,f,", paste(corner_lons, collapse  = ","), " ", subGeoFile))
    # system(paste0("ncatted -O -a corner_lats,global,o,f,", paste(corner_lats, collapse  = ","), " ", subGeoFile))
    d = ds.isel(
        west_east=slice(wrf_bb.left, wrf_bb.right + 1),
        south_north=slice(wrf_bb.bottom, wrf_bb.top + 1),
        # NOTE: I think the west_east_stag and south_north_stag should be +2 since their grids are
        # n+1 of the west_east and south_north dims
        west_east_stag=slice(wrf_bb.left, wrf_bb.right + 1),
        south_north_stag=slice(wrf_bb.bottom, wrf_bb.top + 1),
    )
    # reset corner lat and lon

    unstaggered_west_east_dim = wrf_bb.right - wrf_bb.left + 1
    unstaggered_north_south_dim = wrf_bb.top - wrf_bb.bottom + 1

    # + 1 b.c. Arakawa C-grid staggering on u and v. u has +1 in x direction, v has +1 in y direction
    # see diagram and description: http://amps-backup.ucar.edu/information/configuration/wrf_grid_structure.html
    staggered_west_east_dim = unstaggered_west_east_dim + 1
    staggered_north_south_dim = unstaggered_north_south_dim + 1

    d.attrs["WEST-EAST_GRID_DIMENSION"] = staggered_west_east_dim
    d.attrs["SOUTH-NORTH_GRID_DIMENSION"] = staggered_north_south_dim

    d.attrs["WEST-EAST_PATCH_END_UNSTAG"] = unstaggered_west_east_dim
    d.attrs["SOUTH-NORTH_PATCH_END_UNSTAG"] = unstaggered_north_south_dim

    # NOTE: I think these are deleted by `ncatted`
    d.attrs["WEST-EAST_PATCH_START_STAG"] = 1
    d.attrs["SOUTH-NORTH_PATCH_START_STAG"] = 1

    d.attrs["WEST-EAST_PATCH_END_STAG"] = staggered_west_east_dim
    d.attrs["SOUTH-NORTH_PATCH_END_STAG"] = staggered_north_south_dim

    d.attrs["i_parent_start"] = 1
    d.attrs["j_parent_start"] = 1

    d.attrs["i_parent_end"] = staggered_west_east_dim
    d.attrs["j_parent_end"] = staggered_north_south_dim

    # 'XLAT_M', 'XLAT_U', 'XLAT_V', 'XLAT_C'
    # 'XLONG_M', 'XLONG_U', 'XLONG_V', 'XLONG_C'
    def get_corners(a: npt.ArrayLike) -> Tuple[int, int, int, int]:
        # bottom left, top left, top right, bottom right
        return a[0, 0, 0], a[0, -1, 0], a[0, -1, -1], a[0, 0, -1]

    lat_m = get_corners(d.XLAT_M.values)
    lat_u = get_corners(d.XLAT_U.values)
    lat_v = get_corners(d.XLAT_V.values)

    # nwm.v2.1.6 geo_em file, XLAT_C and XLONG_C are not present
    try:
        lat_c = get_corners(d.XLAT_C.values)
    except AttributeError:
        warn_message = "XLAT_C variable not included in dataset. Estimating XLAT_C"
        warnings.warn(warn_message, RuntimeWarning)
        ec = estimate_geogrid_corners(d)
        lat_c = (ec.bottom_left[1], ec.top_left[1], ec.top_right[1], ec.bottom_right[1])

    long_m = get_corners(d.XLONG_M.values)
    long_u = get_corners(d.XLONG_U.values)
    long_v = get_corners(d.XLONG_V.values)

    try:
        long_c = get_corners(d.XLONG_C.values)
    except AttributeError:
        warn_message = "XLONG_C variable not included in dataset. Estimating XLONG_C"
        warnings.warn(warn_message, RuntimeWarning)
        ec = estimate_geogrid_corners(d)
        long_c = (
            ec.bottom_left[0],
            ec.top_left[0],
            ec.top_right[0],
            ec.bottom_right[0],
        )

    # corner lats from nwm.v2.1.6 geo_em_CONUS.nc file
    # 'XLAT_M'
    # 'XLAT_U'
    # 'XLAT_V'
    # 'XLAT_C'
    # 20.07781f, 52.87278f, 52.87278f, 20.07781f,
    # 20.07671f, 52.87075f, 52.87075f, 20.07671f,
    # 20.07371f, 52.87693f, 52.87693f, 20.07371f,
    # 20.07259f, 52.87489f, 52.87489f, 20.07259f

    # corner_lons
    # -118.1045f, -133.5073f, -60.49268f, -75.89551f,
    # -118.1089f, -133.5142f, -60.48578f, -75.89114f,
    # -118.1033f, -133.5107f, -60.48929f, -75.8967f,
    # -118.1077f, -133.5176f, -60.48242f, -75.89233f

    lat_corners = np.array(lat_m + lat_u + lat_v + lat_c, dtype="float32")
    long_corners = np.array(long_m + long_u + long_v + long_c, dtype="float32")

    d.attrs["corner_lons"] = lat_corners
    d.attrs["corner_lats"] = long_corners

    return d


def subset_wrf_hydro_nwm_geospatial_data_template_land_gis(
    ds: xr.Dataset, wrf_bb: SimpleBoundingBoxIndices
) -> xr.Dataset:
    # system(paste0("ncks -O -d x,", geo_w-1, ",", geo_e-1, " -d y,", geo_s-1, ",", geo_n-1, " ", geoSpatialFile, " ", subGeoSpatialFile))
    return ds.isel(
        x=slice(wrf_bb.left, wrf_bb.right + 1), y=slice(wrf_bb.bottom, wrf_bb.right + 1)
    )


def subset_hydro_tbl_2d(ds: xr.Dataset, wrf_bb: SimpleBoundingBoxIndices) -> xr.Dataset:
    # system(paste0("ncks -O -d west_east,", geo_w-1, ",", geo_e-1, " -d south_north,", geo_s-1, ",", geo_n-1, " ", fullHydro2dFile, " ", subHydro2dFile))
    return ds.isel(
        west_east=slice(wrf_bb.left, wrf_bb.right + 1),
        south_north=slice(wrf_bb.bottom, wrf_bb.right + 1),
    )


def subset_wrfinput(ds: xr.Dataset, wrf_bb: SimpleBoundingBoxIndices) -> xr.Dataset:
    # system(paste0("ncks -O -d west_east,", geo_w-1, ",", geo_e-1, " -d south_north,", geo_s-1, ",", geo_n-1, " ", fullWrfFile, " ", subWrfFile))
    # system(paste0("ncatted -h -a WEST-EAST_GRID_DIMENSION,global,o,l,", geo_e-geo_w+2, " ", subWrfFile))
    # system(paste0("ncatted -h -a SOUTH-NORTH_GRID_DIMENSION,global,o,l,", geo_n-geo_s+2, " ", subWrfFile))
    d = ds.isel(
        west_east=slice(wrf_bb.left, wrf_bb.right + 1),
        south_north=slice(wrf_bb.bottom, wrf_bb.right + 1),
    )
    # NOTE: not sure why this is +2, A.R. thought this should be +1.
    d.attrs["WEST-EAST_GRID_DIMENSION"] = wrf_bb.right - wrf_bb.left + 2
    d.attrs["SOUTH-NORTH_GRID_DIMENSION"] = wrf_bb.top - wrf_bb.bottom + 2
    return d


def subset_soil_veg_properties(
    ds: xr.Dataset, wrf_bb: SimpleBoundingBoxIndices
) -> xr.Dataset:
    # system(paste0("ncks -O -d west_east,", geo_w-1, ",", geo_e-1, " -d south_north,", geo_s-1, ",", geo_n-1, " ", fullSoilparmFile, " ", subSoilparmFile))
    return ds.isel(
        west_east=slice(wrf_bb.left, wrf_bb.right + 1),
        south_north=slice(wrf_bb.bottom, wrf_bb.right + 1),
    )


def subset_fulldom(ds: xr.Dataset, hydro_bb: SimpleBoundingBoxIndices) -> xr.Dataset:
    # system(paste0("ncks -O -d x,", hyd_w-1, ",", hyd_e-1, " -d y,", hyd_min-1, ",", hyd_max-1, " ", fullHydFile, " ", subHydFile))
    return ds.isel(
        x=slice(hydro_bb.left, hydro_bb.right + 1),
        y=slice(hydro_bb.bottom, hydro_bb.right + 1),
    )


def subset_spatialweights(
    ds: xr.Dataset, hydro_bb: SimpleBoundingBoxIndices
) -> xr.Dataset:
    # SpatWts <- read_wt_file(fullSpwtFile)

    # keepIdsPoly <-  dplyr::filter(SpatWts$data,
    #                      i_index >= hyd_w &
    #                      i_index <= hyd_e &
    #                      j_index >= hyd_s &
    #                      j_index <= hyd_n) %>%
    #   dplyr::group_by(IDmask) %>%
    #   dplyr::summarise(sumBas = sum(weight)) %>%
    #   dplyr::filter(sumBas > .999) %>%
    #   dplyr::pull(IDmask)

    # see subset_routelink
    # keepIds <- unique(c(keepIdsPoly, keepIdsLink))

    # subWts = subset_weights(SpatWts, keepIdsPoly, hyd_w, hyd_e, hyd_s, hyd_n)

    # fs::file_copy(fullSpwtFile, subSpwtFile, overwrite = TRUE)

    # system(paste0("ncks -O -d polyid,1,", nrow(subWts[[2]]),
    #                    " -d data,1,", nrow(subWts[[1]]), " ", subSpwtFile, " ",
    #                  subSpwtFile))

    # update_nc(subSpwtFile, subWts[[1]])
    # update_nc(subSpwtFile, subWts[[2]])
    idxs = np.nonzero(
        (ds.i_index.values >= hydro_bb.left)
        & (ds.i_index.values <= hydro_bb.right)
        & (ds.j_index.values >= hydro_bb.bottom)
        & (ds.i_index.values <= hydro_bb.top)
    )

    ds.isel(data=idxs).groupby("IDmask")
    ...


def subset_routelink():
    # rt_link = nc_to_df(fullRtlinkFile)

    # keepIdsLink = rt_link %>%
    #   dplyr::filter(
    #       lon >= min(sp_new_buff_nad83[,1]) &
    #       lon <= max(sp_new_buff_nad83[,1]) &
    #       lat >= min(sp_new_buff_nad83[,2]) &
    #       lat <= max(sp_new_buff_nad83[,2])) %>%
    #   dplyr::distinct(link) %>%
    #   dplyr::pull(link)

    # keepIds <- unique(c(keepIdsPoly, keepIdsLink))

    # subRtlink <- dplyr::filter(rt_link, link %in% keepIds) %>%
    # dplyr::mutate(to = ifelse(to %in% unique(link), to, 0))

    # # reorder the ascendingIndex if ascendingIndex exists in the variables
    # if ("ascendingIndex" %in% names(subRtlink)){
    #   subRtlink = dplyr::mutate(subRtlink, ascendingIndex = (rank(ascendingIndex) - 1))
    # }

    # #rwrfhydro::UpdateLinkFile(subRtlinkFile, subRtlink)
    # fs::file_copy(fullRtlinkFile, subRtlinkFile, overwrite = TRUE)

    # system(paste0("ncks -O -d feature_id,1,", nrow(subRtlink), " ",
    #               subRtlinkFile, " ", subRtlinkFile))

    # update_nc(path = subRtlinkFile, df = subRtlink)
    ...


def subset_gwbuckparm():
    # subGwbuck = nc_to_df(fullGwbuckFile) %>%
    #   dplyr::filter(ComID %in% keepIdsPoly) %>%
    #   dplyr::mutate(Basin = 1:n())

    # file.copy(fullGwbuckFile, subGwbuckFile, overwrite = TRUE)

    # system(paste0("ncks -O -d BasinDim,1,", nrow(subGwbuck),  " ",
    #               subGwbuckFile, " ", subGwbuckFile))

    # update_nc(path = subGwbuckFile, df = subGwbuck)
    ...
