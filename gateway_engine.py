"""Auth0 Management API gateway. Requires a configured machine-to-machine application."""
import json
import os
import re
from urllib.request import Request, urlopen
from urllib.parse import quote

class LuxeraAuth0Gateway:
    def __init__(self, domain, client_id, client_secret):
        if not re.fullmatch(r"[A-Za-z0-9.-]+", domain or "") or not client_id or not client_secret:
            raise ValueError("Valid Auth0 domain and credentials required")
        self.base = "https://" + domain
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None

    def _request(self, path, payload, authenticated=True):
        headers = {"Content-Type": "application/json"}
        if authenticated:
            if not self.token:
                self.token = self._request("/oauth/token", {"grant_type":"client_credentials","client_id":self.client_id,"client_secret":self.client_secret,"audience":self.base+"/api/v2/"}, False)["access_token"]
            headers["Authorization"] = "Bearer " + self.token
        with urlopen(Request(self.base + path, data=json.dumps(payload).encode(), headers=headers, method="POST"), timeout=30) as response:
            body = response.read()
            return json.loads(body) if body else None

    def provision_tenant_organization(self, organization_name, display_name):
        slug = re.sub(r"[^a-z0-9_-]", "", organization_name.lower().replace(" ", "-"))
        if not slug or len(slug) > 50:
            raise ValueError("Invalid organization name")
        return self._request("/api/v2/organizations", {"name":slug,"display_name":display_name})

    def enforce_granular_rbac(self, user_id, organization_id, target_role):
        roles = {"b2b_admin":"AUTH0_ADMIN_ROLE_ID","b2b_team":"AUTH0_TEAM_ROLE_ID","b2b_member":"AUTH0_MEMBER_ROLE_ID"}
        if target_role not in roles:
            raise ValueError("Unknown role")
        role_id = os.environ.get(roles[target_role])
        if not role_id:
            raise ValueError("Configured Auth0 role ID required")
        path = "/api/v2/organizations/" + quote(organization_id,safe="") + "/members/" + quote(user_id,safe="") + "/roles"
        self._request(path, {"roles":[role_id]})
        return {"role_assignment_accepted":True,"role_id":role_id}

class PromptArchitectEngine:
    def trim_contextual_tokens(self, raw_user_input):
        return raw_user_input

if __name__ == "__main__":
    print("Import LuxeraAuth0Gateway with configured credentials. No organizations are created automatically.")
