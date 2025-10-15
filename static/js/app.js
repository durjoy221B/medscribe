// static/script.js
async function loadMedicines(url = '/medicines') {
    const response = await fetch(url);
    const data = await response.json();
    const tableBody = document.getElementById('medicineTable');
    tableBody.innerHTML = '';
    data.forEach(med => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${med['brand id']}</td>
            <td>${med['brand_name']}</td>
            <td>${med.type}</td>
            <td>${med.slug}</td>
            <td>${med['dosage form']}</td>
            <td>${med.generic}</td>
            <td>${med.strength}</td>
            <td>${med.manufacturer}</td>
            <td>${med['package container']}</td>
            <td>${med['Package Size']}</td>
        `;
        tableBody.appendChild(row);
    });
}

document.getElementById('search').addEventListener('input', async (e) => {
    const query = e.target.value;
    if (query) {
        loadMedicines(`/search?q=${query}`);
    } else {
        loadMedicines();
    }
});

loadMedicines();