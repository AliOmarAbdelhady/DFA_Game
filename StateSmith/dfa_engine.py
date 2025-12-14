"""
DFA Engine for StateSmith Game
Handles DFA validation and testing
"""

class DFA:
    """Deterministic Finite Automaton"""
    
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions  # {state: {symbol: next_state}}
        self.start_state = start_state
        self.accept_states = accept_states
    
    def accepts(self, input_string):
        """Check if the DFA accepts the input string"""
        current_state = self.start_state
        
        for symbol in input_string:
            if symbol not in self.alphabet:
                return False
            
            if current_state not in self.transitions:
                return False
                
            if symbol not in self.transitions[current_state]:
                return False
            
            current_state = self.transitions[current_state][symbol]
        
        return current_state in self.accept_states
    
    def run_with_path(self, input_string):
        """Run DFA and return the path taken"""
        path = [self.start_state]
        current_state = self.start_state
        
        for symbol in input_string:
            if symbol not in self.alphabet:
                return {'valid': False, 'error': f'Symbol {symbol} not in alphabet'}
            
            if current_state not in self.transitions or symbol not in self.transitions[current_state]:
                return {'valid': False, 'error': f'No transition from {current_state} on {symbol}'}
            
            current_state = self.transitions[current_state][symbol]
            path.append(current_state)
        
        return {
            'valid': True,
            'path': path,
            'accepted': current_state in self.accept_states
        }


def validate_dfa(dfa_data, alphabet):
    """Validate that DFA structure is correct"""
    
    # Check required fields
    required_fields = ['states', 'transitions', 'start_state', 'accept_states']
    for field in required_fields:
        if field not in dfa_data:
            return {'valid': False, 'error': f'Missing required field: {field}'}
    
    states = set(dfa_data['states'])
    transitions = dfa_data['transitions']
    start_state = dfa_data['start_state']
    accept_states = set(dfa_data['accept_states'])
    
    # Check states not empty
    if not states:
        return {'valid': False, 'error': 'DFA must have at least one state'}
    
    # Check start state is valid
    if start_state not in states:
        return {'valid': False, 'error': f'Start state "{start_state}" is not in the state set'}
    
    # Check accept states are valid
    for state in accept_states:
        if state not in states:
            return {'valid': False, 'error': f'Accept state "{state}" is not in the state set'}
    
    # Check transitions are complete and deterministic
    for state in states:
        if state not in transitions:
            return {'valid': False, 'error': f'State "{state}" has no transitions defined'}
        
        for symbol in alphabet:
            if symbol not in transitions[state]:
                return {'valid': False, 'error': f'State "{state}" missing transition for symbol "{symbol}"'}
            
            next_state = transitions[state][symbol]
            if next_state not in states:
                return {'valid': False, 'error': f'Transition from "{state}" on "{symbol}" goes to invalid state "{next_state}"'}
    
    return {'valid': True}


def test_dfa_against_level(dfa, level):
    """Test DFA against level requirements"""
    
    good_keys = level['good_keys']
    bad_keys = level['bad_keys']
    
    test_results = []
    all_passed = True
    failed_key = None
    
    # Test all good keys (should be accepted)
    for key in good_keys:
        result = dfa.run_with_path(key)
        passed = result.get('accepted', False)
        
        if not passed:
            all_passed = False
            if failed_key is None:
                failed_key = {'key': key, 'expected': 'accept', 'got': 'reject'}
        
        test_results.append({
            'key': key,
            'expected': 'accept',
            'got': 'accept' if passed else 'reject',
            'passed': passed,
            'path': result.get('path', [])
        })
    
    # Test all bad keys (should be rejected)
    for key in bad_keys:
        result = dfa.run_with_path(key)
        passed = not result.get('accepted', True)
        
        if not passed:
            all_passed = False
            if failed_key is None:
                failed_key = {'key': key, 'expected': 'reject', 'got': 'accept'}
        
        test_results.append({
            'key': key,
            'expected': 'reject',
            'got': 'reject' if passed else 'accept',
            'passed': passed,
            'path': result.get('path', [])
        })
    
    stars = 0
    if all_passed:
        stars = 3  
        
        # Bonus star for efficiency (fewer states)
        state_count = len(dfa.states)
        min_states = level.get('min_states', 2)
        
        if state_count == min_states:
            stars = 3 
        elif state_count <= min_states + 1:
            stars = 3  
        elif state_count <= min_states + 2:
            stars = 2 
        else:
            stars = 1 
    
    if all_passed:
        message = f"🎉 Door unlocked! You earned {stars} star{'s' if stars != 1 else ''}!"
        if stars == 3:
            message += " Perfect solution!"
    else:
        message = "❌ Door remains locked. Some keys don't work correctly."
    
    return {
        'passed': all_passed,
        'stars': stars,
        'message': message,
        'test_results': test_results,
        'failed_key': failed_key
    }
