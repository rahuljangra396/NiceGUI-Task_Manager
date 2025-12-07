from nicegui import ui, app
from datetime import date 

# --- Configuration & State ---

# Colors for styling to match the image
COLOR_PRIMARY_DARK = '#34495e' # Sidebar (Quasar will handle the main dark background)
COLOR_ACTIVE_TEAL = '#1abc9c'
COLOR_COMPLETED_GREEN = '#2ecc71'
# Removed COLOR_BACKGROUND_LIGHT as it's no longer needed in dark mode setup.

# Application State/Data
tasks = [
    {'id': 1, 'name': 'Finish Project Proposal', 'due': 'Today 3 PM', 'completed': False, 'color': 'teal'},
    {'id': 2, 'name': 'Buy Groceries', 'due': 'Tomorrow 10 AM', 'completed': False, 'color': 'teal'},
    {'id': 3, 'name': 'Call Mom', 'due': 'Yesterday 6 PM', 'completed': True, 'color': 'green'},
]
# Global containers and state variables
task_list_container = None
task_count_label = None
current_view = 'Active' 
next_task_id = 4 # Start ID after initial tasks

# Input fields (placeholders for referencing them in functions)
task_name_input = None
task_date_input = None
# Global navigation button references (needed for dynamic styling)
nav_all_btn = None
nav_active_btn = None
nav_completed_btn = None

# --- Functions for Task Management ---

def get_next_id():
    """Generates a new unique ID for a new task."""
    global next_task_id
    current_id = next_task_id
    next_task_id += 1
    return current_id

def toggle_task_completion(task_id):
    """Finds a task by ID and toggles its 'completed' status."""
    task_to_toggle = next((t for t in tasks if t['id'] == task_id), None)
    if task_to_toggle:
        task_to_toggle['completed'] = not task_to_toggle['completed']
        ui.notify(f"Task '{task_to_toggle['name']}' {'Completed' if task_to_toggle['completed'] else 'Reopened'}", 
                  color='green' if task_to_toggle['completed'] else 'orange', 
                  position='top')
        refresh_task_list()

def add_task():
    """Adds a new task using input values and refreshes the UI."""
    global task_name_input, task_date_input 
    
    name = task_name_input.value.strip()
    date_str = task_date_input.value.strip()

    if not name:
        ui.notify('Please enter a task description.', color='red', position='top')
        return

    new_task = {
        'id': get_next_id(), 
        'name': name, 
        'due': date_str if date_str else 'No Due Date', 
        'completed': False, 
        'color': 'teal'
    }
    tasks.append(new_task)
    
    # Reset inputs
    task_name_input.set_value('')
    task_date_input.set_value(str(date.today())) 
    
    # Refresh view
    refresh_task_list()
    ui.notify('Task Added!', color='green', position='top')

def refresh_task_list():
    """Refreshes the task list container based on the current view."""
    global task_list_container, task_count_label
    
    # Filtering logic
    if current_view == 'Active':
        filtered_tasks = [t for t in tasks if not t['completed']]
    elif current_view == 'Completed':
        filtered_tasks = [t for t in tasks if t['completed']]
    else: # All Tasks
        filtered_tasks = tasks
        
    # Update the sidebar task count
    if task_count_label:
        task_count_label.set_text(f'{len(tasks)} tasks')
        
    # Re-render the task list
    if task_list_container:
        task_list_container.clear()
        
        with task_list_container:
            # Note: Quasar's dark mode handles label colors, so we don't need explicit text-gray-500
            ui.label(f'{len(filtered_tasks)} tasks').classes('text-xl font-medium mb-4 mt-6')
            if not filtered_tasks:
                 ui.label('No tasks found in this view.').classes('italic')
            
            with ui.column().classes('w-full space-y-4'):
                for task in filtered_tasks:
                    create_task_card(task)
            
def set_view(view):
    """Changes the filter view and refreshes the list, and updates button styling."""
    global current_view
    current_view = view
    
    # Logic to update sidebar button colors
    # Reset all buttons to default white/flat style
    nav_all_btn.style('background-color: transparent; color: white;')
    nav_active_btn.style('background-color: transparent; color: white; font-weight: normal;')
    nav_completed_btn.style('background-color: transparent; color: white;')
        
    # Set the active button style
    if view == 'All Tasks':
        nav_all_btn.style(f'background-color: {COLOR_ACTIVE_TEAL}; color: white; font-weight: bold;')
    elif view == 'Active':
        nav_active_btn.style(f'background-color: {COLOR_ACTIVE_TEAL}; color: white; font-weight: bold;')
    elif view == 'Completed':
        nav_completed_btn.style(f'background-color: {COLOR_ACTIVE_TEAL}; color: white; font-weight: bold;')
    
    refresh_task_list()

