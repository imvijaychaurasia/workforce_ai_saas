import Keycloak from "keycloak-js";

const keycloak = new Keycloak({
  url: "http://localhost:8080",
  realm: "saas-platform",
  clientId: "saas-frontend",
});

export default keycloak;
