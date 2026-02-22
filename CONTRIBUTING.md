# Contributing to Physiology Video Translator

First off, thank you for considering contributing to this project! It's people like you that make this tool better for medical students and educators worldwide.

## How Can I Contribute?

### Reporting Bugs
*   Check the [Issues](https://github.com/your-username/your-repo/issues) tab to see if the bug has already been reported.
*   If not, open a new issue. Clearly describe the problem, including steps to reproduce it and your system environment (OS, GPU, Python version).

### Suggesting Enhancements
*   Open an issue with the "enhancement" label.
*   Explain why this feature would be useful and how it should work.

### Pull Requests
1.  Fork the repository.
2.  Create a new branch for your feature or fix.
3.  Ensure your code follows the project's style (run `black .` if possible).
4.  Submit a pull request with a clear description of your changes.

## Development Setup

We highly recommend using `uv` for development:

```powershell
uv sync
uv run python main.py --help
```

## Medical Accuracy
If you are adding or correcting medical terms in `modules/translator.py`, please provide a reference to a standard medical textbook (e.g., Guyton and Hall, Gray's Anatomy) to ensure accuracy.

## License
By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
