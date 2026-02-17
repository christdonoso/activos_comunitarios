/**
 * map_init.js
 * Inicialización de Leaflet para MAIS Community Assets
 */

var map = L.map('map').setView([0, 0], 2);
const categoryIcons = {
    'espacio_publico': 'park',
    'organizacion_social': 'groups',
    'establecimiento_salud': 'medical_services',
    'establecimiento_educacional': 'school',
    'organizacion_deportiva': 'sports_soccer',
    'grupo_apoyo': 'volunteer_activism',
    'programa_municipal': 'account_balance',
    'centro_cultural': 'theater_comedy',
    'organizacion_adulto_mayor': 'elderly',
    'organizacion_juvenil': 'sentiment_satisfied',
    'red_vecinal': 'home_work',
    'otro': 'location_on'
};


L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 20,
    attribution: '&copy; OpenStreetMap'
}).addTo(map);

// 2. IMPORTANTE: Crear la capa de marcadores GLOBALMENTE
var markersLayer = L.layerGroup().addTo(map);

// 3. Geolocation
navigator.geolocation.getCurrentPosition(
    function (position) {
        var currentLat = position.coords.latitude;
        var currentLng = position.coords.longitude;
        map.setView([currentLat, currentLng], 15);
        L.marker([currentLat, currentLng]).addTo(map).bindPopup("Tu ubicación");
    },
    function (error) {
        console.warn("No se pudo obtener la ubicación");
        // Si falla, centrar en una ubicación por defecto (ej: Quilpué/Villa Alemana)
        map.setView([-33.04, -71.4], 12);
    }
);

async function loadAssets() {
    try {
        // Tip: Usa la URL relativa para evitar problemas de CORS o cambios de IP
        const response = await fetch('/assets_display/get_all_valid_assets', {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });

        if (!response.ok) throw new Error('Error al obtener activos');
        const data = await response.json();
        
        console.log("Datos recibidos:", data.assets); // Para depurar en consola F12
        renderMarkers(data.assets);

    } catch (error) {
        console.error('Error:', error);
    }
}


// Modifica tu función renderMarkers para usar esto:
function renderMarkers(assets) {
    markersLayer.clearLayers(); 

    assets.forEach(asset => {
        const iconName = categoryIcons[asset.category] || 'location_on'; // asset.category debe venir de Django
        
        const customIcon = L.divIcon({
            className: 'custom-marker',
            html: `
                <div class="flex flex-col items-center">
                    <div class="bg-primary text-white p-2 rounded-full shadow-lg border-2 border-white">
                        <span class="material-symbols-outlined text-sm" style="display:block;">${iconName}</span>
                    </div>
                </div>`,
            iconSize: [32, 32],
            iconAnchor: [16, 32]
        });

        L.marker([asset.lat, asset.lng], { icon: customIcon })
            .addTo(markersLayer)
            .bindPopup(`<a href="/comunity_assets/asset_detail/${asset.asset_id}">
                            <b>${asset.name}</b>
                        </a>
                        <p>
                            ${asset.description}
                        </p>
                `);
    });
}

// Ejecutar carga y corregir tamaño de mapa
document.addEventListener('DOMContentLoaded', () => {
    loadAssets();
    // Esto arregla problemas de visualización en contenedores dinámicos
    setTimeout(() => { map.invalidateSize(); }, 200);
});