const token = document.querySelector('meta[name="local-token"]').content;
const form = document.getElementById('image-form');
const submit = document.getElementById('submit-btn');
const status = document.getElementById('status');
const source = document.getElementById('source-image');
const wrapper = document.getElementById('upload-wrapper');
const savedInput = document.getElementById('saved-image');
const savedChoice = document.getElementById('saved-image-choice');
const savedThumb = document.getElementById('saved-image-thumb');
const savedName = document.getElementById('saved-image-name');
const editCurrentButton = document.getElementById('edit-current-btn');
const download = document.getElementById('download-btn');
const downloadFormat = document.getElementById('download-format');
let selectedFilename = null;
let mode = 'generate';

function setMode(nextMode) {
  mode = nextMode;
  for (const tab of document.querySelectorAll('[data-mode]')) {
    const active = tab.dataset.mode === mode;
    tab.classList.toggle('active', active);
    tab.setAttribute('aria-selected', String(active));
  }
  wrapper.classList.toggle('hidden', mode !== 'edit');
  source.required = mode === 'edit' && !savedInput.value;
  submit.textContent = mode === 'edit' ? '✦ Editar imagen' : '✦ Generar imagen';
  status.textContent = '';
}

function clearSavedImage() {
  savedInput.value = '';
  savedChoice.classList.add('hidden');
  savedThumb.removeAttribute('src');
  savedName.textContent = '';
  source.required = mode === 'edit';
}

function selectSavedImage(filename) {
  savedInput.value = filename;
  savedName.textContent = filename;
  savedThumb.src = `/imagenes/${encodeURIComponent(filename)}`;
  savedChoice.classList.remove('hidden');
  source.value = '';
  setMode('edit');
  document.getElementById('prompt').focus();
}

editCurrentButton.addEventListener('click', () => {
  if (selectedFilename) selectSavedImage(selectedFilename);
});
document.getElementById('clear-saved-image').addEventListener('click', clearSavedImage);
source.addEventListener('change', () => {
  if (source.files.length) clearSavedImage();
});

function updateDownloadLink() {
  if (!selectedFilename) return;
  const extension = downloadFormat.value;
  download.href = `/api/download/${encodeURIComponent(selectedFilename)}?format=${extension}`;
  download.download = selectedFilename.replace(/\.webp$/i, `.${extension}`);
}

downloadFormat.addEventListener('change', updateDownloadLink);

for (const tab of document.querySelectorAll('[data-mode]')) {
  tab.addEventListener('click', () => setMode(tab.dataset.mode));
}

function showImage(url, filename) {
  const image = document.getElementById('preview-image');
  image.src = url;
  image.classList.remove('hidden');
  document.getElementById('empty-state').classList.add('hidden');
  document.getElementById('preview').classList.remove('empty');
  selectedFilename = filename;
  editCurrentButton.classList.remove('hidden');
  updateDownloadLink();
  document.getElementById('download-controls').classList.remove('hidden');
}

