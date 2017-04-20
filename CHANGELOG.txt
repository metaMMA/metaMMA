# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]
### Added
- Retrieve meta-data for Rizin FF.
- Add more web addresses to look for LFA poster.
- Add basic meta-data for Victory Fighting Championship

### Changed

## [0.3.13] - 2017-04-19
### Added
- Properly move and rename "Bellator Kickboxing" when it is a preliminary card.
- Added CHANGELOG.md.

### Changed
- updater.py will no longer hang indefinitely if there is no internet connection when attempting to access github.com.
- Consolidated block of code in mover.py that moves video files different places depending on card name.
- Legacy Fighting Alliance events will be moved if named "Legacy Fighting Alliance" or "LFA"
