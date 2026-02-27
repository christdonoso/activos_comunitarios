class CommunityMap {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.esMapaLimpio = true;
        this.userMarker = null;
        this.config = {
            center: options.center || [-33.48, -70.55],
            zoom: options.zoom || 13,
            showMarkers: options.showMarkers !== undefined ? options.showMarkers : true,
            apiUrl: options.apiUrl || '/api/get_all_valid_assets'
        };

        //botones de control del mapa 
        this.controls = {
            btnZoomIn: options.btnZoomIn || 'btn-zoom-in',
            btnZoomOut: options.btnZoomOut || 'btn-zoom-out',
            btnLocate: options.btnLocate || 'btn-locate',
            btnLayer: options.btnLayer || 'btn-layer-toggle'
        };
        // Diccionarios internos para que siempre funcionen los iconos
        this.categoryColors = {
            'espacio_publico': 'bg-emerald-500',
            'organizacion_social': 'bg-purple-500',
            'establecimiento_salud': 'bg-rose-500',
            'organizacion_deportiva': 'bg-blue-500',
            'centro_cultural': 'bg-amber-500',
            'otro': 'bg-slate-500'
        };

        this.categoryIcons = {
            'espacio_publico': 'park',
            'organizacion_social': 'groups',
            'establecimiento_salud': 'local_hospital',
            'establecimiento_educacional': 'school',
            'organizacion_deportiva': 'sports_soccer',
            'centro_cultural': 'theater_comedy',
            'otro': 'location_on'
        };

        this.map = null;
        this.markersLayer = L.layerGroup();
        this.tilesLimpio = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { attribution: '&copy; CartoDB' });
        this.tilesNormal = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap' });

        this.init();
    }

    init() {
        const container = document.getElementById(this.containerId);
        if (!container) return; // Salir si el div no existe

        this.map = L.map(this.containerId, {
            zoomControl: false,
            layers: [this.tilesLimpio]
        }).setView(this.config.center, this.config.zoom);

        this.markersLayer.addTo(this.map);

        this._bindControls();
        this._setupLocationEvents();

        if (this.config.showMarkers) {
            this.loadAssets();
        }
    }
    // --- EL NUEVO MOTOR DE EVENTOS ---
    _bindControls() {
        const bIn = document.getElementById(this.controls.btnZoomIn);
        const bOut = document.getElementById(this.controls.btnZoomOut);
        const bLoc = document.getElementById(this.controls.btnLocate);
        const bLay = document.getElementById(this.controls.btnLayer);

        if (bIn) bIn.onclick = () => this.map.zoomIn();
        if (bOut) bOut.onclick = () => this.map.zoomOut();
        if (bLoc) bLoc.onclick = () => this.map.locate({ setView: true, maxZoom: 16 });

        if (bLay) {
            bLay.onclick = () => {
                const esLimpio = this.toggleLayer();
                this._updateLayerUI(bLay, esLimpio);
            };
        }
    }

    // Método auxiliar para no ensuciar la lógica del mapa con CSS
    _updateLayerUI(button, esLimpio) {
        const icono = button.querySelector('span');
        if (!esLimpio) {
            button.classList.add('bg-primary', 'text-white');
            if (icono) icono.innerText = 'map';
        } else {
            button.classList.remove('bg-primary', 'text-white');
            if (icono) icono.innerText = 'layers';
        }
    }

    // Métodos de acción
    zoomIn() { this.map.zoomIn(); }
    zoomOut() { this.map.zoomOut(); }
    locate() {
        this.map.locate({
            setView: true,
            maxZoom: 16,
            enableHighAccuracy: true
        });
    }
    //cambio de capa
    toggleLayer() {
        // 1. Invertimos el estado inmediatamente
        this.esMapaLimpio = !this.esMapaLimpio;

        // 2. Cambiamos las capas según el nuevo estado
        if (this.esMapaLimpio) {
            this.map.removeLayer(this.tilesNormal);
            this.map.addLayer(this.tilesLimpio);
        } else {
            this.map.removeLayer(this.tilesLimpio);
            this.map.addLayer(this.tilesNormal);
        }

        // 3. Devolvemos el estado para que el HTML sepa qué color ponerse
        return this.esMapaLimpio;
    }

    async loadAssets(category = null) {
        let url = this.config.apiUrl;
        if (category) url = `/api/get_assets_by_category?category=${category}`;

        try {
            const response = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
            const data = await response.json();

            this.assetsData = data.assets; // Guardamos para el buscador

            this.renderMarkers(data.assets);
        } catch (e) { console.error("Error:", e); }
    }

    renderMarkers(assets) {
        this.markersLayer.clearLayers();
        assets.forEach(asset => {
            const iconName = this.categoryIcons[asset.category] || 'location_on';
            const bgColor = this.categoryColors[asset.category] || 'bg-primary';
            // Dentro de renderMarkers en CommunityMap.js
            const accessibilityIcons = `
                <div class="flex gap-1 mt-2 border-t pt-2">
                    ${asset.accesible_silla ? '<span class="material-symbols-outlined text-sm text-emerald-600">accessible</span>' : ''}
                    ${asset.baño_accesible ? '<span class="material-symbols-outlined text-sm text-emerald-600">wc</span>' : ''}
                    ${asset.estacionamiento ? '<span class="material-symbols-outlined text-sm text-emerald-600">local_parking</span>' : ''}
                </div>
            `;

            const customIcon = L.divIcon({
                className: 'custom-marker',
                html: `<div class="size-10 ${bgColor} rounded-2xl border-4 border-white shadow-xl flex items-center justify-center text-white"><span class="material-symbols-outlined">${iconName}</span></div>`,
                iconSize: [40, 40],
                iconAnchor: [20, 40],
                popupAnchor: [0, -45]
            });

            // DISEÑO ATRACTIVO DEL POPUP
            const popupContent = `
            <div class="p-1 max-w-[240px] font-display">
                <div class="flex items-center gap-2 mb-2">
                    <div class="size-8 ${bgColor} rounded-lg flex items-center justify-center text-white shadow-sm">
                        <span class="material-symbols-outlined text-sm">${iconName}</span>
                    </div>
                    <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">${asset.type_display || 'Activo Comunitario'}</span>
                </div>
                
                <h3 class="text-sm font-black text-slate-800 mb-1 leading-tight">${asset.name}</h3>
                <p class="text-[11px] text-slate-600 leading-relaxed mb-3">${asset.description || 'Sin descripción disponible.'}</p>
                
                <div class="flex flex-col gap-1.5 border-t border-slate-100 pt-3">
                    <div class="flex items-center gap-2 text-[10px] font-bold text-slate-500">
                        <span class="material-symbols-outlined text-[14px]">schedule</span>
                        ${asset.horario || 'Horario a consultar'}
                    </div>
                    <div class="flex items-center gap-2 text-[10px] font-bold text-slate-500">
                        <span class="material-symbols-outlined text-[14px]">near_me</span>
                        ${asset.direccion}
                    </div>
                </div>

                <button onclick="window.open('https://www.google.com/maps/dir/?api=1&destination=${asset.lat},${asset.lng}')" 
                    class="w-full mt-3 py-2 bg-slate-900 text-white text-[10px] font-black rounded-lg hover:bg-primary transition-all flex items-center justify-center gap-2">
                    CÓMO LLEGAR
                    <span class="material-symbols-outlined text-xs">arrow_forward</span>
                </button>
            </div>
        `;

            L.marker([asset.lat, asset.lng], { icon: customIcon })
                .addTo(this.markersLayer)
                .bindPopup(popupContent, {
                    maxWidth: 280,
                    className: 'custom-mais-popup'
                });
        });
    }

    _setupLocationEvents() {
        this.map.on('locationfound', (e) => {
            const radius = e.accuracy / 2;

            // Si el marcador ya existe, solo lo movemos
            if (this.userMarker) {
                this.userMarker.setLatLng(e.latlng);
            } else {
                // Si no existe, lo creamos con un estilo distinto (Punto azul)
                this.userMarker = L.marker(e.latlng, {
                    icon: L.divIcon({
                        className: 'user-location-marker',
                        html: `
                            <style>
                                @keyframes ping {
                            0% { transform: scale(1); opacity: 0.8; }
                            100% { transform: scale(3); opacity: 0; }
                            }
                            .animate-ping {
                            animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;
                            }
                            </style>
                            <div class="relative flex items-center justify-center">
                                <div class="absolute size-8 bg-emerald-500/40 rounded-full animate-ping"></div>
                                <div class="size-4 bg-emerald-500 rounded-full border-2 border-white shadow-lg"></div>
                            </div>`,
                        iconSize: [32, 32],
                        iconAnchor: [16, 16],
                        popupAnchor: [0, -15]
                    })
                }).addTo(this.map);

                this.userMarker.bindPopup("Estás aquí").openPopup();
            }
        });

        this.map.on('locationerror', (e) => {
            alert("No pudimos obtener tu ubicación. Revisa los permisos de tu navegador.");
        });
    }
    // Método para enfocar un activo específico (Receta Social)
    // En js/map_handler.js, dentro de la clase CommunityMap

    focusOnAsset(lat, lng, name) {
        if (!this.map) return;

        // 1. Zoom suave
        this.map.flyTo([lat, lng], 16, { animate: true, duration: 1.5 });

        // 2. --- NUEVA ESTRATEGIA: CÍRCULO DE BIENVENIDA ---
        // Limpiamos círculos anteriores si existen
        if (this.welcomeCircle) {
            this.map.removeLayer(this.welcomeCircle);
        }

        // Dibujamos el nuevo círculo
        this.welcomeCircle = L.circle([lat, lng], {
            color: '#137fec',      // Color Primary
            fillColor: '#137fec',  // Relleno Primary
            fillOpacity: 0.15,     // Muy suave
            radius: 150            // Radio en metros
        }).addTo(this.map);

        // 3. Abrir Popup del marcador (Lógica que ya teníamos)
        this.markersLayer.eachLayer((layer) => {
            if (layer instanceof L.Marker) {
                const latLng = layer.getLatLng();
                if (Math.abs(latLng.lat - lat) < 0.0001 && Math.abs(latLng.lng - lng) < 0.0001) {
                    layer.openPopup();
                }
            }
        });

        // Limpiar el círculo si se cancela la receta o se recarga
        this.map.once('movestart', () => {
            if (this.welcomeCircle) {
                this.map.removeLayer(this.welcomeCircle);
                this.welcomeCircle = null;
            }
        });
    }
}