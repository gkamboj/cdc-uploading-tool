import os

import connexion

from config.configuration import configs


swagger_path = os.path.join(os.path.dirname(__file__), 'apis', 'swagger.yml')
app = connexion.App('__name__')
app.add_api(swagger_path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=configs['app.port'])
