# Task Completion Checklist for COGPLAN

## When Completing Any Development Task

### 1. Code Quality Checks
- [ ] Code follows project conventions (PascalCase classes, snake_case functions)
- [ ] Type hints added where appropriate
- [ ] Docstrings added for new classes/methods
- [ ] No hardcoded values - use configuration

### 2. Testing Requirements
```bash
# Run tests to verify nothing broke
source .venv/bin/activate
python3 -m pytest tests/ -v --tb=short

# Check coverage if adding new code
python3 -m pytest tests/ --cov --cov-report=term

# Target: 80% test pass rate minimum
```

### 3. Dependency Management
- [ ] New dependencies added to appropriate requirements file
- [ ] Optional dependencies properly handled with try-except
- [ ] Virtual environment updated if dependencies changed

### 4. Git Workflow
```bash
# Check what changed
git status
git diff

# Stage changes
git add -A

# Commit with descriptive message
git commit -m "feat/fix/docs: Clear description of change"

# Push to remote (if requested)
git push origin branch-name
```

### 5. Documentation Updates
- [ ] Update README if functionality changed
- [ ] Update ROADMAP.md if completing phase objectives
- [ ] Add to docs/ if major feature added
- [ ] Create handover document if ending session

### 6. Verification Steps
- [ ] All tests passing or improved from baseline
- [ ] No new test failures introduced
- [ ] Code runs without import errors
- [ ] Feature works as intended

### 7. Critical Reminders
- **ALWAYS use python3**, never python
- **ALWAYS activate .venv** first
- **NEVER commit secrets or API keys**
- **TEST before claiming completion**

## For Session Handover
1. Document what was done
2. Document current state
3. Document next steps
4. Commit and push all changes
5. Create handover document in docs/progress/