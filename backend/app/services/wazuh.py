import json
import requests
from requests.auth import HTTPBasicAuth


class WazuhClient:
    def __init__(self, base_url: str, username: str, password: str, verify_ssl: bool = False):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.token = None

    def authenticate(self):
        r = requests.post(
            f'{self.base_url}/security/user/authenticate?raw=true',
            auth=HTTPBasicAuth(self.username, self.password),
            verify=self.verify_ssl,
            timeout=20,
        )
        r.raise_for_status()
        self.token = r.text.strip()
        return self.token

    def _headers(self):
        if not self.token:
            self.authenticate()
        return {'Authorization': f'Bearer {self.token}'}

    def list_agents(self):
        r = requests.get(f'{self.base_url}/agents', headers=self._headers(), verify=self.verify_ssl, timeout=20)
        r.raise_for_status()
        return r.json()

    def health(self):
        r = requests.get(f'{self.base_url}/manager/status', headers=self._headers(), verify=self.verify_ssl, timeout=20)
        r.raise_for_status()
        return r.json()


class WazuhIndexerClient:
    def __init__(self, base_url: str, username: str, password: str, verify_ssl: bool = False):
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
        self.verify_ssl = verify_ssl

    def search_alerts(self, limit: int = 50):
        query = {
            'size': limit,
            'sort': [{'@timestamp': {'order': 'desc'}}],
            '_source': ['agent.name', 'rule.level', 'rule.description', '@timestamp'],
            'query': {'match_all': {}}
        }
        r = requests.get(
            f'{self.base_url}/wazuh-alerts-*/_search',
            auth=self.auth,
            verify=self.verify_ssl,
            timeout=20,
            data=json.dumps(query),
            headers={'Content-Type': 'application/json'},
        )
        r.raise_for_status()
        return r.json()
