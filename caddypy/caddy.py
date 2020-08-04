import json

import requests


class Caddy:
    """
    Available methods

    1. `config(path=None, config_id=None)`
        Returns Caddy configuration.
        The `path` and `config_id` configurations are optional.
        Defaults to url: protocol://host:port/config/

        Can be customised by passing `path` or/and `config_id`

        If `config_id` and `path` both are provided, the `path` should be relative to the `config_id`

    2. `load(config)`
        Loads the configuration to the Caddy service.
        NOTE: This will override the previous Caddy configuration.
        `config` is required and either should be valid dict or valid json string

    3. `update()`
        Updates the Caddy configuration

    4. `delete()`
        Deletes the Caddy configuration
    """

    def __init__(self, host, port=2019, protocol='http', headers_origin=None):
        """
        Initialize Caddy object

        :param host: The host URL/IP address of the Caddy server
        :param port: The port on which Caddy server is running. Defaults to Caddy's default port `2019`
        :param protocol: Protocol to use. Either `http` or `https`. Defaults to `http`
        :param headers_origin: Put `Origin` header to use. If not set, will not send `Origin` headers.
        """
        self.host = host
        self.port = port
        self.protocol = protocol
        self.headers_origin = headers_origin

    def _generate_url(self):
        """
        Generate request host url

        :return:
            Base url of format protocol://host:port/
        """
        return '{}://{}:{}/'.format(self.protocol, self.host, self.port)

    def _generate_url_by_path(self, path=None, config_id=None):
        """
        Generates URL using path and config_id
        """

        _url = self._generate_url()

        if not path and not config_id:
            _url = '{}config/'.format(_url)

        if config_id:
            _url = '{}id/{}'.format(_url, config_id)

        if path:
            # Removes trailing slash (/) from left of the path
            _url = '{}/{}'.format(_url, path.lstrip('/'))

        return _url

    def _prepare_config_data(self, config):
        """
        Prepare config data and check for valid configuration.

        Following configurations are supported
        1. dic
        2. JSON string
        3. str

        If parsing failed, will raise JSONDecodeError
        """

        if not type(config) == dict:
            try:
                config = json.loads(config)
            except json.JSONDecodeError as e:
                if not type(config) == str:
                    raise json.JSONDecodeError(e.msg, e.doc, e.pos)

        return config

    def _execute(self, url, method='GET', data=None):
        """
        Execute the request
        """

        headers = {
            'Content-Type': 'application/json'
        }

        if self.headers_origin:
            headers['Origin'] = self.headers_origin

        data = json.dumps(data) if type(data) in [dict, str] else data
        print('data: {}'.format(data))

        res = requests.request(method, url, headers=headers, data=data)

        # Raise exception for non success response. Will raise HTTPError
        res.raise_for_status()

        return res.content

    def config(self, path=None, config_id=None, raw=False):
        f"""
        Get caddy config from the server

        :param path:
            Path of the config.
            If {config_id} is passed, the {path} should be relative to the {config_id}
        :param config_id:
            Get configuration by id.
            Example: `http://server:port/id/{config_id}[/{config_id}]
        :param raw:
            If True, will return raw response content. Otherwise will json parse the response content.
            If any error in the json parse, will return default content
        """

        _url = self._generate_url_by_path(path=path, config_id=config_id)
        res = self._execute(_url)

        if not raw:
            return json.loads(res)

        return res

    def load(self, config):
        """
        Load configuration to the Caddy server.

        NOTE: The previous config will be overridden.
        Check documentation: https://caddyserver.com/docs/api-tutorial
        """

        config = self._prepare_config_data(config)
        _url = self._generate_url_by_path(path='config/')

        return self._execute(_url, 'POST', config)

    def add(self, config, path, config_id=None):
        """
        Adds a new config to the Caddy's configuration

        The endpoint uses PUT method: https://caddyserver.com/docs/api#put-configpath

        Changes Caddy's configuration at the named path to the JSON body of the request.
        If the destination value is a position (index) in an array, PUT inserts;
        if an object, it strictly creates a new value.

        Example:
            ```
            c = Caddy(..)
            c.add('test.example.com', 'host/0', 'host')
            ```

            This will add `test.example.com` to the `host` array in the path were `@id` is `host` assuming the config
            ```
            {
                "@id": "host",
                "host": [
                    "example.com"
                ]
            }
            ```
        """

        config = self._prepare_config_data(config)
        _url = self._generate_url_by_path(path=path, config_id=config_id)

        return self._execute(_url, 'PUT', config)

    def update(self, config, path, config_id=None):
        """
        Update part of the configuration.

        This will use the PATCH method.
        Changes Caddy's configuration at the named path to the JSON body of the request.
        PATCH strictly replaces an existing value or array element.

        See: https://caddyserver.com/docs/api#patch-configpath

        Example:
            Assuming the following configuration
            ```
            {
                "@id": "host",
                "host": [
                    "test.example.com",
                    "example.com"
                ]
            }
            ```

            The usages
            ```
            c = Caddy(..)
            c.update('test2.example.com', 'host/0', 'host')
            ```

            It will update the `host` configuration at the index `0` with the new value. Thus the resulting config
            will be
            ```
            {
                "@id": "host",
                "host": [
                    "test2.example.com",
                    "example.com"
                ]
            }
            ```
        """

        config = self._prepare_config_data(config)
        _url = self._generate_url_by_path(path=path, config_id=config_id)

        return self._execute(_url, 'PATCH', config)

    def stop(self):
        """
        Gracefully shuts down the server and exits the process.
        To only stop the running configuration without exiting the process, use DELETE /config/.
        """

        _url = self._generate_url_by_path(path='stop')
        return self._execute(_url, 'POST')

    def delete(self, path):
        """
        Removes Caddy's configuration at the named path. DELETE deletes the target value.
        """

        _url = self._generate_url_by_path(path=path)

        return self._execute(_url, 'DELETE')
