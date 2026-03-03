// 1. Traducciones
L.drawLocal.draw.toolbar.buttons.polygon = 'Dibujar un sector territorial';
L.drawLocal.draw.toolbar.actions.title = 'Cancelar dibujo';
L.drawLocal.draw.toolbar.actions.text = 'Cancelar';
L.drawLocal.draw.toolbar.undo.title = 'Borrar último punto';
L.drawLocal.draw.toolbar.undo.text = 'Borrar último punto';
L.drawLocal.draw.handlers.polygon.tooltip.start = 'Haz clic para empezar a delimitar el sector.';
L.drawLocal.draw.handlers.polygon.tooltip.cont = 'Haz clic para continuar dibujando.';
L.drawLocal.draw.handlers.polygon.tooltip.end = 'Haz clic en el primer punto para cerrar el sector.';

L.drawLocal.edit.toolbar.actions.save.text = 'Guardar cambios';
L.drawLocal.edit.toolbar.actions.cancel.text = 'Cancelar';
L.drawLocal.edit.handlers.edit.tooltip.text = 'Arrastra los puntos para moverlos.';

// Traducciones Leaflet Draw
L.drawLocal.draw.handlers.polygon.tooltip.start = 'Haz clic para empezar el sector.';
L.drawLocal.draw.handlers.polygon.tooltip.cont = 'Haz clic para continuar dibujando.';
L.drawLocal.draw.handlers.polygon.tooltip.end = 'Haz clic en el primer punto para cerrar.';

class TerritoryDesigner {
    constructor(mapId, service) {
        this.service = service;
        this.map = L.map(mapId).setView([-33.012, -71.543], 14);
        this.drawnItems = new L.FeatureGroup().addTo(this.map);
        this.layersStore = {};
        this.selectedColor = '#3b82f6';
        this.currentDrawingLayer = null;
        this.editingSectorId = null;

        this.initMap();
        this.initDrawControl();

        // Carga inicial desde el servidor
        this.loadExistingSectors();

        setTimeout(() => this.map.invalidateSize(), 400);
    }

    // --- MÉTODOS DE CARGA ---

    async loadExistingSectors() {
        this.updateStatus('Cargando sectores...');
        try {
            const sectores = await this.service.getAll();
            sectores.forEach(sector => this.renderSector(sector));
            this.updateStatus('Sectores cargados correctamente.');
        } catch (error) {
            console.error(error);
            this.updateStatus('Error al cargar sectores existentes.');
        }
    }

    renderSector(sector) {
        // Convierte el GeoJSON almacenado en una capa de Leaflet
        const layer = L.geoJSON(sector.geojson, {
            style: {
                color: sector.color,
                fillColor: sector.color,
                fillOpacity: 0.3,
                weight: 3
            }
        }).getLayers()[0];

        if (layer) {
            this.layersStore[sector.id] = layer;
            this.drawnItems.addLayer(layer);
            this.addSectorToList(sector);
        }
    }

    // --- MÉTODOS DE PERSISTENCIA ---

    async saveSector() {
        const nameInput = document.getElementById('sector-name');
        const popInput = document.getElementById('poblacion');

        if (!nameInput.value || !this.currentDrawingLayer) {
            alert("Completa el nombre y dibuja un sector.");
            return;
        }

        const payload = {
            nombre: nameInput.value,
            poblacion: popInput.value || 0,
            color: this.selectedColor,
            geojson: this.currentDrawingLayer.toGeoJSON()
        };

        try {
            const data = await this.service.save(payload);

            if (data.status === 'success') {
                // Quitamos la capa temporal y renderizamos la oficial con el ID de la DB
                this.map.removeLayer(this.currentDrawingLayer);
                this.renderSector({
                    id: data.id,
                    ...payload
                });

                // Reset UI
                this.currentDrawingLayer = null;
                nameInput.value = '';
                popInput.value = '';
                document.getElementById('btn-save').classList.replace('flex', 'hidden');
                this.updateStatus('Guardado en el servidor.');
            }
        } catch (error) {
            alert(error.message);
        }
    }

    // --- MÉTODOS DE UI (Igual que tu versión estable) ---
    initMap() {
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(this.map);
    }
    

