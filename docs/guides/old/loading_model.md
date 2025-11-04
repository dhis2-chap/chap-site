# Loading your model into Chap

After you have configured your new model in the Chap model configurations, you will need to restart your Chap server. You can do this with:

        >>> docker compose down
        >>> docker compose up

When you start up the Chap server again, Chap will automatically detect and add newly added models that don't already exist in its database. 
