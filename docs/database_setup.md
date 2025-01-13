## Database Setup

Follow these steps to configure the database for your project:

### Create a `.env` File

Create a `.env` file in the root directory of your project to store sensitive environment variables securely. Add the following content to the file:

```env
# Database Configuration
DATABASE_NAME={your_database_name}
DATABASE_USER={your_database_user}
DATABASE_PASSWORD={your_database_password}
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Secret Key
SECRET_KEY=your_secret_key

# Debug Mode
DEBUG=True
```