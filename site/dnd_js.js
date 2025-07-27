// ===== CONFIGURAZIONE ICONE E IMMAGINI =====
const treasureIcons = [
    '🎭', '⚔️', '🏆', '🔮', '💎', '🏰', '🐉', '⚡', '🌟', '💰',
    '🛡️', '🗝️', '📜', '🧙‍♂️', '🏹', '⚗️', '💀', '👑', '🔥', '❄️'
];

const dndImages = {
    'spell-complexity': 'Spell Level Complexity Analysis Multi-Dimensional View',
    'magic-schools': 'Magic School Market Dominance - Bubble size = Total Spells',
    'equipment-tiers': 'Equipment Market Tier Distribution - Stacked by Price Category',
    'racial-advantages': 'Racial Competitive Advantages - Bubble size = Competitive Index',
    'spell-rarity': 'Spell Rarity Distribution Market Share Analysis',
    'class-power': 'Class Power Comparison Multi-Dimensional Analysis',
    'racial-synergy': 'Racial-Class Synergy Network Ability Score Connections',
    'class-centrality': 'Class Network Centrality - Spell Hub Analysis',
    'bridge-spells': 'Top Bridge Spells Class Connectors',
    'spell-heatmap': 'Class Spell Distribution Heatmap - Spells by Level and Class',
    'multiclass-synergy': 'Advanced Multiclass Synergy Network - Edge thickness = Synergy strength',
    'class-similarity': 'Class Similarity Network Jaccard Similarity Index',
    'synergy-matrix': 'Multiclass Synergy Matrix Percentage of Shared Spells',
    'pe-ratio': 'D&D Class Stock Valuation Analysis Price-to-Earnings Ratio Comparison',
    'dividend-analysis': 'D&D Class Stock Dividend Analysis Income Investment Opportunities',
    'market-cap': 'D&D Class Stock Market Capitalization Company Size Comparison',
    'beta-risk': 'D&D Class Beta Risk Analysis',
    'sector-analysis': 'D&D Market Sector Analysis - Caster vs Martial vs Hybrid',
    'price-performance': 'D&D Stock Price vs Performance Analysis Bubble size = Market Cap, Color = Risk Level',
    'trading-volume': 'D&D Stock Trading Volume Analysis',
    'financial-dashboard': 'D&D MARKET FINANCIAL DASHBOARD - Real-Time Analytics'
};

// ===== INIZIALIZZAZIONE =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('🗺️ Inizializzando la Mappa del Tesoro D&D...');
    
    initializeTreasureMap();
    createFloatingIcons();
    setupCardInteractions();
    setupScrollEffects();
    loadAnalysisImages();
    setupNavigationEffects();
    
    console.log('⚔️ Mappa del Tesoro D&D completamente caricata! Buona avventura! 🏰');
});

// ===== INIZIALIZZAZIONE MAPPA =====
function initializeTreasureMap() {
    // Aggiungi effetti di particelle
    createMagicalParticles();
    
    // Setup suoni (opzionale)
    setupSoundEffects();
    
    // Inizializza contatori
    updateTreasureCounters();
    
    // Setup Easter egg compass
    setupCompassEasterEgg();
    
    console.log('🗺️ Mappa del Tesoro D&D inizializzata con successo!');
}