    initDrawControl() {
        this.drawHandler = new L.Draw.Polygon(this.map, {
            allowIntersection: false,
            shapeOptions: { color: this.selectedColor, fillOpacity: 0.3, weight: 3 }
        });

        this.map.on(L.Draw.Event.CREATED, (e) => {
            this.currentDrawingLayer = e.layer;
            this.map.addLayer(this.currentDrawingLayer);
            const btnSave = document.getElementById('btn-save');
            btnSave.classList.replace('hidden', 'flex');
            btnSave.disabled = false;
        });
    }

    startDrawing() {
        this.drawHandler.enable();
        this.updateStatus('Dibujando sector...');
    }

    setColor(color, element) {
        this.selectedColor = color;
        document.querySelectorAll('#color-palette button, #color-palette div').forEach(b => b.classList.remove('active-color-ring'));
        if (element) element.classList.add('active-color-ring');
        this.drawHandler.setOptions({ shapeOptions: { color: color, fillColor: color } });
    }

    updateStatus(text) {
        document.getElementById('status-text').innerText = text;
    }

    addSectorToList(sector) {
        const list = document.getElementById('sectors-list');
        const item = document.createElement('div');
        // Dentro de addSectorToList, añade estos atributos al div principal del item:
        item.onmouseenter = () => this.highlightSector(sector.id, true);
        item.onmouseleave = () => this.highlightSector(sector.id, false);
        item.id = `item-${sector.id}`;
        item.className = "flex items-center justify-between p-3 rounded-2xl bg-white border border-slate-100 hover:shadow-md transition-all group mb-2";

        item.innerHTML = `
        <div class="flex items-center gap-3 cursor-pointer flex-1" onclick="window.designer.focusSector(${sector.id})">
            <div class="size-4 rounded-full shadow-inner" style="background-color: ${sector.color}"></div>
            <div class="flex flex-col">
                <span class="text-sm font-bold text-slate-700">${sector.nombre}</span>
                <span class="text-[10px] text-slate-400 font-medium">${sector.poblacion} Habitantes</span>
            </div>
        </div>
        <div class="flex items-center gap-1">
            <button onclick="window.designer.focusSector(${sector.id})" class="p-2 text-slate-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors" title="Centrar mapa">
                <span class="material-symbols-outlined text-lg">location_searching</span>
            </button>
            <button onclick="window.designer.editSector(${sector.id})" class="p-2 text-slate-400 hover:text-amber-500 hover:bg-amber-50 rounded-lg transition-colors" title="Editar">
                <span class="material-symbols-outlined text-lg">edit</span>
            </button>
            <button onclick="window.designer.deleteSector(${sector.id})" class="p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors" title="Eliminar">
                <span class="material-symbols-outlined text-lg">delete</span>
            </button>
        </div>
    `;
        list.prepend(item);
    }

    focusSector(id) {
        const layer = this.layersStore[id];
        if (layer) {
            // 1. Obtener los límites del polígono
            const bounds = layer.getBounds();

            // 2. Desplazamiento animado
            this.map.flyToBounds(bounds, {
                padding: [50, 50], // Espacio de seguridad en los bordes
                duration: 1.5      // Segundos que dura la animación
            });

            // 3. Efecto visual de "Destello" para identificar cuál es
            layer.setStyle({ fillOpacity: 0.8, weight: 5 });
            setTimeout(() => {
                layer.setStyle({ fillOpacity: 0.3, weight: 3 });
            }, 1500);
        } else {
            console.warn(`No se encontró la capa para el sector ${id}`);
        }
    }
    // --- DENTRO DE LA CLASE TerritoryDesigner ---

    async deleteSector(id) {
        // 1. Verificación de seguridad
        if (!confirm('¿Estás seguro de eliminar este sector permanentemente?')) return;

        try {
            // 2. Llamada al servicio para borrar en Django
            const success = await this.service.delete(id);

            if (success) {
                // 3. Eliminar del Mapa
                const layer = this.layersStore[id];
                if (layer) {
                    this.drawnItems.removeLayer(layer);
                }

                // 4. Eliminar de la Lista UI
                const item = document.getElementById(`item-${id}`);
                if (item) item.remove();

                // 5. Limpiar memoria local
                delete this.layersStore[id];
                this.updateStatus('Sector eliminado del sistema.');
            }
        } catch (error) {
            console.error(error);
            alert("Error al eliminar: " + error.message);
        }
    }

