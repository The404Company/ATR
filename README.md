# ATR - Auto Text Replacer

A Windows application that automatically replaces text shortcuts with symbols, emojis, and special characters as you type.

## Features

- Real-time text replacement while typing
- GUI for managing text replacements
- Pre-configured replacements for common symbols
- Support for:
  - Currency symbols (`€`, `$`, `£`, etc.)
  - Greek letters (`α`, `β`, `γ`, etc.)
  - Mathematical symbols (`≠`, `≤`, `≥`, `∞`, etc.)
  - Arrows (`→`, `←`, `⇒`, etc.)
  - ASCII art emojis (`¯\_(ツ)_/¯`, etc.)
  - Special characters (`™`, `©`, `®`, etc.)
  - Litterally every character you can think of

## Installation

### Method 1: Using the Installer (Recommended)

1. Download and run `installer.py`
2. Click "Install" and wait for the process to complete
3. ATR will automatically start with Windows

### Method 2: Manual Installation

1. Ensure you have Python 3.x installed
2. Install required dependencies:
```sh
pip install pynput pyperclip
```
3. Download or clone this repository
4. Copy the preset `replacements.json` from the `preset` folder to the same directory as `atr.py` (optional)

## Usage

1. Run the program:
```sh
python atr.py
```

2. The GUI will appear, showing all available replacements
3. Type any trigger word followed by a space to automatically replace it with its corresponding symbol
4. Use the GUI to:
   - Add new replacements
   - Edit existing replacements
   - Delete replacements
   - Save changes

## Examples

- Type `eur` + space → `€ `
- Type `alpha` + space → `α `
- Type `->` + space → `→ `
- Type `:shrug:` + space → `¯\_(ツ)_/¯ `

## Configuration

The program uses `replacements.json` to store all text replacements. You can:
- Edit this file directly (make sure to use valid JSON format)
- Use the GUI to manage replacements
- Copy the preset file from `preset/replacements.json` for default replacements (you can modify this file too ofcourse)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.