
var map = L.map('map');
var marker = null; // marcador reutilizable
let currentLat = null // Valor inicial por defecto
let currentLng = null;

const locateBtn = document.getElementById('locate-btn')
const latitude = document.getElementById('latitude')
const longitude = document.getElementById('longitude')



L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 20,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


navigator.geolocation.getCurrentPosition(
    function (position) {

        currentLat = position.coords.latitude;
        currentLng = position.coords.longitude;
        // Mover mapa
        map.setView([currentLat, currentLng], 15);

        // Mover marcador
        marker = L.marker([currentLat, currentLng]).addTo(map);
    },
    function (error) {
        alert("No se pudo obtener la ubicación");
        console.error(error);
    },
)


function onMapClick(e) {

    const lat = e.latlng.lat;
    const lng = e.latlng.lng;

    // Actualizar HTML
    document.getElementById("latitude_display").innerText = lat.toFixed(6);
    document.getElementById("longitude_display").innerText = lng.toFixed(6);

    // Si el marcador ya existe → moverlo
    if (marker) {
        marker.setLatLng(e.latlng);
    } else {
        // Si no existe → crearlo
        marker = L.marker(e.latlng).addTo(map);
    }

    latitude.value = lat.toFixed(6);
    longitude.value = lng.toFixed(6)
}

map.on('click', onMapClick);


locateBtn.addEventListener('click', () => {
    map.setView([currentLat, currentLng], 15)
})