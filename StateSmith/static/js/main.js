// Global state
let currentLevel = null;
let levels = [];
let progress = {};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadProgress();
    loadLevels();
});

// Screen navigation
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
}

function showMenu() {
    showScreen('menu-screen');
}

function showLevelSelect() {
    showScreen('level-select-screen');
    renderLevels();
}

function showInstructions() {
    document.getElementById('instructions-modal').classList.add('active');
}

function showProgress() {
    loadProgress();
    const completed = progress.completed_levels || 0;
    const totalStars = progress.total_stars || 0;
    const totalLevels = levels.length;
    
    showToast(`Progress: ${completed}/${totalLevels} levels completed with ${totalStars} total stars!`, 'info');
}

// Load levels from API
async function loadLevels() {
    try {
        const response = await fetch('/api/levels');
        const data = await response.json();
        if (data.success) {
            levels = data.levels;
        }
    } catch (error) {
        console.error('Error loading levels:', error);
        showToast('Failed to load levels', 'error');
    }
}

// Load progress
async function loadProgress() {
    try {
        const response = await fetch('/api/progress');
        const data = await response.json();
        if (data.success) {
            progress = data.progress;
            updateProgressDisplay();
        }
    } catch (error) {
        console.error('Error loading progress:', error);
    }
}

function updateProgressDisplay() {
    const totalStarsEl = document.getElementById('total-stars');
    if (totalStarsEl) {
        totalStarsEl.textContent = progress.total_stars || 0;
    }
}

// Render levels grid
function renderLevels() {
    const grid = document.getElementById('levels-grid');
    grid.innerHTML = '';
    
    levels.forEach(level => {
        const levelProgress = progress.levels?.[level.id] || {};
        const stars = levelProgress.stars || 0;
        const unlocked = levelProgress.unlocked || false;
        const completed = levelProgress.completed || false;
        
        const card = document.createElement('div');
        card.className = `level-card ${unlocked ? '' : 'locked'}`;
        
        if (unlocked) {
            card.onclick = () => startLevel(level.id);
        }
        
        card.innerHTML = `
            <div class="level-header">
                <span class="level-number">${unlocked ? `Level ${level.id}` : '<i class="fas fa-lock"></i>'}</span>
                <span class="level-difficulty ${level.difficulty}">${level.difficulty}</span>
            </div>
            <h3 class="level-title">${unlocked ? level.title : '???'}</h3>
            <div class="level-stars">
                ${[1, 2, 3].map(i => `<i class="fas fa-star ${i <= stars ? 'earned' : ''}"></i>`).join('')}
            </div>
        `;
        
        grid.appendChild(card);
    });
}

// Start a level
async function startLevel(levelId) {
    try {
        const response = await fetch(`/api/level/${levelId}`);
        const data = await response.json();
        
        if (!data.success) {
            showToast(data.error, 'error');
            return;
        }
        
        currentLevel = data.level;
        showScreen('game-screen');
        renderLevelData();
        resetCanvas();
        
    } catch (error) {
        console.error('Error loading level:', error);
        showToast('Failed to load level', 'error');
    }
}

// Render level data on game screen
function renderLevelData() {
    document.getElementById('level-title').textContent = `Level ${currentLevel.id}: ${currentLevel.title}`;
    document.getElementById('difficulty-badge').textContent = currentLevel.difficulty;
    document.getElementById('level-description').textContent = currentLevel.description;
    document.getElementById('level-rule').textContent = currentLevel.rule;
    
    // Alphabet
    const alphabetDisplay = document.getElementById('alphabet-display');
    alphabetDisplay.innerHTML = currentLevel.alphabet.map(symbol => 
        `<span class="alphabet-symbol">${symbol || 'ε'}</span>`
    ).join('');
    
    // Test keys
    const goodKeysEl = document.getElementById('good-keys');
    goodKeysEl.innerHTML = currentLevel.good_keys.map(key => 
        `<span class="key-badge good">${key || '(empty)'}</span>`
    ).join('');
    
    const badKeysEl = document.getElementById('bad-keys');
    badKeysEl.innerHTML = currentLevel.bad_keys.map(key => 
        `<span class="key-badge bad">${key || '(empty)'}</span>`
    ).join('');
    
    // Clear test results
    document.getElementById('test-results').innerHTML = '<p class="placeholder-text">Build your automaton and test it!</p>';
}

