# NIKKE Automation Framework

This document outlines our development approach for building a reliable automation system for NIKKE: Goddess Of Victory, focusing on the critical components first.

## Core Philosophy

Build from the foundation up, ensuring each critical component works perfectly before adding complexity:

1. **Start with rock-solid recognition** - If the system can't see properly, nothing else matters
2. **Perfect the state management** - Always knowing where we are in the game is crucial
3. **Build robust error recovery** - Prepare for the unexpected, because it will happen
4. **Then add game-specific features** - Only after the foundation is solid

## Components Implemented

- **Screen Capture Module**: Fast, reliable screen grabbing with performance monitoring
- **Template Matching Engine**: Multi-method template matching with confidence scoring
- **State Management System**: Tracking game state with transition pathfinding
- **Input Controller**: Human-like mouse/touch simulation

## Getting Started

### Prerequisites

- Python 3.10 or higher
- OpenCV
- NumPy
- PyAutoGUI
- PyYAML
- Tkinter (for GUI mode)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/nikke-automation.git
   cd nikke-automation
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

You have several options to run the NIKKE Automation Framework:

#### Option 1: Use the Graphical User Interface (GUI)

The easiest way to use the framework is with the GUI:

```
python -m src.cli gui
```

Or just run the CLI without arguments to launch the GUI by default:

```
python -m src.cli
```

The GUI provides a user-friendly interface with tabs for:
- **Template Capture**: Capture template images for game recognition
- **Test**: Run tests to verify the framework's functionality
- **Run Automation**: Start automation with optional navigation to a specific game screen

#### Option 2: Use the Command-Line Interface

For advanced users or automation scripts, the framework includes a convenient CLI:

```
python -m src.cli [command] [options]
```

Available commands:
- `gui` - Launch the graphical user interface
- `capture` - Capture template images
- `test` - Run a test of the framework
- `run` - Start automation (with optional navigation)

Examples:
```
# Capture a template image for a home screen UI
python -m src.cli capture --name main_ui --category home

# Run a framework test
python -m src.cli test

# Run automation and navigate to the shop
python -m src.cli run --navigate SHOP
```

#### Option 3: Use the Batch File (Windows)

On Windows, you can use the included batch file:

```
nikke-auto.bat [command] [options]
```

This works the same way as the CLI option.

#### Option 4: Build and Use the Executable

1. Build the standalone executable:
   ```
   python build_exe.py
   ```

2. Once built, you can run the executable directly:
   ```
   dist/nikke-auto [command] [options]
   ```

   Or simply double-click the executable to launch the GUI interface.

### Creating Template Images

Template images are required for the framework to recognize the game's UI elements.

To capture a template using the GUI:
1. Launch the GUI with `python -m src.cli gui`
2. Go to the "Template Capture" tab
3. Enter the UI element name and select a category
4. Click "Capture Template" and select the region on your screen

To capture a template using the CLI:
1. Run the template capture command:
   ```
   python -m src.cli capture --name main_ui --category home
   ```

2. Use the mouse to select the region of the screen containing the UI element.

3. The template will be saved to `resources/templates/home/main_ui.png`.

#### Key Templates Needed

##### Home Screen Templates
- `home/main_ui` - Full screenshot of home screen UI for state detection
- `home/shop_icon` - Button to navigate to shop

##### Shop Templates
- `shop/shop_ui` - Complete shop screen UI for state detection
- `shop/credit_items` - Templates for items purchasable with CREDITS only
- `shop/confirm_purchase` - The purchase confirmation button
- `shop/currency_credits` - To verify correct currency (NOT gems)

##### Common Elements
- `common/return_home` - Return to home button (appears in multiple screens)
- `common/close_button` - Generic X/close for popup handling
- `common/confirm_button` - Generic OK/confirm for popup handling
- `common/empty_area` - Safe area to click to dismiss popups
- `common/loading_indicator` - To detect when game is loading

### Usage Examples

Basic automation:
```python
from src.main import NikkeAutomation

# Initialize the automation system
automation = NikkeAutomation()

# Update the current state
state = automation.update_state()
print(f"Current state: {state}")

# Navigate to a different state
automation.navigate_to(GameState.SHOP)
```

## Testing

Run the tests using pytest:

```
pytest tests/
```

## Development Path

### 1️⃣ Vision System Foundation (The Eyes)

**Goal**: Build a system that can reliably see and understand the game screen.

**Core Components**:
- **Screen Capture Module**
  - Fast, reliable screen grabbing
  - Region-of-interest optimization
  - Device/emulator compatibility

- **Template Matching Engine**
  - Template storage and organization
  - Multi-method matching (exact, feature-based, color-based)
  - Confidence scoring and threshold management
  
- **OCR Integration**
  - Text region isolation
  - Pre-processing for recognition optimization
  - Text cleaning and normalization

