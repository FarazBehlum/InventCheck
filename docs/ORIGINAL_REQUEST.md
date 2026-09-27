Build me a complete working MVP of a personal price-comparison and local inventory-checking web app inspired by BrickSeek.

The goal is NOT to copy BrickSeek's proprietary system or bypass its subscription. I want my own tool that uses publicly accessible information, retailer-approved APIs where available, and normal public retailer webpages where permitted.

The app should let me enter a UPC, SKU, model number, or product name and compare prices and local availability across multiple retailers.

Start with a clean, working MVP that runs locally on my computer.

TECH STACK

Use:

Frontend:
- React
- TypeScript
- Vite
- Tailwind CSS

Backend:
- Python
- FastAPI

Database:
- SQLite for the first version
- Structure the database layer so Supabase/PostgreSQL can replace SQLite later without rewriting the entire app

Use a simple, modern interface. Do not overengineer the design.

CORE USER FLOW

The homepage should contain:

1. Product search field
   - UPC
   - SKU
   - model number
   - product name

2. ZIP code field

3. Search-radius selector
   - 5 miles
   - 10 miles
   - 25 miles
   - 50 miles

4. Retailer selector

Start with architecture for:
- Walmart
- Target
- Home Depot
- Lowe's
- Best Buy

Not every retailer has to work immediately if there is no legitimate public data source available.

Do NOT fake live retailer data.

If live integration cannot safely or reliably be implemented for a retailer, create a clearly separated adapter interface and use sample/mock data for development.

SEARCH RESULTS

Show results in a table or cards containing:

- Product image
- Product name
- Retailer
- Store name
- Store address
- Distance
- Regular price
- Current price
- Discount percentage
- Inventory status
- Quantity if legitimately available
- Last checked time
- Link to the retailer product page

Possible inventory statuses:

- In stock
- Limited stock
- Out of stock
- Unknown

Allow sorting by:

- Lowest price
- Largest discount
- Closest store
- In-stock first

Allow filtering by:

- Retailer
- Maximum distance
- In-stock only
- Price range

RETAILER ARCHITECTURE

Create a retailer adapter system.

Use a common interface similar to:

RetailerAdapter

Methods:
- search_product()
- get_product_details()
- get_nearby_stores()
- get_store_price()
- get_inventory()

Each retailer should have its own implementation.

Example:

adapters/
    base.py
    walmart.py
    target.py
    homedepot.py
    lowes.py
    bestbuy.py

This is important because I want to add additional stores later without rewriting the application.

DATA COLLECTION RULES

Do not:

- bypass CAPTCHAs
- bypass login systems
- bypass paywalls
- defeat anti-bot protections
- rotate proxies to avoid restrictions
- impersonate authenticated users
- access private APIs without authorization
- circumvent retailer rate limits

Prefer, in this order:

1. Official retailer APIs
2. Public retailer endpoints explicitly accessible without authentication
3. Public structured product data such as JSON-LD
4. Normal publicly accessible product/store webpages where use is permitted
5. Mock provider during development

If a retailer blocks automated access, mark that adapter as unavailable rather than trying to bypass it.

Keep all retailer-specific logic isolated from the rest of the application.

PRODUCT MATCHING

Products across stores may have different names.

Create normalized product matching using, when available:

- UPC
- GTIN
- SKU
- manufacturer model number
- brand
- product title

Exact UPC/GTIN/model matches should receive the highest confidence.

If matching only by product name, show a match-confidence indicator.

DATABASE

Create tables for:

products

Fields should include:
- id
- upc
- gtin
- model_number
- brand
- name
- image_url
- created_at

retailers

Fields:
- id
- name
- website

stores

Fields:
- id
- retailer_id
- store_identifier
- name
- address
- city
- state
- zip
- latitude
- longitude

price_checks

Fields:
- id
- product_id
- store_id
- price
- regular_price
- inventory_status
- inventory_quantity
- checked_at

watchlist

Fields:
- id
- product_id
- target_price
- zip_code
- radius
- created_at

PRICE HISTORY

Save every legitimate price check.

Create a product detail page showing:

- current lowest price
- highest observed price
- lowest observed price
- price history over time
- retailer comparison

Use a simple chart for price history.

WATCHLIST

Allow me to save products.

For each saved product, let me configure:

- target price
- preferred retailers
- ZIP code
- search radius

Create the backend structure for alerts.

For the MVP, alerts can simply appear inside the app.

Structure the notification service so email or SMS can be added later.

LOCATION

Convert ZIP codes into approximate latitude/longitude using a legitimate geocoding source or local ZIP-code dataset.

Calculate store distance using latitude and longitude.

Do not require browser GPS.

