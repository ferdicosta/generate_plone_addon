function initStatusMessages() {
  const messages = document.querySelectorAll('.portalMessage.statusmessage');

  if (!messages.length) return;

  messages.forEach(function (message) {
    const closeBtn = document.createElement('button');
    closeBtn.className = 'portalMessage__close';
    closeBtn.innerHTML = '×';
    closeBtn.setAttribute('aria-label', 'Chiudi messaggio');
    closeBtn.type = 'button';

    message.insertBefore(closeBtn, message.firstChild);

    closeBtn.addEventListener('click', function () {
      message.classList.remove('show');

      setTimeout(function () {
        if (!message.classList.contains('show')) {
          message.style.display = 'none';
        }
      }, 300);
    });

    setTimeout(function () {
      message.classList.add('show');
    }, 100);
  });
}

$(document).ready(function(){
  initStatusMessages();
});
