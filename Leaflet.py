import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


KEPLER_HTML = r"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Schottlandroute — Kepler.gl</title>
  <link rel="stylesheet" href="https://d1a3f4spazzrp4.cloudfront.net/kepler.gl/uber-fonts/4.0.0/superfine.css">
  <link rel="stylesheet" href="https://unpkg.com/kepler.gl@3.3.0-alpha.6/umd/keplergl.min.css">
  <link rel="stylesheet" href="https://api.tiles.mapbox.com/mapbox-gl-js/v1.1.1/mapbox-gl.css">
  <link rel="stylesheet" href="https://unpkg.com/maplibre-gl@4/dist/maplibre-gl.css">
  <style>
    html, body, #app { width: 100%; height: 100%; margin: 0; overflow: hidden; }
    #loading { position: fixed; z-index: 10; inset: 0; display: grid; place-items: center;
      background: #101820; color: white; font: 16px system-ui, sans-serif; }
    #loading[hidden] { display: none; }
  </style>
  <script>window.esmsInitOptions = {shimMode: true};</script>
  <script src="https://unpkg.com/es-module-shims@2.8.1/dist/es-module-shims.js"
    crossorigin="anonymous"></script>
  <script type="importmap-shim">
    {
      "imports": {
        "react": "https://esm.sh/react@19.1.0",
        "react/jsx-runtime": "https://esm.sh/react@19.1.0/jsx-runtime",
        "react-dom": "https://esm.sh/react-dom@19.1.0?external=react",
        "react-dom/client": "https://esm.sh/react-dom@19.1.0/client?external=react",
        "redux": "https://esm.sh/redux@5.0.1",
        "react-redux": "https://esm.sh/react-redux@9.3.0?external=react,react-dom,redux",
        "styled-components": "https://esm.sh/styled-components@6.1.19?external=react,react-dom"
      }
    }
  </script>
</head>
<body>
  <div id="app"></div>
  <div id="loading" role="status">Kepler.gl-Karte wird geladen …</div>
  <script type="module-shim">
    import * as React from "react";
    import * as ReactDOM from "react-dom";
    import {createRoot} from "react-dom/client";
    import * as Redux from "redux";
    import * as ReactRedux from "react-redux";
    import * as StyledComponents from "styled-components";

    window.React = React.default || React;
    window.ReactDOM = ReactDOM.default || ReactDOM;
    window.Redux = Redux.default || Redux;
    window.ReactRedux = ReactRedux.default || ReactRedux;
    window.styled = Object.assign(StyledComponents.default, StyledComponents);

    function loadScript(src) {
      return new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = src;
        script.crossOrigin = "anonymous";
        script.onload = resolve;
        script.onerror = () => reject(new Error(`Kepler.gl konnte nicht geladen werden: ${src}`));
        document.head.appendChild(script);
      });
    }

    const routeData = __TRIP_DATA__;
    const stationsCsv = __STATIONS_CSV__;
    const mapConfig = __MAP_CONFIG__;

    loadScript("https://unpkg.com/kepler.gl@3.3.0-alpha.6/umd/keplergl.min.js")
      .then(() => {
        const reducers = Redux.combineReducers({
          keplerGl: KeplerGl.keplerGlReducer.initialState({
            uiState: {readOnly: false, currentModal: null}
          })
        });
        const middleware = KeplerGl.enhanceReduxMiddleware([]);
        const store = Redux.legacy_createStore(
          reducers,
          {},
          Redux.applyMiddleware(...middleware)
        );

        function App() {
          const [size, setSize] = React.useState({
            width: window.innerWidth,
            height: window.innerHeight
          });
          React.useEffect(() => {
            const resize = () => setSize({
              width: window.innerWidth,
              height: window.innerHeight
            });
            window.addEventListener("resize", resize);
            return () => window.removeEventListener("resize", resize);
          }, []);
          return React.createElement(KeplerGl.KeplerGl, {
            id: "scotland",
            width: size.width,
            height: size.height,
            mapboxApiAccessToken: "pk.xxx.yyy"
          });
        }

        const root = createRoot(document.getElementById("app"));
        root.render(React.createElement(
          ReactRedux.Provider,
          {store},
          React.createElement(App)
        ));

        const datasets = [
          {
            info: {id: "scotland-trip", label: "Schottlandroute"},
            data: KeplerGl.processGeojson(routeData)
          },
          {
            info: {id: "scotland-stations", label: "Stationen"},
            data: KeplerGl.processCsvData(stationsCsv)
          }
        ];
        window.setTimeout(() => {
          store.dispatch(KeplerGl.addDataToMap({
            datasets,
            config: mapConfig,
            options: {centerMap: true}
          }));
          document.getElementById("loading").hidden = true;
        }, 500);
      })
      .catch((error) => {
        console.error(error);
        document.getElementById("loading").textContent =
          "Karte konnte nicht geladen werden. Bitte Internetverbindung und Browserkonsole prüfen.";
      });
  </script>
