# Contributing to Jira MCP Server

Thank you for your interest in contributing to the Jira MCP Server!

## 🚨 Read-Only Principle

**CRITICAL:** This server MUST maintain read-only access to Jira. Any contributions that introduce write, update, delete, or transition operations will be rejected.

## 🎯 Areas for Contribution

### Acceptable Contributions

✅ **New Read-Only Tools**
- Additional read-only Jira API endpoints
- Enhanced search capabilities
- Custom field retrieval
- User and group information (read-only)
- Worklog information (read-only)
- Board and sprint details (read-only)

✅ **Improvements**
- Better error handling
- Performance optimizations
- Caching mechanisms
- Documentation improvements
- Test coverage
- Code quality improvements
- Logging enhancements

✅ **Features**
- Export capabilities (CSV, JSON, etc.)
- Advanced filtering
- Batch operations (read-only)
- Analytics and reporting
- Integration examples

### Unacceptable Contributions

❌ **Write Operations** - Never
- Creating issues
- Updating issues
- Deleting issues
- Transitioning issues
- Adding comments
- Modifying attachments
- Any other write operation

## 🛠️ Development Setup

1. Fork the repository
2. Clone your fork
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or .\venv\Scripts\activate on Windows
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Configure your test Jira instance in `config/config.env`
6. Run tests:
   ```bash
   python test_connection.py
   ```

## 📝 Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Include docstrings for all functions and classes
- Keep functions focused and single-purpose
- Use meaningful variable names

## 🧪 Testing

- Test all new features with real Jira instances
- Ensure error handling is comprehensive
- Verify that no write operations are possible
- Test with different Jira configurations

## 📚 Documentation

- Update README.md if adding new tools
- Add examples for new features
- Document any new configuration options
- Update CHANGELOG.md

## 🔒 Security Considerations

- Never commit credentials
- Use environment variables for sensitive data
- Validate all inputs
- Handle API rate limits gracefully
- Log security-relevant events

## 🚀 Submitting Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the guidelines above

3. Test thoroughly

4. Commit with clear messages:
   ```bash
   git commit -m "Add feature: description of what was added"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request with:
   - Clear description of changes
   - Rationale for the changes
   - Test results
   - Updated documentation

## 🐛 Bug Reports

When reporting bugs, include:
- Python version
- MCP SDK version
- Jira version (Cloud/Server/Data Center)
- Steps to reproduce
- Expected vs actual behavior
- Error messages and logs

## 💡 Feature Requests

When requesting features:
- Explain the use case
- Describe the expected behavior
- Confirm it maintains read-only access
- Consider performance implications

## 📧 Questions?

- Check existing documentation
- Review closed issues
- Open a new issue with your question

## 🙏 Thank You!

Your contributions help make this project better for everyone using AI agents with Jira!

---

**Remember: Read-only access is not negotiable. Security first!**
