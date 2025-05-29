// Основные функции для интерактивности сайта

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация слайдера
    initSlider();
    
    // Инициализация мобильного меню
    initMobileMenu();
    
    // Инициализация кнопки "Наверх"
    initBackToTop();
    
    // Инициализация анимаций при прокрутке
    initScrollAnimations();
    
    // Инициализация функциональности "Читать далее" для журнала
    initReadMore();
    
    // Добавление активного класса к текущему пункту меню
    highlightCurrentPage();
});

// Функция инициализации слайдера
function initSlider() {
    const sliderContainer = document.querySelector('.slider-container');
    if (!sliderContainer) return;
    
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.slider-dot');
    const prevBtn = document.querySelector('.slider-prev');
    const nextBtn = document.querySelector('.slider-next');
    
    let currentSlide = 0;
    let slideInterval;
    
    // Функция для показа слайда
    function showSlide(index) {
        // Скрываем все слайды
        slides.forEach(slide => {
            slide.classList.remove('active');
        });
        
        // Убираем активный класс у всех точек
        dots.forEach(dot => {
            dot.classList.remove('active');
        });
        
        // Показываем текущий слайд и активируем соответствующую точку
        slides[index].classList.add('active');
        if (dots[index]) {
            dots[index].classList.add('active');
        }
        
        currentSlide = index;
    }
    
    // Показываем первый слайд
    showSlide(0);
    
    // Функция для перехода к следующему слайду
    function nextSlide() {
        let next = currentSlide + 1;
        if (next >= slides.length) {
            next = 0;
        }
        showSlide(next);
    }
    
    // Функция для перехода к предыдущему слайду
    function prevSlide() {
        let prev = currentSlide - 1;
        if (prev < 0) {
            prev = slides.length - 1;
        }
        showSlide(prev);
    }
    
    // Запускаем автоматическую смену слайдов
    function startSlideInterval() {
        slideInterval = setInterval(nextSlide, 5000);
    }
    
    // Останавливаем автоматическую смену слайдов
    function stopSlideInterval() {
        clearInterval(slideInterval);
    }
    
    // Добавляем обработчики событий для кнопок и точек
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            prevSlide();
            stopSlideInterval();
            startSlideInterval();
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            nextSlide();
            stopSlideInterval();
            startSlideInterval();
        });
    }
    
    dots.forEach((dot, index) => {
        dot.addEventListener('click', function() {
            showSlide(index);
            stopSlideInterval();
            startSlideInterval();
        });
    });
    
    // Запускаем автоматическую смену слайдов
    startSlideInterval();
    
    // Останавливаем автоматическую смену слайдов при наведении на слайдер
    sliderContainer.addEventListener('mouseenter', stopSlideInterval);
    sliderContainer.addEventListener('mouseleave', startSlideInterval);
}

// Функция инициализации мобильного меню
function initMobileMenu() {
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (!navToggle || !navLinks) return;
    
    navToggle.addEventListener('click', function() {
        navLinks.classList.toggle('active');
        this.classList.toggle('active');
    });
}

// Функция инициализации кнопки "Наверх"
function initBackToTop() {
    const backToTopBtn = document.querySelector('.back-to-top');
    if (!backToTopBtn) return;
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.classList.add('visible');
        } else {
            backToTopBtn.classList.remove('visible');
        }
    });
    
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Функция инициализации анимаций при прокрутке
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animatedElements.length === 0) return;
    
    function checkScroll() {
        animatedElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementTop < windowHeight * 0.8) {
                element.classList.add('animate-fade-in');
            }
        });
    }
    
    // Проверяем при загрузке страницы
    checkScroll();
    
    // Проверяем при прокрутке
    window.addEventListener('scroll', checkScroll);
}

// Функция инициализации "Читать далее" для журнала
function initReadMore() {
    const readMoreButtons = document.querySelectorAll('.read-more');
    
    readMoreButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const card = this.closest('.post-card');
            const expanded = card.classList.toggle('expanded');
            this.textContent = expanded ? 'Свернуть' : 'Читать далее';
        });
    });
}

// Функция подсветки текущей страницы в меню
function highlightCurrentPage() {
    const currentPage = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('nav a');
    
    navLinks.forEach(link => {
        const linkHref = link.getAttribute('href');
        if (linkHref === currentPage || (currentPage === '' && linkHref === 'index.html')) {
            link.classList.add('active');
        }
    });
}

// Функция для анимации счетчиков
function animateCounters() {
    const counters = document.querySelectorAll('.counter');
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000; // 2 секунды
        const step = target / (duration / 16); // 16мс - примерно один кадр при 60fps
        let current = 0;
        
        const updateCounter = () => {
            current += step;
            if (current < target) {
                counter.textContent = Math.floor(current);
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };
        
        updateCounter();
    });
}

// Функция для инициализации параллакс-эффекта
function initParallax() {
    const parallaxElements = document.querySelectorAll('.parallax');
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset;
        
        parallaxElements.forEach(element => {
            const speed = element.getAttribute('data-speed') || 0.5;
            element.style.transform = `translateY(${scrollTop * speed}px)`;
        });
    });
}
