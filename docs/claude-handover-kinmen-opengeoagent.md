# Claude Handover: Kinmen OpenGeoAgent QGIS Analysis

This handover is for continuing Justin's Kinmen satellite imagery analysis in
QGIS with OpenGeoAgent. It records the current local setup, code fixes,
research goal, data inventory, known caveats, and recommended next steps.

Current date of handover: 2026-05-03.

## User Context

Justin recently moved from Windows to macOS and is still learning Terminal and
QGIS. Explanations should be step-by-step, concrete, and written in Traditional
Chinese unless Justin asks otherwise.

Important collaboration preference from Justin:

- After each meaningful work segment, sync updates to GitHub.
- Do not commit the licensed or large satellite imagery files.
- Commit documentation, code fixes, and workflow notes only.

## Repository State

Local repository:

```text
/Users/justin/Library/CloudStorage/GoogleDrive-jhihsiang94030@gmail.com/我的雲端硬碟/GeoAgent/GeoAgent
```

GitHub fork:

```text
https://github.com/garden94030/GeoAgent.git
```

Remote setup:

```text
origin   https://github.com/garden94030/GeoAgent.git
upstream https://github.com/opengeos/GeoAgent.git
```

Current branch:

```text
main
```

Latest commits already pushed to `origin/main`:

```text
231c2de Ensure QGIS chat worker applies dependency shim
9df7e37 Fix macOS QGIS typing extensions dependency clash
c7f81a5 Load editable GeoAgent install from QGIS plugin venv
5940ecd Fix macOS QGIS dependency installer Python detection
e51d14a Add Kinmen Google Earth workflow
f30ad0f Add Kinmen ROI zonal statistics guide
97ce7be Add Kinmen QGIS beginner steps
05d4067 Add Kinmen satellite analysis workflow
```

Before editing, always check:

```bash
git status --short --branch
```

After a meaningful update:

```bash
git add <changed-files>
git commit -m "<clear message>"
git push origin main
```

## QGIS And OpenGeoAgent Current Status

QGIS is installed on macOS:

```text
/Applications/QGIS.app
```

OpenGeoAgent QGIS plugin is installed under:

```text
/Users/justin/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/open_geoagent
```

OpenGeoAgent dependency venv:

```text
/Users/justin/.open_geoagent/venv_py3.12
```

OpenGeoAgent is now working inside QGIS. Justin successfully tested:

```text
請列出目前 QGIS 專案裡的圖層名稱
```

OpenGeoAgent answered with the current project layers and used:

```text
Tool: list_project_layers
Elapsed: 10.52s
```

This confirms the main QGIS chat + project inspection path is functional.

## Important Fixed QGIS Plugin Issues

### 1. QGIS Python Interpreter Detection

Original problem:

QGIS showed a red error similar to:

```text
無效的資料來源:
/import sys; sys.path = ["/Users/justin/.cache/uv/.tmp..."] + sys.path;
from python.get_interpreter_info import main; main()
不是有效或被識別的資料來源。
```

Root cause:

The dependency installer treated:

```text
/Applications/QGIS.app/Contents/MacOS/QGIS
```

as if it were the Python interpreter. QGIS then interpreted a Python probe
snippet as a map data source.

Fix:

`qgis_geoagent/open_geoagent/deps_manager.py` now detects the actual macOS QGIS
Python binary:

```text
/Applications/QGIS.app/Contents/MacOS/python3.12
```

and sets:

```text
PYTHONHOME=/Applications/QGIS.app/Contents/Frameworks
```

for subprocess calls.

Commit:

```text
5940ecd Fix macOS QGIS dependency installer Python detection
```

### 2. Editable GeoAgent Install Not Found

Original problem:

Most provider packages installed, but:

```text
GeoAgent[providers]>=1.4.1
```

still showed `Not installed`.

Root cause:

The plugin used `sys.path.insert()` to add the venv. Editable installs rely on
`.pth` files, and those are processed by `site.addsitedir()`, not by a plain
path insert.

Fix:

`ensure_venv_packages_available()` now uses:

```python
site.addsitedir(site_packages)
```

Commit:

```text
c7f81a5 Load editable GeoAgent install from QGIS plugin venv
```

### 3. `typing_extensions.Sentinel` Import Failure

Original problem:

Chat jobs failed with:

```text
ImportError: cannot import name 'Sentinel' from 'typing_extensions'
(/Applications/QGIS.app/Contents/Frameworks/lib/python3.12/site-packages/typing_extensions.py)
```

Root cause:

QGIS bundles an older `typing_extensions.py` that does not include `Sentinel`.
`strands` imports `pydantic`, and `pydantic_core` expects `Sentinel`.

