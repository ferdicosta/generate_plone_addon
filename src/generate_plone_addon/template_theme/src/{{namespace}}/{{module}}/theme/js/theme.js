class StatusMessage {
  constructor(el) {
    this.el = el;
    this.close = this.close.bind(this);

    this.closeBtn = document.createElement('button');
    this.closeBtn.type = 'button';
    this.closeBtn.className = 'portalMessage__close';
    this.closeBtn.textContent = '×';
    this.closeBtn.setAttribute('aria-label', 'Chiudi messaggio');
    this.el.insertBefore(this.closeBtn, this.el.firstChild);

    this.bindEvents();
    setTimeout(() => this.open(), 100);
  }

  bindEvents() {
    this.closeBtn.addEventListener('click', this.close);
  }

  open() {
    this.el.classList.add('show');
  }

  close() {
    this.el.classList.remove('show');

    setTimeout(() => {
      if (!this.el.classList.contains('show')) {
        this.el.style.display = 'none';
      }
    }, 300);
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
  document.querySelectorAll('.portalMessage.statusmessage').forEach((el) => new StatusMessage(el));
});
