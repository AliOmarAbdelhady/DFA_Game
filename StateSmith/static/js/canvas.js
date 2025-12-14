// Canvas state management
let canvas, ctx;
let states = [];
let transitions = {};
let startState = null;
let acceptStates = new Set();
let selectedState = null;
let draggedState = null;
let stateCounter = 0;
let offsetX = 0, offsetY = 0;

// Constants
const STATE_RADIUS = 30;
const STATE_COLOR = '#1a1f3a';
const STATE_BORDER = '#ff6b35';
const START_COLOR = '#06d6a0';
const ACCEPT_COLOR = '#ffd23f';
const SELECTED_COLOR = '#ef476f';
const TRANSITION_COLOR = '#9fa8da';

// Initialize canvas
function initCanvas() {
    canvas = document.getElementById('state-canvas');
    if (!canvas) return;
    
    ctx = canvas.getContext('2d');
    
    // Event listeners
    canvas.addEventListener('click', handleCanvasClick);
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('contextmenu', handleRightClick);
    
    drawCanvas();
}

function resetCanvas() {
    states = [];
    transitions = {};
    startState = null;
    acceptStates = new Set();
    selectedState = null;
    stateCounter = 0;
    
    updateSelectedStateDisplay();
    
    if (canvas) {
        drawCanvas();
    } else {
        setTimeout(initCanvas, 100);
    }
}

// Drawing functions
function drawCanvas() {
    if (!ctx || !canvas) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw transitions
    Object.keys(transitions).forEach(fromState => {
        Object.keys(transitions[fromState]).forEach(symbol => {
            const toState = transitions[fromState][symbol];
            drawTransition(fromState, toState, symbol);
        });
    });
    
    // Draw states
    states.forEach(state => {
        drawState(state);
    });
}

function drawState(state) {
    // Main circle
    ctx.beginPath();
    ctx.arc(state.x, state.y, STATE_RADIUS, 0, 2 * Math.PI);
    ctx.fillStyle = STATE_COLOR;
    ctx.fill();
    
    // Border
    ctx.strokeStyle = selectedState === state.id ? SELECTED_COLOR : STATE_BORDER;
    ctx.lineWidth = 3;
    ctx.stroke();
    
    // Accept state (double circle)
    if (acceptStates.has(state.id)) {
        ctx.beginPath();
        ctx.arc(state.x, state.y, STATE_RADIUS - 6, 0, 2 * Math.PI);
        ctx.strokeStyle = ACCEPT_COLOR;
        ctx.lineWidth = 2;
        ctx.stroke();
    }
    
    // Start state (arrow)
    if (startState === state.id) {
        ctx.strokeStyle = START_COLOR;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(state.x - STATE_RADIUS - 30, state.y);
        ctx.lineTo(state.x - STATE_RADIUS - 5, state.y);
        ctx.stroke();
        
        // Arrowhead
        ctx.beginPath();
        ctx.moveTo(state.x - STATE_RADIUS - 5, state.y);
        ctx.lineTo(state.x - STATE_RADIUS - 15, state.y - 5);
        ctx.lineTo(state.x - STATE_RADIUS - 15, state.y + 5);
        ctx.closePath();
        ctx.fillStyle = START_COLOR;
        ctx.fill();
    }
    
    // State label
    ctx.fillStyle = '#e8eaf6';
    ctx.font = 'bold 16px Inter';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(state.id, state.x, state.y);
}