async function refreshGallery() {
  try {
    const response = await fetch('/api/gallery');
    if (!response.ok) throw new Error('No se pudo cargar la galería.');
    const data = await response.json();
    const gallery = document.getElementById('gallery');
    gallery.replaceChildren();
    if (!data.images.length) {
      const p = document.createElement('p');
      p.className = 'muted';
      p.textContent = 'Todavía no hay imágenes guardadas.';
      gallery.append(p);
      return;
    }
    for (const item of data.images) {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'gallery-item';
      button.title = 'Ver imagen';
      const img = document.createElement('img');
      img.src = item.url;
      img.alt = 'Creación guardada';
      img.loading = 'lazy';
      button.append(img);
      button.addEventListener('click', () => showImage(item.url, item.filename));
      gallery.append(button);
    }
  } catch (error) {
    status.textContent = error.message;
    status.className = 'status error';
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (mode === 'edit' && source.files[0]?.size > 12 * 1024 * 1024) {
    status.textContent = 'El archivo supera los 12 MB.';
    status.className = 'status error';
    return;
  }
  submit.disabled = true;
  submit.textContent = 'Generando…';
  status.className = 'status';
  status.textContent = 'Procesando la solicitud. Puede tardar un poco.';
  try {
    const response = await fetch(mode === 'edit' ? '/api/edit' : '/api/generate', {
      method: 'POST',
      headers: { 'X-Local-Token': token },
      body: new FormData(form),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'No se pudo generar la imagen.');
    showImage(data.url, data.filename);
    status.textContent = '¡Imagen lista! Se guardó en tu PC.';
    await refreshGallery();
  } catch (error) {
    status.className = 'status error';
    status.textContent = error.message;
  } finally {
    submit.disabled = false;
    submit.textContent = mode === 'edit' ? '✦ Editar imagen' : '✦ Generar imagen';
  }
});

document.getElementById('refresh-gallery').addEventListener('click', refreshGallery);
refreshGallery();


const apiKeyInput = document.getElementById('api-key-input');
const rememberApiKey = document.getElementById('remember-api-key');
const keyState = document.getElementById('api-key-state');
const keyFeedback = document.getElementById('key-feedback');
const saveKeyButton = document.getElementById('save-api-key');
const forgetKeyButton = document.getElementById('forget-api-key');

function updateKeyState(data) {
  const sources = {
    saved: '✓ Clave guardada en Windows',
    session: '✓ Clave activa esta sesión',
    environment: '✓ Clave configurada en .env',
    missing: 'Sin configurar',
  };
  keyState.textContent = sources[data.source] || 'Sin configurar';
  keyState.classList.toggle('configured', Boolean(data.configured));
  forgetKeyButton.disabled = data.source === 'missing' || data.source === 'environment';
}

async function refreshKeyState() {
  try {
    const response = await fetch('/api/key', {
      headers: {'X-Local-Token': token},
      cache: 'no-store',
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'No se pudo comprobar la clave.');
    updateKeyState(data);
  } catch (error) {
    keyState.textContent = 'No disponible';
    keyFeedback.textContent = error.message;
    keyFeedback.classList.add('error');
  }
}

saveKeyButton.addEventListener('click', async () => {
  const value = apiKeyInput.value.trim();
  if (value.length < 10) {
    keyFeedback.textContent = 'Introduce tu clave API.';
    keyFeedback.classList.add('error');
    return;
  }
  saveKeyButton.disabled = true;
  keyFeedback.textContent = 'Configurando…';
  keyFeedback.classList.remove('error');
  try {
    const response = await fetch('/api/key', {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'X-Local-Token': token},
      body: JSON.stringify({api_key: value, remember: rememberApiKey.checked}),
      cache: 'no-store',
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'No se pudo guardar la clave.');
    apiKeyInput.value = '';
    updateKeyState(data);
    keyFeedback.textContent = data.source === 'saved'
      ? 'Clave guardada de forma segura. Podrás usarla al volver a abrir la aplicación.'
      : 'Clave disponible hasta cerrar la aplicación.';
  } catch (error) {
    keyFeedback.textContent = error.message;
    keyFeedback.classList.add('error');
  } finally {
    saveKeyButton.disabled = false;
  }
});

forgetKeyButton.addEventListener('click', async () => {
  forgetKeyButton.disabled = true;
  keyFeedback.textContent = 'Quitando clave…';
  keyFeedback.classList.remove('error');
  try {
    const response = await fetch('/api/key/forget', {
      method: 'POST',
      headers: {'X-Local-Token': token},
      cache: 'no-store',
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'No se pudo quitar la clave.');
    apiKeyInput.value = '';
    updateKeyState(data);
    keyFeedback.textContent = data.source === 'environment'
      ? 'Clave guardada eliminada. Todavía existe una clave configurada en tu archivo .env.'
      : 'Clave eliminada de este equipo.';
  } catch (error) {
    keyFeedback.textContent = error.message;
    keyFeedback.classList.add('error');
  } finally {
    await refreshKeyState();
  }
});

refreshKeyState();
