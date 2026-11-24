# Nordsky

Zwei dunkle Themes in tiefem Marineblau für JetBrains-IDEs (IntelliJ IDEA, WebStorm, PyCharm, …)
und VS Code. Beide stecken im selben Plugin bzw. in derselben Erweiterung.

## Nordsky

Blaue Schlüsselwörter, grüne Strings, orange Keys und Konstanten, türkise Typen, korallrote Zahlen.

![Nordsky](docs/preview-nordsky.png)

## Nordsky Console

Der Look des Terminals, aus dem die Palette stammt: rote Strings, grüne Zahlen, graue
Annotationen, weisse Konstanten und Felder, helle Kommentare.

![Nordsky Console](docs/preview-nordsky-console.png)

| Rolle | Nordsky | Nordsky Console |
|---|---|---|
| Editor-Hintergrund | `#011C33` | `#03182B` |
| Text | `#DCE7F2` | `#E8EEF4` |
| Schlüsselwörter | `#4DA3FF` | `#4A96EA` |
| Strings | `#7EDC8A` | `#F0616D` |
| Unquotierte Werte (YAML) | `#B5EBC0` | `#F5A3AA` |
| Keys | `#F5A742` | `#6DB5F7` |
| Konstanten | `#F5A742` | `#E8EEF4` |
| Zahlen | `#FF7B8A` | `#56D06C` |
| Typen | `#4FD6BE` | `#3EC9A7` |
| Tags (XML/HTML) | `#9FE8D5` | `#3EC9A7` |
| Funktionsdeklarationen | `#FFD98A` | `#6DB5F7` |
| Felder, Attribute | `#9CCBFF` | `#E8EEF4` |
| Annotationen | `#B3A5F5` | `#71869B` |
| Kommentare | `#5E86AE` | `#A9B8C7` |
| Doc-Kommentare | `#5FA595` | `#58B878` |

Alle Textfarben erreichen auf dem Editor-Hintergrund mindestens WCAG-AA-Kontrast (4.5:1);
der Generator bricht ab, wenn eine Farbe darunter fällt.

## JetBrains-IDEs

Gebaut wird mit dem offiziellen [IntelliJ Platform Gradle Plugin](https://plugins.jetbrains.com/docs/intellij/tools-intellij-platform-gradle-plugin.html)
(benötigt JDK 21, Gradle kommt über den Wrapper):

```bash
cd jetbrains
```

```bash
./gradlew buildPlugin
```

Das Ergebnis liegt in `jetbrains/build/distributions/nordsky-theme-<version>.zip`.
Installation: *Settings → Plugins → ⚙ → Install Plugin from Disk…*, danach unter
*Settings → Appearance & Behavior → Appearance → Theme* **Nordsky** oder **Nordsky Console** wählen. Das Plugin bringt
UI-Theme und Editor-Farbschema mit; unterstützt werden IDEs ab 2023.1.

Weitere Tasks:

| Task | Zweck |
|---|---|
| `./gradlew runIde` | startet eine Sandbox-IDE mit dem Theme |
| `./gradlew verifyPlugin` | JetBrains Plugin Verifier gegen 2023.1 und 2024.3 |
| `./gradlew publishPlugin` | Veröffentlichung im Marketplace (Token nötig) |

## VS Code

Gebaut wird mit dem offiziellen Tool [`@vscode/vsce`](https://github.com/microsoft/vscode-vsce):

```bash
cd vscode
```

```bash
npm install
```

```bash
npm run package
```

Installation der erzeugten `nordsky-theme-<version>.vsix`: *Extensions → … → Install from VSIX…*,
danach *Preferences: Color Theme → Nordsky* oder *Nordsky Console*.

## Farben anpassen

Sämtliche Theme-Dateien werden von `scripts/generate.py` erzeugt. Jedes Theme besteht aus einer
Palette (`P`, `CONSOLE`) und einer Zuordnung der Syntax-Rollen auf Palettenfarben (`ROLES`,
`CONSOLE_ROLES`); ein weiteres Theme ist ein zusätzlicher Eintrag in `THEMES`. Nach Änderungen:

```bash
python3 scripts/generate.py
```

Das schreibt pro Theme das JetBrains-Farbschema, das UI-Theme, das VS-Code-Theme und die
Vorschau unter `docs/` neu. Anschliessend die Pakete wie oben bauen.

```
scripts/generate.py                      Palette und Generator
jetbrains/                               Gradle-Projekt des JetBrains-Plugins
  src/main/resources/META-INF/plugin.xml
  src/main/resources/themes/             *.theme.json, *.xml (generiert)
vscode/                                  VS-Code-Erweiterung
  themes/*-color-theme.json              (generiert)
docs/                                    Vorschau
```
