function isElementInViewport(element) {
  const rect = element.getBoundingClientRect();
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <=
      (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  );
}

function handleIntersection(entries, observer) {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}

const observer = new IntersectionObserver(handleIntersection, {
  root: null,
  rootMargin: '0px',
  threshold: 0.3,
});

const fadeElements = document.querySelectorAll('.fade-in');

fadeElements.forEach((element) => {
  observer.observe(element);
});

window.addEventListener('scroll', () => {
  fadeElements.forEach((element) => {
    if (isElementInViewport(element)) {
      element.classList.add('visible');
      observer.unobserve(element);
    } else {
      element.classList.remove('visible'); // Reset the state when out of view
      observer.observe(element); // Reobserve the element
    }
  });
});
