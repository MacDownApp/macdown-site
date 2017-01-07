(function ($) {

$(function () {
  if (window.location.hash) {
    var el = $(window.location.hash);
    el.addClass('active');
    $('body').scrollTop($('body').scrollTop() - $(el).prev().height());
  }
});

$('.accordion .content').on('toggled', function () {
  $('.accordion .content').not(this).removeClass('active');   // Close others.
  var isActive = $(this).hasClass('active');
  var currentTop = $('body').scrollTop();
  window.location.hash = isActive ? '#' + this.id : '';
  if (isActive)   // Scroll back a bit to reveal the title block.
    currentTop = $('body').scrollTop() - $(this).prev().height() * 2;
  $('body').scrollTop(currentTop);
});

})(jQuery);
