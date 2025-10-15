class MedicineInventory {
    constructor() {
        this.medicines = [];
        this.filteredMedicines = [];
        this.currentPage = 1;
        this.perPage = 20;
        this.totalResults = 0;
        this.sortBy = 'brand_name';
        this.sortOrder = 'asc';
        this.filters = {
            query: '',
            type: '',
            dosage_form: '',
            search_type: 'brand_name' // New filter for search type
        };
        
        this.init();
    }
    
    async init() {
        await this.loadFilterOptions();
        await this.loadStatistics();
        await this.loadMedicines();
        this.bindEvents();
        this.initializeAnimations();
    }
    
    async loadFilterOptions() {
        try {
            const response = await fetch('/api/filters');
            const data = await response.json();
            
            this.populateFilterOptions('type-filter', data.types);
            this.populateFilterOptions('dosage-filter', data.dosage_forms);
            // Removed manufacturer filter
        } catch (error) {
            console.error('Error loading filter options:', error);
        }
    }
    
    populateFilterOptions(elementId, options) {
        const select = document.getElementById(elementId);
        select.innerHTML = `<option value="">All ${elementId.replace('-filter', '').replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}</option>`;
        
        options.forEach(option => {
            if (option) {
                const optionElement = document.createElement('option');
                optionElement.value = option;
                optionElement.textContent = option;
                select.appendChild(optionElement);
            }
        });
    }
    
    async loadStatistics() {
        try {
            const response = await fetch('/api/statistics');
            const stats = await response.json();
            
            // Animate statistics
            this.animateCounter('total-medicines', stats.total_medicines);
            this.animateCounter('total-manufacturers', stats.total_manufacturers);
            this.animateCounter('total-types', stats.total_types);
            this.animateCounter('avg-price', Math.round(stats.average_price), '৳');
            
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }
    
    animateCounter(elementId, targetValue, prefix = '') {
        const element = document.getElementById(elementId);
        const duration = 2000;
        const startValue = 0;
        const startTime = performance.now();
        
        const updateCounter = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
            element.textContent = prefix + currentValue.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        };
        
        requestAnimationFrame(updateCounter);
    }
    
    async loadMedicines() {
        try {
            this.showLoading();
            
            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: this.perPage,
                sort_by: this.sortBy,
                sort_order: this.sortOrder,
                search_type: this.filters.search_type, // Include search type
                ...(this.filters.query && { query: this.filters.query }),
                ...(this.filters.type && { type: this.filters.type }),
                ...(this.filters.dosage_form && { dosage_form: this.filters.dosage_form })
            });
            
            const response = await fetch(`/api/medicines/search?${params}`);
            const data = await response.json();
            
            this.medicines = data.medicines;
            this.filteredMedicines = data.medicines;
            this.totalResults = data.total;
            this.currentPage = data.page;
            
            this.renderMedicines();
            this.updatePagination();
            this.hideLoading();
            
        } catch (error) {
            console.error('Error loading medicines:', error);
            this.showError();
        }
    }
    
    renderMedicines() {
        const tbody = document.getElementById('medicine-table-body');
        const loadingRow = document.getElementById('loading-row');
        
        if (loadingRow) {
            loadingRow.remove();
        }
        
        if (this.filteredMedicines.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="px-6 py-12 text-center">
                        <div class="text-text-secondary">
                            <svg class="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.47-.881-6.08-2.33"></path>
                            </svg>
                            <p class="text-lg font-medium">No medicines found</p>
                            <p class="text-sm">Try adjusting your search criteria</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = this.filteredMedicines.map((medicine, index) => `
            <tr class="table-row hover:bg-slate-50" data-medicine-id="${medicine.id}">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-text-primary">${medicine.brand_name || 'N/A'}</div>
                    <div class="text-xs text-text-secondary">${medicine.slug || ''}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-text-primary">${medicine.generic || 'N/A'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${this.getTypeBadgeClass(medicine.type)}">
                        ${medicine.type || 'N/A'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-text-primary">${medicine.dosage_form || 'N/A'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-text-primary">${medicine.strength || 'N/A'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-text-primary">${medicine.manufacturer || 'N/A'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-medical-green">
                        ${medicine.price ? '৳' + medicine.price.toFixed(2) : 'N/A'}
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button class="text-medical-blue hover:text-blue-600 mr-3" onclick="viewMedicine(${medicine.id})">
                        View
                    </button>
                    <button class="text-medical-teal hover:text-cyan-600" onclick="editMedicine(${medicine.id})">
                        Edit
                    </button>
                </td>
            </tr>
        `).join('');
        
        // Animate rows
        this.animateTableRows();
        
        // Update results count
        document.getElementById('results-count').textContent = 
            `${this.totalResults} medicine${this.totalResults !== 1 ? 's' : ''} found`;
    }
    
    getTypeBadgeClass(type) {
        const classes = {
            'allopathic': 'bg-blue-100 text-blue-800',
            'herbal': 'bg-green-100 text-green-800',
            'ayurvedic': 'bg-orange-100 text-orange-800',
            'homeopathic': 'bg-purple-100 text-purple-800'
        };
        return classes[type?.toLowerCase()] || 'bg-gray-100 text-gray-800';
    }
    
    animateTableRows() {
        const rows = document.querySelectorAll('.table-row');
        rows.forEach((row, index) => {
            row.style.opacity = '0';
            row.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                anime({
                    targets: row,
                    opacity: 1,
                    translateY: 0,
                    duration: 600,
                    easing: 'easeOutCubic',
                    delay: index * 50
                });
            }, 100);
        });
    }
    
    updatePagination() {
        const totalPages = Math.ceil(this.totalResults / this.perPage);
        const paginationControls = document.getElementById('pagination-controls');
        const showingFrom = document.getElementById('showing-from');
        const showingTo = document.getElementById('showing-to');
        const totalResultsEl = document.getElementById('total-results');
        
        // Update showing info
        const from = (this.currentPage - 1) * this.perPage + 1;
        const to = Math.min(this.currentPage * this.perPage, this.totalResults);
        
        showingFrom.textContent = from;
        showingTo.textContent = to;
        totalResultsEl.textContent = this.totalResults;
        
        // Create pagination controls
        let paginationHTML = '';
        
        // Previous button
        paginationHTML += `
            <button class="px-3 py-2 text-sm font-medium text-text-secondary bg-white border border-slate-200 rounded-lg hover:bg-slate-50 ${this.currentPage === 1 ? 'opacity-50 cursor-not-allowed' : ''}" 
                    ${this.currentPage === 1 ? 'disabled' : ''} 
                    onclick="window.inventory.goToPage(${this.currentPage - 1})">
                Previous
            </button>
        `;
        
        // Page numbers
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <button class="px-3 py-2 text-sm font-medium ${i === this.currentPage ? 'text-white bg-medical-blue' : 'text-text-secondary bg-white border border-slate-200 hover:bg-slate-50'} rounded-lg" 
                        onclick="window.inventory.goToPage(${i})">
                    ${i}
                </button>
            `;
        }
        
        // Next button
        paginationHTML += `
            <button class="px-3 py-2 text-sm font-medium text-text-secondary bg-white border border-slate-200 rounded-lg hover:bg-slate-50 ${this.currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : ''}" 
                    ${this.currentPage === totalPages ? 'disabled' : ''} 
                    onclick="window.inventory.goToPage(${this.currentPage + 1})">
                Next
            </button>
        `;
        
        paginationControls.innerHTML = paginationHTML;
    }
    
    goToPage(page) {
        const totalPages = Math.ceil(this.totalResults / this.perPage);
        if (page >= 1 && page <= totalPages && page !== this.currentPage) {
            this.currentPage = page;
            this.loadMedicines();
        }
    }
    
    bindEvents() {
        // Search input
        const searchInput = document.getElementById('main-search');
        let searchTimeout;
        
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.filters.query = e.target.value;
                this.currentPage = 1;
                this.loadMedicines();
            }, 300);
        });
        
        // Filter dropdowns
        document.getElementById('type-filter').addEventListener('change', (e) => {
            this.filters.type = e.target.value;
            this.currentPage = 1;
            this.loadMedicines();
        });
        
        document.getElementById('dosage-filter').addEventListener('change', (e) => {
            this.filters.dosage_form = e.target.value;
            this.currentPage = 1;
            this.loadMedicines();
        });
        
        // New search type filter
        document.getElementById('search-type-filter').addEventListener('change', (e) => {
            this.filters.search_type = e.target.value;
            this.currentPage = 1;
            this.loadMedicines();
        });
        
        // Clear filters
        document.getElementById('clear-filters').addEventListener('click', () => {
            this.clearFilters();
        });
        
        // Export button
        document.getElementById('export-btn').addEventListener('click', () => {
            this.exportToCSV();
        });
        
        // Sortable columns
        document.querySelectorAll('[data-sort]').forEach(header => {
            header.addEventListener('click', () => {
                const sortBy = header.dataset.sort;
                this.sortMedicines(sortBy);
            });
        });
    }
    
    sortMedicines(sortBy) {
        if (this.sortBy === sortBy) {
            this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortBy = sortBy;
            this.sortOrder = 'asc';
        }
        
        this.currentPage = 1;
        this.loadMedicines();
        
        // Update sort indicators
        document.querySelectorAll('[data-sort]').forEach(header => {
            header.classList.remove('sort-asc', 'sort-desc');
            if (header.dataset.sort === sortBy) {
                header.classList.add(this.sortOrder === 'asc' ? 'sort-asc' : 'sort-desc');
            }
        });
    }
    
    clearFilters() {
        this.filters = {
            query: '',
            type: '',
            dosage_form: '',
            search_type: 'brand_name' // Reset search type
        };
        
        document.getElementById('main-search').value = '';
        document.getElementById('type-filter').value = '';
        document.getElementById('dosage-filter').value = '';
        document.getElementById('search-type-filter').value = 'brand_name'; // Reset search type dropdown
        
        this.currentPage = 1;
        this.loadMedicines();
    }
    
    exportToCSV() {
        if (this.filteredMedicines.length === 0) {
            alert('No data to export');
            return;
        }
        
        const headers = ['Brand Name', 'Generic Name', 'Type', 'Dosage Form', 'Strength', 'Manufacturer', 'Price'];
        const csvContent = [
            headers.join(','),
            ...this.filteredMedicines.map(med => [
                `"${med.brand_name || ''}"`,
                `"${med.generic || ''}"`,
                `"${med.type || ''}"`,
                `"${med.dosage_form || ''}"`,
                `"${med.strength || ''}"`,
                `"${med.manufacturer || ''}"`,
                med.price || 0
            ].join(','))
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `medicine_inventory_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    }
    
    showLoading() {
        const tbody = document.getElementById('medicine-table-body');
        tbody.innerHTML = `
            <tr id="loading-row">
                <td colspan="8" class="px-6 py-12 text-center">
                    <div class="flex items-center justify-center space-x-2">
                        <div class="w-4 h-4 bg-medical-blue rounded-full animate-pulse"></div>
                        <div class="w-4 h-4 bg-medical-blue rounded-full animate-pulse" style="animation-delay: 0.2s;"></div>
                        <div class="w-4 h-4 bg-medical-blue rounded-full animate-pulse" style="animation-delay: 0.4s;"></div>
                    </div>
                    <p class="text-text-secondary mt-2">Loading medicines...</p>
                </td>
            </tr>
        `;
    }
    
    hideLoading() {
        const loadingRow = document.getElementById('loading-row');
        if (loadingRow) {
            loadingRow.remove();
        }
    }
    
    showError() {
        const tbody = document.getElementById('medicine-table-body');
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="px-6 py-12 text-center">
                    <div class="text-text-secondary">
                        <svg class="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                        </svg>
                        <p class="text-lg font-medium">Error loading medicines</p>
                        <p class="text-sm">Please try refreshing the page</p>
                    </div>
                </td>
            </tr>
        `;
    }
    
    initializeAnimations() {
        // Animate search bar focus
        const searchInput = document.getElementById('main-search');
        searchInput.addEventListener('focus', () => {
            anime({
                targets: searchInput,
                scale: 1.02,
                duration: 300,
                easing: 'easeOutCubic'
            });
        });
        
        searchInput.addEventListener('blur', () => {
            anime({
                targets: searchInput,
                scale: 1,
                duration: 300,
                easing: 'easeOutCubic'
            });
        });
        
        // Animate filter dropdowns
        document.querySelectorAll('select').forEach(select => {
            select.addEventListener('focus', () => {
                anime({
                    targets: select,
                    scale: 1.02,
                    duration: 200,
                    easing: 'easeOutCubic'
                });
            });
            
            select.addEventListener('blur', () => {
                anime({
                    targets: select,
                    scale: 1,
                    duration: 200,
                    easing: 'easeOutCubic'
                });
            });
        });
    }
}

// Global functions for table actions
async function viewMedicine(medicineId) {
    const viewModal = document.getElementById('view-medicine-modal');
    const closeBtn = document.getElementById('view-medicine-close-btn');

    try {
        const response = await fetch(`/api/medicines/${medicineId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const medicine = await response.json();

        document.getElementById('view-brand-name').textContent = medicine.brand_name || 'N/A';
        document.getElementById('view-generic-name').textContent = medicine.generic || 'N/A';
        document.getElementById('view-type').textContent = medicine.type || 'N/A';
        document.getElementById('view-dosage-form').textContent = medicine.dosage_form || 'N/A';
        document.getElementById('view-strength').textContent = medicine.strength || 'N/A';
        document.getElementById('view-manufacturer').textContent = medicine.manufacturer || 'N/A';
        document.getElementById('view-price').textContent = medicine.price ? '৳' + medicine.price.toFixed(2) : 'N/A';

        viewModal.classList.remove('hidden');

        closeBtn.onclick = () => {
            viewModal.classList.add('hidden');
        };

        window.onclick = (event) => {
            if (event.target == viewModal) {
                viewModal.classList.add('hidden');
            }
        };

    } catch (error) {
        console.error('Error viewing medicine:', error);
        alert('Failed to load medicine details.');
    }
}

