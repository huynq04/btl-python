## Authentication Endpoints
- **POST** `/identity/auth/token`
- **POST** `/identity/auth/introspect`
- **POST** `/identity/auth/logout`
- **POST** `/identity/auth/refresh`
- **POST** `/identity/auth/outbound/authentication`

# Khánh
## File Endpoints
- **GET** `/identity/api/v1/file/{slug}`
- **POST** `/identity/api/v1/file/add/{slug}`
- **GET** `/identity/api/v1/file/document/{id}`
- **DELETE** `/identity/api/v1/file/document/{id}`
- **DELETE** `/identity/api/v1/file/document`

# Minh
## Folder Endpoints
- **GET** `/identity/api/v1/folder`
- **POST** `/identity/api/v1/folder/add`
- **DELETE** `/identity/api/v1/folder/delete`

## OTP Endpoints
- **GET** `/identity/api/v1/otp/send-otp/{username}`
- **POST** `/identity/api/v1/check-otp/{username}`

## Search Endpoints
- **GET** `/identity/api/v1/search`

## User Document Endpoints
- **GET** `/identity/users/my-documents`

# Tân cc
## Favorites Endpoints
- **PUT** `/identity/users/my-favorites/add/{id}`
- **DELETE** `/identity/users/my-favorites/delete/{id}`
- **GET** `/identity/users/my-favorites`

## User Endpoints
- **POST** `/identity/users`
- **GET** `/identity/users/myInfo`
- **PUT** `/identity/users/{userId}`
- **PUT** `/identity/users/update-picture/{userId}`
- **POST** `/identity/users/activate`
- **GET** `/identity/users/get-hidden-email/{username}`
- **PUT** `/identity/users/change-password`
- **PUT** `/identity/users/reset-password`