# --- UI Components ---

def create_task_card(task):
    """Creates a stylized card for a single task."""
    card_classes = (
        'w-full shadow-md rounded-xl p-4 transition-all duration-300 '
        f'border-l-4 border-{task["color"]}-500' # No explicit bg-white for dark mode compatibility
    )
    name_classes = 'text-lg font-semibold'
    
    if task['completed']:
        card_classes += ' opacity-80'
        name_classes += ' line-through' # No explicit text-gray-500 for dark mode compatibility

    with ui.card().classes(card_classes).style('min-height: 80px'):
        with ui.row().classes('items-center w-full'):
            icon_name = 'check_circle' if task['completed'] else 'radio_button_unchecked'
            icon_color = COLOR_COMPLETED_GREEN if task['completed'] else COLOR_ACTIVE_TEAL
            
            # Icon that toggles completion when clicked
            ui.icon(icon_name) \
                .classes('text-2xl cursor-pointer') \
                .style(f'color: {icon_color};') \
                .on('click', lambda: toggle_task_completion(task['id']))
            
            with ui.column().classes('flex-grow'):
                ui.label(task['name']).classes(name_classes)
                ui.label(task['due']).classes('text-sm')

# --- Page Layout ---

@ui.page('/')
def main_page():
    global task_list_container, task_count_label, task_name_input, task_date_input
    global nav_all_btn, nav_active_btn, nav_completed_btn
    
    ui.page_title('Task Manager')
    
    # 🌟 NEW: Enable Dark Mode permanently
    ui.dark_mode().enable()
    
    # 0. Header (No Dark Mode Toggle needed)
    with ui.header().classes('items-center justify-between'):
        ui.label('Task Manager').classes('text-xl font-bold text-white') # Explicit text-white for header
    
    # 1. Left Sidebar
    with ui.left_drawer().classes('p-5 text-white').style(f'background-color: {COLOR_PRIMARY_DARK}; width: 250px'):
        # Navigation Links
        nav_all_btn = ui.button('All Tasks', icon='list').props('flat').classes('w-full justify-start text-left mb-2').style('color: white').on('click', lambda: set_view('All Tasks'))

        nav_active_btn = ui.button('Active', icon='radio_button_unchecked').props('flat').classes('w-full justify-start text-left mb-2').on('click', lambda: set_view('Active'))

        nav_completed_btn = ui.button('Completed', icon='check_circle').props('flat').classes('w-full justify-start text-left mb-2').style('color: white').on('click', lambda: set_view('Completed'))
            
        task_count_label = ui.label(f'{len(tasks)} tasks').classes('mt-8 opacity-70 text-sm')

    # 2. Main Content Area
    with ui.column().classes('flex-grow p-10 w-full'):
        ui.label('Dashboard').classes('text-3xl font-light mb-6') 

        # --- Add Task Section (Top Row) ---
        with ui.row().classes('w-full items-center mb-4'):
            # Task Name Input
            # Note: NiceGUI/Quasar handles input styling for dark mode automatically
            task_name_input = ui.input(placeholder='Add a new task...').classes('flex-grow') \
                .props('rounded outlined')
            
            # Add Button (Icon)
            ui.button(icon='add').classes('rounded-full h-12 w-12 text-lg').style(f'background-color: {COLOR_ACTIVE_TEAL}; color: white;').on('click', add_task)

        # --- Date and Button Row (Simplified) ---
        with ui.row().classes('items-center mb-10'):
            
            # Date Picker
            task_date_input = ui.date(value=str(date.today()), 
                                      mask='YYYY-MM-DD').classes('w-36') \
                                  .props('rounded outlined icon=event')
            
            # Main Add Task button
            ui.button('Add Task').classes('font-bold').style(f'background-color: {COLOR_COMPLETED_GREEN}; color: white;').on('click', add_task)


        # --- Task List Container ---
        task_list_container = ui.column().classes('w-full')
        
        # Initial call to set the view and apply styling
        set_view(current_view) 


# --- Run the App ---
if __name__ in {"__main__", "__mp_main__"}:
    ui.run()