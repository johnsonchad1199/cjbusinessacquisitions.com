// CJ Business Acquisitions — shared behavior

document.addEventListener('DOMContentLoaded', function () {
  // Mobile nav toggle
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var isOpen = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
    nav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Footer year
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();
});

/**
 * Generic Web3Forms submit handler.
 * Attach to any <form data-web3forms> element.
 */
function initWeb3FormsHandler(formSelector) {
  var form = document.querySelector(formSelector);
  if (!form) return;

  var statusEl = form.querySelector('#form-status') || document.getElementById('form-status');
  var submitBtn = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    if (statusEl) {
      statusEl.className = 'sending';
      statusEl.textContent = 'Sending — please wait...';
    }
    if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Sending...'; }

    var formData = new FormData(form);
    var originalBtnText = submitBtn ? submitBtn.getAttribute('data-original-text') || 'Submit' : null;

    fetch('https://api.web3forms.com/submit', {
      method: 'POST',
      headers: { Accept: 'application/json' },
      body: formData,
    })
      .then(function (response) { return response.json(); })
      .then(function (data) {
        if (data.success) {
          if (statusEl) {
            statusEl.className = 'success';
            statusEl.textContent = "Thank you — your submission was received. We'll be in touch shortly.";
          }
          form.reset();
        } else {
          throw new Error(data.message || 'Submission failed');
        }
      })
      .catch(function () {
        if (statusEl) {
          statusEl.className = 'error';
          statusEl.textContent = 'Something went wrong sending your message. Please email us directly at cjohnson@cjbusinessacquisitions.com.';
        }
      })
      .finally(function () {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = originalBtnText || 'Submit';
        }
      });
  });
}