BACKEND API

Create REST endpoints similar to:

GET /api/search

GET /api/products/{id}

GET /api/products/{id}/prices

GET /api/products/{id}/history

GET /api/stores

POST /api/watchlist

GET /api/watchlist

DELETE /api/watchlist/{id}

GET /api/health

Use Pydantic models and proper validation.

PROJECT STRUCTURE

Use a clean repository layout such as:

brickseek-alternative/

    frontend/

    backend/

        app/

            main.py

            api/

            models/

            schemas/

            services/

            adapters/

            database/

            utils/

        tests/

        requirements.txt

    README.md

    .env.example

    .gitignore

ENVIRONMENT VARIABLES

Do not hard-code secrets.

Put API keys and configuration in environment variables.

Include .env.example.

The application should still run in demonstration mode when API keys are unavailable.

DEMO MODE

Create a DEMO_MODE option.

When DEMO_MODE=true:

- return realistic sample products
- return sample nearby stores
- return sample prices
- return different inventory statuses

Make it obvious in the UI when results are demo data.

Never present sample data as live information.

ERROR HANDLING

Handle situations such as:

- product not found
- retailer unavailable
- retailer timeout
- invalid ZIP code
- missing API credentials
- no nearby stores
- malformed retailer response
- rate limiting

One retailer failing should not cause the entire search to fail.

Show results from retailers that completed successfully.

PERFORMANCE

Search retailers concurrently where reasonable.

Add:

- request timeouts
- basic caching
- retries only where appropriate
- structured logging

Do not hammer retailer websites.

TESTING

Create automated tests for:

- product normalization
- UPC matching
- price calculations
- discount calculations
- distance calculations
- retailer adapter failures
- database operations
- API validation

Include at least one mocked retailer-adapter integration test.

USER INTERFACE

Pages:

1. Search
2. Search Results
3. Product Details
4. Watchlist
5. Settings/About

The Search Results page should clearly highlight:

- cheapest price
- nearest in-stock store
- largest discount

Do not claim that inventory is guaranteed.

Display a notice such as:

"Store inventory and pricing can change quickly. Verify with the retailer before traveling to the store."

DESIGN

Keep the interface clean and practical.

Desktop and mobile responsive.

Use a dashboard-style layout.

Prioritize usability over animations.

DOCUMENTATION

Write a thorough README that includes:

- what the application does
- architecture
- prerequisites
- installation
- backend setup
- frontend setup
- environment variables
- running in demo mode
- running tests
- adding a new retailer
- known limitations

Also create:

ARCHITECTURE.md

Explain:
- frontend/backend communication
- database structure
- retailer adapter pattern
- product normalization
- caching
- error handling

Create:

RETAILERS.md

For each retailer document:

- integration status
- data source being used
- credentials required
- fields available
- limitations
- whether inventory quantity is available
- whether store-level pricing is available

IMPLEMENTATION ORDER

Build this in stages.

Stage 1:
Create the repository structure and README.

Stage 2:
Build the FastAPI backend.

Stage 3:
Create the retailer adapter interface.

Stage 4:
Implement demo retailer adapters.

Stage 5:
Build the React frontend.

Stage 6:
Connect frontend and backend.

Stage 7:
Add SQLite persistence.

Stage 8:
Add price history.

Stage 9:
Add watchlist.

Stage 10:
Research legitimate live-data integrations for the five retailers.

Stage 11:
Implement only integrations that can be accessed appropriately.

Stage 12:
Add tests and fix errors.

Stage 13:
Run the entire application and verify the main workflow.

IMPORTANT WORKING INSTRUCTIONS

Do not stop after merely generating starter files.

Actually implement the working MVP.

After each major stage:

- run the relevant code
- resolve compilation errors
- run tests
- fix failures before continuing

Do not leave placeholder functions where a working implementation can reasonably be created.

If a live retailer integration cannot be completed legitimately, keep that retailer running through DEMO_MODE and document exactly what is missing.

Do not invent APIs, endpoint URLs, API keys, or retailer capabilities.

When you are unsure whether a retailer endpoint is legitimate or current, research it before implementing it.

At completion:

1. Run backend tests.
2. Run frontend build.
3. Start the backend.
4. Verify the health endpoint.
5. Verify a demo search.
6. Verify sorting and filtering.
7. Verify the watchlist.
8. Verify price history.
9. Fix any errors found.
10. Update README with the final working instructions.

Finally, give me a short summary containing:

- what was built
- which retailers currently have live integrations
- which retailers use demo adapters
- exact commands to run the project
- known limitations
- the next three features you recommend implementing

The priority is reliability and a working foundation. Do not sacrifice functionality just to make the interface look fancy.