function drawTransition(fromId, toId, symbol) {
    const fromState = states.find(s => s.id === fromId);
    const toState = states.find(s => s.id === toId);
    
    if (!fromState || !toState) return;
    
    // Self-loop
    if (fromId === toId) {
        drawSelfLoop(fromState, symbol);
        return;
    }
    
    // Calculate arrow position
    const dx = toState.x - fromState.x;
    const dy = toState.y - fromState.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    const fromX = fromState.x + (dx / distance) * STATE_RADIUS;
    const fromY = fromState.y + (dy / distance) * STATE_RADIUS;
    const toX = toState.x - (dx / distance) * STATE_RADIUS;
    const toY = toState.y - (dy / distance) * STATE_RADIUS;
    
    // Draw arrow
    ctx.strokeStyle = TRANSITION_COLOR;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(fromX, fromY);
    ctx.lineTo(toX, toY);
    ctx.stroke();
    
    // Arrowhead
    const angle = Math.atan2(dy, dx);
    const arrowSize = 10;
    
    ctx.beginPath();
    ctx.moveTo(toX, toY);
    ctx.lineTo(
        toX - arrowSize * Math.cos(angle - Math.PI / 6),
        toY - arrowSize * Math.sin(angle - Math.PI / 6)
    );
    ctx.lineTo(
        toX - arrowSize * Math.cos(angle + Math.PI / 6),
        toY - arrowSize * Math.sin(angle + Math.PI / 6)
    );
    ctx.closePath();
    ctx.fillStyle = TRANSITION_COLOR;
    ctx.fill();
    
    // Label
    const midX = (fromState.x + toState.x) / 2;
    const midY = (fromState.y + toState.y) / 2;
    
    ctx.fillStyle = '#1a1f3a';
    ctx.fillRect(midX - 12, midY - 12, 24, 24);
    ctx.fillStyle = '#ffd23f';
    ctx.font = 'bold 14px Courier New';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(symbol, midX, midY);
}

function drawSelfLoop(state, symbol) {
    const loopRadius = 25;
    const loopX = state.x;
    const loopY = state.y - STATE_RADIUS - loopRadius;
    
    ctx.strokeStyle = TRANSITION_COLOR;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(loopX, loopY, loopRadius, 0, 2 * Math.PI);
    ctx.stroke();
    
    // Arrow
    ctx.beginPath();
    ctx.moveTo(loopX + 10, loopY + loopRadius);
    ctx.lineTo(loopX + 15, loopY + loopRadius - 5);
    ctx.lineTo(loopX + 5, loopY + loopRadius - 5);
    ctx.closePath();
    ctx.fillStyle = TRANSITION_COLOR;
    ctx.fill();
    
    // Label
    ctx.fillStyle = '#ffd23f';
    ctx.font = 'bold 14px Courier New';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(symbol, loopX, loopY);
}

// Event handlers
function handleCanvasClick(e) {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Check if clicked on existing state
    const clickedState = states.find(s => {
        const dist = Math.sqrt((s.x - x) ** 2 + (s.y - y) ** 2);
        return dist <= STATE_RADIUS;
    });
    
    if (clickedState) {
        selectState(clickedState.id);
    } else {
        // Add new state
        addStateAt(x, y);
    }
}

function handleMouseDown(e) {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const clickedState = states.find(s => {
        const dist = Math.sqrt((s.x - x) ** 2 + (s.y - y) ** 2);
        return dist <= STATE_RADIUS;
    });
    
    if (clickedState) {
        draggedState = clickedState;
        offsetX = x - clickedState.x;
        offsetY = y - clickedState.y;
    }
}

function handleMouseMove(e) {
    if (!draggedState) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    draggedState.x = x - offsetX;
    draggedState.y = y - offsetY;
    
    // Keep within bounds
    draggedState.x = Math.max(STATE_RADIUS + 20, Math.min(canvas.width - STATE_RADIUS - 20, draggedState.x));
    draggedState.y = Math.max(STATE_RADIUS + 20, Math.min(canvas.height - STATE_RADIUS - 20, draggedState.y));
    
    drawCanvas();
}

function handleMouseUp() {
    draggedState = null;
}

function handleRightClick(e) {
    e.preventDefault();
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const clickedState = states.find(s => {
        const dist = Math.sqrt((s.x - x) ** 2 + (s.y - y) ** 2);
        return dist <= STATE_RADIUS;
    });
    
    if (clickedState && currentLevel) {
        showTransitionDialog(clickedState.id);
    }
}

// State management
function addState() {
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    addStateAt(centerX, centerY);
}