Naive fix that must not be repeated:

Do not simply put the entire OpenGeoAgent venv before QGIS's own
`site-packages` on macOS. macOS QGIS uses library validation. If the venv's
native extension wheels are imported inside the signed QGIS process, QGIS may
fail with code-signing errors such as:

```text
code signature ... not valid for use in process:
mapping process and mapped file (non-platform) have different Team IDs
```

Correct fix:

On macOS QGIS, keep QGIS's signed native wheels such as `pydantic_core`, but
load the venv's newer pure-Python `typing_extensions.py`.

Files changed:

```text
qgis_geoagent/open_geoagent/deps_manager.py
qgis_geoagent/open_geoagent/dialogs/chat_dock.py
qgis_geoagent/open_geoagent/dialogs/settings_dock.py
qgis_geoagent/tests/test_startup_performance.py
qgis_geoagent/tests/test_whitebox_integration.py
qgis_geoagent/tests/test_settings_diagnostics.py
```

Commits:

```text
9df7e37 Fix macOS QGIS typing extensions dependency clash
231c2de Ensure QGIS chat worker applies dependency shim
```

The second commit is important. The first fix worked for dependency checking,
but the actual chat worker still needed to call the dependency shim immediately
before importing `geoagent`.

Verification command:

```bash
PYTHONHOME=/Applications/QGIS.app/Contents/Frameworks \
PYTHONPATH="/Applications/QGIS.app/Contents/Resources/python3.11/site-packages:$HOME/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins" \
/Applications/QGIS.app/Contents/MacOS/python3.12 - <<'PY'
import typing_extensions
print('before:', typing_extensions.__file__, hasattr(typing_extensions, 'Sentinel'))
from open_geoagent import deps_manager
deps_manager.ensure_venv_packages_available()
import typing_extensions as after_typing
print('after:', after_typing.__file__, hasattr(after_typing, 'Sentinel'))
from geoagent import GeoAgentConfig
print('GeoAgentConfig import: OK')
PY
```

Expected result:

```text
before: /Applications/QGIS.app/.../typing_extensions.py False
after: /Users/justin/.open_geoagent/venv_py3.12/.../typing_extensions.py True
GeoAgentConfig import: OK
```

Non-fatal warning that may appear:

```text
Failed to import fsevents. Fall back to kqueue
```

This warning is not the current blocker.

## Reinstall The QGIS Plugin After Code Changes

When changing the QGIS plugin code, reinstall it:

```bash
cd "/Users/justin/Library/CloudStorage/GoogleDrive-jhihsiang94030@gmail.com/我的雲端硬碟/GeoAgent/GeoAgent"
python3 qgis_geoagent/install.py
find "$HOME/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/open_geoagent" -name '__pycache__' -type d -prune -exec rm -rf {} +
```

Then Justin must fully quit and reopen QGIS:

```text
QGIS > Quit QGIS
```

or:

```text
Command + Q
```

Closing only the project window is not enough.

## Dependency Status

The plugin dependency status was verified from QGIS Python:

```text
Core Providers missing: []
All missing: []
```

Important advice:

- For normal OpenGeoAgent chat, use `Core Providers`.
- Do not repeatedly press `Install Dependencies` unless there is a real missing
  package.
- The `All` set includes optional packages such as Whitebox, Earth Engine,
  geemap, STAC, and Planetary Computer. These are useful later but not required
  for the Kinmen project inspection workflow.

## Current QGIS Project Layers

Justin successfully asked OpenGeoAgent to list project layers. The project
currently includes:

```text
Google Satellite
Google Satellite Hybrid
I2603172-PAN-UTM.1.bsq
I2603173_MS_4bands NEW
I2603173-MS-UTM.1.bsq
I2603173-MS-UTM.1.bsq
I2603173-MS-UTM.2.bsq
I2603173-MS-UTM.2.bsq
I2603173-MS-UTM.3.bsq
I2603173-MS-UTM.3.bsq
I2603173-MS-UTM.4.bsq
I2603174-PAN-UTM.1.bsq
I2603175-MS-UTM.1.bsq
I2603175-MS-UTM.2.bsq
I2603175-MS-UTM.3.bsq
I2603175-MS-UTM.4.bsq
NDVI_MERGE_NEW
NDVI_post_I2603175-MS-UTM
NDVI_post_I2603175-MS-UTM
NDVI_pre_I2603173-MS-UTM
NDVI_pre_I2603173-MS-UTM
NDWI_MERGE_NEW
NDWI_post_I2603175-MS-UTM
NDWI_post_I2603175-MS-UTM
NDWI_pre_I2603173-MS-UTM
NDWI_pre_I2603173-MS-UTM
12603175_MS_4bands NEW
合併
虛擬
金門水域 正義使命
```

