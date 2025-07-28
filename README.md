# Windows Directory Structure Synchronizer

[English](README.md) | [简体中文](README.zh_Hans.md) | [繁體中文](README.zh_Hant.md)

A tool for synchronizing Windows directory structures that replaces large files with placeholders, perfect for media library backups and similar scenarios.

## ✨ Features

- **📄 Non-destructive**: Preserves complete directory structure while replacing large files with placeholders;
- **🎯 Smart Filtering**: Supports intelligent filtering by file size, extensions, and directory exclusion rules;
- **⚡ Efficient Sync**: Direct directory synchronization for fast processing of large file collections;
- **🔧 Flexible Configuration**: Supports force replace/keep rules for specific file extensions;
- **💻 Portable**: No installation required, runs standalone with no external dependencies;
- **🌐 Multi-language Support**: Supports English, Simplified Chinese, and Traditional Chinese;

## 🎮 Usage

Simply download the latest version from [Releases](https://github.com/fernvenue/path-dumper-windows/releases/latest) and run - no installation required.

![image](./assets/images/D7E918710762045D.webp)

1. **Select Source Directory**: Click browse to select the source directory to sync;
2. **Select Output Directory**: Choose the destination for synchronized files;
3. **Set Large File Threshold**: Files exceeding this size will be replaced with placeholders (default 30MB);
4. **Configure Exclusion Rules**: Optionally exclude specific directories (e.g., .git, node_modules);
5. **Set Extension Rules**: Force replace or keep files with specific extensions;
6. **Start Sync**: Click "Start Sync" to begin the operation;

## 🚀 Build from Source

Python environment required.

Clone the repository:

```bash
git clone https://github.com/fernvenue/path-dumper-windows.git
cd path-dumper-windows
```

Run the build script:

```bash
build.bat
```

## License

This tool is open-sourced under the GPLv3 license. See [LICENSE](./LICENSE) for details.
