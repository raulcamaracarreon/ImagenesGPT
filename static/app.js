const token = document.querySelector('meta[name="local-token"]').content;
const form = document.getElementById('image-form');
const submit = document.getElementById('submit-btn');
const status = document.getElementById('status');
const source = document.getElementById('source-image');
const wrapper = document.getElementById('upload-wrapper');
let mode = 'generate';

for (const tab of document.querySelectorAll('[data-mode]')) {
  tab.addEventListener('click', () => {
    mode = tab.dataset.mode;
    for (const other of document.querySelectorAll('[data-mode]')) {
      const selected = other === tab;
      other.classList.toggle('active', selected);
      other.setAttribute('aria-selected', String(selected));
    }
    wrapper.classList.toggle('hidden', mode !== 'edit');
    source.required = mode === 'edit';
    submit.textContent = mode === 'edit' ? '✦ Editar imagen' : '✦ Generar imagen';
    status.textContent = '';
  });
}

function showImage(url) {
  const image = document.getElementById('preview-image');
  image.src = url;
  image.classList.remove('hidden');
  document.getElementById('empty-state').classList.add('hidden');
  document.getElementById('preview').classList.remove('empty');
  const download = document.getElementById('download-btn');
  download.href = url;
  download.classList.remove('hidden');
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
      button.addEventListener('click', () => showImage(item.url));
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
    showImage(data.url);
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
