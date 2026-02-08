# Phase V: Features Specification

**Feature Branch**: `005-name-phase5-cloud`
**Created**: 2026-02-06
**Status**: Draft

## Overview

Phase V introduces advanced task management capabilities with event-driven notifications, comprehensive search, audit logging, and analytics. All features are built on a microservices architecture with Dapr and Kafka.

## Feature Catalog

### F1: Recurring Tasks

**Description**: Users can create tasks that automatically repeat on a schedule (daily, weekly, monthly, custom).

**Business Value**: Reduces manual work for habitual tasks, improves productivity for recurring workflows.

**User Scenarios**:

1. **Given** a user has authenticated
   **When** they create a todo with recurrence pattern "every Monday at 9am"
   **Then** the system creates the first instance and schedules future instances

2. **Given** a recurring task exists
   **When** the current instance is completed
   **Then** the system automatically creates the next instance based on the recurrence rule

3. **Given** a recurring task exists
   **When** the user updates the recurrence pattern
   **Then** future instances reflect the new pattern, but past/current instances remain unchanged

**Acceptance Criteria**:
- ✅ Support iCalendar RRULE syntax (RFC 5545)
- ✅ Patterns: daily, weekly, monthly, yearly, custom cron-like expressions
- ✅ End conditions: after N occurrences, by specific date, or never
- ✅ Each instance is a separate todo entity with parent reference
- ✅ Completing one instance does NOT complete the series
- ✅ Deleting a series offers options: this instance, future instances, or entire series

**Technical Requirements**:
- **FR-F1-001**: Todo Service MUST store recurrence rules in iCalendar RRULE format
- **FR-F1-002**: Notification Service MUST subscribe to `todo.completed` events and create next instance
- **FR-F1-003**: System MUST generate instances no more than 30 days in advance
- **FR-F1-004**: Each instance MUST have a `parent_series_id` field linking to the original todo

