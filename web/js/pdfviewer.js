const viewer = document.getElementById('viewer');
const pdfjsLib = window['pdfjs-dist/build/pdf'];
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

let currentMatchIndex = 0;
let matchesInPdf = [];

async function renderPDF(pdfUrl, termo) {
  const pdfDoc_ = await pdfjsLib.getDocument(pdfUrl).promise;
  const pdfContainer = document.createElement('div');
  pdfContainer.className = 'viewer';
  viewer.innerHTML = '';
  viewer.appendChild(pdfContainer);

  currentMatchIndex = 0;
  matchesInPdf = [];

  for (let pageNum = 1; pageNum <= pdfDoc_.numPages; pageNum++) {
    const canvas = document.createElement('canvas');
    canvas.id = `page-${pageNum}`;
    pdfContainer.appendChild(canvas);

    const page = await pdfDoc_.getPage(pageNum);
    const viewport = page.getViewport({ scale: 1.5 });
    const context = canvas.getContext('2d');
    canvas.width = viewport.width;
    canvas.height = viewport.height;

    const renderContext = {
      canvasContext: context,
      viewport: viewport
    };

    await page.render(renderContext).promise;

    if (termo) {
      const pageMatches = await highlightText(page, termo, context, viewport);
      if (pageMatches.length > 0) {
        matchesInPdf.push({ pageNum, matches: pageMatches });
      }
    }
  }

  if (matchesInPdf.length > 0) {
    navigateToMatch();
    updateNavigationButtons();
  } else {
    alert('Nenhuma correspondência encontrada no PDF.');
  }

  prevButton.addEventListener('click', () => {
    if (currentMatchIndex > 0) {
      currentMatchIndex--;
      navigateToMatch();
    }
  });

  nextButton.addEventListener('click', () => {
    if (currentMatchIndex < matchesInPdf.length - 1) {
      currentMatchIndex++;
      navigateToMatch();
    }
  });
}

async function highlightText(page, searchTerm, context, viewport) {
  const textContent = await page.getTextContent();
  const regex = new RegExp(searchTerm, 'gi');
  let pageMatches = [];

  textContent.items.forEach((item) => {
    if (regex.test(item.str)) {
      const [x, y, width, height] = calculateTextBounds(item, viewport);
      context.fillStyle = 'rgba(255, 255, 0, 0.5)';
      context.fillRect(x, y - height, width, height);
      pageMatches.push({ x, y });
    }
  });

  return pageMatches;
}

function calculateTextBounds(item, viewport) {
  const transform = pdfjsLib.Util.transform(viewport.transform, item.transform);
  const x = transform[4];
  const y = transform[5];
  const width = item.width * viewport.scale;
  const height = item.height * viewport.scale;
  return [x, y, width, height];
}

function updateNavigationButtons() {
  prevButton.disabled = currentMatchIndex === 0;
  nextButton.disabled = currentMatchIndex === matchesInPdf.length - 1;
}

function navigateToMatch() {
  const match = matchesInPdf[currentMatchIndex];
  const canvas = document.getElementById(`page-${match.pageNum}`);
  if (canvas) {
    canvas.scrollIntoView({ behavior: 'smooth' });
  }
}