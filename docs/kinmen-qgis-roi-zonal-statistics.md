# Kinmen QGIS ROI And Zonal Statistics

This guide continues after the beginner QGIS setup. The goal is to draw a few
research areas, then calculate NDVI and NDWI statistics for each area.

In QGIS, these research areas are usually called ROI, AOI, or polygons. ROI
means region of interest.

## Goal

By the end of this step, you should have:

1. A new polygon layer named `kinmen_analysis_roi.gpkg`.
2. Several manually drawn research areas.
3. A table with pre-event and post-event NDVI/NDWI statistics for each area.
4. A small evidence table that can support a research report.

## Recommended ROI Types

Start with only 5 to 8 polygons. Keep them simple.

| ROI Type | Why It Matters |
| --- | --- |
| Port or pier | Useful for observing shoreline and vessel-adjacent surface change. |
| Shoreline | Useful for detecting waterline, shallow-water, or beach changes. |
| Island | Useful for stable land/water comparison. |
| Urban/built area | Useful as a built-surface reference. |
| Vegetated area | Useful for NDVI comparison. |
| Open water | Useful for NDWI comparison. |
| Control area | An area expected to change little, used as a sanity check. |

Do not draw too many polygons at the beginning. The first pass is for learning
the workflow and checking whether the statistics make sense.

## Create A New ROI Layer

1. In QGIS, go to `Layer` > `Create Layer` > `New GeoPackage Layer`.
2. Click the `...` button beside Database.
3. Save it inside the local imagery folder:

```text
<KINMEN_DATA_DIR>/qgis_outputs/kinmen_analysis_roi.gpkg
```

If `qgis_outputs` does not exist, create that folder in Finder first.

4. Layer name:

```text
kinmen_analysis_roi
```

5. Geometry type:

```text
Polygon
```

6. CRS: use the project CRS or the raster CRS. If unsure, keep the default that
   QGIS suggests.
7. Add these fields:

| Field Name | Type | Length | Purpose |
| --- | --- | ---: | --- |
| `name` | Text | 80 | Short ROI name |
| `roi_type` | Text | 40 | Port, shoreline, water, vegetation, control |
| `note` | Text | 200 | Why this area is selected |

8. Click `OK`.

The new layer should appear in the `Layers` panel.

## Draw The First Polygon

1. Click the `kinmen_analysis_roi` layer in the `Layers` panel.
2. Click the pencil icon to start editing.
3. Click `Add Polygon Feature`.
4. Click points around your first area of interest.
5. Right-click to finish the polygon.
6. Fill the attribute form:

| Field | Example |
| --- | --- |
| `name` | `port_01` |
| `roi_type` | `port` |
| `note` | `Visible shoreline and water-pattern comparison area` |

7. Click `OK`.
8. Click the save edits icon.

Repeat this for several areas. Suggested first set:

| Name | Type |
| --- | --- |
| `port_01` | `port` |
| `shoreline_01` | `shoreline` |
| `island_01` | `island` |
| `urban_01` | `built` |
| `vegetation_01` | `vegetation` |
| `water_01` | `water` |
| `control_01` | `control` |

## Drawing Tips

For the first round:

- Draw medium-size polygons, not tiny shapes.
- Avoid clouds, cloud shadows, and image edge artifacts.
- Avoid polygons that mix too much land and water unless that is intentional.
- Put each ROI fully inside the area covered by both dates.
- Use a control area that should not have changed much.

If a polygon is wrong:

1. Select the ROI layer.
2. Turn on editing.
3. Use the select tool to select the polygon.
4. Press Delete.
5. Save edits.

## Run Zonal Statistics

Zonal statistics calculates raster values inside each polygon. This is how you
turn NDVI and NDWI maps into a table.

1. Go to `Processing` > `Toolbox`.
2. Search for `Zonal statistics`.
3. Open `Zonal statistics`.
4. Set input polygon layer:

```text
kinmen_analysis_roi
```

5. Choose the first raster layer:

```text
NDVI_pre_I2603173-MS-UTM.bin
```

6. Select these statistics:

```text
Mean
Minimum
Maximum
Standard deviation
```

7. Set output column prefix:

```text
ndvi_pre_
```

8. Run the tool.

Repeat the tool for each raster:

| Raster Layer | Prefix |
| --- | --- |
| `NDVI_pre_I2603173-MS-UTM.bin` | `ndvi_pre_` |
| `NDVI_post_I2603175-MS-UTM.bin` | `ndvi_post_` |
| `NDWI_pre_I2603173-MS-UTM.bin` | `ndwi_pre_` |
| `NDWI_post_I2603175-MS-UTM.bin` | `ndwi_post_` |

After each run, open the ROI layer attribute table. New columns should appear.

## Add Change Columns

After zonal statistics, calculate change values.

1. Right-click `kinmen_analysis_roi`.
2. Choose `Open Attribute Table`.
3. Click the field calculator icon.
4. Create a new decimal field:

```text
ndvi_delta
```

5. Expression:

```text
"ndvi_post_mean" - "ndvi_pre_mean"
```

6. Create another decimal field:

```text
ndwi_delta
```

7. Expression:

```text
"ndwi_post_mean" - "ndwi_pre_mean"
```

If your column names are slightly different, pick the matching `mean` columns
from the field list in the expression builder.

## Interpret The ROI Table

Use these simple rules:

| Metric | Positive Change | Negative Change |
| --- | --- | --- |
| `ndvi_delta` | More vegetation signal or greener surface | Less vegetation signal or more bare/built/shadow/water signal |
| `ndwi_delta` | Stronger water signal | Weaker water signal or more land/built/mixed surface signal |

Important: these values show spectral change, not cause. For example, NDWI may
change because of tide, turbidity, sun angle, haze, or shallow-water exposure.

## Export The ROI Table

To save the table for a report:

1. Right-click `kinmen_analysis_roi`.
2. Choose `Export` > `Save Features As`.
3. Format:

```text
Comma Separated Value [CSV]
```

4. Save as:

```text
<KINMEN_DATA_DIR>/qgis_outputs/kinmen_roi_statistics.csv
```

5. Click `OK`.

This CSV can be opened in Excel, Numbers, Google Sheets, or Python.

## Suggested Report Table

Create a report table like this:

| ROI | Type | NDVI Pre Mean | NDVI Post Mean | NDVI Change | NDWI Pre Mean | NDWI Post Mean | NDWI Change | Interpretation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `port_01` | port | | | | | | | Check shoreline and water signal |
| `shoreline_01` | shoreline | | | | | | | Check waterline and shallow-water variation |
| `vegetation_01` | vegetation | | | | | | | Check vegetation condition |
| `control_01` | control | | | | | | | Should remain relatively stable |

## Quality Checks

Before using the numbers in a report:

1. Confirm every ROI is inside both dates of imagery.
2. Confirm the pre and post rasters visually overlap.
3. Confirm no ROI is dominated by cloud or cloud shadow.
4. Compare ROI statistics against the visible map.
5. Use the control ROI to judge whether broad image conditions changed.

If control areas also show large changes, be careful: the change may come from
image conditions rather than real ground change.

