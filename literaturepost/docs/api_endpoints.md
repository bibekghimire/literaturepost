# API Endpoints
## Authentication Endpoints (JWT-based)
- `POST /api/login/` — Get access & refresh tokens  
- `POST /api/token/refresh/` — Refresh access token  
- `POST /api/token/verify/` — Verify token validity
- `POST /api/logout/` - Logout 

## Literature Endpoints /api/literature
### type: poem, gajal, story, chhanda
- `GET /public/<str: type> ` - List all Published <literature:type>
- `GET /public/<str: type>/id`- Retrieve specific <literature:type> by ID
- `GET /user/uuid/<str: type>` - List All <literature:type> for specific user by UUID
- `GET /user/uuid/<str: type>/id` - Retrieve specific <literature:type> of specific user by user UUID and <literature:type> ID
- `GET /user/<uuid:uuid>/<str:type>/<int:id>` - Retrieve specific <literature:type> by ID created by the user with uuid: uuid
- `GET /admin/<str: type>/all` - List All <literature:type>
- `POST /public/<str: type>` - Post a literature of type: type
- `PUT /public/<str: type>/id` - Update literature of type: type with id
- `PATCH /public/<str: type>/id` - Partial Update literature of type: type with id
- `DELETE /public/<str: type>/id` - DELETE literature of type: type with id
- `PUT /user/<uuid:uuid>/<str:type>/<int:id>` - Update specific <literature:type> by ID created by the user with uuid: uuid
- `PATCH /user/<uuid:uuid>/<str:type>/<int:id>` - Partial Update specific <literature:type> by ID created by the user with uuid: uuid
- `DELETE /user/<uuid:uuid>/<str:type>/<int:id>` - DELETE specific <literature:type> by ID created by the user with uuid: uuid

#### Example: poems
- `GET /public/poem ` - List all Published poem
- `GET /public/poem/id`- Retrieve specific poem by ID
- `GET /user/uuid/poem` - List All poem for specific user by UUID
- `GET /user/uuid/poem/id` - Retrieve specific poem of specific user by user UUID and poem ID
- `GET /user/<uuid:uuid>/<str:type>/<int:id>` - Retrieve specific poem by ID created by the user with uuid: uuid
- `GET /admin/poem/all` - List All poem
- `POST /public/poem` - Post a literature of type: type
- `PUT /public/poem/id` - Update literature of type: type with id
- `PATCH /public/poem/id` - Partial Update literature of type: type with id
- `DELETE /public/poem/id` - DELETE literature of type: type with id
- `PUT /user/<uuid:uuid>/<str:type>/<int:id>` - Update specific poem by ID created by the user with uuid: uuid
- `PATCH /user/<uuid:uuid>/<str:type>/<int:id>` - Partial Update specific poem by ID created by the user with uuid: uuid
- `DELETE /user/<uuid:uuid>/<str:type>/<int:id>` - DELETE specific poem by ID created by the user with uuid: uuid
