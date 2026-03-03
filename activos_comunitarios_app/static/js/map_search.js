class MapSearch {
    constructor(mapInstance, inputId, options = {}) {
        this.mapInstance = mapInstance;
        this.input = document.getElementById(inputId);
        // Buscamos el icono que está al lado del input para transformarlo en spinner
        this.searchIcon = this.input.parentElement.querySelector('.material-symbols-outlined');
        this.resultsContainer = null;
        this.debounceTimer = null;
        this.isLoading = false;
        
        this.options = {
            minChars: 3,
            limit: 5,
            ...options
        };

        if (this.input) this._init();
    }

    _init() {
        // ... (mismo código de creación de resultsContainer)
        this.resultsContainer = document.createElement('div');
        this.resultsContainer.className = 'absolute top-full left-0 right-0 bg-white dark:bg-slate-900 mt-2 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden hidden z-[100]';
        this.input.parentElement.style.position = 'relative';
        this.input.parentElement.appendChild(this.resultsContainer);

        this.input.addEventListener('input', (e) => this._onInput(e.target.value));
        
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target)) this._hideResults();

        });

        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this._handleEsc();
            }
        });

        const clearBtn = document.getElementById('clear-search');
        if (clearBtn) {
            clearBtn.onclick = () => this._handleEsc();
            
            // Mostrar/ocultar el botón según si hay texto
            this.input.addEventListener('input', (e) => {
                clearBtn.classList.toggle('hidden', e.target.value.length === 0);
            });
        }
    }   

    _handleEsc() {
        // 1. Si hay texto, lo limpia
        this.input.value = '';
        // 2. Oculta resultados
        this._hideResults();
        // 3. Quita el foco del input para que el usuario pueda usar flechas en el mapa, etc.
        this.input.blur();
        // 4. Aseguramos que el spinner se apague si estaba activo
        this._toggleLoading(false);
    }
    

    _toggleLoading(show) {
        this.isLoading = show;
        if (!this.searchIcon) return;

        if (show) {
            // Cambiamos la lupa por un spinner de Tailwind/CSS
            this.searchIcon.innerText = 'sync'; // Icono de refrescar
            this.searchIcon.classList.add('animate-spin', 'text-primary');
            this.searchIcon.classList.remove('text-slate-400');
        } else {
            // Volvemos a la lupa normal
            this.searchIcon.innerText = 'search';
            this.searchIcon.classList.remove('animate-spin', 'text-primary');
            this.searchIcon.classList.add('text-slate-400');
        }
    }

    _onInput(query) {
        clearTimeout(this.debounceTimer);
        if (query.length < this.options.minChars) {
            this._hideResults();
            this._toggleLoading(false);
            return;
        }

        // Mostramos feedback inmediato de que estamos "esperando" a que termine de escribir
        this._toggleLoading(true);

        this.debounceTimer = setTimeout(() => {
            this._search(query);
        }, 500); // Un poco más de delay para no saturar la API
    }

    async _search(query) {
        // 1. Buscar en activos locales
        const localResults = this._searchInLocalAssets(query);
        
        // 2. Buscar en direcciones (esto es lo que demora)
        const geoResults = await this._searchAddress(query);

        this._renderResults(localResults, geoResults);
        this._toggleLoading(false); // Apagar spinner al terminar
    }

    // ... (Métodos _searchInLocalAssets y _searchAddress quedan igual)
    
    _searchInLocalAssets(query) {
        if (!this.mapInstance.assetsData) return [];
        return this.mapInstance.assetsData.filter(asset => 
            asset.name.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 3);
    }

    async _searchAddress(query) {
        try {
            const response = await fetch(
                `https://nominatim.openstreetmap.org/search?format=json&q=${query}&countrycodes=cl&limit=5`
            );
            return await response.json();
        } catch (e) {
            console.error("Error", e);
            return [];
        }
    }

    _renderResults(assets, addresses) {
        this.resultsContainer.innerHTML = '';
        
        if (assets.length === 0 && addresses.length === 0) {
            this._hideResults();
            return;
        }

        // Sección de Activos
        if (assets.length > 0) {
            this._addSectionTitle('Activos de la Comunidad');
            assets.forEach(asset => {
                this._addResultItem(asset.name, 'location_on', () => {
                    this.mapInstance.map.flyTo([asset.lat, asset.lng], 17);
                    this._hideResults();
                });
            });
        }

        // Sección de Direcciones
        if (addresses.length > 0) {
            this._addSectionTitle('Direcciones y Calles');
            addresses.forEach(addr => {
                this._addResultItem(addr.display_name, 'map', () => {
                    this.mapInstance.map.flyTo([addr.lat, addr.lon], 16);
                    this._hideResults();
                });
            });
        }

        this.resultsContainer.classList.remove('hidden');
    }

    _addSectionTitle(title) {
        const div = document.createElement('div');
        div.className = 'px-4 py-2 text-[10px] font-black uppercase text-slate-400 bg-slate-50 dark:bg-slate-800/50';
        div.innerText = title;
        this.resultsContainer.appendChild(div);
    }

    _addResultItem(text, icon, onClick) {
        const btn = document.createElement('button');
        btn.className = 'w-full px-4 py-3 text-left text-sm hover:bg-primary/5 dark:hover:bg-primary/10 flex items-center gap-3 transition-colors border-b border-slate-100 dark:border-slate-800 last:border-0';
        btn.innerHTML = `
            <span class="material-symbols-outlined text-slate-400 text-lg">${icon}</span>
            <span class="truncate dark:text-slate-300">${text}</span>
        `;
        btn.onclick = onClick;
        this.resultsContainer.appendChild(btn);
    }

    _hideResults() {
        this.resultsContainer.classList.add('hidden');
    }
}