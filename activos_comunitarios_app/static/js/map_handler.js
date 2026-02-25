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

            const customIcon = L.divIcon({
                className: 'custom-marker',
                html: `<div class="size-10 ${bgColor} rounded-2xl border-4 border-white shadow-xl flex items-center justify-center text-white"><span class="material-symbols-outlined">${iconName}</span></div>`,
                iconSize: [40, 40],
                iconAnchor: [20, 40],
            });

            L.marker([asset.lat, asset.lng], { icon: customIcon })
                .addTo(this.markersLayer)
                .bindPopup(`<b>${asset.name}</b><br>${asset.description}`);
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
}