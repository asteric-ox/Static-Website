/**
 * St. Sebastian's Shrine - Main JS
 * Handles navigation, multilingual toggle, and scroll animations.
 */

document.addEventListener('DOMContentLoaded', () => {
    // ── Preloader ────────────────────────────────────────────────
    const preloader = document.getElementById('preloader');
    if (preloader) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                preloader.classList.add('fade-out');
                setTimeout(() => preloader.remove(), 1000);
            }, 2000); // 2-second delay to show the intro animation
        });
    }

    // ── Navigation ────────────────────────────────────────────────
    const nav = document.getElementById('main-nav');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    // Scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    });

    // Mobile menu toggle
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // ── Multilingual Support ──────────────────────────────────────
    let currentLang = localStorage.getItem('church_lang') || 'en';
    
    const updateContent = (translations) => {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            const translation = key.split('.').reduce((obj, i) => (obj ? obj[i] : null), translations);
            if (translation) {
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                    el.placeholder = translation;
                } else {
                    el.innerText = translation;
                }
            }
        });
        // Update document lang
        document.documentElement.lang = currentLang;
    };

    const loadLanguage = async (lang) => {
        try {
            const response = await fetch(`/api/translations/${lang}`);
            if (!response.ok) throw new Error('Failed to load translations');
            const data = await response.ok ? await response.json() : null;
            if (data) {
                updateContent(data);
                currentLang = lang;
                localStorage.setItem('church_lang', lang);
                updateLangButtons();
            }
        } catch (error) {
            console.error('Translation error:', error);
        }
    };

    const updateLangButtons = () => {
        const toggleBtns = [document.getElementById('lang-toggle'), document.getElementById('lang-toggle-mobile')];
        toggleBtns.forEach(btn => {
            if (btn) btn.innerText = currentLang === 'en' ? 'EN | മല' : 'മല | EN';
        });
    };

    const toggleLang = () => {
        const nextLang = currentLang === 'en' ? 'ml' : 'en';
        loadLanguage(nextLang);
    };

    const langBtn = document.getElementById('lang-toggle');
    const langBtnMobile = document.getElementById('lang-toggle-mobile');
    if (langBtn) langBtn.addEventListener('click', toggleLang);
    if (langBtnMobile) langBtnMobile.addEventListener('click', toggleLang);

    // Initial load
    if (currentLang !== 'en') {
        loadLanguage(currentLang);
    }

    // ── Scroll Animations ─────────────────────────────────────────
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    document.querySelectorAll('.timeline-entry').forEach(el => {
        observer.observe(el);
    });

    // ── Flash Messages ────────────────────────────────────────────
    const flashMsgs = document.querySelectorAll('.flash-msg');
    flashMsgs.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-20px)';
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });
});
