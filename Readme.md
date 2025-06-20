## Menginstall Virtual Environment
python -m venv skripsi

## Mengaktifkan Virtual Environment
skripsi\scripts\activate

## Install library
pip install -r requirements.txt

## Mendaftarken environment sebagai kernel di Jupyter
python -m ipykernel install --user --name=skripsi --display-name "Python (skripsi)"

## Membuka file jupyter notebook
jupyter notebook

## Stop kernel jupyter
ctrl+c

## Menonaktifkan virtual environment
deactivate