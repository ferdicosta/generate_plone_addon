function validateVisualAid($form, response_data) {
  const $submitButton = $(':submit', $form);
  $form.find('.js-validation-message').remove();
  $form.find('.has-error').removeClass('has-error');

  const $apiError = $('.js-api-error');
  $apiError.empty();
  $apiError.hide();
  let hasApiError = false;

  $.each(response_data.errors, function (key, value) {
    let template = $("#error-message");
    let markupTemplate = template[0].innerHTML;

    let $markup = $(markupTemplate);
    $markup.find('span').text(value);

    let $field = $('[data-name="' + key + '"]');
    $field.addClass('has-error');
    $field.find('input[type="text"]').on('focus', function () {
      let $fieldWrapper = $(this).parents('.has-error');
      $fieldWrapper.removeClass('has-error');
      $fieldWrapper.find('.js-error-wrapper').empty();
      $(this).unbind('focus');
    });

    $field.find('select').unbind('change');
    $field.find('select').on('change', function () {
      let $fieldWrapper = $(this).parents('.has-error');
      $fieldWrapper.removeClass('has-error');
      $fieldWrapper.find('.js-error-wrapper').empty();
    });

    if (key === 'generic') {
      hasApiError = true;
      $apiError.html(value);
      $apiError.fadeIn()
    }

    $markup.appendTo($field.find('.js-error-wrapper'));
  });

  let $firstError = $(".register__error.js-validation-message");

  // if ($firstError.length > 0) {
  //   $([document.documentElement, document.body]).animate({
  //     scrollTop: $firstError.offset().top - 200
  //   }, 400);
  // }

  // in caso di errori di validazione riattiviamo il bottone
  $submitButton.prop('disabled', false);
}

$(function () {
  const $form = $('.js-ajax-form');

  $form.unbind('submit');
  $form.on('submit', function (e) {
    e.preventDefault();
    let $form = $(this);
    let $submit = $form.find('.js-submit');

    let data = new FormData(this);
    let $clicked = $('button.clicked');
    if ($clicked.attr('name') === 'form.draft') {
      data.append('form.draft', '')
    }

    $submit.prop('disabled', true);

    $.ajax({
      url: $form.attr("action"),
      type: $form.attr("method"),
      dataType: "JSON",
      data: data,
      processData: false,
      contentType: false,
      success: function (response, status) {
        if (response.status === false) {
          if (response.type === 'validation') {
            validateVisualAid($form, response.data);
            $submit.prop('disabled', false);

            let $firstError = $(".has-error");

            if ($firstError.length > 0) {
              $([document.documentElement, document.body]).animate({
                scrollTop: $firstError.offset().top - 200
              }, 400);
            }
          }
        } else {
          if (response.type === 'redirect') {
            window.location = response.data.url;
          } else if (response.type === 'reload') {
            window.location.reload();
          }
        }
      },
      error: function (xhr, desc, err) {
        console.log('error')
      },
      complete: function () {
      }
    });
  });

})
