# Contributing to AI Engineering Curriculum

Thank you for your interest in contributing! This curriculum is designed to help developers learn AI engineering through hands-on practice.

## 🎯 How to Contribute

### 1. Report Issues

Found a bug or error in a chapter?

- Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md)
- Include the chapter number and specific section
- Provide steps to reproduce if applicable

### 2. Suggest Improvements

Have ideas for better explanations or examples?

- Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md)
- Explain the improvement and why it would help learners
- Provide code examples if relevant

### 3. Submit Pull Requests

Want to fix errors or add content?

**Before submitting:**

- Read the chapter template: `curriculum/templates/MASTER-CHAPTER-TEMPLATE-V2.md`
- Ensure your changes follow the template structure
- Test all code examples
- Run verification scripts

**PR Guidelines:**

- One chapter/topic per PR
- Clear commit messages
- Reference related issues
- Include before/after examples

## 📝 Chapter Quality Standards

All chapters must include:

### 1. Complete Metadata

- Phase, time estimate, difficulty
- Prerequisites and dependencies
- Project thread (component evolution)
- Correctness properties

### 2. Verification Section

- 3-5 automated test scripts
- Expected output examples
- Clear pass/fail criteria
- Runnable without modifications

### 3. Summary Section

- Minimum 7 bullet points
- Key takeaway statement
- Skills unlocked
- Looking ahead connector

### 4. Hands-On Exercises

- Minimum 2 "Try This!" exercises
- Progressive difficulty
- Hints and solutions provided

## 🧪 Testing Requirements

### Property-Based Tests

Use Hypothesis for testing:

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_property(input_text):
    result = process(input_text)
    assert isinstance(result, str)
```

### Verification Scripts

Each chapter needs verification scripts:

```python
# verify_chapter_XX.py
def verify_implementation():
    """Test the chapter's main concepts."""
    # Test code here
    print("✅ All verifications passed!")

if __name__ == "__main__":
    verify_implementation()
```

## 🎨 Code Style

### Python

- Follow PEP 8
- Use type hints
- Document with docstrings
- Keep functions focused

### Markdown

- Use clear headings
- Include code blocks with language tags
- Add emoji for visual clarity (sparingly)
- Keep lines under 120 characters

## 🔄 Development Workflow

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b fix/chapter-15-typo`
3. **Make** your changes
4. **Test** thoroughly
5. **Commit** with clear messages: `git commit -m "Fix typo in Chapter 15 chunking example"`
6. **Push** to your fork: `git push origin fix/chapter-15-typo`
7. **Submit** a pull request

## 📚 Documentation

### Adding New Chapters

1. Use the template: `curriculum/templates/MASTER-CHAPTER-TEMPLATE-V2.md`
2. Update `PROJECT-THREAD.md` with component dependencies
3. Add Civil Engineering examples from `ce-contexts.md`
4. Create verification scripts
5. Update progress tracking

### Updating Existing Chapters

1. Maintain backward compatibility
2. Update verification scripts if needed
3. Increment template version if structure changes
4. Document breaking changes

## 🤝 Community Guidelines

### Be Respectful

- Welcome beginners
- Provide constructive feedback
- Assume good intentions
- Help others learn

### Be Clear

- Explain your reasoning
- Provide examples
- Link to relevant resources
- Use simple language

### Be Patient

- Learning takes time
- Everyone has different backgrounds
- Questions are encouraged
- Mistakes are learning opportunities

## 🏆 Recognition

Contributors will be:

- Listed in the README
- Credited in relevant chapters
- Thanked in release notes
- Part of the AI education community

## 📞 Questions?

- **General Questions**: Use [GitHub Discussions](../../discussions)
- **Bug Reports**: Use [Issues](../../issues)
- **Chapter Feedback**: Use the chapter feedback template
- **Direct Contact**: Open an issue for maintainer attention

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make AI education accessible to everyone!** 🚀
