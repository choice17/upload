# Miscellaneous


1. linter

A. prettier online gui for webpage code

https://www.10bestdesign.com/dirtymarkup/

B. nodejs package

* prettier - https://prettier.io/
* eslint - https://eslint.org/
* stylelint - https://stylelint.io/

```bash
# for css
$ npx prettier --write css/
$ npx stylelint --fix css/

# for js
$ npx prettier --write js/
$ npx eslint --fix js/
```


C. clang-format ex.

`$ find . -name "*.[ch]" -exec clang-format-8 -i {} \;`

