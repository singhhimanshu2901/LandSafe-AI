def compute_terrain_features(location_row):
    features = {
        "terrain_elevation": location_row.get("elevation"),
        "terrain_slope": location_row.get("slope"),
        # TODO: aspect and curvature require DEM raster integration - not yet available
        "terrain_aspect": None,
        "terrain_curvature": None,
    }
    return features