// ===== CREAZIONE ICONE FLUTTUANTI =====
function createFloatingIcons() {
    const container = document.querySelector('.background-icons');
    const iconData = [
        { emoji: '💰', top: '10%', left: '15%' },
        { emoji: '🏆', top: '30%', right: '10%' },
        { emoji: '🔮', top: '50%', left: '5%' },
        { emoji: '🗝️', top: '70%', right: '20%' },
        { emoji: '⚔️', top: '20%', left: '80%' },
        { emoji: '🛡️', top: '80%', left: '25%' },
        { emoji: '🐉', top: '15%', right: '40%' },
        { emoji: '🏰', top: '60%', right: '5%' },
        { emoji: '📜', top: '40%', left: '30%' },
        { emoji: '👑', top: '85%', right: '35%' },
        { emoji: '🌟', top: '5%', left: '60%' },
        { emoji: '💎', top: '75%', left: '70%' }
    ];

    iconData.forEach((icon, index) => {
        const iconElement = document.createElement('div');
        iconElement.classList.add('floating-icon');
        iconElement.textContent = icon.emoji;
        iconElement.style.fontSize = '2rem';
        iconElement.style.position = 'absolute';
        iconElement.style.top = icon.top;
        
        if (icon.left) iconElement.style.left = icon.left;
        if (icon.right) iconElement.style.right = icon.right;
        
        iconElement.style.animationDelay = `${index * 0.5}s`;
        iconElement.style.zIndex = '1';
        
        container.appendChild(iconElement);
    });
}

// ===== CARICAMENTO IMMAGINI =====
/*
function loadAnalysisImages() {
    const images = document.querySelectorAll('.analysis-image');
    images.forEach((img, index) => {
        const card = img.closest('.treasure-card');
        const analysisType = card.getAttribute('data-analysis');
        
        // Crea placeholder SVG per le immagini
        img.src = createImagePlaceholder(dndImages[analysisType] || 'D&D Analysis Chart');
        
        // Effetto di caricamento
        img.style.opacity = '0';
        setTimeout(() => {
            img.style.transition = 'opacity 0.5s ease';
            img.style.opacity = '1';
        }, index * 100);
        
        // Gestione errori di caricamento
        img.onerror = function() {
            this.src = createImagePlaceholder('Immagine non disponibile');
        };
    });
}*/
function loadAnalysisImages() {
    // Ora i percorsi sono relativi alla cartella principale
    const existingImages = {
        'school-matrix': './dnd_images/11_school_competition_matrix.png',  
        'magic-schools': './dnd_images/3_school_market_dominance.png',         
        'bridge-spells': './dnd_images/10_spell_bridge_analysis.png',
        'component-dependency': './dnd_images/12_component_dependency_analysis.png',
        'class-power': './dnd_images/1_class_power_metrics.png',
        'school-dominance': './dnd_images/9_school_dominance_ecosystem.png',
        'equipment-tiers': './dnd_images/4_equipment_tiers.png',
        'multiclass-synergy': './dnd_images/8_multiclass_synergy_network.png',
        'racial-advantages': './dnd_images/5_racial_advantages.png',
        'spell-network': './dnd_images/7_spell_class_network.png',
        'spell-heatmap': './dnd_images/6_spell_distribution_heatmap.png',
        'spell-rarity': './dnd_images/2_spell_rarity_distribution.png',
        'synergy-matrix': './dnd_images/13_power_progression_curves.png',

        'pe-ratio': './market_images/1_pe_ratio_valuation.png',
        'dividend-analysis': './market_images/2_dividend_yield_ranking.png',
        'market-cap': './market_images/3_market_cap_visualization.png',
        'beta-risk': './market_images/4_beta_risk_assessment.png',
        'sector-analysis': './market_images/5_sector_performance_comparison.png',
        'price-performance': './market_images/6_price_performance_bubble.png',
        'trading-volume': './market_images/7_volume_activity_analysis.png',
        'financial-dashboard': './market_images/8_comprehensive_dashboard.png'
    };
    
    console.log('🖼️ Caricando da cartella principale...');
    console.log('📍 URL base:', window.location.href);
    
    const images = document.querySelectorAll('.analysis-image');
    images.forEach((img, index) => {
        const card = img.closest('.treasure-card');
        const analysisType = card.getAttribute('data-analysis');
        
        if (existingImages[analysisType]) {
            const imagePath = existingImages[analysisType];
            console.log(`📷 Tentativo caricamento: ${analysisType} -> ${imagePath}`);
            
            // Test se l'immagine esiste prima di caricarla
            const testImg = new Image();
            testImg.onload = function() {
                console.log(`✅ SUCCESSO: ${imagePath}`);
                img.src = imagePath;
                img.style.opacity = '1';
                img.style.transition = 'opacity 0.5s ease';
            };
            
            testImg.onerror = function() {
                console.log(`❌ ERRORE: ${imagePath}`);
                console.log(`🔍 URL completo tentato: ${window.location.origin}${window.location.pathname.replace('index.html', '')}${imagePath}`);
                img.src = createImagePlaceholder(`${dndImages[analysisType]} - Errore: ${imagePath}`);
                img.style.opacity = '1';
            };
            
            testImg.src = imagePath;
        } else {
            console.log(`⚠️ Immagine non in lista: ${analysisType}`);
            img.src = createImagePlaceholder(`${dndImages[analysisType] || analysisType} - Da aggiungere`);
            img.style.opacity = '1';
        }
    });
}

