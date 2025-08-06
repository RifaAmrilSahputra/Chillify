// script.js
function isElementInViewport(element) {
    var rect = element.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <=
        (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
  }
  
  function animateElements() {
    var elements = document.querySelectorAll(".animated");
    elements.forEach(function (element) {
      if (isElementInViewport(element)) {
        element.classList.add("animate");
      }
    });
  }
  
  window.addEventListener("scroll", animateElements);
  
  animateElements();
  