**Success Requirements**:
- Detect UI elements with >95% accuracy
- Identify text content correctly >90% of time
- Process screens fast enough for real-time decision making (<100ms)
- Handle different resolutions and aspect ratios

### 2️⃣ State Management System (The Brain)

**Goal**: Create a system that always knows exactly where it is in the game.

**Core Components**:
- **State Representation**
  - Hierarchical state structure (main screens → sub-screens → actions)
  - State verification mechanisms
  - State transition rules

- **Navigation Engine**
  - Pathfinding between states
  - Minimum-action navigation calculations
  - Navigation verification

- **Context Awareness**
  - Game event detection
  - Time-dependent state handling
  - Dynamic element tracking

**Success Requirements**:
- Maintain accurate state tracking through 100+ state transitions
- Recover from incorrect state assessments
- Navigate efficiently between any two states
- Detect when navigation fails

### 3️⃣ Input & Error Recovery System (The Hands & Immune System)

**Goal**: Develop reliable interaction with perfect timing and resilience to failures.

**Core Components**:
- **Input Simulation**
  - Precise click/tap positioning
  - Natural timing patterns
  - Gesture simulation (swipes, drags)

- **Error Detection**
  - Unexpected state detection
  - Timeout management
  - Performance monitoring

- **Recovery Mechanisms**
  - Multi-tiered recovery strategies
  - Safe state return procedures
  - Incremental retry logic

**Success Requirements**:
- Simulate human-like input patterns
- Detect >90% of error conditions
- Recover automatically from common errors
- Gracefully handle unexpected situations

### 4️⃣ Game Task Implementation (The Skills)

**Goal**: Build specific game automation features on top of the solid foundation.

**Implementation Order** (easiest to hardest):
1. **Daily Login & Collection**
   - Login rewards
   - Mail collection
   - Shop free items

2. **Resource Management**
   - Dispatch missions
   - Arena entries
   - Material dungeon runs

3. **Event Participation**
   - Event stage completion
   - Token/currency usage
   - Reward collection

4. **Combat Automation**
   - Team selection
   - Battle execution
   - Skill activation

## Technical Implementation

### Core Technology
- **Language**: Python 3.10+
- **Primary Libraries**:
  - OpenCV (computer vision)
  - PyAutoGUI (screen interaction)
  - Tesseract (OCR)
  - NumPy (data processing)

### Project Structure
```
src/
├── core/
│   ├── vision/          # Screen capture & recognition
│   ├── state/           # State management 
│   ├── input/           # Input simulation
│   └── recovery/        # Error handling
├── game/
│   ├── screens/         # Screen definitions
│   ├── tasks/           # Task implementations
│   └── navigation/      # Navigation maps
├── utils/
│   ├── logging/         # Detailed logging
│   ├── calibration/     # System tuning
│   └── templates/       # Image templates
└── main.py              # Entry point
```

## Development Process

### Phase 1: Foundation (Weeks 1-3)
Focus exclusively on the Vision, State, and Input systems:

1. **Develop template matching workflow**
   - Create template capture utility
   - Build multi-method matching engine
   - Test against various game screens

2. **Build core state detection**
   - Map main game screens
   - Implement state detection logic
   - Create transition testing utility

3. **Input simulation engine**
   - Implement click patterns with variable timing
   - Create swipe and gesture simulator
   - Test input accuracy and reliability

**Phase 1 Success Criteria**: Navigate between 5 main game screens reliably, detect UI elements with >95% accuracy, and recover from basic errors.

### Phase 2: First Tasks (Weeks 4-5)
Implement the simplest daily activities:

1. **Daily login automation**
   - Login sequence detection and execution
   - Reward collection
   - Completion verification

2. **Mail and shop collection**
   - Navigation to mail/shop
   - Item collection logic
   - Return to main screen

**Phase 2 Success Criteria**: Complete daily login routine with no manual intervention for 5 consecutive days.

### Phase 3: Expanding Capabilities (Weeks 6-8)
Add more complex game interactions:

1. **Resource optimization**
   - Dispatch mission management
   - Arena participation
   - Material dungeon farming

2. **Event participation**
   - Event detection
   - Stage completion
   - Resource management

**Phase 3 Success Criteria**: Handle multiple game activities with appropriate prioritization and time management.

### Phase 4: Advanced Features (Weeks 9-10)
Tackle the most challenging aspects:

1. **Combat automation**
   - Team composition
   - Battle execution
   - Strategy implementation

2. **Dynamic adaptation**
   - New event handling
   - Unfamiliar screen detection
   - Self-optimization

**Phase 4 Success Criteria**: Complete full daily routine including combat with high efficiency and minimal errors.

## Starting Point

Begin by building the absolute core of the system:

1. Create the screen capture module
2. Build a simple template matcher for main menu elements
3. Implement basic state detection for 2-3 main screens
4. Test navigation between these screens

This foundation will reveal early challenges and allow us to adjust our approach before building more complex features.