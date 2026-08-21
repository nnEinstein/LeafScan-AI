document.addEventListener('DOMContentLoaded', function () {
  // ---- Mobile nav toggle ----
  var toggle = document.querySelector('.navbar__toggle');
  var menu = document.querySelector('.navbar__menu');

  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      var isOpen = menu.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
  }

  // ---- Upload form: drag & drop + auto submit ----
  var form = document.getElementById('form-upload');
  var dropzone = document.getElementById('dropzone');
  var inputGambar = document.getElementById('input-gambar');
  var inputFoto = document.getElementById('input-foto');
  var namaFile = document.getElementById('dropzone-filename');

  if (!form || !dropzone) return;

  function kirimForm(file) {
    if (!file) return;
    namaFile.textContent = file.name;
    namaFile.hidden = false;
    dropzone.classList.add('is-loading');
    form.requestSubmit ? form.requestSubmit() : form.submit();
  }

  if (inputGambar) {
    inputGambar.addEventListener('change', function () {
      kirimForm(this.files[0]);
    });
  }

  if (inputFoto) {
    inputFoto.addEventListener('change', function () {
      kirimForm(this.files[0]);
    });
  }

  ['dragenter', 'dragover'].forEach(function (evt) {
    dropzone.addEventListener(evt, function (e) {
      e.preventDefault();
      dropzone.classList.add('is-dragover');
    });
  });

  ['dragleave', 'drop'].forEach(function (evt) {
    dropzone.addEventListener(evt, function (e) {
      e.preventDefault();
      dropzone.classList.remove('is-dragover');
    });
  });

  dropzone.addEventListener('drop', function (e) {
    var file = e.dataTransfer.files[0];
    if (!file) return;
    inputGambar.files = e.dataTransfer.files;
    kirimForm(file);
  });
});