function addStateAt(x, y) {
    const newState = {
        id: `q${stateCounter}`,
        x: x,
        y: y
    };
    
    states.push(newState);
    transitions[newState.id] = {};
    
    // Auto-set first state as start state
    if (states.length === 1) {
        startState = newState.id;
    }
    
    stateCounter++;
    selectState(newState.id);
    drawCanvas();
    
    showToast(`State ${newState.id} added!`, 'info');
}

function selectState(stateId) {
    selectedState = stateId;
    updateSelectedStateDisplay();
    drawCanvas();
}

function updateSelectedStateDisplay() {
    const display = document.getElementById('selected-state-display');
    if (display) {
        display.textContent = selectedState || 'None';
    }
}

function toggleStartState() {
    if (!selectedState) {
        showToast('Select a state first!', 'error');
        return;
    }
    
    startState = selectedState;
    drawCanvas();
    showToast(`${selectedState} set as start state!`, 'success');
}

function toggleAcceptState() {
    if (!selectedState) {
        showToast('Select a state first!', 'error');
        return;
    }
    
    if (acceptStates.has(selectedState)) {
        acceptStates.delete(selectedState);
        showToast(`${selectedState} is no longer an accept state`, 'info');
    } else {
        acceptStates.add(selectedState);
        showToast(`${selectedState} is now an accept state!`, 'success');
    }
    
    drawCanvas();
}

function deleteSelected() {
    if (!selectedState) {
        showToast('Select a state first!', 'error');
        return;
    }
    
    if (!confirm(`Delete state ${selectedState}?`)) {
        return;
    }
    
    // Remove state
    states = states.filter(s => s.id !== selectedState);
    
    // Remove transitions
    delete transitions[selectedState];
    Object.keys(transitions).forEach(from => {
        Object.keys(transitions[from]).forEach(symbol => {
            if (transitions[from][symbol] === selectedState) {
                delete transitions[from][symbol];
            }
        });
    });
    
    // Clear if start/accept
    if (startState === selectedState) startState = null;
    acceptStates.delete(selectedState);
    
    selectedState = null;
    updateSelectedStateDisplay();
    drawCanvas();
    
    showToast('State deleted!', 'info');
}

function clearCanvas() {
    if (!confirm('Clear all states and transitions?')) {
        return;
    }
    
    resetCanvas();
    showToast('Canvas cleared!', 'info');
}

// Transition management
function showTransitionDialog(fromState) {
    if (!currentLevel) return;
    
    const alphabet = currentLevel.alphabet;
    
    let message = `Add transitions from ${fromState}:\n\n`;
    
    alphabet.forEach(symbol => {
        const current = transitions[fromState]?.[symbol] || 'none';
        const input = prompt(`${message}Transition on "${symbol}" goes to:\n(Current: ${current})`, current);
        
        if (input !== null && input.trim() !== '') {
            const toState = input.trim();
            
            // Validate target state exists
            if (!states.find(s => s.id === toState)) {
                showToast(`State "${toState}" doesn't exist!`, 'error');
                return;
            }
            
            if (!transitions[fromState]) {
                transitions[fromState] = {};
            }
            transitions[fromState][symbol] = toState;
        }
    });
    
    drawCanvas();
    showToast('Transitions updated!', 'success');
}

// Get DFA data for testing
function getDFAFromCanvas() {
    if (states.length === 0) {
        showToast('Add some states first!', 'error');
        return null;
    }
    
    if (!startState) {
        showToast('Set a start state!', 'error');
        return null;
    }
    
    if (acceptStates.size === 0) {
        showToast('Set at least one accept state!', 'error');
        return null;
    }
    
    // Check all transitions are defined
    const alphabet = currentLevel.alphabet;
    for (let state of states) {
        for (let symbol of alphabet) {
            if (!transitions[state.id] || !transitions[state.id][symbol]) {
                showToast(`Missing transition from ${state.id} on "${symbol}"!`, 'error');
                return null;
            }
        }
    }
    
    return {
        states: states.map(s => s.id),
        transitions: transitions,
        start_state: startState,
        accept_states: Array.from(acceptStates)
    };
}

// Initialize when DOM is ready
setTimeout(() => {
    initCanvas();
}, 100);
