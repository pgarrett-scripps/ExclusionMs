# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0]

### Added
- Added stress_tester.py script (Requires running ExclusionMSAPI)
- More API calls: load_or_clear_exclusion_list & get_log_entries
- Basic logging and timing decorator for exclusionms.apihandler
- Added exclusionms.random module to aid in making random exclusion interval and points
- Handler class to exclusionms.apihandler to allow for a single declaration of the exclusioms ip and args
- More tests
- Added MIT license

### Changed
- Moved version to init
- Converted repo to src-layout
- Switched to pyproject.toml
- Updated requirements.txt file with pip-tools
- Relaxed package dependency requirements

## [0.0.11]
### Removed
- Removed intensity tolerance log2foldchange

### Fixed
- Fixed interval.dict()
- Added Enum for Interval, Point, Tolerance keys

## [0.0.10]
### Fixed
- Fixed logic bug with sys.float.min

## [0.0.9]
### Changed
- Made intensity tolerance log2foldchange

### Added
- Added proper tolerance dict