There are duplicated layer names. Do not assume every duplicate is redundant
until checking each layer source path in QGIS layer properties.

## Local Satellite Data Path

Main local imagery folder:

```text
/Users/justin/Library/CloudStorage/GoogleDrive-jhihsiang94030@gmail.com/我的雲端硬碟/2026年_委託研究案_中共對周邊國家灰區侵擾暨各國之反制對兩岸關係的影響_backup/2026年委託研究/中央大學太空及遙測中心 金門衛星影像
```

Important files:

```text
金門水域.qgz
金門水域 正義使命.tif
金門水域 正義使命.tif.aux.xml
金門水域 圖層.qlr
I2603172-PAN-UTM.1.bsq
I2603173-MS-UTM.1.bsq
I2603173-MS-UTM.2.bsq
I2603173-MS-UTM.3.bsq
I2603173-MS-UTM.4.bsq
I2603174-PAN-UTM.1.bsq
I2603175-MS-UTM.1.bsq
I2603175-MS-UTM.2.bsq
I2603175-MS-UTM.3.bsq
I2603175-MS-UTM.4.bsq
NDVI_MERGE_NEW.tif
NDWI_MERGE_NEW.tif
ndvi_ndwi_analysis.py
merge_bands_to_color.py
NDVI_NDWI_Explanation_Report.md
NDVI_NDWI_Explanation_Report  MORE　DETAIL.md
```

Quick-look PNG files include:

```text
CSR_A0033564_SP6H1M_20251208.png
CSR_A0033565_SP6H1P_20251208.png
CSR_A0033742_SP6H1M_20251229.png
CSR_A0033743_SP6H1P_20251229.png
```

Do not commit these data files to GitHub. They are large and may be licensed.

## Imagery Dates And Roles

Existing documentation identifies two main dates:

```text
2025-12-08: pre-event / control date
2025-12-29: post-event / comparison date
```

Approximate file mapping:

```text
2025-12-08 multispectral: I2603173 / CSR_A0033564_SP6H1M_20251208
2025-12-08 panchromatic:  I2603172 / CSR_A0033565_SP6H1P_20251208
2025-12-29 multispectral: I2603175 / CSR_A0033742_SP6H1M_20251229
2025-12-29 panchromatic:  I2603174 / CSR_A0033743_SP6H1P_20251229
```

The working assumption from earlier docs:

- SPOT-6 multispectral imagery has about 6 m resolution.
- SPOT-6 panchromatic imagery has about 1.5 m resolution.
- Multispectral bands:
  - Band 1: Blue
  - Band 2: Green
  - Band 3: Red
  - Band 4: Near infrared

Use the panchromatic image for visual interpretation of vessel-like objects
when possible. Use multispectral and NDVI/NDWI for broader land-water and
surface-change interpretation.

## Existing Kinmen Documentation In Repo

Relevant docs already written:

```text
docs/kinmen-satellite-analysis.md
docs/kinmen-qgis-beginner-steps.md
docs/kinmen-qgis-roi-zonal-statistics.md
docs/kinmen-google-earth-simplified.md
```

Read these before writing new workflow instructions, to avoid repeating or
contradicting them.

## User's Research Goal

Justin wants to analyze Kinmen waters before and after the "正義使命" exercise
using the two satellite image dates provided by National Central University.

Main questions:

1. Distribution of coast guard vessels and surface vessels.
2. Important nearby changes before and after the exercise.
3. How to explain environmental or surface-condition changes around the
   exercise period.

The output should support a research report on gray-zone activity and
countermeasures, but the analysis must distinguish observed image changes from
causal claims.

## Recommended Analysis Strategy

Use three parallel tracks:

1. Vessel and surface-object interpretation.
2. Water and shoreline environmental change.
3. Land/nearshore surface change.

Do not start with heavy automation. Start with manual interpretation and
structured QGIS layers. The image resolution and water clutter make purely
automatic vessel detection risky without training data and quality control.

## Track 1: Vessel And Surface-Object Distribution

Best data:

- Panchromatic layers: `I2603172-PAN-UTM.1.bsq` and `I2603174-PAN-UTM.1.bsq`
- Color composites: `I2603173_MS_4bands NEW`, `12603175_MS_4bands NEW`, or
  `金門水域 正義使命`
- Google Satellite should be used only as a background reference, not as
  primary evidence.

Create a point layer:

```text
qgis_outputs/kinmen_vessel_points.gpkg
```

