const searchForm = document.getElementById('searchForm');
const searchText = document.getElementById('search');
const pdfList = document.getElementById('pdfList'); 

searchForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const termo = searchText.value.trim();
  if (termo) {
    pdfs = await buscarPDFs(termo);
    if (pdfs.length > 0) {
      updatePdfList(pdfs);
    } else {
      alert('Nenhum PDF encontrado para o termo fornecido.');
    }
  } else {
    alert('Digite um termo para busca.');
  }
});

async function buscarPDFs(termo) {
  const response = await fetch('http://localhost:5000/encontrar-pdfs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ termo: termo })
  });

  if (response.ok) {
    const data = await response.json();
    return data.pdfs;
  } else {
    console.error("Erro ao buscar PDFs:", response.statusText);
    return [];
  }
}

function updatePdfList(pdfs) {
  pdfList.innerHTML = '';
  pdfs.forEach((pdf, index) => {
    const li = document.createElement('li');
    li.style.animationDelay = `${index * 0.5}s`;
    li.innerHTML = `<div class="card">
                      <div class="card-container">
                        <div class="left">
                          <div class="status-ind"></div>
                        </div>
                        <div class="right">
                          <div class="text-wrap">
                            <p class="text-content">
                              <a class="text-link" href="#">${pdf.cidade}</a>
                            </p>
                            <p class="time"><a class="text-link" href="#">${pdf.quantidade_correspondencias}</a> Correspondências para <a class="text-link" href="#">${pdf.termo}</a></p>
                          </div>
                          <div class="button-wrap">
                            <button class="primary-cta">Clique Aqui</button>
                            <button class="secondary-cta">Data do boletim:<a class="text-link" href="#"> ${pdf.data}</a></button>
                          </div>
                        </div>
                      </div>
                    </div>`;
    li.addEventListener('click', async () => {
      const pdfUrl = `http://localhost:5000/boletim_dc/${pdf.nome_pdf}`;
      await renderPDF(pdfUrl, searchText.value.trim());
    });
    pdfList.appendChild(li);
  });
}