## Database Setup

Follow these steps to configure the database for your project:

### Create a `.env` File

Create a `.env` file in the root directory of your project `(./blog_app)` to store sensitive environment variables securely. Add the following content to the file:

```env
# Database Configuration
DB_NAME={your_database_name}
DB_USER={your_database_user}
DB_PASSWORD={your_database_password}
DB_HOST=localhost
DB_PORT=5432

# Secret Key
SECRET_KEY=your_secret_key

# Debug Mode
DEBUG=True
```

***Note:*** Ensure that the database name matches the value assigned to `DB_NAME` in the `.env` file. Create this database before running migrations.