// Exit level
function exitLevel() {
    if (confirm('Exit this level? Your progress will be lost.')) {
        currentLevel = null;
        showLevelSelect();
    }
}

// Test solution
async function testSolution() {
    if (!currentLevel) return;
    
    const dfa = getDFAFromCanvas();
    
    if (!dfa) {
        showToast('Please build a complete automaton first!', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/test_solution', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                level_id: currentLevel.id,
                dfa: dfa
            })
        });
        
        const result = await response.json();
        
        if (!result.success) {
            showToast(result.error, 'error');
            if (result.hint) {
                showToast(result.hint, 'info');
            }
            return;
        }
        
        // Display test results
        displayTestResults(result.test_results);
        
        // Show result modal
        if (result.passed) {
            showSuccessModal(result);
            
            // Show achievement notifications
            if (result.new_achievements && result.new_achievements.length > 0) {
                result.new_achievements.forEach((achievement, index) => {
                    setTimeout(() => {
                        showAchievementNotification(achievement);
                    }, 1000 + (index * 4500)); // Stagger notifications
                });
            }
        } else {
            showFailureModal(result);
        }
        
    } catch (error) {
        console.error('Error testing solution:', error);
        showToast('Failed to test solution', 'error');
    }
}

// Display test results
function displayTestResults(results) {
    const container = document.getElementById('test-results');
    container.innerHTML = '';
    
    results.forEach(result => {
        const item = document.createElement('div');
        item.className = `test-result-item ${result.passed ? 'passed' : 'failed'}`;
        
        const icon = result.passed ? '<i class="fas fa-check-circle" style="color: var(--success);"></i>' : '<i class="fas fa-times-circle" style="color: var(--danger);"></i>';
        
        item.innerHTML = `
            <div class="result-key">"${result.key || '(empty)'}"</div>
            <div class="result-status">
                ${icon}
                <span>Expected: ${result.expected} | Got: ${result.got}</span>
            </div>
        `;
        
        container.appendChild(item);
    });
}

// Show success modal
function showSuccessModal(result) {
    const modal = document.getElementById('result-modal');
    const content = document.getElementById('result-content');
    
    const stars = result.stars;
    const starsHTML = [1, 2, 3].map(i => 
        `<i class="fas fa-star ${i <= stars ? 'star-sparkle' : ''}" style="${i <= stars ? 'color: var(--accent);' : 'color: var(--border);'}"></i>`
    ).join('');
    
    content.innerHTML = `
        <div class="result-icon success celebrate">
            <i class="fas fa-door-open"></i>
        </div>
        <div class="result-message">${result.message}</div>
        <div class="result-stars">${starsHTML}</div>
        <div class="result-buttons">
            ${result.next_level_unlocked ? '<button class="result-btn primary" onclick="nextLevel()"><i class="fas fa-arrow-right"></i> Next Level</button>' : ''}
            <button class="result-btn secondary" onclick="closeResultModal()"><i class="fas fa-redo"></i> Try Again</button>
            <button class="result-btn secondary" onclick="exitToMenu()"><i class="fas fa-list"></i> Level Select</button>
        </div>
    `;
    
    modal.classList.add('active');
    
    // Create confetti effect for 3-star solutions
    if (stars === 3) {
        createConfetti();
    }
    
    // Update progress
    loadProgress();
}

// Confetti celebration effect
function createConfetti() {
    const colors = ['#ff6b35', '#ffd23f', '#06d6a0', '#ef476f', '#9b59b6'];
    
    for (let i = 0; i < 50; i++) {
        setTimeout(() => {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.animationDelay = Math.random() * 0.5 + 's';
            confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
            
            document.body.appendChild(confetti);
            
            setTimeout(() => confetti.remove(), 3000);
        }, i * 30);
    }
}