// ===== CREAZIONE PLACEHOLDER IMMAGINI =====
function createImagePlaceholder(text) {
    return `data:image/svg+xml;base64,${btoa(`
        <svg width="500" height="300" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#f4e4bc;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#ddc49a;stop-opacity:1" />
                </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#grad1)" stroke="#8b4513" stroke-width="2"/>
            <text x="50%" y="45%" text-anchor="middle" dy=".3em" 
                  font-family="Georgia, serif" font-size="14" fill="#8b4513" font-weight="bold">
                ${text}
            </text>
            <text x="50%" y="65%" text-anchor="middle" dy=".3em" 
                  font-family="Georgia, serif" font-size="12" fill="#a0522d">
                [Sostituisci con la tua immagine reale]
            </text>
            <circle cx="250" cy="150" r="80" fill="none" stroke="#cd853f" stroke-width="2" stroke-dasharray="5,5">
                <animateTransform attributeName="transform" type="rotate" 
                    values="0 250 150;360 250 150" dur="10s" repeatCount="indefinite"/>
            </circle>
            <polygon points="250,90 270,130 230,130" fill="#daa520" opacity="0.7">
                <animateTransform attributeName="transform" type="rotate" 
                    values="0 250 150;360 250 150" dur="8s" repeatCount="indefinite"/>
            </polygon>
        </svg>
    `)}`;
}

