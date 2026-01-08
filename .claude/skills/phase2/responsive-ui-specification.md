# Skill: responsive-ui-specification

## 1. Skill Name
`responsive-ui-specification`

## 2. Purpose
Define responsive behavior and layout patterns for the todo application UI across different screen sizes (mobile, tablet, desktop) without prescribing specific implementation details, ensuring usability on all devices.

## 3. Applicable Agents
- **nextjs-frontend-architect** (primary)
- fullstack-spec-architect (UX coordination)

## 4. Inputs
- **Target Devices**: Mobile (320px+), Tablet (768px+), Desktop (1024px+)
- **UI Components**: Todo list, forms, navigation, modals
- **User Workflows**: CRUD operations on different screen sizes
- **Accessibility Requirements**: Touch targets, keyboard navigation

## 5. Outputs
- **Breakpoint Specification**: Screen size thresholds and behaviors
- **Layout Pattern Documentation**: Grid, flex, stack patterns
- **Component Responsive Behaviors**: How components adapt to screen size
- **Touch-Friendly Specifications**: Button sizes, spacing, gestures
- **Accessibility Requirements**: ARIA labels, keyboard navigation, focus management

## 6. Scope & Boundaries

### In Scope
- Responsive layout patterns (semantic, not CSS)
- Component behavior across breakpoints
- Touch target sizing (44px minimum)
- Mobile navigation patterns
- Form usability on small screens

### Out of Scope
- Specific CSS frameworks or libraries
- Visual design (colors, fonts, branding)
- Animation specifications
- Dark mode theming (Phase 3+)

## 7. Reusability Notes
- **Phase 2**: Basic responsive patterns for todo CRUD
- **Phase 3**: Extends to real-time notifications on mobile
- **Phase 4**: Collaborative features on tablet/desktop
- **Phase 5**: AI chatbot responsive interface

## 8. Dependencies

### Upstream Dependencies
- UI component list (todos, forms, navigation)
- User workflows (CRUD operations)

### Downstream Dependencies
- Frontend implementation tasks
- Responsive design testing

## 9. Quality Expectations

### Usability
- All features accessible on mobile, tablet, desktop
- No horizontal scrolling on mobile
- Touch targets minimum 44x44px
- Form inputs appropriately sized

### Performance
- Mobile-first approach (progressive enhancement)
- Critical content prioritized on small screens
- Responsive images (where applicable)

## 10. Example Usage (Spec-Level)

### Breakpoint Specification

**Breakpoints:**
```
Mobile: 320px - 767px (default, mobile-first)
Tablet: 768px - 1023px
Desktop: 1024px+
```

**Design Principle: Mobile-First**
- Start with mobile layout (smallest screen)
- Add enhancements for larger screens
- Core functionality available at all sizes

### Component Responsive Behaviors

**Component 1: Todo List**

**Mobile (320px - 767px):**
```
Layout: Single column, full width
Each Todo: Stacked vertically
  - Title: Full width, 16px font
  - Description: Below title, 14px font, truncated with "..." if long
  - Actions: Horizontal row of icon buttons (Complete, Edit, Delete)
  - Spacing: 12px padding, 8px gap between todos
Touch Targets: 44px min height for clickable areas
```

**Tablet (768px - 1023px):**
```
Layout: Single column with more breathing room
Each Todo: Slightly wider, max-width 600px centered
  - Title: 18px font
  - Description: Not truncated, full text visible
  - Actions: Larger icons, 16px spacing
```

**Desktop (1024px+):**
```
Layout: Max-width 800px, centered
Each Todo: Two-column layout option
  - Left: Title and description
  - Right: Actions (aligned right)
  - Hover: Show additional options (e.g., timestamps)
```

---

**Component 2: Todo Form (Add/Edit)**

**Mobile:**
```
Layout: Full-screen or modal
Fields:
  - Title input: Full width, 48px height (easy touch)
  - Description textarea: Full width, 120px height
  - Buttons: Full width, stacked vertically
    - Submit: 48px height, primary color
    - Cancel: 48px height, secondary color
Keyboard: Auto-focus title field on open
```

**Tablet:**
```
Layout: Modal with max-width 500px
Fields: Same as mobile but not full-width of viewport
Buttons: Horizontal row, not full width
```

**Desktop:**
```
Layout: Modal max-width 600px
Fields: Labels above inputs (more space available)
Buttons: Inline, right-aligned (Submit, Cancel)
```

---

**Component 3: Navigation/Header**

**Mobile:**
```
Layout: Fixed header, 56px height
Content:
  - Left: Hamburger menu icon (mobile menu toggle)
  - Center: App title "My Todos"
  - Right: User avatar/menu (dropdown)
Mobile Menu: Slide-in drawer
  - Login/Logout
  - Profile (Phase 3+)
  - Settings (Phase 3+)
```

