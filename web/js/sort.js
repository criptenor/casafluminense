const prevButton = document.getElementById('prevButton');
const nextButton = document.getElementById('nextButton');
const sortDateButton = document.getElementById('sortDateButton');
const sortQuantityButton = document.getElementById('sortQuantityButton');

sortDateButton.addEventListener('click', () => {
  let ascending = true;
  if (sortDateButton.dataset.order === 'asc') {
    ascending = false;
    sortDateButton.dataset.order = 'desc';
    sortDateButton.querySelector(".arrow").textContent = "↓";
  } else {
    sortDateButton.dataset.order = 'asc';
    sortDateButton.querySelector(".arrow").textContent = "↑";
  }
  updatePdfList(sortByDate(pdfs, ascending));
});

sortQuantityButton.addEventListener('click', () => {
  let ascending = true;
  if (sortQuantityButton.dataset.order === 'asc') {
    ascending = false;
    sortQuantityButton.dataset.order = 'desc';
    sortQuantityButton.querySelector(".arrow").textContent = "↓";
  } else {
    sortQuantityButton.dataset.order = 'asc';
    sortQuantityButton.querySelector(".arrow").textContent = "↑";
  }
  updatePdfList(sortByQuantity(pdfs, ascending));
});

// Função para ordenar por data
function sortByDate(pdfs, ascending = true) {
  return pdfs.sort((a, b) => {
    const dateA = new Date(a.data);
    const dateB = new Date(b.data);
    return ascending ? dateA - dateB : dateB - dateA;
  });
}

// Função para ordenar por quantidade de correspondências
function sortByQuantity(pdfs, ascending = true) {
  return pdfs.sort((a, b) => {
    return ascending ? a.quantidade_correspondencias - b.quantidade_correspondencias : b.quantidade_correspondencias - a.quantidade_correspondencias;
  });
}