Layer name:

```text
kinmen_vessel_points
```

Geometry:

```text
Point
```

Suggested fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `obs_date` | Text | `2025-12-08` or `2025-12-29` |
| `phase` | Text | `pre` or `post` |
| `obj_type` | Text | `large_vessel`, `small_vessel`, `wake`, `buoy`, `uncertain` |
| `confidence` | Text | `high`, `medium`, `low` |
| `zone` | Text | water zone or nearby feature |
| `length_est` | Decimal | optional approximate visible length in meters |
| `note` | Text | why the object was marked |
| `image_layer` | Text | source layer used |

Suggested manual interpretation rules:

- Mark only objects visible on the same date's satellite imagery.
- Use `high` confidence only when object shape, wake, shadow, and context are
  consistent with a vessel.
- Use `uncertain` for wave crests, docks, buoys, fish-farm structures, or
  artifacts.
- Do not label anything as "海警船" from imagery alone unless there is
  independent evidence. Use "suspected vessel" or "vessel-like object" unless
  confirmed by external reporting/AIS/official source.
- Compare counts by zone, not just total counts.

Suggested zones:

```text
open_water
near_bridge
near_port
near_shoreline
between_islands
main_channel
control_water
```

Possible outputs:

- Vessel point map for 2025-12-08.
- Vessel point map for 2025-12-29.
- Before/after density or count by zone.
- Table of high/medium/low-confidence vessel-like objects.
- Short caveat paragraph about resolution and identification limits.

## Track 2: Water And Shoreline Environmental Change

Use NDWI and visual water color/turbidity interpretation.

Relevant layers:

```text
NDWI_pre_I2603173-MS-UTM
NDWI_post_I2603175-MS-UTM
NDWI_MERGE_NEW
```

Core questions:

- Did the water signal become stronger or weaker in specific zones?
- Are there visible sediment plumes, turbidity changes, wakes, disturbed water,
  or shallow-water exposure?
- Are changes concentrated near ports, channels, bridges, or coastlines?

Create or reuse ROI polygons:

```text
qgis_outputs/kinmen_analysis_roi.gpkg
```

Suggested ROI types:

```text
port
shoreline
bridge/channel
open_water
shallow_water
control_water
island_coast
```

For each ROI, run zonal statistics on:

```text
NDWI_pre_I2603173-MS-UTM
NDWI_post_I2603175-MS-UTM
```

Create a field:

```text
ndwi_delta = ndwi_post_mean - ndwi_pre_mean
```

Interpret carefully:

- Positive `ndwi_delta`: stronger water signal.
- Negative `ndwi_delta`: weaker water signal or more mixed/non-water signal.
- Possible causes include tide, turbidity, sun angle, haze, shallow-water
  exposure, waves, sediment, sensor differences, or real activity-related
  disturbance.

Do not claim "military exercise caused NDWI change" from NDWI alone.

## Track 3: Land/Nearshore Surface Change

Use NDVI and color composites.

Relevant layers:

```text
NDVI_pre_I2603173-MS-UTM
NDVI_post_I2603175-MS-UTM
NDVI_MERGE_NEW
```

Core questions:

- Did vegetation signal change near coastal areas?
- Are there new bare-ground, construction, staging, shoreline, or land-use
  changes?
- Are changes localized around ports, roads, beaches, or military-relevant
  infrastructure?

Run zonal statistics on:

```text
NDVI_pre_I2603173-MS-UTM
NDVI_post_I2603175-MS-UTM
```

Create:

```text
ndvi_delta = ndvi_post_mean - ndvi_pre_mean
```

Interpret carefully:

- Positive `ndvi_delta`: stronger vegetation signal or greener surface.
- Negative `ndvi_delta`: weaker vegetation signal, more bare/built/shadow/water
  signal, or seasonal/sensor effects.

## Suggested QGIS Work Products

Create a `qgis_outputs` folder inside the imagery folder for analysis outputs:

```text
<KINMEN_DATA_DIR>/qgis_outputs
```

Recommended outputs:

```text
kinmen_vessel_points.gpkg
kinmen_analysis_roi.gpkg
kinmen_change_hotspots.gpkg
kinmen_vessel_counts_by_zone.csv
kinmen_roi_ndvi_ndwi_change.csv
maps/01_before_after_overview.png
maps/02_vessel_points_pre_post.png
maps/03_ndwi_change_by_roi.png
maps/04_ndvi_change_by_roi.png
maps/05_interpretation_hotspots.png
```

Suggested report structure:

