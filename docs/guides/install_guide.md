# Install Guide
The following guide will show you how to install and set up your own Remedicado server

## Pre-req

Before you can install anything you will need to download and set up the following components:
* The remedicado system from [github](https://github.com/Sam-Clutterbuck/remedicado)
    * Before downloading you should also decide which plugins you require if any
* Latest stable release of Python 
* The packages listed in the [requirements.txt](../../requirements.txt)
* A MySQL server *(either locally or on your network)*

## Installation steps

### Set up the sql database

1. Deploy the sql database
2. Add the database details to the [config file](../../data/remedicado_config.yaml) including 
    ```
    host: <localhost / MySQL server ip>
    database: remedicado <or alternate name>
    db_user: <database username>
    db_pass: <database password>
    ```
3. Once the database details are added to config file configure the database tables following the format listed in the [sql_database_structure](../sql_database_structure.md)
4. Create a default user for system 
    ```
    INSERT INTO accounts (username, salt, password) 
    VALUES (admin, 056940668ef070eed781b45b06f0d7eb3e147ef7c0fcba33625f72af268d59075ad51b785321695cd6bb608f1a4df817337a644fe7b7f1fa19c2117960323932,
    2f020a84144f04edfd9760decbf95e69795c24ef91e23a813875801f9fb8c90c);

    ```
    This SQL command creates a default account with the following credentials
    
    default username : `admin`

    default password : `avacado`

### System Setup

1. Install the Remedicado packages in a central location on your server.
2. Set up permissions to only allow root access to the `/web`, `/src`, `/data` directories. This will stop unauthenticated users from adding to or editing code or the uploaded / created files.
3. Install the required plugins to the `/src/plugins` directory and add the plugins verified hash to the `/data/valid_plugins.yaml` file