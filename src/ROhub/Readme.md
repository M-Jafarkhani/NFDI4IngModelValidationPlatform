# Installation for using the package ROhub with the development server
Install the package via pip (in conda) using the options

`--editable=git+https://gitlab.pcss.pl/daisd-public/rohub/rohub-api.git#egg=rohub`

Find the location of the local installation (`pip show rohub`) and copy the file `.env` into this directory using a single command:

```bash
cp -v .env "$(pip show rohub | awk -F': ' '/Editable project location/ {print $2}')/.env"
```