**Edge Cases**:
- Skipped instances (e.g., Feb 30th becomes Feb 28th/29th)
- Timezone changes (respect user's current timezone)
- Series deletion while instances are in progress (orphan handling)

**API Endpoints**:
```
POST /api/v1/todos - Create todo with optional recurrence field
PUT /api/v1/todos/{id}/recurrence - Update recurrence rule
GET /api/v1/todos/{id}/series - Get all instances in a series
DELETE /api/v1/todos/series/{series_id} - Delete series with options
```

**Events Published**:
- `todo.series.created` - New recurring series created
- `todo.series.updated` - Series recurrence rule changed
- `todo.series.instance.created` - New instance generated
- `todo.series.deleted` - Entire series deleted

---

### F2: Reminders and Notifications

**Description**: Users receive proactive reminders for upcoming or overdue tasks via email, push notifications, or in-app alerts.

**Business Value**: Increases task completion rates, reduces missed deadlines, improves user engagement.

**User Scenarios**:

1. **Given** a todo has a due date of "tomorrow at 10am"
   **When** the reminder triggers (e.g., 1 hour before)
   **Then** the user receives an email notification with task details

2. **Given** a todo is overdue by 24 hours
   **When** the daily overdue check runs
   **Then** the user receives a digest email listing all overdue tasks

3. **Given** a user has notification preferences set to "push only"
   **When** a reminder triggers
   **Then** the system sends a push notification via web push API

**Acceptance Criteria**:
- ✅ Reminder offsets: 5min, 15min, 1hr, 1day, 1week before due date
- ✅ User configurable per todo or global preferences
- ✅ Delivery channels: email (primary), push (future), in-app (future)
- ✅ Overdue digest: daily summary at 9am user local time
- ✅ Respect quiet hours (no notifications 10pm-7am user local time)
- ✅ Idempotent delivery (do not send duplicate reminders)

**Technical Requirements**:
- **FR-F2-001**: Notification Service MUST subscribe to `todo.reminder.due` Kafka topic
- **FR-F2-002**: Todo Service MUST publish `todo.reminder.due` events at scheduled times
- **FR-F2-003**: Notification Service MUST use Dapr Output Binding for SMTP email
- **FR-F2-004**: User Service MUST store notification preferences per user
- **FR-F2-005**: System MUST track sent notifications to prevent duplicates

**Edge Cases**:
- Email delivery failures (retry with exponential backoff)
- User deletes todo after reminder is scheduled (cancel reminder)
- Timezone changes during reminder scheduling (recalculate)
- User opts out of all notifications (honor unsubscribe)

**API Endpoints**:
```
GET /api/v1/users/{id}/notification-preferences
PUT /api/v1/users/{id}/notification-preferences
POST /api/v1/todos/{id}/reminders - Set custom reminder
GET /api/v1/notifications - Get user's notification history
```

**Events Consumed**:
- `todo.reminder.due` - Trigger notification
- `todo.completed` - Cancel pending reminders
- `todo.deleted` - Cancel pending reminders
- `user.settings.updated` - Update notification preferences

**Events Published**:
- `notification.sent` - Notification delivered successfully
- `notification.failed` - Delivery failed (for retry)

---

### F3: Priority Levels

**Description**: Users can assign priority levels (Low, Medium, High, Urgent) to tasks for better organization and focus.

**Business Value**: Enables prioritization, improves decision-making on what to work on next.

**User Scenarios**:

1. **Given** a user is creating a todo
   **When** they set priority to "Urgent"
   **Then** the todo appears at the top of their task list

2. **Given** a user has mixed-priority tasks
   **When** they filter by priority "High"
   **Then** only high-priority tasks are displayed

3. **Given** an AI chatbot interaction
   **When** the user says "add high priority task: prepare presentation"
   **Then** the todo is created with priority=High automatically

**Acceptance Criteria**:
- ✅ Priority levels: Low (P3), Medium (P2), High (P1), Urgent (P0)
- ✅ Default priority: Medium
- ✅ Priority affects sort order (Urgent first, then High, Medium, Low)
- ✅ Priority is mutable (can be changed after creation)
- ✅ Priority is visible in all UI views (list, details, calendar)

**Technical Requirements**:
- **FR-F3-001**: Todo entity MUST have `priority` field (enum: low, medium, high, urgent)
- **FR-F3-002**: Todo Service MUST support filtering by priority
- **FR-F3-003**: Todo Service MUST support sorting by priority
- **FR-F3-004**: Chat Service MUST extract priority from natural language (NLP parsing)

**Edge Cases**:
- Priority changes trigger re-ordering in UI (real-time via events)
- Priority-based filtering with recurring tasks (applies to current instance)
- Bulk priority update (e.g., "set all overdue tasks to urgent")

**API Endpoints**:
```
GET /api/v1/todos?priority=high - Filter by priority
PUT /api/v1/todos/{id}/priority - Update priority
POST /api/v1/todos/bulk-update-priority - Bulk update
```

**Events Published**:
- `todo.priority.updated` - Priority changed

---

### F4: Tags and Categories

**Description**: Users can organize tasks using custom tags (e.g., #work, #personal, #shopping) for flexible categorization.

**Business Value**: Enables personalized organization systems, improves findability, supports cross-cutting concerns.

**User Scenarios**:

1. **Given** a user creates a todo "Buy groceries"
   **When** they add tags "#personal #shopping #weekly"
   **Then** the todo is tagged and searchable by any of those tags

2. **Given** a user has multiple todos tagged "#work"
   **When** they filter by "#work"
   **Then** all work-related tasks are displayed

3. **Given** a user wants to rename a tag
   **When** they rename "#work" to "#office"
   **Then** all todos with "#work" are updated to "#office"

**Acceptance Criteria**:
- ✅ Tags are free-form strings (alphanumeric + hyphen/underscore)
- ✅ Tags are case-insensitive (stored lowercase, displayed as entered)
- ✅ Multiple tags per todo (many-to-many relationship)
- ✅ Tag autocomplete suggestions from existing tags
- ✅ Tag cloud view (frequency-based sizing)
- ✅ Rename/delete tag affects all associated todos

**Technical Requirements**:
- **FR-F4-001**: Todo Service MUST store tags in separate `tags` table (many-to-many)
- **FR-F4-002**: Todo Service MUST support filtering by one or more tags (AND/OR logic)
- **FR-F4-003**: Todo Service MUST provide tag autocomplete API
- **FR-F4-004**: Chat Service MUST extract hashtags from natural language input

**Edge Cases**:
- Tag with special characters (sanitize, allow only [a-z0-9-_])
- Tag deletion (cascade delete or leave orphan todos)
- Tag merge (combine two tags into one)
- Maximum tags per todo (soft limit: 10)

**API Endpoints**:
```
GET /api/v1/tags - List all tags with usage count
GET /api/v1/todos?tags=work,personal - Filter by tags (OR)
POST /api/v1/todos/{id}/tags - Add tags to todo
DELETE /api/v1/todos/{id}/tags/{tag} - Remove tag from todo
PUT /api/v1/tags/{tag}/rename - Rename tag globally
DELETE /api/v1/tags/{tag} - Delete tag globally
```

**Events Published**:
- `todo.tags.added` - Tags added to todo
- `todo.tags.removed` - Tags removed from todo
- `tag.renamed` - Tag renamed globally
- `tag.deleted` - Tag deleted globally

---

### F5: Full-Text Search

**Description**: Users can search todos by title, description, tags, and other metadata using natural language queries.

**Business Value**: Improves discoverability, reduces time spent searching, enables power users.

**User Scenarios**:

1. **Given** a user has hundreds of todos
   **When** they search for "presentation deadline"
   **Then** all todos containing those keywords in title/description are returned, ranked by relevance

2. **Given** a user searches "overdue #work"
   **When** the query is executed
   **Then** the system returns overdue todos tagged with "#work"

3. **Given** a user searches with typos "mtng notes"
   **When** the query is executed
   **Then** the system suggests "meeting notes" and returns fuzzy matches

**Acceptance Criteria**:
- ✅ Search fields: title, description, tags, notes
- ✅ Search operators: AND, OR, NOT, phrase matching ("exact phrase")
- ✅ Filters: status, priority, due date, tags (combined with search)
- ✅ Fuzzy matching: typo tolerance (Levenshtein distance ≤ 2)
- ✅ Ranking: TF-IDF or BM25 algorithm for relevance scoring
- ✅ Pagination: 20 results per page

**Technical Requirements**:
- **FR-F5-001**: Todo Service MUST implement full-text search using PostgreSQL `tsvector`
- **FR-F5-002**: Todo Service MUST build full-text index on title, description, tags
- **FR-F5-003**: Search API MUST support query syntax parsing (AND/OR/NOT)
- **FR-F5-004**: Chat Service MUST use search API for "find all tasks about X" queries

**Edge Cases**:
- Empty search query (return recent todos)
- Special characters in query (sanitize, escape for SQL)
- Search performance with 10,000+ todos (index optimization, query timeout)
- Search with all filters applied (multi-column index)

**API Endpoints**:
```
GET /api/v1/todos/search?q=presentation&status=pending&priority=high
GET /api/v1/todos/search/suggest?q=mtng - Autocomplete suggestions
```

**Events Published**:
- `todo.searched` - Analytics event for search query tracking

---

### F6: Audit Logging

**Description**: The system maintains an immutable log of all user actions for compliance, debugging, and forensics.

**Business Value**: Enables compliance with regulations (GDPR, SOC2), supports debugging production issues, provides transparency.

**User Scenarios**:

1. **Given** a user deletes a todo
   **When** the deletion occurs
   **Then** an audit log entry records: user ID, todo ID, action=DELETE, timestamp, IP address

2. **Given** an administrator investigates a data loss issue
   **When** they query the audit log
   **Then** they see a complete history of actions on the affected entity

3. **Given** a user requests their data history (GDPR)
   **When** the export is generated
   **Then** the audit log is included in the export

**Acceptance Criteria**:
- ✅ Log all CRUD operations on todos, users, conversations
- ✅ Capture: user ID, entity ID, action, timestamp, IP address, user agent
- ✅ Immutable: audit log entries cannot be modified or deleted
- ✅ Searchable: by user, entity, action, date range
- ✅ Retention: 7 years (compliance requirement)
- ✅ Performance: async logging (does not block main flow)

**Technical Requirements**:
- **FR-F6-001**: Audit Service MUST subscribe to ALL Kafka topics (`*.*`)
- **FR-F6-002**: Audit Service MUST store events in append-only `audit_log` table
- **FR-F6-003**: Audit log table MUST have no UPDATE or DELETE privileges
- **FR-F6-004**: Audit log MUST include event payload (full entity snapshot)

**Edge Cases**:
- Audit log storage growth (partition by month, archive to cold storage)
- Kafka lag (audit service falls behind, catch-up mechanism)
- Sensitive data in audit log (encrypt PII fields)
- Bulk operations (log each individual action)

**API Endpoints**:
```
GET /api/v1/audit-log?user_id={id}&start_date={date}&end_date={date}
GET /api/v1/audit-log/{event_id} - Get specific audit event
GET /api/v1/users/{id}/audit-export - Export user's audit history (GDPR)
```

**Events Consumed**:
- `*.*` (ALL events from ALL services)

**Events Published**:
- None (sink service)

---

### F7: Analytics and Insights

**Description**: Users see visualizations and insights about their task completion patterns, productivity trends, and usage statistics.

**Business Value**: Increases self-awareness, gamification potential, drives engagement.

**User Scenarios**:

1. **Given** a user has completed 50 tasks this month
   **When** they view the dashboard
   **Then** they see: completion trend graph, tasks by priority, tasks by tag, average completion time

2. **Given** a user has overdue tasks
   **When** they view insights
   **Then** they see a warning "You have 5 overdue tasks, 3 of which are high priority"

3. **Given** a user completes a recurring task
   **When** they view the series insights
   **Then** they see completion streaks (e.g., "7-day streak!")

**Acceptance Criteria**:
- ✅ Metrics: total tasks, completed tasks, completion rate, average time to complete
- ✅ Trends: daily, weekly, monthly completion graphs
- ✅ Breakdowns: by priority, by tag, by status
- ✅ Streaks: consecutive days with completed tasks
- ✅ Insights: actionable recommendations (e.g., "Focus on high-priority overdue tasks")

**Technical Requirements**:
- **FR-F7-001**: Analytics Service MUST subscribe to `todo.*` and `user.*` events
- **FR-F7-002**: Analytics Service MUST aggregate metrics hourly (background job)
- **FR-F7-003**: Analytics Service MUST store time-series data for graphs
- **FR-F7-004**: Analytics API MUST support date range filtering

**Edge Cases**:
- New user with no data (show empty state, onboarding tips)
- Historical data gaps (handle missing data gracefully)
- Timezone changes (recalculate metrics in user's current timezone)
- Large data volume (pre-aggregate monthly metrics)

**API Endpoints**:
```
GET /api/v1/analytics/dashboard - High-level metrics
GET /api/v1/analytics/trends?start_date={date}&end_date={date}
GET /api/v1/analytics/insights - AI-generated insights
GET /api/v1/analytics/streaks - Completion streaks
```

**Events Consumed**:
- `todo.created`, `todo.completed`, `todo.deleted`
- `user.created`, `user.updated`

**Events Published**:
- `analytics.report.generated` - Periodic report generation

---

## Feature Dependencies

```
F1 (Recurring Tasks) ──> F2 (Reminders) [Recurring tasks need reminders]
F3 (Priority) ──────────> F5 (Search) [Search by priority]
F4 (Tags) ──────────────> F5 (Search) [Search by tags]
F1, F3, F4 ─────────────> F7 (Analytics) [Metrics on all features]
ALL ───────────────────> F6 (Audit) [Audit logs all actions]
```

## Implementation Priority

**Phase V.1 (MVP - Week 1-2)**:
1. F3: Priority Levels (simplest, no external dependencies)
2. F4: Tags and Categories (standalone feature)
3. F6: Audit Logging (foundational for compliance)

**Phase V.2 (Core - Week 3-4)**:
4. F5: Full-Text Search (builds on F3, F4)
5. F2: Reminders and Notifications (critical for engagement)

**Phase V.3 (Advanced - Week 5-6)**:
6. F1: Recurring Tasks (complex, depends on F2)
7. F7: Analytics and Insights (depends on all features generating events)

## Success Metrics

**Feature Adoption:**
- 80% of users create at least one recurring task within 30 days
- 60% of users apply tags to todos within 7 days
- 50% of users use search at least once per week

**User Engagement:**
- 40% increase in daily active users (DAU) compared to Phase IV
- 25% reduction in overdue task rate (due to reminders)
- 15% increase in task completion rate

**Technical Metrics:**
- Event processing latency < 1 second (p95)
- Search query response time < 200ms (p95)
- Audit log write throughput > 10,000 events/second

## Non-Functional Requirements

**Usability:**
- All features accessible via natural language chatbot
- Mobile-responsive UI for all features
- Keyboard shortcuts for power users

**Accessibility:**
- WCAG 2.1 Level AA compliance
- Screen reader support for all features
- High-contrast mode for visually impaired users

**Internationalization:**
- Support for 3 languages: English (en), Spanish (es), French (fr)
- Timezone-aware reminders and analytics
- Localized date/time formatting

## Open Questions

1. **Recurring Tasks**: Should we support exceptions (e.g., skip one instance)?
   - **Decision Needed**: Week 1 of implementation
   - **Stakeholder**: Product Manager

2. **Reminders**: Should we integrate with third-party services (Slack, SMS)?
   - **Decision Needed**: Week 2 of implementation
   - **Stakeholder**: Engineering Lead

3. **Analytics**: Should we build a dashboard UI or API-only?
   - **Decision Needed**: Week 4 of implementation
   - **Stakeholder**: UX Designer

4. **Search**: Should we use PostgreSQL full-text or Elasticsearch?
   - **Decision Needed**: Week 3 of implementation
   - **Stakeholder**: Engineering Lead

## References

- [iCalendar RRULE (RFC 5545)](https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.5.3) - Recurring task specification
- [PostgreSQL Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html) - Search implementation
- [CloudEvents Specification](https://cloudevents.io/) - Event schema standards

---

**Next Steps:**
1. Review feature priorities with stakeholders
2. Create detailed event schemas for each feature in `events.md`
3. Define Dapr components needed for features in `dapr.md`
4. Design service APIs for features in `services.md`