// Show failure modal
function showFailureModal(result) {
    const modal = document.getElementById('result-modal');
    const content = document.getElementById('result-content');
    
    let failureDetails = '';
    if (result.failed_key) {
        failureDetails = `<p style="color: var(--text-muted); margin: 15px 0;">Failed on key: "${result.failed_key.key}" (expected: ${result.failed_key.expected}, got: ${result.failed_key.got})</p>`;
    }
    
    content.innerHTML = `
        <div class="result-icon failure">
            <i class="fas fa-door-closed"></i>
        </div>
        <div class="result-message">${result.message}</div>
        ${failureDetails}
        <div class="result-buttons">
            <button class="result-btn primary" onclick="closeResultModal()"><i class="fas fa-edit"></i> Fix Automaton</button>
            <button class="result-btn secondary" onclick="exitToMenu()"><i class="fas fa-list"></i> Level Select</button>
        </div>
    `;
    
    modal.classList.add('active');
}

function closeResultModal() {
    document.getElementById('result-modal').classList.remove('active');
}

function nextLevel() {
    closeResultModal();
    if (currentLevel) {
        startLevel(currentLevel.id + 1);
    }
}

function exitToMenu() {
    closeResultModal();
    showLevelSelect();
}

// Show hint
async function showHint() {
    if (!currentLevel) return;
    
    try {
        const response = await fetch(`/api/hint/${currentLevel.id}`);
        const data = await response.json();
        
        if (data.success) {
            showToast(`Hint: ${data.hint}`, 'info');
        }
    } catch (error) {
        console.error('Error getting hint:', error);
    }
}

// Modal controls
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Achievements
async function showAchievements() {
    try {
        const response = await fetch('/api/achievements');
        const data = await response.json();
        
        if (data.success) {
            const grid = document.getElementById('achievements-grid');
            
            // Define all possible achievements with locked state
            const allAchievements = [
                { id: 'first_escape', title: 'First Escape', description: 'Complete your first level', icon: 'fa-door-open' },
                { id: 'perfect_escape', title: 'Perfect Escape', description: 'Get 3 stars on any level', icon: 'fa-star' },
                { id: 'dungeon_crawler', title: 'Dungeon Crawler', description: 'Complete 5 levels', icon: 'fa-dungeon' },
                { id: 'state_master', title: 'State Master', description: 'Complete 10 levels', icon: 'fa-crown' },
                { id: 'perfectionist', title: 'Perfectionist', description: 'Get 3 stars on 5 levels', icon: 'fa-gem' },
                { id: 'efficiency_expert', title: 'Efficiency Expert', description: 'Complete a level with minimal states', icon: 'fa-compress' },
                { id: 'grand_master', title: 'Grand Master', description: 'Complete all levels', icon: 'fa-trophy' },
                { id: 'flawless_victory', title: 'Flawless Victory', description: 'Get 3 stars on all levels', icon: 'fa-medal' },
                { id: 'quick_learner', title: 'Quick Learner', description: 'Complete tutorial without hints', icon: 'fa-graduation-cap' },
                { id: 'star_collector', title: 'Star Collector', description: 'Collect 20 stars total', icon: 'fa-stars' }
            ];
            
            const unlockedIds = new Set(data.achievements.map(a => a.id));
            
            grid.innerHTML = allAchievements.map(achievement => {
                const unlocked = unlockedIds.has(achievement.id);
                return `
                    <div class="achievement-card ${unlocked ? 'unlocked' : 'locked'}">
                        <div class="achievement-icon">
                            <i class="fas ${achievement.icon}"></i>
                        </div>
                        <h4>${achievement.title}</h4>
                        <p>${achievement.description}</p>
                        ${unlocked ? '<div class="achievement-badge">✓ Unlocked</div>' : '<div class="achievement-badge">Locked</div>'}
                    </div>
                `;
            }).join('');
            
            document.getElementById('achievements-modal').classList.add('active');
        }
    } catch (error) {
        console.error('Error loading achievements:', error);
        showToast('Failed to load achievements', 'error');
    }
}

function showAchievementNotification(achievement) {
    const notification = document.getElementById('achievement-notification');
    notification.querySelector('.achievement-icon i').className = `fas ${achievement.icon}`;
    notification.querySelector('.achievement-title').textContent = `🎉 ${achievement.title}`;
    notification.querySelector('.achievement-description').textContent = achievement.description;
    
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}

// Toast notification
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}
