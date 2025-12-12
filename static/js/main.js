// Rating system for reviews
document.addEventListener('DOMContentLoaded', function() {
    
    // Star rating interaction
    const ratingContainers = document.querySelectorAll('.rating-input');
    
    ratingContainers.forEach(container => {
        const stars = container.querySelectorAll('.star');
        const input = container.querySelector('input[name="rating"]');
        
        stars.forEach((star, index) => {
            star.addEventListener('click', () => {
                const rating = index + 1;
                input.value = rating;
                
                // Update visual state
                stars.forEach((s, i) => {
                    if (i < rating) {
                        s.classList.add('filled');
                    } else {
                        s.classList.remove('filled');
                    }
                });
            });
            
            star.addEventListener('mouseenter', () => {
                stars.forEach((s, i) => {
                    if (i <= index) {
                        s.classList.add('filled');
                    } else {
                        s.classList.remove('filled');
                    }
                });
            });
        });
        
        container.addEventListener('mouseleave', () => {
            const currentRating = parseInt(input.value) || 0;
            stars.forEach((s, i) => {
                if (i < currentRating) {
                    s.classList.add('filled');
                } else {
                    s.classList.remove('filled');
                }
            });
        });
    });
    
    // Confirmation dialogs for delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const message = button.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s';
            setTimeout(() => message.remove(), 500);
        }, 5000);
    });
    
    // Search suggestions (optional enhancement)
    const searchInput = document.querySelector('.nav-search input[name="q"]');
    
    if (searchInput) {
        let timeout;
        
        searchInput.addEventListener('input', (e) => {
            clearTimeout(timeout);
            
            const query = e.target.value;
            
            if (query.length < 2) return;
            
            timeout = setTimeout(() => {
                // Here you could make an AJAX call to get search suggestions
                // For now, we'll skip this advanced feature
                console.log('Searching for:', query);
            }, 300);
        });
    }
    
    // Image lazy loading
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
});

// Helper function for AJAX requests
function makeRequest(url, method = 'GET', data = null) {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: data ? JSON.stringify(data) : null
    })
    .then(response => response.json())
    .catch(error => console.error('Error:', error));
}
document.addEventListener('DOMContentLoaded', function () {
  const ratingContainers = document.querySelectorAll('.star-rating');

  ratingContainers.forEach(container => {
    const stars = container.querySelectorAll('.star');
    const form = container.closest('form');
    const input = form ? form.querySelector('input[name="rating"]') : null;

    // Initial selected rating
    let selected = 0;
    if (container.dataset.currentRating) {
      selected = Number(container.dataset.currentRating) || 0;
    } else if (input && input.value) {
      selected = Number(input.value) || 0;
    }

    function paint(rating) {
      stars.forEach(star => {
        const v = Number(star.dataset.value);
        star.classList.toggle('is-active', v <= rating);
      });
    }

    paint(selected);

    stars.forEach(star => {
      const value = Number(star.dataset.value);

      star.addEventListener('mouseenter', () => {
        paint(value);
      });

      star.addEventListener('click', () => {
        selected = value;
        if (input) input.value = value;
        paint(selected);
      });
    });

    container.addEventListener('mouseleave', () => {
      paint(selected);
    });
  });
});

document.addEventListener('DOMContentLoaded', function () {

  document.querySelectorAll('.activity-carousel').forEach(carousel => {
    const slides = carousel.querySelectorAll('.activity-slide');
    if (!slides.length) return;

    let current = 0;

    function showSlide(index) {
      slides.forEach((slide, i) => {
        slide.classList.toggle('is-active', i === index);
      });
    }

    const prevBtn = carousel.querySelector('.carousel-prev');
    const nextBtn = carousel.querySelector('.carousel-next');

    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        current = (current - 1 + slides.length) % slides.length;
        showSlide(current);
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        current = (current + 1) % slides.length;
        showSlide(current);
      });
    }

    // Ensure initial slide is visible
    showSlide(current);
  });
});
