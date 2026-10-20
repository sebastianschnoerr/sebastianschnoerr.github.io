const infoElement = document.querySelector("#info");
const defaultInfo =
  "Klicken Sie auf ein Gebäude, um sich dessen Attribute anzeigen zu lassen.";

infoElement.textContent = defaultInfo;

const viewer = new Cesium.Viewer("cesiumContainer", {
  shadows: false,
  geocoder: false,
  baseLayerPicker: false,
  baseLayer: false,
  animation: false,
  timeline: false,
  homeButton: false,
  sceneModePicker: false,
  navigationHelpButton: false,
  fullscreenButton: false,
  infoBox: false,
  selectionIndicator: false,
});

viewer.imageryLayers.addImageryProvider(
  new Cesium.OpenStreetMapImageryProvider({
    url: "https://tile.openstreetmap.org/",
    credit: new Cesium.Credit(
      '<a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">© OpenStreetMap contributors</a>',
      true
    ),
  })
);

const basemapProvider = new Cesium.WebMapServiceImageryProvider({
  url: "https://sgx.geodatenzentrum.de/wms_basemapde",
  layers: "de_basemapde_web_raster_farbe",
  parameters: {
    transparent: true,
    format: "image/png",
  },
});
viewer.imageryLayers.addImageryProvider(basemapProvider);

viewer.camera.flyTo({
  destination: Cesium.Cartesian3.fromDegrees(6.958215, 50.932767, 1500),
  orientation: {
    heading: Cesium.Math.toRadians(0),
    pitch: Cesium.Math.toRadians(-50),
    roll: 0,
  },
});

async function addBuildingTileset() {
  try {
    const tileset = await Cesium.Cesium3DTileset.fromUrl(
      "https://sgx.geodatenzentrum.de/gdz_basemapde_3d_gebaeude/lod2_4326_null.json",
      { showOutline: false }
    );
    viewer.scene.primitives.add(tileset);

    tileset.style = new Cesium.Cesium3DTileStyle({
      color: {
        conditions: [
          ["${surface} === 'wall'", "color('#f2f2f2')"],
          ["${surface} === 'roof'", "color('#ff5c4d')"],
          ["${surface} === 'bridge'", "color('#999999')"],
          ["true", "color('#c2c2c2')"],
        ],
      },
    });
  } catch (error) {
    console.error("Die LoD2-Gebäude konnten nicht geladen werden:", error);
    infoElement.textContent =
      "Die 3D-Gebäude konnten nicht geladen werden. Bitte prüfen Sie Ihre Internetverbindung.";
  }
}

const clickHandler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
clickHandler.setInputAction((movement) => {
  const pickedFeature = viewer.scene.pick(movement.position);
  if (!(pickedFeature instanceof Cesium.Cesium3DTileFeature)) {
    infoElement.textContent = defaultInfo;
    return;
  }

  const heading = document.createElement("strong");
  heading.textContent = "Gebäudeattribute";
  const details = document.createElement("dl");

  for (const propertyName of pickedFeature.getPropertyIds()) {
    const term = document.createElement("dt");
    term.textContent = propertyName;

    const description = document.createElement("dd");
    description.textContent = String(pickedFeature.getProperty(propertyName));
    details.append(term, description);
  }

  infoElement.replaceChildren(heading, details);
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);

viewer.scene.globe.tileLoadProgressEvent.addEventListener((pendingRequests) => {
  if (pendingRequests === 0) {
    viewer.scene.requestRender();
  }
});

addBuildingTileset();
