// 1. Configuración Inicial Global
var map = L.map('map').setView([-33.04, -71.4], 12);
var markersLayer = L.layerGroup().addTo(map);

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

// --- FUNCIONES DE UTILIDAD (Fuera para que sean accesibles) ---

function showLoader() {
    const loader = document.getElementById('map-loader');
    if (loader) {
        loader.classList.remove('hidden');
        loader.classList.add('flex');
    }
}

function hideLoader() {
    const loader = document.getElementById('map-loader');
    if (loader) {
        loader.classList.add('hidden');
        loader.classList.remove('flex');
    }
}

async function loadAssets(category = null) {
    showLoader();
    try {
        let url = '/assets_display/get_all_valid_assets';
        if (category) {
            url = `/assets_display/get_assets_by_category?category=${category}`;
        }

        const response = await fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        
        if (!response.ok) throw new Error("Error en servidor");
        
        const data = await response.json();
        renderMarkers(data.assets);
    } catch (error) {
        console.error("Error cargando activos:", error);
    } finally {
        // Un pequeño delay opcional para que el spinner no parpadee demasiado rápido
        setTimeout(hideLoader, 300);
    }
}

function renderMarkers(assets) {
    markersLayer.clearLayers(); // Limpia los puntos anteriores

    assets.forEach(asset => {
        const iconName = categoryIcons[asset.category] || 'location_on';
        
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
            .bindPopup(`
                <div class="p-2">
                    <a href="/comunity_assets/asset_detail/${asset.asset_id}" class="text-primary font-bold hover:underline">
                        ${asset.name}
                    </a>
                    <p class="text-sm text-gray-600 mt-1">${asset.description}</p>
                </div>
            `);
    });
}

// --- INICIALIZACIÓN AL CARGAR EL DOM ---

document.addEventListener('DOMContentLoaded', () => {
    // Geolocation
    navigator.geolocation.getCurrentPosition(
        function (position) {
            var currentLat = position.coords.latitude;
            var currentLng = position.coords.longitude;
            map.setView([currentLat, currentLng], 15);
            L.marker([currentLat, currentLng]).addTo(map).bindPopup("Tu ubicación");
        }
    );

    // Eventos de Filtro
    document.querySelectorAll('.category-filter').forEach(button => {
        button.addEventListener('click', () => {
            const category = button.dataset.category;

            // Feedback visual de botón seleccionado
            document.querySelectorAll('.category-filter').forEach(b => {
                b.classList.remove('bg-primary/10', 'text-primary', 'ring-2', 'ring-primary/20');
            });
            button.classList.add('bg-primary/10', 'text-primary');

            loadAssets(category);
        });
    });

    // Carga inicial (Todos los activos)
    loadAssets();

    // Fix para problemas de renderizado de Leaflet en contenedores dinámicos
    setTimeout(() => { map.invalidateSize(); }, 200);
});