You are a coding assistant. Your task is to generate a **self-contained example project** demonstrating Clerk user authentication with Python FastAPI. This project is a learning boilerplate for developers to understand the login → JWT → backend verification flow. It should be fully runnable, heavily commented, and include detailed logging.

---

### Project Requirements

#### 1. Backend (FastAPI)

- Use **FastAPI**, **uvicorn**, **python-dotenv**, **clerk-backend-api**, and **httpx**.
- Serve both backend API endpoints **and the frontend page**.
- Endpoints:

1. `/` (GET)
   - Serves a simple HTML page with embedded JS (frontend) for login and fetching user data.
2. `/auth/login` (GET)
   - Returns JSON `{ "redirect_url": "<Clerk hosted sign-in URL>" }`.
   - Uses `CLERK_FRONTEND_API` from `.env` and appends the redirect URL to the frontend page.
3. `/users/me` (GET)
   - Protected endpoint: requires JWT from `Authorization: Bearer <token>` or `__session` cookie.
   - Verifies JWT using `clerk.authenticate_request()`.
   - On success, fetches user info from Clerk API and returns JSON `{ "clerk_user_id": ..., "email": ..., ... }`.
   - On failure, returns HTTP 401 with detailed logging.
4. `/debug/token` (optional, POST)
   - Accepts a raw JWT and decodes it without verification (for debugging).

- Include middleware to log:
  - All requests: path, method, headers.
  - JWT verification results: success/failure, user ID, or error messages.
  - Responses returned to the client.

- Load environment variables from `.env`:
```

CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
CLERK_FRONTEND_API=clerk.<region>.accounts.dev
REDIRECT_URL=[http://localhost:8000/](http://localhost:8000/)

````

---

#### 2. Frontend (served from FastAPI)

- Serve a **single HTML + JS page** from `/`.
- Use Clerk frontend SDK via:
```html
<script src="https://cdn.jsdelivr.net/npm/@clerk/clerk-js@latest"></script>
````

* Workflow:

  1. Initialize Clerk with `window.Clerk.load({ publishableKey: "<CLERK_PUBLISHABLE_KEY>" })`.
  2. If not signed in:

     * Display a “Login with Clerk” button.
     * On click, call `/auth/login`, get redirect URL, redirect user to Clerk hosted login page.
  3. After redirect back:

     * Use `await Clerk.session.getToken()` to retrieve JWT.
     * Call `/users/me` with `Authorization: Bearer <token>`.
     * Display JSON result on screen.
  4. Include `console.log()` for each step: token retrieval, API calls, and errors.

* Keep frontend minimal and self-contained; no frameworks required.

---

#### 3. File Structure

```
clerk_fastapi_demo/
│
├── main.py             # FastAPI backend + frontend serving
├── .env                # Environment variables for Clerk
├── requirements.txt    # Dependencies
└── templates/
    └── index.html      # Frontend page
```

---

#### 4. Logging & Debugging

* Backend must log:

  * Incoming requests and headers.
  * Token verification success/failure, user ID, and error messages.
  * API responses.
* Frontend must log:

  * Token retrieval success/failure.
  * API responses and errors.
* Include enough detail so a developer can trace the **entire Clerk login → JWT → API verification flow**.

---

#### 5. Optional Enhancements

* Add `/debug/token` to decode JWT for inspection.
* Handle CORS for localhost if necessary.
* Include comments in all files explaining each step of the flow.
* Include a `README.md` explaining:

  * How to configure Clerk keys.
  * How the login and JWT verification flow works.
  * How to run the demo project.

---

#### Deliverable Requirements

* Fully working codebase.
* Self-contained and runnable on localhost.
* Minimal frontend + Python FastAPI backend.
* Detailed comments and logging for educational purposes.

---

Your output should be a **ready-to-run codebase**, with all files and content written inline, using code blocks for file separation. Ensure the generated code is fully functional and can be run for testing Clerk authentication and JWT verification.

```