1. Data source and dates.
2. Methodology.
3. Vessel-like object distribution.
4. Water and shoreline change.
5. Land/nearshore change.
6. Interpretation limits.
7. Appendix with ROI table and map exports.

## Recommended OpenGeoAgent Prompts For Justin

Start with inspect-only prompts:

```text
請列出目前 QGIS 專案中每個圖層的名稱、資料來源路徑、CRS、像元大小或幾何類型，並整理成表格。
```

```text
請根據目前 QGIS 專案圖層，判斷哪些是 2025-12-08 前期影像、哪些是 2025-12-29 後期影像，並說明你的判斷依據。
```

```text
請檢查目前專案中 NDVI 與 NDWI 圖層是否有前期與後期對應，並列出可以用來做差異分析的圖層配對。
```

When Justin is ready to create layers, tell him to change OpenGeoAgent
permission from `Inspect only` to an execution-capable profile, then use:

```text
請幫我建立一個 GeoPackage 點圖層 kinmen_vessel_points，欄位包含 obs_date、phase、obj_type、confidence、zone、length_est、note、image_layer，用來人工標記船隻或疑似水面目標。
```

```text
請幫我建立一個 GeoPackage 多邊形圖層 kinmen_analysis_roi，欄位包含 name、roi_type、phase_scope、note，用來畫港口、航道、近岸、水域控制區等分析區。
```

For interpretation:

```text
請根據我選取的 ROI，說明 NDWI 前後變化應如何解讀，並列出不能直接推論為演習造成的限制因素。
```

```text
請根據 vessel_points 圖層，統計 2025-12-08 與 2025-12-29 各 zone 的 high/medium/low confidence 目標數量，並產生一段研究報告用的文字。
```

## Important Analytic Caveats

This is the most important part for research integrity.

Vessel identification caveats:

- SPOT panchromatic imagery may show larger vessels, wakes, and bright objects,
  but small boats can be difficult or impossible to identify reliably.
- A bright line or spot on water may be a wave, wake, buoy, fish-farm structure,
  pier, artifact, or cloud/glint effect.
- The imagery alone usually cannot prove that a vessel is "海警船".
- Use terms such as "疑似船隻", "水面目標", or "vessel-like object" unless
  confirmed externally.

Before/after comparison caveats:

- The two dates are 2025-12-08 and 2025-12-29.
- Tide level can change shoreline and shallow-water visibility.
- Sun angle, haze, wave state, turbidity, cloud shadow, and sensor processing
  can change spectral values.
- Image alignment differences can create false edge changes.
- Whole-scene averages are less useful than ROI-based comparisons.

Causal interpretation caveat:

- Satellite imagery can show "what changed".
- It rarely proves "why it changed" by itself.
- Link changes to "正義使命" only as a hypothesis unless supported by
  additional evidence such as official notices, AIS, news reports, local
  observations, or more dates.

## Suggested Immediate Next Step For Claude

If Claude is taking over, do this next:

1. Ask Justin whether QGIS is currently open and whether he wants to start with
   vessel marking or ROI/NDWI analysis.
2. If starting with vessel marking, guide him to create
   `kinmen_vessel_points.gpkg` and mark 10 to 20 obvious high-confidence
   examples first.
3. If starting with environmental change, guide him to create 5 to 8 ROI
   polygons and run zonal statistics on NDWI/NDVI.
4. Keep every step beginner-friendly, with exact QGIS menu names.
5. Commit any new documentation or scripts to GitHub after each completed
   segment.

Recommended first instruction to Justin:

```text
我們先不要一次做全部。第一步先建立兩個分析圖層：
1. kinmen_vessel_points：用點標疑似船隻和水面目標。
2. kinmen_analysis_roi：用多邊形框出港口、航道、近岸、開放水域和控制區。

完成這兩個圖層後，再做前後期統計與地圖輸出。
```

## Known Test Note

Targeted tests for the macOS QGIS dependency fix passed:

```text
13 passed
```

A broader local test run encountered one unrelated existing failure:

```text
test_chat_worker_uses_stac_factory
```

The failure concerned `auto_approve_tools` behavior in STAC mode and was not
related to the `typing_extensions.Sentinel` import fix. Do not treat it as the
current QGIS chat blocker unless Justin asks to work on STAC mode.

## Tone And Support Guidance For Claude

Justin is actively learning QGIS and macOS Terminal. Prefer:

- Clear steps.
- One screen or one task at a time.
- Traditional Chinese.
- Explain what to click in QGIS.
- Avoid assuming Terminal fluency.
- Avoid overclaiming satellite interpretation.
- When using Terminal commands, quote long paths because the Google Drive path
  contains spaces and Chinese characters.

