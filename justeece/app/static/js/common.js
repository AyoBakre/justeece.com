$(document).ready(() => {
  $(window).scroll(function () {
    var scroll = $(window).scrollTop();

    if (scroll >= 0) {
      $(".navbar").addClass("navbar-border-bottom");
    }
    if (scroll == 0) {
      $(".navbar").removeClass("navbar-border-bottom");
    }
  });
});

function openNav() {
  document.getElementById("myNav").style.height = "100%";
}

function closeNav() {
  document.getElementById("myNav").style.height = "0%";
}

jQuery(document).ready(function($) {
  "use strict";
  //  TESTIMONIALS CAROUSEL HOOK
  $('#customers-testimonials').owlCarousel({
      loop: true,
      center: true,
      items: 3,
      margin: 0,
      nav:true,
      autoplay: false,
      dots:true,
      autoplayTimeout: 8500,
      smartSpeed: 450,
      responsive: {
        0: {
          items: 1
        },
        768: {
          items: 2
        },
        1170: {
          items: 3
        }
      }
  });
});