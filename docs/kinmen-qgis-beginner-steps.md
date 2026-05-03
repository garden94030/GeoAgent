# Kinmen QGIS Beginner Steps

This guide starts after `金門水域.qgz` is already open in QGIS. It is written
for first-time QGIS users who need to inspect the Kinmen SPOT-6 imagery and
prepare basic before/after evidence.

Menu names below include English labels because QGIS may show either Chinese or
English depending on the local installation.

## Stage 1: Get Oriented In QGIS

First make sure the basic panels are visible:

1. Go to `View` > `Panels`.
2. Turn on `Layers`.
3. Turn on `Browser`.
4. If the map looks empty, right-click a visible raster layer and choose
   `Zoom to Layer`.

The most important panel is the `Layers` panel. It controls what appears on the
map. A checked box means the layer is visible. An unchecked box means the layer
is hidden.

If the project reports missing files, do not panic. Some saved layers may point
to temporary Windows paths. Use the local files inside `<KINMEN_DATA_DIR>`
instead.

## Stage 2: Know The Main Layers

Start with these layers:

| Layer Or File | Meaning | First Action |
| --- | --- | --- |
| `Google Satellite Hybrid` | Background reference map | Keep at bottom and use only as reference |
| `I2603173_MS_4bands.tif` or `I2603173_MS_4bands NEW.tif` | 2025-12-08 multispectral image | Use as pre-event image |
| `I2603175_MS_4bands.tif` or `I2603175_MS_4bands NEW.tif` | 2025-12-29 multispectral image | Use as post-event image |
| `NDVI_pre_I2603173-MS-UTM.bin` | 2025-12-08 vegetation index | Style as pseudocolor |
| `NDVI_post_I2603175-MS-UTM.bin` | 2025-12-29 vegetation index | Style as pseudocolor |
| `NDWI_pre_I2603173-MS-UTM.bin` | 2025-12-08 water index | Style as pseudocolor |
| `NDWI_post_I2603175-MS-UTM.bin` | 2025-12-29 water index | Style as pseudocolor |

Keep only one or two layers visible at a time while learning. Too many visible
layers makes QGIS feel confusing.

## Stage 3: Compare The Two Color Images

Use this to visually compare the scene before looking at index maps.

1. In the `Layers` panel, turn off most layers.
2. Turn on the 2025-12-08 color image.
3. Right-click it and choose `Zoom to Layer`.
4. Turn on the 2025-12-29 color image above it.
5. Toggle the 2025-12-29 layer on and off to compare before/after.

If the image looks too dark, too bright, or strangely colored:

1. Right-click the raster layer.
2. Choose `Properties`.
3. Go to `Symbology`.
4. Set render type to `Multiband color`.
5. Set channels:

| QGIS Channel | SPOT-6 Band |
| --- | --- |
| Red | Band 3 |
| Green | Band 2 |
| Blue | Band 1 |

6. Set contrast enhancement to `Stretch to MinMax`.
7. Use cumulative count cut around `2% - 98%` if available.
8. Click `Apply`, then `OK`.

This creates a natural-color view.

## Stage 4: Use Transparency For Before/After

Transparency helps you compare two images without constantly toggling.

1. Put the 2025-12-29 layer above the 2025-12-08 layer.
2. Right-click the 2025-12-29 layer.
3. Choose `Properties`.
4. Go to `Transparency`.
5. Set global opacity to around `50%`.
6. Click `Apply`.

Now the post-event image is partially transparent over the pre-event image.
Look for shoreline differences, bright new surfaces, water-color differences,
and unusual linear features.

## Stage 5: Style NDVI

NDVI is for vegetation and bare-ground interpretation.

1. Turn off the color image layers.
2. Turn on `NDVI_pre_I2603173-MS-UTM.bin`.
3. Right-click the NDVI layer.
4. Choose `Properties`.
5. Go to `Symbology`.
6. Set render type to `Singleband pseudocolor`.
7. Set value range approximately:

| Minimum | Maximum |
| ---: | ---: |
| `-0.2` | `0.8` |

8. Choose a red-yellow-green color ramp if available.
9. Click `Classify`.
10. Click `Apply`.

Interpretation:

| NDVI Value | Meaning |
| --- | --- |
| `< 0.0` | Water or shadow |
| `0.0 - 0.1` | Bare ground, paved surface, built surface |
| `0.1 - 0.3` | Sparse vegetation |
| `0.3 - 0.6` | Vegetation, grass, cropland |
| `> 0.6` | Dense vegetation |

Repeat the same style steps for `NDVI_post_I2603175-MS-UTM.bin`.

## Stage 6: Style NDWI

NDWI is for water and wet-surface interpretation.

1. Turn on `NDWI_pre_I2603173-MS-UTM.bin`.
2. Right-click the layer.
3. Choose `Properties`.
4. Go to `Symbology`.
5. Set render type to `Singleband pseudocolor`.
6. Set value range approximately:

| Minimum | Maximum |
| ---: | ---: |
| `-0.5` | `0.5` |

7. Choose a brown-to-blue or yellow-to-blue color ramp.
8. Click `Classify`.
9. Click `Apply`.

Interpretation:

