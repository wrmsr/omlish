const container = document.getElementById('jsoneditor');
const jmespathInput = document.getElementById('jmespath-input');
const errorMessage = document.getElementById('error-message');
const historyDataList = document.getElementById('jmespath-history');

let jmespathHistory = [];

const options = {
  mode: 'tree',
      modes: ['code', 'form', 'text', 'tree', 'view', 'preview'],
      onError: function (err) {
    alert(err.toString());
  }
};

const editor = new JSONEditor(container, options);
editor.set(originalJsonData);
editor.expandAll();

let debounceTimer;

function updateHistory(expression) {
  if (!expression || jmespathHistory.includes(expression)) {
    return;
  }

  jmespathHistory.unshift(expression);

  historyDataList.innerHTML = '';
  jmespathHistory.forEach(item => {
    const option = document.createElement('option');
    option.value = item;
    historyDataList.appendChild(option);
  });
}

function updateView() {
  const expression = jmespathInput.value.trim();
  errorMessage.textContent = '';

  if (expression === '') {
    editor.set(originalJsonData);
    editor.expandAll();
    return;
  }

  try {
    const result = jmespath.search(originalJsonData, expression);
    editor.set(result);
    editor.expandAll();
    updateHistory(expression);
  } catch (err) {
    errorMessage.textContent = 'Invalid JMESPath expression';
  }
}

jmespathInput.addEventListener('input', () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(updateView, 50);
});

jmespathInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    clearTimeout(debounceTimer);
    updateView();
  }
});
