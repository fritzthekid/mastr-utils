fetch("data/stromerzeuger_pv_500k_brd.csv")
  .then(response => response.text())
  .then(data => {
    const lines = data.trim().split("\n");
    const table = document.getElementById("pv-table");

    if (!table) return;

    // Kopfzeile erstellen
    const headerRow = document.createElement("tr");
    lines[0].split(";").forEach(col => {
      const th = document.createElement("th");
      th.textContent = col;
      headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    // Datenzeilen
    for (let i = 1; i < Math.min(lines.length, 15); i++) {
      const row = document.createElement("tr");
      lines[i].split(";").forEach(cell => {
        const td = document.createElement("td");
        td.textContent = parseInt(cell.replace(",", "."), 10) || 0;
        row.appendChild(td);
      });
      table.appendChild(row);
    }
  });
  