**Tablet:**
```
Layout: Fixed header, 64px height
Content:
  - Left: App title
  - Right: Inline navigation links + user menu
No hamburger: Sufficient space for links
```

**Desktop:**
```
Layout: Fixed header, 64px height
Content: Same as tablet, more spacing
Additional: Breadcrumbs or tabs (if multi-page)
```

---

**Component 4: Authentication Forms (Login/Register)**

**Mobile:**
```
Layout: Full-screen, centered content
Form:
  - Email input: Full width, 48px height
  - Password input: Full width, 48px height
  - Submit button: Full width, 48px height
  - Link: "Don't have an account? Register" below button
Spacing: 16px between fields
```

**Tablet/Desktop:**
```
Layout: Card/modal, max-width 400px, centered
Form: Same fields, not full-width
Background: Subtle shadow or background color
```

---

### Touch-Friendly Specifications

**Touch Target Minimum Sizes:**
```
Buttons: 44px x 44px minimum (WCAG 2.1 guideline)
Input fields: 48px height minimum
Clickable todo items: 56px height minimum
Icon buttons: 44px x 44px touch area (even if icon is smaller)
Spacing: 8px minimum between interactive elements
```

**Gestures:**
```
Phase 2:
  - Tap: Primary interaction (no swipe gestures yet)
  - Long-press: Not used (keep simple)

Phase 3+ (Optional):
  - Swipe left: Delete todo
  - Swipe right: Complete todo
  - Pull-to-refresh: Sync todos
```

---

### Layout Patterns

**Pattern 1: Stacked Layout (Mobile)**
```
Used for: Todo list, forms, content-heavy sections
Behavior: All elements stack vertically
Benefit: Maximum readability on narrow screens
```

**Pattern 2: Split Layout (Tablet/Desktop)**
```
Used for: Dashboard, multi-column views (Phase 3+)
Behavior: Sidebar + main content area
Benefit: Efficient use of horizontal space
```

**Pattern 3: Grid Layout (Phase 3+)**
```
Used for: Multiple resource types (todos, projects, tags)
Behavior: 2-column (tablet), 3-column (desktop)
Benefit: Visual organization, scanning efficiency
```

---

### Accessibility Requirements

**Keyboard Navigation:**
```
Tab Order: Logical flow (top to bottom, left to right)
Focus Indicators: Visible outline on all interactive elements
Shortcuts (Phase 3+):
  - "N": New todo
  - "Esc": Close modal
  - Enter: Submit form
```

**Screen Reader Support:**
```
ARIA Labels:
  - Buttons: aria-label="Mark todo as complete"
  - Inputs: aria-describedby for error messages
  - Modals: aria-modal="true", focus trap

Semantic HTML:
  - <button> for actions (not <div>)
  - <form> for input groups
  - <ul><li> for todo lists
  - <h1>, <h2> for headings
```

**Focus Management:**
```
Modal Open: Focus first input field
Modal Close: Return focus to trigger button
Form Submit: Focus first error field (if validation fails)
Todo Delete: Focus next todo in list (or "Add" button if list empty)
```

---

### Responsive Form Validation

**Mobile:**
```
Inline Errors: Below each field (not floating)
Error Messages: Clear, actionable (e.g., "Title cannot be empty")
Submit Button: Disabled until valid (with visual indicator)
```

**Desktop:**
```
Inline Errors: Next to field (right-side if space)
Tooltips: Hover for validation hints (Phase 3+)
Real-time Validation: On blur or after 500ms typing pause
```

---

### Responsive Data Loading

**Mobile:**
```
Initial Load: Show first 20 todos
Pagination: "Load More" button at bottom (no infinite scroll Phase 2)
Loading State: Spinner with "Loading todos..." text
Empty State: "No todos yet. Tap + to add one."
```

**Desktop:**
```
Initial Load: Show first 50 todos (larger viewport)
Pagination: Traditional pagination (1, 2, 3, ..., Next)
Loading State: Skeleton UI (placeholder cards)
Empty State: Centered message with illustration (Phase 3+)
```

---

### Testing Requirements

**Responsive Testing Checklist:**
```
✅ Mobile (375x667): iPhone SE viewport
✅ Tablet (768x1024): iPad viewport
✅ Desktop (1920x1080): Standard desktop

Test Cases:
  - All features functional at each breakpoint
  - No horizontal scrolling on any screen size
  - Touch targets minimum 44px on mobile
  - Forms usable with on-screen keyboard
  - Navigation accessible on all devices
  - Text readable without zooming
```

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 2
- **Last Updated**: 2025-12-30
- **Skill Type**: Specification
- **Execution Surface**: Agent (nextjs-frontend-architect)
