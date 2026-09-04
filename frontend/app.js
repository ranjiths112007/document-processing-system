const fileInput = document.getElementById('file');
const button = document.getElementById('process');
const result = document.getElementById('result');

button.addEventListener('click', async () => {
  const file = fileInput.files[0];
  if (!file) {
    result.textContent = 'Please choose a document first.';
    return;
  }

  try {
    result.textContent = 'Uploading...';
    const form = new FormData();
    form.append('file', file);
    form.append('document_type', 'invoice');

    const upload = await fetch('/documents/upload', { method: 'POST', body: form });
    if (!upload.ok) throw new Error((await upload.json()).detail || 'Upload failed');
    const { document_id } = await upload.json();

    result.textContent = 'Processing with OpenCV + OCR...';
    const process = await fetch(`/documents/${document_id}/process`, { method: 'POST' });
    if (!process.ok) throw new Error((await process.json()).detail || 'Processing failed');

    const output = await fetch(`/documents/${document_id}`);
    if (!output.ok) throw new Error('Could not fetch result');
    result.textContent = JSON.stringify(await output.json(), null, 2);
  } catch (error) {
    result.textContent = `Error: ${error.message}`;
  }
});
