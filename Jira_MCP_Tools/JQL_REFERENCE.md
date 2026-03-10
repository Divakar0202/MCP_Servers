# JQL Quick Reference

JQL (Jira Query Language) reference for the `search_issues` tool.

## Basic Syntax

```jql
field operator value
```

Combine with `AND`, `OR`, `NOT`

## Common Fields

| Field | Description | Example |
|-------|-------------|---------|
| `project` | Project key | `project = MYPROJ` |
| `type` | Issue type | `type = Bug` |
| `status` | Issue status | `status = Open` |
| `priority` | Priority | `priority = High` |
| `assignee` | Assigned user | `assignee = currentUser()` |
| `reporter` | Reporter | `reporter = "John Doe"` |
| `created` | Creation date | `created >= -7d` |
| `updated` | Update date | `updated >= "2024-01-01"` |
| `resolved` | Resolution date | `resolved >= -30d` |
| `labels` | Labels | `labels = urgent` |
| `component` | Component | `component = Backend` |
| `text` | Text search | `text ~ "login bug"` |

## Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `status = Done` |
| `!=` | Not equals | `status != Closed` |
| `>` | Greater than | `priority > Low` |
| `>=` | Greater or equal | `created >= -7d` |
| `<` | Less than | `priority < High` |
| `<=` | Less or equal | `updated <= -30d` |
| `~` | Contains | `summary ~ "login"` |
| `!~` | Not contains | `summary !~ "test"` |
| `IN` | In list | `status IN (Open, "In Progress")` |
| `NOT IN` | Not in list | `status NOT IN (Done, Closed)` |
| `IS` | Is (null check) | `assignee IS EMPTY` |
| `IS NOT` | Is not | `assignee IS NOT EMPTY` |

## Functions

| Function | Description | Example |
|----------|-------------|---------|
| `currentUser()` | Current logged-in user | `assignee = currentUser()` |
| `now()` | Current time | `created >= now()` |
| `startOfDay()` | Start of today | `created >= startOfDay()` |
| `startOfWeek()` | Start of week | `created >= startOfWeek()` |
| `endOfWeek()` | End of week | `due <= endOfWeek()` |

## Date Formats

```jql
# Relative dates
created >= -7d        # Last 7 days
updated >= -2w        # Last 2 weeks
resolved >= -1M       # Last month

# Absolute dates
created >= "2024-01-01"
updated <= "2024-12-31"
```

## Example Queries

### Get all open bugs
```jql
project = MYPROJ AND type = Bug AND status != Done
```

### Get high priority issues assigned to me
```jql
assignee = currentUser() AND priority = High
```

### Get recently updated issues
```jql
project = MYPROJ AND updated >= -7d ORDER BY updated DESC
```

### Get unassigned issues
```jql
project = MYPROJ AND assignee IS EMPTY
```

### Get issues with attachments
```jql
project = MYPROJ AND attachments IS NOT EMPTY
```

### Get stories in a sprint
```jql
project = MYPROJ AND type = Story AND sprint = "Sprint 1"
```

### Get overdue issues
```jql
due < now() AND status != Done
```

### Get issues by label
```jql
project = MYPROJ AND labels IN (urgent, critical)
```

### Get epics with linked issues
```jql
type = Epic AND issueFunction IN linkedIssuesOf("project = MYPROJ")
```

### Get closed issues from last month
```jql
project = MYPROJ AND status = Done AND resolved >= -30d
```

### Search text in summary or description
```jql
project = MYPROJ AND text ~ "database connection"
```

### Get issues created by a specific user
```jql
project = MYPROJ AND reporter = "john@example.com"
```

### Complex query with multiple conditions
```jql
project = MYPROJ 
AND type IN (Bug, Story) 
AND status NOT IN (Done, Closed) 
AND priority >= Medium 
AND created >= -14d 
ORDER BY priority DESC, created DESC
```

## Sorting

Add `ORDER BY` at the end:

```jql
# Sort by created date (newest first)
project = MYPROJ ORDER BY created DESC

# Sort by priority then status
project = MYPROJ ORDER BY priority DESC, status ASC

# Sort by multiple fields
project = MYPROJ ORDER BY updated DESC, key ASC
```

## Pagination

Use `start_at` and `max_results` parameters in the tool:

```python
search_issues(
    jql_query="project = MYPROJ",
    max_results=50,
    start_at=0  # For page 2, use start_at=50
)
```

## Common Patterns

### Sprint queries
```jql
# Current sprint
sprint IN openSprints()

# Specific sprint
sprint = "Sprint 10"

# Future sprints
sprint IN futureSprints()
```

### Status categories
```jql
# In progress
statusCategory = "In Progress"

# To do
statusCategory = "To Do"

# Done
statusCategory = Done
```

### Date ranges
```jql
# This week
created >= startOfWeek() AND created <= endOfWeek()

# Last quarter
created >= startOfYear(-1q) AND created <= endOfYear(-1q)
```

## Tips

1. **Use quotes** for multi-word values: `status = "In Progress"`
2. **Case sensitivity** - field names are case-insensitive, values are case-sensitive
3. **Parentheses** - use for complex logic: `(A OR B) AND C`
4. **Test queries** - test in Jira's issue search first
5. **Performance** - specific queries are faster than broad searches

## Resources

- [Official JQL Documentation](https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/)
- [JQL Functions Reference](https://support.atlassian.com/jira-software-cloud/docs/jql-functions/)
- [JQL Autocomplete](https://support.atlassian.com/jira-software-cloud/docs/use-jql-autocomplete/)
