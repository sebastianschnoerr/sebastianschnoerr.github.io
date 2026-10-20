import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const container = document.querySelector("#three-map");
const status = document.querySelector("#three-status");
const stopList = document.querySelector("#stop-list");
const radius = 2;

const scene = new THREE.Scene();
scene.background = new THREE.Color("#101a26");

const camera = new THREE.PerspectiveCamera(
  42,
  container.clientWidth / container.clientHeight,
  0.1,
  100
);
camera.position.set(0.2, 0.5, 6.8);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
container.append(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.minDistance = 3.2;
controls.maxDistance = 10;

scene.add(new THREE.HemisphereLight("#d8efff", "#15202d", 2.1));
const sunLight = new THREE.DirectionalLight("#ffffff", 2.5);
sunLight.position.set(-4, 3, 5);
scene.add(sunLight);

const globe = new THREE.Mesh(
  new THREE.SphereGeometry(radius, 96, 64),
  new THREE.MeshStandardMaterial({
    color: "#17334a",
    roughness: 0.86,
    metalness: 0.08,
  })
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
  (error) => {
    console.error("Die Erdtextur konnte nicht geladen werden:", error);
  }
);

const atmosphere = new THREE.Mesh(
  new THREE.SphereGeometry(radius * 1.035, 64, 48),
  new THREE.MeshBasicMaterial({
    color: "#3c91b8",
    transparent: true,
    opacity: 0.08,
    side: THREE.BackSide,
  })
);
scene.add(atmosphere);

function coordinatesToVector([longitude, latitude], featureRadius = radius) {
  const phi = THREE.MathUtils.degToRad(90 - latitude);
  const theta = THREE.MathUtils.degToRad(longitude + 180);
  return new THREE.Vector3(
    -featureRadius * Math.sin(phi) * Math.cos(theta),
    featureRadius * Math.cos(phi),
    featureRadius * Math.sin(phi) * Math.sin(theta)
  );
}

function setInitialCamera() {
  camera.position.copy(coordinatesToVector([-4.5, 56.5], radius * 3.3));
  controls.target.set(0, 0, 0);
  controls.update();
}

setInitialCamera();

function addGraticule() {
  const material = new THREE.LineBasicMaterial({
    color: "#7093a6",
    transparent: true,
    opacity: 0.23,
  });
  const lineRadius = radius * 1.002;

  for (let latitude = -60; latitude <= 60; latitude += 30) {
    const points = [];
    for (let longitude = -180; longitude <= 180; longitude += 3) {
      points.push(coordinatesToVector([longitude, latitude], lineRadius));
    }
    scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), material));
  }

  for (let longitude = -180; longitude < 180; longitude += 30) {
    const points = [];
    for (let latitude = -90; latitude <= 90; latitude += 3) {
      points.push(coordinatesToVector([longitude, latitude], lineRadius));
    }
    scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), material));
  }
}

addGraticule();

const stationMeshes = [];
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const defaultStatus =
  "Wähle eine Station in der Liste oder klicke direkt auf einen Marker.";

function selectStation(station, marker) {
  status.textContent = `${station.order}. ${station.name} — ${station.description}`;
  for (const item of stopList.querySelectorAll("button")) {
    item.setAttribute("aria-pressed", String(item.dataset.name === station.name));
  }

  const target = marker.position.clone().normalize().multiplyScalar(radius);
  controls.target.copy(target);
}

function addRoute(routeCoordinates) {
  const curvePoints = [];
  for (let segment = 0; segment < routeCoordinates.length - 1; segment += 1) {
    const start = coordinatesToVector(routeCoordinates[segment]).normalize();
    const end = coordinatesToVector(routeCoordinates[segment + 1]).normalize();

    for (let step = 0; step <= 32; step += 1) {
      const point = start
        .clone()
        .slerp(end, step / 32)
        .multiplyScalar(radius * 1.012);
      curvePoints.push(point);
    }
  }

  const route = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints(curvePoints),
    new THREE.LineBasicMaterial({ color: "#f3c969", linewidth: 2 })
  );
  scene.add(route);
}

function addStation(station) {
  const position = coordinatesToVector(station.coordinates, radius * 1.025);
  const marker = new THREE.Mesh(
    new THREE.SphereGeometry(0.055, 20, 16),
    new THREE.MeshStandardMaterial({
      color: "#ff785f",
      emissive: "#8c2a20",
      emissiveIntensity: 0.6,
      roughness: 0.35,
    })
  );
  marker.position.copy(position);
  marker.userData.station = station;
  scene.add(marker);
  stationMeshes.push(marker);

  const stem = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints([
      coordinatesToVector(station.coordinates, radius * 1.003),
      position,
    ]),
    new THREE.LineBasicMaterial({ color: "#ffb8a7" })
  );
  scene.add(stem);

  const listItem = document.createElement("li");
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = `${station.order}. ${station.name}`;
  button.dataset.name = station.name;
  button.setAttribute("aria-pressed", "false");
  button.addEventListener("click", () => selectStation(station, marker));
  listItem.append(button);
  stopList.append(listItem);
}

async function loadGeoJson() {
  try {
    const response = await fetch("scotland-route.geojson");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status} beim Laden der GeoJSON-Datei.`);
    }

    const geojson = await response.json();
    const routeFeature = geojson.features.find(
      (feature) =>
        feature.geometry?.type === "LineString" &&
        feature.properties?.kind === "route"
    );
    const stations = geojson.features
      .filter((feature) => feature.geometry?.type === "Point")
      .map((feature) => ({
        ...feature.properties,
        coordinates: feature.geometry.coordinates,
      }))
      .sort((first, second) => first.order - second.order);

    if (!routeFeature || stations.length === 0) {
      throw new Error("GeoJSON enthält keine Route oder Stationspunkte.");
    }

    addRoute(routeFeature.geometry.coordinates);
    stations.forEach(addStation);
    status.textContent = defaultStatus;
  } catch (error) {
    console.error("Die GeoJSON-Route konnte nicht geladen werden:", error);
    status.textContent =
      "Die Routendaten konnten nicht geladen werden. Öffne die Seite über einen Webserver und prüfe die GeoJSON-Datei.";
  }
}

renderer.domElement.addEventListener("click", (event) => {
  const bounds = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - bounds.left) / bounds.width) * 2 - 1;
  pointer.y = -((event.clientY - bounds.top) / bounds.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);

  const [marker] = raycaster.intersectObjects(stationMeshes);
  if (marker) {
    selectStation(marker.object.userData.station, marker.object);
  }
});

document.querySelector("#reset-globe").addEventListener("click", () => {
  setInitialCamera();
  status.textContent = defaultStatus;
  for (const item of stopList.querySelectorAll("button")) {
    item.setAttribute("aria-pressed", "false");
  }
});

function resizeScene() {
  const { clientWidth, clientHeight } = container;
  camera.aspect = clientWidth / clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(clientWidth, clientHeight);
}

new ResizeObserver(resizeScene).observe(container);

function animate() {
  controls.update();
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);
loadGeoJson();
