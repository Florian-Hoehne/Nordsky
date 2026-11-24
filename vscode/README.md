# Nordsky for VS Code

Two deep-navy dark themes. **Nordsky**: blue keywords, green strings, orange keys and constants,
teal types, coral numbers. **Nordsky Console**: the terminal look with red strings, green numbers
and grey annotations. Generated from the shared palette in `../scripts/generate.py`.

Build the installable package with the official VS Code extension tool:

```bash
npm install
```

```bash
npm run package
```

Then install `nordsky-theme-1.0.0.vsix` via *Extensions → … → Install from VSIX…* and pick
**Nordsky** or **Nordsky Console** under *Preferences: Color Theme*.
