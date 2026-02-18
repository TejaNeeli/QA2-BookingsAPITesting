# Deploying to Heroku

## Prerequisites

- Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- Create a free [Heroku account](https://signup.heroku.com/)

## Steps

1. **Login to Heroku:**
   ```sh
   heroku login
   ```

2. **Create a new Heroku app:**
   ```sh
   heroku create
   ```
   This will create a new app and give you a URL (e.g., `https://your-app-name.herokuapp.com/`).

   > **If you see an error like `heroku: command not found`, make sure the Heroku CLI is installed and available in your PATH.**
   >
   > **If you see an error about authentication, make sure you are logged in using `heroku login`.**
   >
   > **If you want to specify a custom app name:**
   > ```
   > heroku create your-custom-app-name
   > ```

3. **Prepare your project:**
   - Ensure you have a `requirements.txt` file listing all Python dependencies.
   - Add a `Procfile` in your project root with the following content:
     ```
     web: gunicorn app:app
     ```
     (Assuming your Flask app is in `app.py` and the Flask instance is named `app`.)

4. **Initialize git (if not already):**
   ```sh
   git init
   git add .
   git commit -m "Initial commit"
   ```

   > **If you see `error: src refspec master does not match any`, it means you have not created a branch named `master` or have not made an initial commit.**
   > 
   > **To fix:**
   > 1. Make sure you have committed at least once (see above).
   > 2. If your default branch is `main` (common with newer git versions), push using:  
   >    ```
   >    git push heroku main
   >    ```
   >    instead of  
   >    ```
   >    git push heroku master
   >    ```

   > **If you see `fatal: 'heroku' does not appear to be a git repository`, you need to add the Heroku remote.**
   > 
   > **To fix:**
   > 1. Run:
   >    ```
   >    heroku git:remote -a your-app-name
   >    ```
   >    Replace `your-app-name` with the name given by `heroku create` or visible in your Heroku dashboard.
   > 2. Then push again:
   >    ```
   >    git push heroku main
   >    ```
   >    (or `master` if your branch is named master)

5. **Deploy to Heroku:**
   ```sh
   git push heroku main
   ```
   *(or use `master` if your branch is named master)*

6. **Open your app:**
   ```sh
   heroku open
   ```

## Notes

- If you use files or directories for logs/reports, ensure they are created at runtime, as Heroku's filesystem is ephemeral.
- For persistent storage, use an external service (e.g., AWS S3, Heroku Postgres).