// ===== PARTICELLE MAGICHE =====
function createMagicalParticles() {
    const particlesContainer = document.createElement('div');
    particlesContainer.className = 'magical-particles';
    particlesContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 1;
    `;
    document.body.appendChild(particlesContainer);

    // Crea particelle magiche
    for (let i = 0; i < 20; i++) {
        setTimeout(() => createParticle(particlesContainer), i * 500);
    }
}

function createParticle(container) {
    const particle = document.createElement('div');
    const icons = ['✨', '⭐', '💫', '🌟', '✦', '✧'];
    
    particle.textContent = icons[Math.floor(Math.random() * icons.length)];
    particle.style.cssText = `
        position: absolute;
        font-size: ${Math.random() * 15 + 10}px;
        left: ${Math.random() * 100}%;
        top: ${Math.random() * 100}%;
        opacity: 0;
        animation: particleFloat ${Math.random() * 10 + 15}s linear infinite;
        color: #daa520;
        text-shadow: 0 0 10px rgba(218, 165, 32, 0.8);
        z-index: 1;
    `;
    
    container.appendChild(particle);
    
    // Rimuovi la particella dopo l'animazione
    setTimeout(() => {
        if (particle.parentNode) {
            particle.parentNode.removeChild(particle);
            createParticle(container); // Crea una nuova particella
        }
    }, 25000);
}

// ===== INTERAZIONI DELLE CARTE =====
function setupCardInteractions() {
    const cards = document.querySelectorAll('.treasure-card');
    
    cards.forEach((card, index) => {
        // Hover effects
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-15px) scale(1.03)';
            this.style.boxShadow = '0 25px 50px rgba(139, 69, 19, 0.4), 0 0 40px rgba(218, 165, 32, 0.6)';
            
            // Effetto particelle al hover
            createHoverParticles(this);
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
            this.style.boxShadow = '0 20px 40px rgba(139, 69, 19, 0.3), 0 0 30px rgba(218, 165, 32, 0.4)';
        });
        
        // Click effects
        card.addEventListener('click', function() {
            expandCard(this);
            showTreasureDiscovered(index);
        });
        
        // Touch effects per mobile
        card.addEventListener('touchstart', function() {
            this.style.transform = 'translateY(-8px) scale(1.01)';
        });
        
        card.addEventListener('touchend', function() {
            setTimeout(() => {
                this.style.transform = 'translateY(-10px) scale(1.02)';
            }, 100);
        });
    });
}

// ===== EFFETTI HOVER PARTICELLE =====
function createHoverParticles(card) {
    const rect = card.getBoundingClientRect();
    
    for (let i = 0; i < 5; i++) {
        const particle = document.createElement('div');
        particle.textContent = treasureIcons[Math.floor(Math.random() * treasureIcons.length)];
        particle.style.cssText = `
            position: fixed;
            left: ${rect.left + Math.random() * rect.width}px;
            top: ${rect.top + Math.random() * rect.height}px;
            font-size: 20px;
            pointer-events: none;
            z-index: 1000;
            animation: hoverParticle 1s ease-out forwards;
        `;
        
        document.body.appendChild(particle);
        
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        }, 1000);
    }
}

// ===== ESPANSIONE CARTE =====
function expandCard(card) {
    // Crea overlay modale
    const modal = document.createElement('div');
    modal.className = 'treasure-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(139, 69, 19, 0.9);
        z-index: 2000;
        display: flex;
        justify-content: center;
        align-items: center;
        animation: modalAppear 0.3s ease-out;
    `;
    
    const modalContent = card.cloneNode(true);
    modalContent.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        transform: scale(1.2);
        position: relative;
        overflow-y: auto;
        margin: 20px;
    `;
    
    // Pulsante chiudi
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '❌';
    closeBtn.style.cssText = `
        position: absolute;
        top: 10px;
        right: 10px;
        background: #8b4513;
        color: white;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        font-size: 20px;
        cursor: pointer;
        z-index: 2001;
        transition: all 0.3s ease;
    `;
    
    closeBtn.addEventListener('mouseenter', () => {
        closeBtn.style.background = '#cd853f';
        closeBtn.style.transform = 'scale(1.1)';
    });
    
    closeBtn.addEventListener('mouseleave', () => {
        closeBtn.style.background = '#8b4513';
        closeBtn.style.transform = 'scale(1)';
    });
    
    closeBtn.addEventListener('click', () => {
        modal.style.animation = 'modalDisappear 0.3s ease-out forwards';
        setTimeout(() => {
            if (document.body.contains(modal)) {
                document.body.removeChild(modal);
            }
        }, 300);
    });
    
    modalContent.appendChild(closeBtn);
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Chiudi cliccando fuori
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeBtn.click();
        }
    });
    
    // Chiudi con ESC
    const escapeHandler = (e) => {
        if (e.key === 'Escape') {
            closeBtn.click();
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);
}

// ===== EFFETTI SCROLL =====
function setupScrollEffects() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'cardAppear 0.8s ease-out forwards';
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.treasure-card').forEach(card => {
        observer.observe(card);
    });
}

// ===== NAVIGAZIONE FLUIDA =====
function setupNavigationEffects() {
    // Scroll fluido tra sezioni
    const sections = ['mongodb-section', 'neo4j-section', 'financial-section'];
    
    // Crea menu di navigazione
    const nav = document.createElement('nav');
    nav.className = 'treasure-nav';
    
    sections.forEach((sectionId, index) => {
        const navBtn = document.createElement('button');
        const icons = ['📊', '🕸️', '💹'];
        const titles = ['MongoDB', 'Neo4j', 'Mercato'];
        
        navBtn.innerHTML = icons[index];
        navBtn.title = titles[index];
        navBtn.setAttribute('aria-label', `Vai alla sezione ${titles[index]}`);
        
        navBtn.addEventListener('click', () => {
            const section = document.getElementById(sectionId);
            if (section) {
                section.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
                
                // Effetto feedback visivo
                navBtn.style.background = '#daa520';
                setTimeout(() => {
                    navBtn.style.background = 'rgba(244, 228, 188, 0.9)';
                }, 300);
            }
        });
        
        nav.appendChild(navBtn);
    });
    
    document.body.appendChild(nav);
}

// ===== NOTIFICHE TESORO =====
function showTreasureDiscovered(index) {
    const notification = document.createElement('div');
    notification.className = 'treasure-notification';
    notification.innerHTML = `
        <div style="font-size: 30px; margin-bottom: 10px;">🏆</div>
        <div style="font-size: 18px; font-weight: bold; color: #8b4513;">Tesoro Scoperto!</div>
        <div style="font-size: 14px; color: #a0522d;">Analisi ${index + 1} sbloccata</div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'notificationFade 0.5s ease-out forwards';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 500);
        }
    }, 2500);
}