    editSector(id) {
        const layer = this.layersStore[id];
        if (!layer) {
            console.error("No se encontró la capa para el ID:", id);
            return;
        }

        // Si ya estábamos editando otro, lo cerramos
        if (this.editingSectorId && this.editingSectorId !== id) {
            this.finishEditing();
        }

        this.editingSectorId = id;
        this.focusSector(id);

        // Resaltado en la lista
        const listItem = document.getElementById(`item-${id}`);
        if (listItem) listItem.classList.add('editing-active');

        // Habilitar edición de Leaflet (los puntos blancos)
        layer.editing.enable();

        // UI: Cambiar botones del panel
        document.getElementById('btn-draw').classList.add('hidden');
        const btnSave = document.getElementById('btn-save');

        btnSave.innerHTML = `<span class="material-symbols-outlined text-sm">task_alt</span> Finalizar Edición`;
        btnSave.classList.replace('bg-emerald-500', 'bg-blue-600');
        btnSave.classList.replace('hidden', 'flex');
        btnSave.disabled = false;

        // Cambiamos el comportamiento del botón temporalmente
        btnSave.onclick = () => this.finishEditing();

        this.updateStatus('Editando sector... Arrastra los vértices.');
    }
    async finishEditing() {
        if (!this.editingSectorId) return;

        const id = this.editingSectorId;
        const layer = this.layersStore[id];

        if (layer) {
            layer.editing.disable();

            // 1. Capturar los nuevos datos
            const payload = {
                id: id,
                geojson: layer.toGeoJSON()
            };

            try {
                // 2. Guardar en el servidor
                await this.service.update(id, payload);
                this.updateStatus('Cambios guardados correctamente.');
            } catch (error) {
                alert("Error al actualizar: " + error.message);
                return; // Salimos si hay error para no resetear la UI mal
            }
        }

        // 3. LIMPIEZA DE UI: Volver al estado inicial

        // Quitar resaltado de la lista
        const listItem = document.getElementById(`item-${id}`);
        if (listItem) listItem.classList.remove('editing-active');

        // Resetear botones
        const btnDraw = document.getElementById('btn-draw');
        const btnSave = document.getElementById('btn-save');

        // Mostramos el botón de "Iniciar Trazado" y ocultamos el de "Guardar/Finalizar"
        btnDraw.classList.remove('hidden');
        btnSave.classList.replace('flex', 'hidden'); // Esto es clave para que no se quede visible

        // IMPORTANTE: Restaurar la función original de guardado para el futuro
        btnSave.onclick = () => this.saveSector();
        btnSave.innerHTML = `<span class="material-symbols-outlined text-sm">check_circle</span> Confirmar y Guardar`;

        this.editingSectorId = null;
    }
    // Resaltar sector desde la lista
    highlightSector(id, isHover) {
        const layer = this.layersStore[id];
        if (layer) {
            if (isHover) {
                layer.setStyle({ fillOpacity: 0.7, weight: 5, dashArray: '5, 5' });
                layer.bringToFront();
            } else {
                layer.setStyle({ fillOpacity: 0.3, weight: 3, dashArray: '' });
            }
        }
    }
}



const SectorService = {
    // Helper para obtener el token CSRF de las cookies
    getCsrfToken() {
        return document.cookie.split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
    },

    async getAll() {
        const response = await fetch('/api/get_all_sectors'); // Asegúrate que esta URL coincida con tu urls.py
        if (!response.ok) throw new Error('Error al obtener sectores');
        return await response.json();
    },

    async save(payload) {
        const response = await fetch('/sectorization/save_sector', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Error al guardar');
        }
        return await response.json();
    },
    // Actualizar sector existente
    async update(id, payload) {
        const response = await fetch(`/sectorization/update_sector/${id}`, {
            method: 'POST', // O PUT si lo prefieres
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.getCsrfToken() },
            body: JSON.stringify(payload)
        });
        return response.ok;
    },

    // Borrar sector
    async delete(id) {
        const response = await fetch(`/sectorization/delete_sector/${id}`, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': this.getCsrfToken() }
        });
        if (!response.ok) throw new Error('No se pudo eliminar en el servidor');
        return true;
    },
};