# JWT Auth — Delta Spec

## ADDED

### Token Generation on Login
GIVEN a user submits valid credentials (email + password)
WHEN POST /auth/login is called
THEN the response is 200 with `{ token: <JWT string>, expiresIn: 3600 }`

### Token Rejection on Invalid Credentials
GIVEN a user submits an incorrect password or unknown email
WHEN POST /auth/login is called
THEN the response is 401 with `{ error: "Invalid credentials" }`

### Protected Route Access with Valid Token
GIVEN a valid JWT is present in the Authorization header as `Bearer <token>`
WHEN any protected route is requested
THEN the request proceeds and returns the expected resource

### Protected Route Rejection with Missing Token
GIVEN no Authorization header is present
WHEN any protected route is requested
THEN the response is 401 with `{ error: "No token provided" }`

### Protected Route Rejection with Expired Token
GIVEN an expired JWT is present in the Authorization header
WHEN any protected route is requested
THEN the response is 401 with `{ error: "Token expired" }`

### Protected Route Rejection with Malformed Token
GIVEN a malformed or tampered JWT is present in the Authorization header
WHEN any protected route is requested
THEN the response is 401 with `{ error: "Invalid token" }`

### Token Refresh
GIVEN a valid (non-expired) JWT is present in the Authorization header
WHEN POST /auth/refresh is called
THEN the response is 200 with a new `{ token: <JWT string>, expiresIn: 3600 }`

### Logout / Token Revocation
GIVEN a valid JWT is present in the Authorization header
WHEN POST /auth/logout is called
THEN the response is 200 with `{ message: "Logged out" }` and the token is invalidated for future requests
