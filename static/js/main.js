/**
 * St. Sebastian's Shrine - Main JS
 * Handles navigation, multilingual toggle, and scroll animations.
 */

document.addEventListener('DOMContentLoaded', () => {
    // ── Preloader (only on first visit per session) ────────────────
    const preloader = document.getElementById('preloader');
    if (preloader) {
        if (sessionStorage.getItem('intro_shown')) {
            // Already seen in this session — remove immediately
            preloader.remove();
        } else {
            // First visit — show the intro animation
            window.addEventListener('load', () => {
                setTimeout(() => {
                    preloader.classList.add('fade-out');
                    setTimeout(() => preloader.remove(), 1000);
                    sessionStorage.setItem('intro_shown', 'true');
                }, 2000);
            });
        }
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


// ── Priest Profile Modal ──────────────────────────────────────────
function openPriestModal(index) {
    const cards = document.querySelectorAll('.priest-card');
    if (!cards[index]) return;

    const card = cards[index];
    const name = card.dataset.name;
    const role = card.dataset.role;
    const phone = card.dataset.phone;
    const image = card.dataset.image;
    const dob = card.dataset.dob;
    const feast = card.dataset.feast;
    const normalMass = card.dataset.normalMass;
    const specialMass = card.dataset.specialMass;

    // Populate modal
    document.getElementById('modal-name').textContent = name;
    document.getElementById('modal-role').textContent = role;
    document.getElementById('modal-role-detail').textContent = role;

    // Additional fields
    const dobRow = document.getElementById('modal-dob-row');
    if (dob && dob !== '—' && dob !== '') {
        dobRow.style.display = 'flex';
        document.getElementById('modal-dob').textContent = dob;
    } else {
        dobRow.style.display = 'none';
    }

    const feastRow = document.getElementById('modal-feast-row');
    if (feast && feast !== '—' && feast !== '') {
        feastRow.style.display = 'flex';
        document.getElementById('modal-feast').textContent = feast;
    } else {
        feastRow.style.display = 'none';
    }

    const normalMassRow = document.getElementById('modal-normal-mass-row');
    if (normalMass && normalMass !== '') {
        normalMassRow.style.display = 'flex';
        document.getElementById('modal-normal-mass').textContent = normalMass;
    } else {
        normalMassRow.style.display = 'none';
    }

    const specialMassRow = document.getElementById('modal-special-mass-row');
    if (specialMass && specialMass !== '') {
        specialMassRow.style.display = 'flex';
        document.getElementById('modal-special-mass').textContent = specialMass;
    } else {
        specialMassRow.style.display = 'none';
    }

    // Photo
    const photoEl = document.getElementById('modal-photo');
    if (image) {
        photoEl.innerHTML = `<img src="${image}" alt="${name}" class="w-full h-full object-cover"/>`;
    } else {
        photoEl.innerHTML = `<span>${name.charAt(0)}</span>`;
    }

    // Phone
    const phoneRow = document.getElementById('modal-phone-row');
    const phoneLink = document.getElementById('modal-phone');
    const callBtn = document.getElementById('modal-call-btn');
    if (phone) {
        phoneRow.style.display = 'flex';
        phoneLink.textContent = phone;
        phoneLink.href = `tel:${phone}`;
        callBtn.href = `tel:${phone}`;
        callBtn.style.display = 'inline-flex';
    } else {
        phoneRow.style.display = 'none';
        callBtn.style.display = 'none';
    }

    // Show modal with animation
    const modal = document.getElementById('priest-modal');
    const backdrop = document.getElementById('priest-modal-backdrop');
    const content = document.getElementById('priest-modal-content');

    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.body.style.overflow = 'hidden';

    // Trigger animation
    backdrop.style.opacity = '0';
    content.style.opacity = '0';
    content.style.transform = 'scale(0.85) translateY(30px)';

    requestAnimationFrame(() => {
        backdrop.style.transition = 'opacity 0.4s ease';
        backdrop.style.opacity = '1';
        content.style.transition = 'opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1), transform 0.5s cubic-bezier(0.16, 1, 0.3, 1)';
        content.style.opacity = '1';
        content.style.transform = 'scale(1) translateY(0)';
    });
}

function closePriestModal() {
    const modal = document.getElementById('priest-modal');
    const backdrop = document.getElementById('priest-modal-backdrop');
    const content = document.getElementById('priest-modal-content');

    backdrop.style.opacity = '0';
    content.style.opacity = '0';
    content.style.transform = 'scale(0.9) translateY(20px)';

    setTimeout(() => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = '';
    }, 350);
}

// Close on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modal = document.getElementById('priest-modal');
        if (modal && !modal.classList.contains('hidden')) {
            closePriestModal();
        }
        const tModal = document.getElementById('trustee-modal');
        if (tModal && !tModal.classList.contains('hidden')) {
            closeTrusteeModal();
        }
    }
});

// ── Trustee Profile Modal (Slide Up Animation) ────────────────────
function openTrusteeModal(index) {
    const cards = document.querySelectorAll('.trustee-card');
    if (!cards[index]) return;

    const card = cards[index];
    const name = card.dataset.name;
    const role = card.dataset.role;
    const phone = card.dataset.phone;
    const image = card.dataset.image;

    // Populate
    document.getElementById('t-modal-name').textContent = name;
    document.getElementById('t-modal-role').textContent = role;
    
    const photoEl = document.getElementById('t-modal-photo');
    if (image) {
        photoEl.innerHTML = `<img src="${image}" alt="${name}" class="w-full h-full object-cover"/>`;
    } else {
        photoEl.innerHTML = `<span>${name.charAt(0)}</span>`;
    }

    // Details rows
    const phoneRow = document.getElementById('t-modal-phone-row');
    const phoneEl = document.getElementById('t-modal-phone');
    if (phone && phone !== '') {
        phoneRow.style.display = 'flex';
        phoneEl.textContent = phone;
        phoneEl.href = 'tel:' + phone;
    } else {
        phoneRow.style.display = 'none';
    }

    const callBtn = document.getElementById('t-modal-call-btn');
    if (phone) {
        callBtn.style.display = 'inline-flex';
        callBtn.href = 'tel:' + phone;
    } else {
        callBtn.style.display = 'none';
    }

    // Animation
    const modal = document.getElementById('trustee-modal');
    const backdrop = document.getElementById('trustee-modal-backdrop');
    const content = document.getElementById('trustee-modal-content');

    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.body.style.overflow = 'hidden';

    backdrop.style.opacity = '0';
    content.style.opacity = '0';
    content.style.transform = 'translateY(100px)';

    requestAnimationFrame(() => {
        backdrop.style.transition = 'opacity 0.5s ease';
        backdrop.style.opacity = '1';
        content.style.transition = 'all 0.6s cubic-bezier(0.23, 1, 0.32, 1)';
        content.style.opacity = '1';
        content.style.transform = 'translateY(0)';
    });
}

function closeTrusteeModal() {
    const modal = document.getElementById('trustee-modal');
    const backdrop = document.getElementById('trustee-modal-backdrop');
    const content = document.getElementById('trustee-modal-content');

    backdrop.style.opacity = '0';
    content.style.opacity = '0';
    content.style.transform = 'translateY(100px)';

    setTimeout(() => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = '';
    }, 500);
}

