# Changelog


## Current master

[Full Changelog](https://github.com/pubs/pubs/compare/v0.8.2...master)

### Implemented enhancements

- New git plugin to commit changes to the repository ([#193](https://github.com/pubs/pubs/pull/193) by [Amlesh Sivanantham](http://github.com/zamlz))

- Add `citekey` filter to `query` ([#191(https://github.com/pubs/pubs/pull/191) by [Shane Stone](https://github.com/shanewstone))

- The `--config` and `--force-colors` command line options now appear when invoking `pubs --help`

### Fixed bugs


## [v0.8.2](https://github.com/pubs/pubs/compare/v0.8.1...v0.8.2) (2019-01-06)

Fixes install on python2, and adding old-style arXiv references.

### Fixed bugs

- Fixes adding papers with slashes in their citekeys. [(#179)](https://github.com/pubs/pubs/pull/179) (thanks [Amlesh Sivanantham](https://github.com/zamlz) for reporting.)
- Fix missing readme.md for python2 pip install. [(#174)](https://github.com/pubs/pubs/pull/174)

### Implemented enhancements

- [(#45)](https://github.com/pubs/pubs/issues/45) Doc extension visible in pubs list ([#168](https://github.com/pubs/pubs/pull/168))


## [v0.8.1](https://github.com/pubs/pubs/compare/v0.8.0...v0.8.1) (2018-08-28)

A hotfix release. All users of 0.8.0 are urged to upgrade.

### Fixed bugs

- Fix adding paper with DOIs, ISBNs or arXiv references. [(#165)](https://github.com/pubs/pubs/pull/165)

- Fix statistics command when there is not yet any paper in the repository. [(#164)](https://github.com/pubs/pubs/pull/164)


## [v0.8.0](https://github.com/pubs/pubs/compare/v0.7.0...v0.8.0) (2018-08-20)

A long overdue feature release. Add supports for arXiv bibtex fetching, and many other enhancements.

### Implemented enhancements

- Adds `move`, and `link` options for handling of documents during `import` (copy being the default). Makes `copy` the default for document handling during `add`. [(#159)](https://github.com/pubs/pubs/pull/159)

- Support for downloading arXiv reference from their ID ([#146](https://github.com/pubs/pubs/issues/146) by [joe-antognini](https://github.com/joe-antognini))

- Better feedback when an error is encountered while adding a reference from a DOI, ISBN or arXiv ID [#155](https://github.com/pubs/pubs/issues/155)

- Better dialog after editing paper [(#142)](https://github.com/pubs/pubs/issues/142)

- Add a command to open urls ([#139](https://github.com/pubs/pubs/issues/139) by [ksunden](https://github.com/ksunden))

- More robust cache on version change [(#138)](https://github.com/pubs/pubs/issues/138)

- Allow utf8 citekeys [(#133)](https://github.com/pubs/pubs/issues/133)

- Adds tag list completion in `pubs add -t ` [(#130)](https://github.com/pubs/pubs/issues/130)

- Wider Travis coverage ([#107](https://github.com/pubs/pubs/issues/107) and [#108](https://github.com/pubs/pubs/issues/108))

- Uses bibtexparser bwriter instead of internal encoder and adds `--ignore-fields` option to export. [(#106)](https://github.com/pubs/pubs/issues/106)

- Configurable alias descriptions ([#104](https://github.com/pubs/pubs/issues/104) by [wflynny](https://github.com/wflynny))

- Support year ranges in query [(#102)](https://github.com/pubs/pubs/issues/102)

- Tests can now be run with `python setup.py test` [#155](https://github.com/pubs/pubs/issues/155)

### Fixed bugs

- [[#144]](https://github.com/pubs/pubs/issues/144) More robust handling of the `doc_add` options [(#159)](https://github.com/pubs/pubs/pull/159)

- [[#149]](https://github.com/pubs/pubs/issues/149) More robust handling of parsing and citekey errors [(#87)](https://github.com/pubs/pubs/pull/87)

- [[#148]](https://github.com/pubs/pubs/issues/148) Fix compatibility with Pyfakefs 3.7 [(#151)](https://github.com/pubs/pubs/pull/151)

- [[#95]](https://github.com/pubs/pubs/issues/95) Error message when editor is missing [(#141)](https://github.com/pubs/pubs/issues/141)

- Fixes tests for printing help on `--help` and without argument. [(#137)](https://github.com/pubs/pubs/issues/137)

- [[#126]](https://github.com/pubs/pubs/issues/126) Removes journal customization [(#127)](https://github.com/pubs/pubs/issues/127)

- Fixes Travis failure on installing python3 for OSX [(#125)](https://github.com/pubs/pubs/issues/125)

- [[#119]](https://github.com/pubs/pubs/issues/119) Removes link and DOI customization. [(#124)](https://github.com/pubs/pubs/issues/124)

- [[#122]](https://github.com/pubs/pubs/issues/122) Fixes common strings [(#123)](https://github.com/pubs/pubs/issues/123)

- [[#28]](https://github.com/pubs/pubs/issues/28) allow utf8 in citekeys [(#120)](https://github.com/pubs/pubs/issues/120)

- Fixes field orders to use 'url' and fixes broken test. [(#118)](https://github.com/pubs/pubs/issues/118)

- [[#25]](https://github.com/pubs/pubs/issues/25) Fix bibtex testcase [(#117)](https://github.com/pubs/pubs/issues/117)

- [[#103]](https://github.com/pubs/pubs/issues/103) Fixes unicode comparison [(#116)](https://github.com/pubs/pubs/issues/116)

- [[#95]](https://github.com/pubs/pubs/issues/95) robust handling of DOIs ([#105](https://github.com/pubs/pubs/issues/105) by [wflynny](https://github.com/wflynny))

- [[#99]](https://github.com/pubs/pubs/issues/99) Print help when no subcommand is provided ([#100](https://github.com/pubs/pubs/issues/100) by [wflynny](https://github.com/wflynny))

- Fix defaults not used in config. [(#97)](https://github.com/pubs/pubs/issues/97)

- Fixes content not read from urls because of call to `os.abspath` [(#96)](https://github.com/pubs/pubs/issues/96)

- [[#93]](https://github.com/pubs/pubs/issues/93) actually save the modifications on `edit -m`. [(#94)](https://github.com/pubs/pubs/issues/94)

- [[#88]](https://github.com/pubs/pubs/issues/88) Adds proper escaping for
arguments in alias plugin. [(#91)](https://github.com/pubs/pubs/issues/91)


## [v0.7.0](https://github.com/pubs/pubs/compare/v0.6.0...v0.7.0) (2017-08-06)

[Full Changelog](https://github.com/pubs/pubs/compare/v0.6.0...v0.7.0)
