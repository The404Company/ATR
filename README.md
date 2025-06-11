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

### Using the Installer

1. Download the latest `ATR_Installer.exe` from [Releases](https://github.com/The404Company/ATR/releases)
2. Run the installer (requires administrator privileges)
3. Click "Install" and wait for the process to complete
4. ATR will automatically start with Windows
5. (Optional) Download the preset replacements from [preset/replacements.json] and copy it to the `%AppData%\Roaming\ATR` directory to use the default replacements made by the developers
6. (Optional) go to `C:\Program Files\ATR`, right-click `ATR.exe`, and create a shortcut to your desktop or pin it to the Start-Menu for easy access

### Not using the Installer
1. You have to figure out yourself how to run the program uncompiled and without installer 😁

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