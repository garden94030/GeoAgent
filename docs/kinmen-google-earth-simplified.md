# Kinmen Google Earth Simplified Workflow

This guide is the simpler Google Earth path for the Kinmen satellite imagery.
Use it when QGIS feels too complex and the immediate goal is visual inspection,
annotation, and presentation.

Google Earth is easier than QGIS for map viewing, placemarks, polygons, and
storytelling. QGIS is still better for NDVI/NDWI calculation, zonal statistics,
and reproducible quantitative analysis.

## Recommended Tool

Use **Google Earth Pro on desktop**.

Google Earth Pro is available for Mac, PC, and Linux and is the version meant
for more advanced desktop work. It can import and export GIS data and supports
historical imagery. Google also documents that Google Earth Pro can import TIFF
files, including GeoTIFF and compressed TIFF files.

Useful official references:

- Google Earth versions: https://www.google.com/earth/about/versions/
- Import map data in Google Earth Pro: https://support.google.com/earth/answer/176685
- Import GIS data tutorial: https://www.google.com/earth/outreach/learn/importing-geographic-information-systems-gis-data-in-google-earth/

## What Google Earth Can Do Well

Use Google Earth Pro for:

1. Opening GeoTIFF imagery as map overlays.
2. Toggling before/after layers.
3. Adjusting overlay transparency.
4. Adding placemarks, paths, and polygons.
5. Saving a KMZ project for sharing or presentation.
6. Exporting screenshots or map figures.

## What Google Earth Cannot Replace

Do not rely on Google Earth Pro for:

1. Calculating NDVI or NDWI from raw multispectral bands.
2. Running zonal statistics.
3. Producing rigorous area-change tables.
4. Managing large scientific raster workflows.
5. Reproducible academic analysis.

For these tasks, use QGIS or Python.

## About Ask Google Earth

Google has been adding Gemini capabilities to Google Earth and Google Earth AI.
As of Google's October 2025 update, some experimental capabilities were planned
for U.S. Google Earth Professional and Professional Advanced users, and higher
limits were announced for U.S. Google AI Pro and Ultra subscribers.

Treat `Ask Google Earth` as an optional AI helper, not as the main analysis
tool for this local SPOT-6 package. It may not be available to every account or
region, and it may not directly analyze your licensed local GeoTIFF files in the
same way QGIS does.

Official reference:

- Google Earth AI access update: https://blog.google/innovation-and-ai/technology/research/new-updates-and-more-access-to-google-earth-ai/

## Simplest Local Workflow

### Step 1: Open Google Earth Pro

On Mac:

1. Press `Command + Space`.
2. Search `Google Earth Pro`.
3. Open the app.

If it is not installed, download Google Earth Pro from:

```text
https://www.google.com/earth/about/versions/
```

### Step 2: Import One GeoTIFF

Start with one file only.

Recommended first choices:

| File | Why |
| --- | --- |
| `金門水域 正義使命.tif` | Main combined imagery |
| `NDVI_MERGE_NEW.tif` | Vegetation-index result |
| `NDWI_MERGE_NEW.tif` | Water-index result |

In Google Earth Pro:

1. Go to `File` > `Open`.
2. Select a `.tif` file.
3. If Google Earth asks how to handle a large image, choose one of:

| Option | Use When |
| --- | --- |
| `Scale` | You want a quick preview and can accept lower resolution |
| `Crop` | You only need one smaller area |
| `Create Super Overlay` | You want to view a large image at better detail |

For a first test, use `Scale`. If it works and you need more detail, import
again with `Create Super Overlay`.

### Step 3: Rename And Save The Overlay

After import:

1. Look at the `Places` panel on the left.
2. Rename the imported layer clearly, for example:

```text
Kinmen imagery - 2025 comparison
```

3. Drag it into `My Places` if needed.
4. Right-click the layer or folder.
5. Choose `Save Place As`.
6. Save as:

```text
kinmen_google_earth_view.kmz
```

### Step 4: Add Simple Markers

Use markers for places you want to discuss in the report.

1. Click the yellow pushpin icon.
2. Click the location on the map.
3. Name it, for example:

```text
port_01
```

4. Add a short note:

```text
Visible shoreline and water-signal comparison area.
```

5. Click `OK`.

### Step 5: Draw Simple Polygons

Use polygons to mark areas of interest.

1. Click the polygon icon.
2. Click points around the target area.
3. Name it, for example:

```text
shoreline_01
```

4. Use a transparent fill so the imagery remains visible.
5. Click `OK`.

Suggested first set:

| Name | Meaning |
| --- | --- |
| `port_01` | Port or pier area |
| `shoreline_01` | Shoreline comparison area |
| `island_01` | Island reference area |
| `water_01` | Open water reference area |
| `control_01` | Area expected to change little |

### Step 6: Export A Presentation Image

1. Adjust the view to the area of interest.
2. Turn on only the layers and markers you need.
3. Go to `File` > `Save` > `Save Image`.
4. Add or remove title, legend, and scale options as needed.
5. Save the image into:

```text
<KINMEN_DATA_DIR>/qgis_outputs/
```

## Best Combined Workflow

Use the tools this way:

| Task | Best Tool |
| --- | --- |
| Quick visual inspection | Google Earth Pro |
| Public basemap context | Google Earth Pro |
| Marking places for a report | Google Earth Pro |
| NDVI/NDWI calculation | QGIS or Python |
| Area statistics | QGIS |
| Final evidence table | QGIS, CSV, spreadsheet |
| Final story map or screenshot | Google Earth Pro |

## Practical Recommendation

For this Kinmen project:

1. Use Google Earth Pro first to inspect and mark obvious areas.
2. Save markers and polygons as KMZ.
3. Use QGIS only for the specific calculation steps that Google Earth cannot do.
4. Keep the original large satellite files out of GitHub.
5. Commit only notes, scripts, small derived tables, and publishable figures.