</body>
</html>
"""


THREEJS_HTML = r"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#101a26">
  <title>Schottlandroute — Three.js</title>
  <script type="importmap">
    {
      "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/"
      }
    }
  </script>
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; background: #101a26; color: #edf4f7; font: 16px system-ui, sans-serif; }
    main { min-height: 100vh; display: grid; grid-template-columns: minmax(0, 1fr) 310px; }
    #globe { min-height: 100vh; position: relative; }
    #globe canvas { display: block; width: 100%; height: 100%; }
    aside { padding: 30px 24px; background: #172431; }
    h1 { margin: 8px 0 10px; font-size: 1.8rem; }
    .eyebrow { color: #91c8a9; font-size: .8rem; text-transform: uppercase; letter-spacing: .12em; }
    #status { min-height: 3.5em; color: #c5d3dc; line-height: 1.5; }
    ol { padding-left: 24px; }
    li { margin: 10px 0; }
    button { border: 1px solid #547184; border-radius: 6px; padding: 8px 12px;
      color: inherit; background: #203443; cursor: pointer; font: inherit; }
    button:hover, button[aria-pressed="true"] { background: #285c49; }
    #reset { margin-top: 10px; }
    .hint { color: #a9bac5; font-size: .9rem; line-height: 1.5; }
    @media (max-width: 760px) {
      main { grid-template-columns: 1fr; }
      #globe { min-height: 58vh; }
      aside { padding: 20px; }
    }
  </style>
</head>
<body>
  <main>
    <section id="globe" aria-label="Drehbarer Globus mit animierter Schottlandroute"></section>
    <aside>
      <p class="eyebrow">Three.js · animierte Route</p>
      <h1>Schottland entdecken</h1>
      <p id="status" role="status">Route wird geladen …</p>
      <h2>Stationen</h2>
      <ol id="stations"></ol>
      <button id="reset" type="button">Ansicht zurücksetzen</button>
      <p class="hint">Globus ziehen zum Drehen, scrollen zum Zoomen. Die Route läuft automatisch ab.</p>
    </aside>
  </main>
  <script type="module">
    import * as THREE from "three";
    import {OrbitControls} from "three/addons/controls/OrbitControls.js";

    const routeData = __ROUTE_DATA__;
    const stationData = __STATION_DATA__;
    const container = document.getElementById("globe");
    const status = document.getElementById("status");
    const radius = 2;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#101a26");

    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
    const renderer = new THREE.WebGLRenderer({antialias: true});
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.minDistance = 3.2;
    controls.maxDistance = 10;

    scene.add(new THREE.HemisphereLight("#d8efff", "#15202d", 2.1));
    const sun = new THREE.DirectionalLight("#ffffff", 2.5);
    sun.position.set(-4, 3, 5);
    scene.add(sun);

    const globe = new THREE.Mesh(
      new THREE.SphereGeometry(radius, 96, 64),
      new THREE.MeshStandardMaterial({color: "#17334a", roughness: 0.86})
    );
    scene.add(globe);
    new THREE.TextureLoader().load(
      "https://threejs.org/examples/textures/planets/earth_atmos_2048.jpg",
      (texture) => {
        texture.colorSpace = THREE.SRGBColorSpace;
        globe.material.map = texture;
        globe.material.color.set("#ffffff");
        globe.material.needsUpdate = true;
      },
      undefined,
      (error) => console.error("Die Erdtextur konnte nicht geladen werden:", error)
    );

    const toVector = ([longitude, latitude], featureRadius = radius) => {
      const phi = THREE.MathUtils.degToRad(90 - latitude);
      const theta = THREE.MathUtils.degToRad(longitude + 180);
      return new THREE.Vector3(
        -featureRadius * Math.sin(phi) * Math.cos(theta),
        featureRadius * Math.cos(phi),
        featureRadius * Math.sin(phi) * Math.sin(theta)
      );
    };

    const coords = routeData.features.find((feature) =>
      feature.geometry.type === "LineString"
    )?.geometry.coordinates;
    if (!coords || coords.length < 2 || stationData.length === 0) {
      throw new Error("Die Routendaten enthalten keine gültige Route oder Stationen.");
    }

    camera.position.copy(toVector([-4.5, 56.5], radius * 3.3));
    controls.target.set(0, 0, 0);

    const routePoints = [];
    for (let segment = 0; segment < coords.length - 1; segment += 1) {
      const start = toVector(coords[segment]).normalize();
      const end = toVector(coords[segment + 1]).normalize();
      const rotation = new THREE.Quaternion().setFromUnitVectors(start, end);
      for (let step = 0; step <= 40; step += 1) {
        const fraction = step / 40;
        const interpolation = new THREE.Quaternion().identity().slerp(rotation, fraction);
        routePoints.push(
          start.clone().applyQuaternion(interpolation).multiplyScalar(radius * 1.012)
        );
      }
    }

    const fullRoute = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints(routePoints),
      new THREE.LineBasicMaterial({color: "#647b86", transparent: true, opacity: 0.65})
    );
    scene.add(fullRoute);
    const animatedRoute = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints(routePoints),
      new THREE.LineBasicMaterial({color: "#f3c969"})
    );
    animatedRoute.geometry.setDrawRange(0, 1);
    scene.add(animatedRoute);
    const traveler = new THREE.Mesh(
      new THREE.SphereGeometry(0.075, 20, 16),
      new THREE.MeshStandardMaterial({color: "#ff785f", emissive: "#8c2a20"})
    );
    scene.add(traveler);

    for (const station of stationData) {
      const marker = new THREE.Mesh(
        new THREE.SphereGeometry(0.045, 16, 12),
        new THREE.MeshStandardMaterial({color: "#91c8a9", emissive: "#285c49"})
      );
      marker.position.copy(toVector(station.coordinates, radius * 1.025));
      scene.add(marker);

      const item = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = station.name;
      button.setAttribute("aria-pressed", "false");
      button.addEventListener("click", () => {
        status.textContent = `${station.order}. ${station.name} — ${station.description}`;
        controls.target.copy(marker.position.clone().normalize().multiplyScalar(radius));
        document.querySelectorAll("#stations button").forEach((element) =>
          element.setAttribute("aria-pressed", String(element === button))
        );
      });
      item.appendChild(button);
      document.getElementById("stations").appendChild(item);
    }

    status.textContent = "Die Route von Edinburgh nach Inverness wird animiert.";
    document.getElementById("reset").addEventListener("click", () => {
      camera.position.copy(toVector([-4.5, 56.5], radius * 3.3));
      controls.target.set(0, 0, 0);
      controls.update();
      status.textContent = "Die Route von Edinburgh nach Inverness wird animiert.";
      document.querySelectorAll("#stations button").forEach((button) =>
        button.setAttribute("aria-pressed", "false")
      );
    });

    function resize() {
      const {clientWidth, clientHeight} = container;
      camera.aspect = clientWidth / clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(clientWidth, clientHeight);
    }
    new ResizeObserver(resize).observe(container);
    resize();

    const clock = new THREE.Clock();
    const duration = 24;
    renderer.setAnimationLoop(() => {
      const progress = (clock.getElapsedTime() % duration) / duration;
      const traveled = progress * (routePoints.length - 1);
      const index = Math.min(Math.floor(traveled), routePoints.length - 2);
      const fraction = traveled - index;
      traveler.position.copy(routePoints[index]).lerp(routePoints[index + 1], fraction);
      animatedRoute.geometry.setDrawRange(0, Math.max(2, Math.ceil(traveled) + 1));
      controls.update();
      renderer.render(scene, camera);
    });
  </script>
</body>
</html>
"""