async function editMedicine(medicineId) {
    const editModal = document.getElementById('edit-medicine-modal');
    const closeBtn = document.getElementById('edit-medicine-close-btn');
    const editForm = document.getElementById('edit-medicine-form');

    try {
        const response = await fetch(`/api/medicines/${medicineId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const medicine = await response.json();

        document.getElementById('edit-medicine-id').value = medicine.id;
        document.getElementById('edit-brand-name').value = medicine.brand_name || '';
        document.getElementById('edit-generic-name').value = medicine.generic || '';
        document.getElementById('edit-type').value = medicine.type || '';
        document.getElementById('edit-dosage-form').value = medicine.dosage_form || '';
        document.getElementById('edit-strength').value = medicine.strength || '';
        document.getElementById('edit-manufacturer').value = medicine.manufacturer || '';
        document.getElementById('edit-price').value = medicine.price || '';

        editModal.classList.remove('hidden');

        closeBtn.onclick = () => {
            editModal.classList.add('hidden');
        };

        window.onclick = (event) => {
            if (event.target == editModal) {
                editModal.classList.add('hidden');
            }
        };

        editForm.onsubmit = async (e) => {
            e.preventDefault();
            const updatedMedicine = {
                brand_name: document.getElementById('edit-brand-name').value,
                generic: document.getElementById('edit-generic-name').value,
                type: document.getElementById('edit-type').value,
                dosage_form: document.getElementById('edit-dosage-form').value,
                strength: document.getElementById('edit-strength').value,
                manufacturer: document.getElementById('edit-manufacturer').value,
                price: parseFloat(document.getElementById('edit-price').value) || 0
            };

            try {
                const updateResponse = await fetch(`/api/medicines/${medicineId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(updatedMedicine)
                });

                if (!updateResponse.ok) {
                    throw new Error(`HTTP error! status: ${updateResponse.status}`);
                }

                alert('Medicine updated successfully!');
                editModal.classList.add('hidden');
                window.inventory.loadMedicines(); // Reload medicines to reflect changes

            } catch (updateError) {
                console.error('Error updating medicine:', updateError);
                alert('Failed to update medicine.');
            }
        };

    } catch (error) {
        console.error('Error editing medicine:', error);
        alert('Failed to load medicine details for editing.');
    }
}