async function loadData() {
  const response = await fetch('data/data.csv');
  const text     = await response.text();

  // Parse CSV into array of objects
  const lines  = text.trim().split('\n');
  const header = lines[0].split(',');
  const rows   = lines.slice(1).map(line => {
    const values = line.split(',');
    return {
      date:               values[0],
      total_accounts:     parseInt(values[1]),
      new_since_last_month: parseInt(values[2])
    };
  });

  return rows;
}

async function renderCharts() {
  const data  = await loadData();
  const dates  = data.map(r => r.date);
  const totals = data.map(r => r.total_accounts);
  const news   = data.map(r => r.new_since_last_month);

  // Fill in the stat boxes
  document.getElementById('total').textContent   = totals[totals.length - 1].toLocaleString();
  document.getElementById('monthly').textContent = news[news.length - 1].toLocaleString();
  document.getElementById('updated').textContent = dates[dates.length - 1];

  // New accounts per month bar chart
  new Chart(document.getElementById('newChart'), {
    type: 'bar',
    data: {
      labels: dates,
      datasets: [{
        label:           'New accounts',
        data:            news,
        backgroundColor: '#4a9eff',
        borderRadius:    4
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales:  { y: { beginAtZero: true } }
    }
  });

  // Total accounts line chart
  new Chart(document.getElementById('totalChart'), {
    type: 'line',
    data: {
      labels: dates,
      datasets: [{
        label:           'Total accounts',
        data:            totals,
        borderColor:     '#ff6b35',
        backgroundColor: 'rgba(255, 107, 53, 0.1)',
        fill:            true,
        tension:         0.3
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales:  { y: { beginAtZero: false } }
    }
  });
}

renderCharts();
