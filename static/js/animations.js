/**
 * Shawarma Falafel City — Globale Animationen
 * Elemente poppen auf wenn sie ins Bild scrollen
 */

document.addEventListener('DOMContentLoaded', () => {

    /* =============================================
       1. Scroll-Pop Animationen (alle Seiten)
       ============================================= */
    const popTargets = document.querySelectorAll(
        '.menu-card, .info-item, .category-tab, .dash-stat, .dash-order, h1, h2, .section-title, .section-label, .cart-table, .checkout-box'
    );

    const popObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                const delay = (entry.target.dataset.delay || 0);
                setTimeout(() => {
                    entry.target.classList.add('pop-in');
                }, delay);
                popObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    // Karten in Reihen versetzt animieren
    let cardIndex = 0;
    popTargets.forEach(el => {
        el.classList.add('pop-ready');
        if (el.classList.contains('menu-card') || el.classList.contains('info-item') || el.classList.contains('dash-stat')) {
            el.dataset.delay = cardIndex * 80;
            cardIndex++;
        } else {
            el.dataset.delay = 0;
        }
        popObserver.observe(el);
    });

    /* =============================================
       2. Info-Strip Zahlen hochzählen
       ============================================= */
    // (für spätere Erweiterung)

    /* =============================================
       3. Menükarten: Feuer-Glow beim Hover
       ============================================= */
    document.querySelectorAll('.menu-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-6px) scale(1.02)';
            card.style.boxShadow = '0 0 24px rgba(255,102,0,0.5), 0 8px 32px rgba(0,0,0,0.6)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
            card.style.boxShadow = '';
        });
    });

    /* =============================================
       4. "Hinzufügen" Button: kurze Bounce-Animation
       ============================================= */
    document.querySelectorAll('.btn-add').forEach(btn => {
        btn.addEventListener('click', function () {
            this.classList.add('btn-bounce');
            setTimeout(() => this.classList.remove('btn-bounce'), 400);
        });
    });

    /* =============================================
       5. Navbar: aktiver Link markieren
       ============================================= */
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        if (link.href === window.location.href) {
            link.classList.add('nav-active');
        }
    });

    /* =============================================
       6. Hero Scroll-Indikator ausblenden beim Scrollen
       ============================================= */
    const scrollHint = document.querySelector('.hero-scroll');
    if (scrollHint) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 80) {
                scrollHint.style.opacity = '0';
            } else {
                scrollHint.style.opacity = '1';
            }
        }, { passive: true });
    }

    /* =============================================
       7. Kategorie-Tabs: Bounce beim Klicken
       ============================================= */
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.addEventListener('click', function () {
            this.classList.add('tab-bounce');
            setTimeout(() => this.classList.remove('tab-bounce'), 300);
        });
    });

});