| NDWI Value | Meaning |
| --- | --- |
| `> 0.3` | Strong water signal |
| `0.0 - 0.3` | Shallow water, wetland, mixed pixels |
| `< 0.0` | Land, vegetation, buildings, dry surfaces |

Repeat the same style steps for `NDWI_post_I2603175-MS-UTM.bin`.

## Stage 7: Make A Simple Change Map

If the pre/post NDVI or NDWI rasters are loaded, QGIS can calculate a change
layer.

For NDVI change:

1. Go to `Raster` > `Raster Calculator`.
2. Build this expression, using the exact layer names shown in your QGIS list:

```text
"NDVI_post_I2603175-MS-UTM@1" - "NDVI_pre_I2603173-MS-UTM@1"
```

3. Set output file to something like:

```text
<KINMEN_DATA_DIR>/output_analysis/NDVI_change_qgis.tif
```

4. Click `OK` or `Run`.

For NDWI change:

```text
"NDWI_post_I2603175-MS-UTM@1" - "NDWI_pre_I2603173-MS-UTM@1"
```

Suggested output:

```text
<KINMEN_DATA_DIR>/output_analysis/NDWI_change_qgis.tif
```

Style change layers with `Singleband pseudocolor`:

| Change Value | Meaning |
| --- | --- |
| Negative | Decrease after 2025-12-29 minus 2025-12-08 |
| Around `0` | Little or no change |
| Positive | Increase after 2025-12-29 minus 2025-12-08 |

For NDVI, strong negative areas may indicate vegetation loss or new bare
surface. For NDWI, strong positive or negative areas may indicate water-signal
change, but tide and turbidity must be considered.

## Stage 8: Mark Areas Of Interest

Do this when you see suspicious or important change areas.

1. Go to `Layer` > `Create Layer` > `New GeoPackage Layer`.
2. Save it as:

```text
<KINMEN_DATA_DIR>/kinmen_analysis_roi.gpkg
```

3. Geometry type: `Polygon`.
4. CRS: use the project CRS or the raster CRS. Do not change it unless needed.
5. Add fields:

| Field Name | Type | Purpose |
| --- | --- | --- |
| `name` | Text | Area name |
| `type` | Text | Port, shoreline, island, control area, etc. |
| `note` | Text | Why it matters |

6. Click `OK`.
7. Turn on editing with the pencil icon.
8. Use `Add Polygon Feature`.
9. Draw a polygon around one area of interest.
10. Fill in `name`, `type`, and `note`.
11. Save edits.

Start with 3 to 5 areas only:

1. One obvious shoreline or port area.
2. One island area.
3. One urban/built area.
4. One water area.
5. One control area that should not change much.

## Stage 9: Get Statistics For Each Area

Use zonal statistics to turn map interpretation into numbers.

1. Open `Processing` > `Toolbox`.
2. Search for `Zonal statistics`.
3. Input polygon layer: `kinmen_analysis_roi`.
4. Raster layer: choose one NDVI or NDWI raster.
5. Statistics: select at least `mean`, `min`, `max`, and `standard deviation`.
6. Prefix: use a short name such as `ndvi_pre_`.
7. Run.

Repeat for:

| Raster | Suggested Prefix |
| --- | --- |
| `NDVI_pre_I2603173-MS-UTM.bin` | `ndvi_pre_` |
| `NDVI_post_I2603175-MS-UTM.bin` | `ndvi_post_` |
| `NDWI_pre_I2603173-MS-UTM.bin` | `ndwi_pre_` |
| `NDWI_post_I2603175-MS-UTM.bin` | `ndwi_post_` |

Open the attribute table of the ROI layer to see the new statistics columns.

## Stage 10: Export A Map For The Report

1. Set the map view to the area you want.
2. Turn on only the layers needed for the figure.
3. Go to `Project` > `New Print Layout`.
4. Give it a name, for example `Kinmen_NDVI_Change`.
5. In the layout window, choose `Add Map`.
6. Drag a rectangle to place the map.
7. Add title, legend, scale bar, and north arrow if needed.
8. Export using `Layout` > `Export as Image` or `Export as PDF`.

Use clear titles:

| Figure | Suggested Title |
| --- | --- |
| Natural color before/after | Kinmen SPOT-6 Before/After Comparison |
| NDVI | Kinmen Vegetation Index Change |
| NDWI | Kinmen Water Index Change |
| ROI table | Region-Based NDVI/NDWI Statistics |

## Beginner Safety Rules

Do not overwrite the original satellite data. Save new outputs into
`output_analysis` or a new folder such as `qgis_outputs`.

Keep interpretation cautious:

- NDVI shows vegetation or surface-cover change, not intent by itself.
- NDWI shows water-signal change, not vessel activity by itself.
- Tide, turbidity, haze, shadow, sun angle, seasonal vegetation, and image
  alignment can all affect results.
- Strong claims should be supported by additional dates or independent sources.

## First Session Goal

For the first QGIS session, finish only this checklist:

1. Open `金門水域.qgz`.
2. Turn layers on/off confidently.
3. Display the 2025-12-08 and 2025-12-29 color images.
4. Style NDVI pre/post.
5. Style NDWI pre/post.
6. Export one screenshot or map image.

After this, move to ROI polygons and zonal statistics.

