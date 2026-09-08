document.addEventListener('DOMContentLoaded', function () {
  // ---- Mobile nav toggle ----
  var navToggle = document.getElementById('navbar-toggle');
  var navMenu = document.getElementById('navbar-menu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', function () {
      var isOpen = navMenu.classList.toggle('hidden');
      navToggle.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
    });
  }

  // ---- Upload form: drag & drop + auto submit ----
  var form = document.getElementById('form-upload');
  var dropzone = document.getElementById('dropzone');
  var dropzoneActions = document.getElementById('dropzone-actions');
  var dropzoneLoading = document.getElementById('dropzone-loading');
  var inputGambar = document.getElementById('input-gambar');
  var inputFoto = document.getElementById('input-foto');
  var namaFile = document.getElementById('dropzone-filename');

  if (!form || !dropzone) return;

  var DRAGOVER_CLASSES = ['bg-green-100', 'border-green-700'];
  var IDLE_CLASSES = ['bg-green-50'];

  function kirimForm(file) {
    if (!file) return;
    namaFile.textContent = file.name;
    namaFile.hidden = false;

    dropzoneActions.classList.add('opacity-40', 'pointer-events-none');
    dropzoneLoading.classList.remove('hidden');
    dropzoneLoading.classList.add('flex');

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
      dropzone.classList.remove.apply(dropzone.classList, IDLE_CLASSES);
      dropzone.classList.add.apply(dropzone.classList, DRAGOVER_CLASSES);
    });
  });

  ['dragleave', 'drop'].forEach(function (evt) {
    dropzone.addEventListener(evt, function (e) {
      e.preventDefault();
      dropzone.classList.remove.apply(dropzone.classList, DRAGOVER_CLASSES);
      dropzone.classList.add.apply(dropzone.classList, IDLE_CLASSES);
    });
  });

  dropzone.addEventListener('drop', function (e) {
    var file = e.dataTransfer.files[0];
    if (!file) return;
    inputGambar.files = e.dataTransfer.files;
    kirimForm(file);
  });
});
