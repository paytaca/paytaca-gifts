# paytaca-gifts
## Minimum requirements
- **Python: 3.8+**
- **Sanic: 21.9+**

## Build setup
```bash

# to setup virtualenv with python 3.8
virtualenv venv --python=python3.8

# activate virtualenv
source venv/bin/activate

# install dependencies
pip install sanic
pip install sanic[ext]
pip install tortoise-orm
```
## Development build
```bash
sanic main.app --dev
# or
sanic main.app --debug
```
## Production build
```bash
sanic main.app
```
Links to documentation page: 
- [http://localhost:8000/docs](http://localhost:8000/docs)
- [http://localhost:8000/docs/redoc](http://localhost:8000/docs/redoc)
- [http://localhost:8000/docs/swagger](http://localhost:8000/docs/swagger)
