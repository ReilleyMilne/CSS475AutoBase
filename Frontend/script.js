async function fetchPrimaryKey(tableName) {
  const res = await fetch(`http://127.0.0.1:5000/primary_key/${tableName}`);
  const data = await res.json();
  return data.COLUMN_NAME || null;
}

async function fetchTableData(tableName) {
  const table = document.getElementById("dataTable");
  table.innerHTML = "";

  try {
    const [pk, tableDataRes] = await Promise.all([
      fetchPrimaryKey(tableName),
      fetch(`http://127.0.0.1:5000/${tableName.toLowerCase()}`)
    ]);

    const data = await tableDataRes.json();
    if (!data || data.length === 0) {
      table.innerHTML = `<tr><td>No data found for ${tableName}</td></tr>`;
      return;
    }

    let headers = Object.keys(data[0]);
    if (pk && headers.includes(pk)) {
      headers = headers.sort((a, b) => (a === pk ? -1 : b === pk ? 1 : 0));
    }

    // Create header row
    const headerRow = document.createElement("tr");
    headers.forEach(header => {
      const th = document.createElement("th");
      th.textContent = header;
      headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    // Populate data rows
    data.forEach(row => {
      const tr = document.createElement("tr");
      headers.forEach(header => {
        const td = document.createElement("td");
        td.textContent = row[header];
        tr.appendChild(td);
      });
      table.appendChild(tr);
    });
  } catch (err) {
    console.error(err);
    table.innerHTML = `<tr><td>Error loading data for ${tableName}</td></tr>`;
  }
}

async function populateTableDropdown() {
  const select = document.getElementById("tableSelect");
  const res = await fetch("http://127.0.0.1:5000/tables");
  const tables = await res.json();

  tables.forEach(table => {
    const option = document.createElement("option");
    option.value = table;
    option.textContent = table;
    select.appendChild(option);
  });
}

// Automatically populate tables
populateTableDropdown();

// Handle dropdown + button
document.getElementById("loadBtn").addEventListener("click", () => {
  const tableName = document.getElementById("tableSelect").value;
  fetchTableData(tableName);
});
