# Changelog

## 0.4.4

-  Do not call any command unless all arguments are valid (#8)

## 0.4.3

- removed usage of reserved pyton 3.7 keyword `async`

### 0.4.0

- allow to chain commands (`script.py command1 arg1 command2 arg2`)
- fixed command registered multiple time when chaining @cli calls
- `_` in command name are replaced by `-` (but original name is kept as alias)
- fixed arbitrary callable as annotation not working with kwargs

## 0.3.0

- added `@wrap` decorator as before/after hook
- BREAKING: removed support for python 3.5 and above

## 0.2.0

- allow to override parser options (`name`…)

## 0.1.0

First release.