def script_json(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )


def load_geojson(path):
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def create_kepler_html():
    trip_data = load_geojson(ROOT / "kepler-scotland-trip.geojson")
    stations_path = ROOT / "kepler-scotland-stations.csv"
    stations_csv = stations_path.read_text(encoding="utf-8")
    station_rows = list(csv.DictReader(stations_csv.splitlines()))
    if not station_rows:
        raise ValueError(f"Keine Stationsdaten in {stations_path.name}.")

    timestamps = [
        coordinate[3]
        for feature in trip_data.get("features", [])
        if feature.get("geometry", {}).get("type") == "LineString"
        for coordinate in feature["geometry"].get("coordinates", [])
        if len(coordinate) >= 4
    ]
    if not timestamps:
        raise ValueError("Die Kepler-GeoJSON enthält keine Zeitstempel für die Route.")

    trip_id = "scotland-trip"
    stations_id = "scotland-stations"
    map_config = {
        "version": "v1",
        "config": {
            "visState": {
                "layers": [
                    {
                        "id": "route-layer",
                        "type": "trip",
                        "config": {
                            "dataId": trip_id,
                            "columnMode": "geojson",
                            "label": "Animierte Schottlandroute",
                            "color": [243, 201, 105],
                            "columns": {"geojson": "_geojson"},
                        },
                    },
                    {
                        "id": "station-layer",
                        "type": "point",
                        "config": {
                            "dataId": stations_id,
                            "label": "Stationen",
                            "color": [255, 120, 95],
                            "columns": {
                                "lat": "point_latitude",
                                "lng": "point_longitude",
                            },
                            "isVisible": True,
                        },
                    },
                ],
                "animationConfig": {
                    "currentTime": max(timestamps) * 1000,
                    "speed": 1,
                },
                "layerBlending": "normal",
            },
            "mapState": {
                "latitude": 56.5,
                "longitude": -4.5,
                "zoom": 6,
                "bearing": 0,
                "pitch": 0,
            },
            "mapStyle": {"styleType": "positron"},
        },
    }

    page = (
        KEPLER_HTML.replace("__TRIP_DATA__", script_json(trip_data))
        .replace("__STATIONS_CSV__", script_json(stations_csv))
        .replace("__MAP_CONFIG__", script_json(map_config))
    )
    (ROOT / "kepler.html").write_text(page, encoding="utf-8")


def create_threejs_html():
    route_data = load_geojson(ROOT / "scotland-route.geojson")
    stations = [
        {
            "name": feature["properties"]["name"],
            "order": feature["properties"]["order"],
            "description": feature["properties"]["description"],
            "coordinates": feature["geometry"]["coordinates"],
        }
        for feature in route_data.get("features", [])
        if feature.get("geometry", {}).get("type") == "Point"
    ]
    stations.sort(key=lambda station: station["order"])
    if not stations:
        raise ValueError("Die GeoJSON enthält keine Stationspunkte.")

    page = (
        THREEJS_HTML.replace("__ROUTE_DATA__", script_json(route_data))
        .replace("__STATION_DATA__", script_json(stations))
    )
    (ROOT / "threejs.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    create_kepler_html()
    print("Gespeichert: kepler.html")
    create_threejs_html()
    print("Gespeichert: threejs.html")
