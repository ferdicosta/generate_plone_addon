class AjaxForm {
  constructor(form) {
    this.form = form;
    this.submit = form.querySelector('.js-submit');
    this.apiError = form.querySelector('.js-api-error');
    this.errorTemplate = form.querySelector('.js-error-template');

    this.onSubmit = this.onSubmit.bind(this);

    this.bindEvents();
  }

  bindEvents() {
    this.form.addEventListener('submit', this.onSubmit);
  }

  async onSubmit(event) {
    event.preventDefault();

    const data = new FormData(this.form);

    if (event.submitter && event.submitter.name === 'form.draft') {
      data.append('form.draft', '');
    }

    this.setSubmitting(true);

    let response;

    try {
      const res = await fetch(this.form.action, {
        method: this.form.method || 'post',
        body: data,
        credentials: 'same-origin',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json',
        },
      });
      response = await res.json();
    } catch (error) {
      console.error('Errore durante l\'invio del form', error);
      this.setSubmitting(false);
      return;
    }

    if (response.status === false) {
      if (response.type === 'validation') {
        this.showErrors(response.data);
        this.setSubmitting(false);
        this.scrollToFirstError();
      }
    } else if (response.type === 'redirect') {
      window.location = response.data.url;
    } else if (response.type === 'reload') {
      window.location.reload();
    }
  }

  setSubmitting(isSubmitting) {
    if (isSubmitting) {
      if (this.submit) {
        this.submit.disabled = true;
      }
    } else {
      this.form.querySelectorAll('[type="submit"], button:not([type])').forEach((btn) => {
        btn.disabled = false;
      });
    }
  }

  clearErrors() {
    this.form.querySelectorAll('.js-validation-message').forEach((el) => el.remove());
    this.form.querySelectorAll('.is-error').forEach((el) => el.classList.remove('is-error'));

    if (this.apiError) {
      this.apiError.innerHTML = '';
      this.apiError.style.display = 'none';
    }
  }

  showErrors(responseData) {
    this.clearErrors();

    Object.entries(responseData.errors || {}).forEach(([key, value]) => {
      if (key === 'generic') {
        this.showApiError(value);
      }

      const field = this.form.querySelector(`[data-name="${CSS.escape(key)}"]`);

      if (!field) {
        return;
      }

      field.classList.add('is-error');

      field.querySelectorAll('input[type="text"]').forEach((input) => {
        input.addEventListener('focus', () => this.clearFieldError(input), { once: true });
      });
      field.querySelectorAll('select').forEach((select) => {
        select.addEventListener('change', () => this.clearFieldError(select), { once: true });
      });

      const wrapper = field.querySelector('.js-error-wrapper');
      const message = this.buildErrorMessage(value);

      if (wrapper && message) {
        wrapper.appendChild(message);
      }
    });
  }

  clearFieldError(input) {
    const field = input.closest('.is-error');

    if (!field) {
      return;
    }

    field.classList.remove('is-error');

    const wrapper = field.querySelector('.js-error-wrapper');

    if (wrapper) {
      wrapper.innerHTML = '';
    }
  }

  buildErrorMessage(text) {
    if (!this.errorTemplate) {
      return null;
    }

    const message = this.errorTemplate.content.firstElementChild.cloneNode(true);
    const span = message.querySelector('span');

    if (span) {
      span.textContent = text;
    }

    return message;
  }

  showApiError(html) {
    if (!this.apiError) {
      return;
    }

    this.apiError.innerHTML = html;
    this.apiError.style.display = '';
    this.apiError.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 400 });
  }

  scrollToFirstError() {
    const firstError = this.form.querySelector('.is-error');

    if (firstError) {
      window.scrollTo({
        top: firstError.getBoundingClientRect().top + window.scrollY - 200,
        behavior: 'smooth',
      });
    }
  }
}

function onReady(callback) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', callback);
  } else {
    callback();
  }
}

onReady(() => {
  document.querySelectorAll('.js-ajax-form').forEach((form) => new AjaxForm(form));
});
