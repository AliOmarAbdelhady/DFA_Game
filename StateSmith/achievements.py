# Achievements System for StateSmith

ACHIEVEMENTS = [
    {
        'id': 'first_escape',
        'title': 'First Escape',
        'description': 'Complete your first level',
        'icon': 'fa-door-open',
        'requirement': lambda progress: progress['completed_levels'] >= 1
    },
    {
        'id': 'perfect_escape',
        'title': 'Perfect Escape',
        'description': 'Get 3 stars on any level',
        'icon': 'fa-star',
        'requirement': lambda progress: any(level['stars'] == 3 for level in progress['levels'].values())
    },
    {
        'id': 'dungeon_crawler',
        'title': 'Dungeon Crawler',
        'description': 'Complete 5 levels',
        'icon': 'fa-dungeon',
        'requirement': lambda progress: progress['completed_levels'] >= 5
    },
    {
        'id': 'state_master',
        'title': 'State Master',
        'description': 'Complete 10 levels',
        'icon': 'fa-crown',
        'requirement': lambda progress: progress['completed_levels'] >= 10
    },
    {
        'id': 'perfectionist',
        'title': 'Perfectionist',
        'description': 'Get 3 stars on 5 levels',
        'icon': 'fa-gem',
        'requirement': lambda progress: sum(1 for level in progress['levels'].values() if level['stars'] == 3) >= 5
    },
    {
        'id': 'efficiency_expert',
        'title': 'Efficiency Expert',
        'description': 'Complete a level with minimal states',
        'icon': 'fa-compress',
        'requirement': lambda progress: any(level['stars'] == 3 for level in progress['levels'].values())
    },
    {
        'id': 'grand_master',
        'title': 'Grand Master',
        'description': 'Complete all levels',
        'icon': 'fa-trophy',
        'requirement': lambda progress: progress['completed_levels'] >= 12
    },
    {
        'id': 'flawless_victory',
        'title': 'Flawless Victory',
        'description': 'Get 3 stars on all levels',
        'icon': 'fa-medal',
        'requirement': lambda progress: all(level['stars'] == 3 for level in progress['levels'].values() if level['completed'])
    },
    {
        'id': 'quick_learner',
        'title': 'Quick Learner',
        'description': 'Complete tutorial without hints',
        'icon': 'fa-graduation-cap',
        'requirement': lambda progress: progress['levels'].get(1, {}).get('completed', False)
    },
    {
        'id': 'star_collector',
        'title': 'Star Collector',
        'description': 'Collect 20 stars total',
        'icon': 'fa-stars',
        'requirement': lambda progress: progress['total_stars'] >= 20
    }
]

def check_achievements(progress):
    """Check which achievements have been unlocked"""
    unlocked = []
    for achievement in ACHIEVEMENTS:
        try:
            if achievement['requirement'](progress):
                unlocked.append({
                    'id': achievement['id'],
                    'title': achievement['title'],
                    'description': achievement['description'],
                    'icon': achievement['icon']
                })
        except:
            pass
    return unlocked

def get_new_achievements(old_progress, new_progress):
    """Get newly unlocked achievements"""
    old_achievements = set(a['id'] for a in check_achievements(old_progress))
    new_achievements = set(a['id'] for a in check_achievements(new_progress))
    newly_unlocked = new_achievements - old_achievements
    
    return [a for a in ACHIEVEMENTS if a['id'] in newly_unlocked]