// ===== EASTER EGG COMPASS =====
function setupCompassEasterEgg() {
    let clickCount = 0;
    const compass = document.querySelector('.compass');
    
    if (compass) {
        compass.addEventListener('click', function() {
            clickCount++;
            
            // Effetto visivo ad ogni click
            this.style.transform = 'scale(1.2)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 200);
            
            if (clickCount === 5) {
                showSecretTreasure();
                clickCount = 0;
            }
        });
    }
}

function showSecretTreasure() {
    const secret = document.createElement('div');
    secret.innerHTML = `
        <div style="font-size: 40px;">🎉</div>
        <div style="font-size: 20px; margin: 10px 0;">Tesoro Segreto Scoperto!</div>
        <div style="font-size: 14px;">Hai trovato l'Easter Egg del Compass!</div>
        <div style="font-size: 30px; margin-top: 10px;">🗝️✨🏆✨🗝️</div>
    `;
    secret.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: radial-gradient(ellipse, rgba(255, 215, 0, 0.95), rgba(255, 140, 0, 0.9));
        border: 4px solid #ff8c00;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        z-index: 3000;
        color: #8b4513;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        box-shadow: 0 20px 60px rgba(255, 140, 0, 0.6);
        animation: secretTreasure 3s ease-out forwards;
    `;
    
    document.body.appendChild(secret);
    
    setTimeout(() => {
        secret.style.animation = 'secretTreasureFade 1s ease-out forwards';
        setTimeout(() => {
            if (secret.parentNode) {
                secret.parentNode.removeChild(secret);
            }
        }, 1000);
    }, 2000);
}

// ===== SUONI (OPZIONALE) =====
function setupSoundEffects() {
    // Sistema audio pronto ma disabilitato di default
    // Puoi abilitare aggiungendo file audio e decommentando il codice
    
    /*
    const sounds = {
        cardHover: new Audio('sounds/card-hover.mp3'),
        cardClick: new Audio('sounds/card-click.mp3'),
        treasure: new Audio('sounds/treasure-found.mp3'),
        secret: new Audio('sounds/secret-unlocked.mp3')
    };
    
    // Precarica i suoni
    Object.values(sounds).forEach(sound => {
        sound.preload = 'auto';
        sound.volume = 0.3;
    });
    
    // Funzione per riprodurre suoni
    window.playSound = function(soundName) {
        if (sounds[soundName]) {
            sounds[soundName].currentTime = 0;
            sounds[soundName].play().catch(e => console.log('Audio not available'));
        }
    };
    */
    
    console.log('🔊 Sistema audio pronto (disabilitato di default)');
}

// ===== CONTATORI TESORI =====
function updateTreasureCounters() {
    const stats = document.querySelector('.completion-stats');
    if (stats) {
        const counters = stats.querySelectorAll('span');
        counters.forEach((counter, index) => {
            const finalCount = [6, 7, 8][index];
            animateCounter(counter, finalCount, index);
        });
    }
}

function animateCounter(element, target, delay) {
    setTimeout(() => {
        let current = 0;
        const increment = target / 50;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            
            const text = element.textContent;
            const prefix = text.split(':')[0];
            element.textContent = `${prefix}: ${Math.floor(current)} Analisi`;
        }, 50);
    }, delay * 500);
}

// ===== UTILITY FUNCTIONS =====

// Smooth scroll per browser più vecchi
function smoothScrollTo(element) {
    if (element) {
        const start = window.pageYOffset;
        const target = element.offsetTop - 100;
        const distance = target - start;
        const duration = 1000;
        let startTime = null;

        function animation(currentTime) {
            if (startTime === null) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const run = ease(timeElapsed, start, distance, duration);
            window.scrollTo(0, run);
            if (timeElapsed < duration) requestAnimationFrame(animation);
        }

        function ease(t, b, c, d) {
            t /= d / 2;
            if (t < 1) return c / 2 * t * t + b;
            t--;
            return -c / 2 * (t * (t - 2) - 1) + b;
        }

        requestAnimationFrame(animation);
    }
}

// Debounce function per performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function per scroll events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// ===== EVENT LISTENERS GLOBALI =====

// Gestione ridimensionamento finestra
window.addEventListener('resize', debounce(() => {
    // Aggiorna posizionamenti se necessario
    console.log('🔄 Finestra ridimensionata, aggiornando layout...');
}, 250));

// Gestione scroll per effetti parallax leggeri
window.addEventListener('scroll', throttle(() => {
    const scrolled = window.pageYOffset;
    const parallax = scrolled * 0.1;
    
    // Effetto parallax leggero per le icone di sfondo
    const floatingIcons = document.querySelectorAll('.floating-icon');
    floatingIcons.forEach((icon, index) => {
        const speed = (index % 3 + 1) * 0.05;
        icon.style.transform = `translateY(${parallax * speed}px)`;
    });
}, 16));

// Gestione visibilità pagina per animazioni
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Pausa animazioni quando la pagina non è visibile
        document.body.style.animationPlayState = 'paused';
    } else {
        // Riprendi animazioni quando la pagina torna visibile
        document.body.style.animationPlayState = 'running';
    }
});

// ===== ACCESSIBILITÀ =====

// Gestione focus per navigazione da tastiera
document.addEventListener('keydown', (e) => {
    // Evidenzia elementi focusabili
    if (e.key === 'Tab') {
        document.body.classList.add('keyboard-navigation');
    }
});

document.addEventListener('mousedown', () => {
    document.body.classList.remove('keyboard-navigation');
});

// Skip link per accessibilità
const skipLink = document.createElement('a');
skipLink.href = '#mongodb-section';
skipLink.textContent = 'Salta alla navigazione principale';
skipLink.style.cssText = `
    position: absolute;
    top: -40px;
    left: 6px;
    background: #8b4513;
    color: white;
    padding: 8px;
    text-decoration: none;
    z-index: 9999;
    border-radius: 4px;
`;
skipLink.addEventListener('focus', () => {
    skipLink.style.top = '6px';
});
skipLink.addEventListener('blur', () => {
    skipLink.style.top = '-40px';
});
document.body.insertBefore(skipLink, document.body.firstChild);

// ===== PERFORMANCE MONITORING =====
if (typeof PerformanceObserver !== 'undefined') {
    const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
            if (entry.entryType === 'measure') {
                console.log(`⚡ ${entry.name}: ${entry.duration.toFixed(2)}ms`);
            }
        });
    });
    observer.observe({ entryTypes: ['measure'] });
    
    // Misura il tempo di caricamento
    performance.mark('treasure-map-start');
    window.addEventListener('load', () => {
        performance.mark('treasure-map-end');
        performance.measure('treasure-map-load', 'treasure-map-start', 'treasure-map-end');
    });
}

// ===== EXPORT PER TESTING (se necessario) =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        createImagePlaceholder,
        debounce,
        throttle,
        smoothScrollTo
    };
}